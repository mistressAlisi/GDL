import json
from datetime import timedelta, datetime

from asgiref.sync import sync_to_async
from django.db import transaction
from django.http import JsonResponse
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET

from game.gdlfront.models import GDLTicketCartCache
from game.gdlfront.toolkit.gdl import gdl_get_tickets_caller
from cashier.engine import Cashier
from game.gdlcore.toolkit.tickets import create_gdl_ticket, prevalidate_all_tickets, \
    _play_app_confirm_tickets_tx

from minerve.toolkit.responses import generic_json_success, silent_json_success
from minerve.toolkit.serialisers import simple_serialiser, filtered_serialiser_many

from toolkit.decorators import account_login

# Create your views here.
@csrf_protect
def play_app_generate_tickets(request):
    if 'HTTP_X_REAL_IP' in request.META:
        current_ip = request.META['HTTP_X_REAL_IP']
    else:
        current_ip = request.META['REMOTE_ADDR']
    sports = None
    teams = None
    events_within = None
    if "event_cutoff" in request.POST:
        if request.POST["event_cutoff"] != "all":
            events_within = int(request.POST["event_cutoff"])*3600
        else:
            events_within = None
    sports_filters = []
    for k in request.POST.keys():
        if k.startswith("sport_"):
            sports_filters.append(request.POST[k])
    gdl_settings = {
        "min_payout": int(request.POST["minwin"]),
        "depth": int(request.POST["events"]),
        "stake": int(request.POST["stake"]),
        "count": int(request.POST["count"]),
        "events_within": events_within,
        "sports_filters": sports_filters,

    }
    # print(gdl_settings)
    tickets = gdl_get_tickets_caller(request.vhost, request.vdomain, request, request.account, sports, teams, gdl_settings)
    return JsonResponse({"res":"ok","msg":"New Tickets have been generated!","tickets":tickets,"stake":gdl_settings["stake"],"towin":gdl_settings["min_payout"],'events':gdl_settings["depth"]},safe=False)

@csrf_protect
async def play_app_confirm_tickets(request):
    ticket_objs = await sync_to_async(list, thread_sensitive=True)(
        GDLTicketCartCache.objects.filter(
            vhost=request.vhost,
            domain=request.vdomain,
            account=request.account,
            selected=True
        )
    )

    # 🔥 ASYNC FAN-OUT
    results = await prevalidate_all_tickets(ticket_objs)

    for res in results:
        if not res.ok:
            return JsonResponse(
                {"res": "err", "err": res.error},
                safe=False
            )

    # ✅ ONLY NOW enter the sync transactional core
    return await sync_to_async(
        _play_app_confirm_tickets_tx,
        thread_sensitive=True
    )(request)


@csrf_protect
@account_login
def reject_ticket(request,tuuid):
    try:
        ticketObj = GDLTicketCartCache.objects.get(uuid=tuuid)
    except GDLTicketCartCache.DoesNotExist:
        ticketObj = False
    if ticketObj:
        ticketObj.delete()

    if ticketObj:
        retr = "Ticket Rejected/Removed!"
    else:
        retr = "Ticket had already expired."
    return generic_json_success(retr,data={"old":tuuid})


@csrf_protect
# @account_login
def accept_ticket(request):
    print(request.POST)
    print("Request",request.account,request.vhost)
    matches = request.POST["matches"].split(",")
    types = request.POST["type"].split(",")
    lines = request.POST["lines"].split(",")
    stake = int(request.POST["stake"])
    outcome_meta = json.loads(request.POST["outcome_meta"])
    returns = int(request.POST["returns"])
    depth = len(matches)
    uuid = request.POST["uuid"]
    ticketData = {
        # "id":random.randint(1000,10000),
        "matches": matches,
        "mlen": depth,
        "types": types,
        "returns": returns,
        "stake": stake,
        "lines": lines,
        "outcome_meta":outcome_meta,
        "status": "C",
    }
    selected = True
    selected_expires_at = now() + timedelta(minutes=45)
    ticketCacheObj = GDLTicketCartCache(vhost=request.vhost, domain=request.vdomain, account=request.account, risk=stake,
                                        returns=returns, events=depth,
                                        expires_at=selected_expires_at,
                                        selected_expires_at=selected_expires_at, selected=selected,
                                        ticket_data=ticketData)
    ticketCacheObj.save()
    tickets = GDLTicketCartCache.objects.filter(vhost=request.vhost, domain=request.vdomain, account=request.account, selected=True)
    ticket_count = len(tickets)
    ticket_ser, _, _ = filtered_serialiser_many(tickets, ["uuid", "events", "risk", "returns"])
    return silent_json_success("Ticket(s) Added to Cart!",data={"old":uuid,"count":ticket_count,"tickets":ticket_ser})



@csrf_protect
@account_login
def get_ticket_cart(request):

    GDLTicketCartCache.objects.filter(vhost=request.vhost, domain=request.vdomain,account=request.account,expires_at__lte=now()).delete()
    tickets = GDLTicketCartCache.objects.filter(vhost=request.vhost, domain=request.vdomain, account=request.account, selected=True)
    ticket_count = len(tickets)
    if ticket_count > 0:
        ticket_ser,_,_ = filtered_serialiser_many(tickets,["uuid","events","risk","returns"])
    else:
        ticket_ser = []

    return generic_json_success("ok",data={"count":ticket_count,"tickets":ticket_ser,"silent":True})


@csrf_protect
@account_login
def play_app_get_quick_picks(request):
    if 'HTTP_X_REAL_IP' in request.META:
        current_ip = request.META['HTTP_X_REAL_IP']
    else:
        current_ip = request.META['REMOTE_ADDR']

    sports = None
    teams = None
    events_within = None
    if "event_cutoff" in request.POST:
        if request.POST["event_cutoff"] != "all":
            events_within = int(request.POST["event_cutoff"])*3600
        else:
            events_within = None
    sports_filters = []
    for k in request.POST.keys():
        if k.startswith("sport_"):
            sports_filters.append(request.POST[k])
    gdl_settings = {
        "min_payout": int(request.POST["minwin"]),
        "depth": int(request.POST["events"]),
        "stake": int(request.POST["stake"]),
        "count": int(request.POST["count"]),
        "events_within": events_within,
        "sports_filters": sports_filters,

    }
    # print(gdl_settings)
    tickets = gdl_get_tickets_caller(request.vhost, request.vdomain, request, request.account, sports, teams, gdl_settings,ticket_selected=True)
    # print(tickets)
    return JsonResponse({"res":"ok","msg":"Quick Picks have been added to cart!","quick_pick":True},safe=False)



@account_login
def get_acct_balances(request):
    cashier = Cashier(account=request.account,vhost=request.vhost)
    latest_balance = cashier.get_balance()
    latest_bonus = cashier.get_available_bonus()
    pending = cashier.get_at_risk_balance()
    balance = cashier.get_available_balance()+latest_bonus
    return JsonResponse({"res":"ok","silent":"true","available":f"{balance:.2f}","bonus":f"{latest_bonus:.2f}","pending":f"{pending:.2f}","balance":f"{latest_balance:.2f}"},safe=False)


@csrf_protect
@account_login
def empty_cart(request):
    print("Tickets")
    ticketObj = GDLTicketCartCache.objects.filter(account=request.account,vhost=request.vhost).delete()
    retr = "Cart has been cleared!"
    return generic_json_success(retr)


