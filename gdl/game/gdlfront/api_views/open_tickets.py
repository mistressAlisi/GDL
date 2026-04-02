import math,pytz
from datetime import timedelta, datetime, time

from django.conf import settings
from django.db.models import Sum, Case, F, When, Value, DecimalField
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from game.gdlcore.toolkit.tickets import get_gdl_ticket
from minerve.toolkit.paginator import paginator_json_response, paginator_paginate_and_serialise

from toolkit.decorators import account_login
from wager.models import Wager

# Create your views here.
@csrf_protect
@account_login
def get_open_tickets_handle(request):

    # print(request.POST)
    count = int(request.POST["count"])
    page = int(request.POST["page"])
    total_pages = 1
    if page == 0: page = 1
    ticketCount = Wager.objects.filter(vhost=request.vhost,account=request.account,status__in=["P","M"],gdl_ticket=True,bet_data__root_wager=True,grade_outcome__isnull=False,hide_in_reports=False).count()
    if ticketCount < count:
        ticketObjs = Wager.objects.filter(vhost=request.vhost,account=request.account,status__in=["P","M"],gdl_ticket=True,bet_data__root_wager=True,grade_outcome__isnull=False,hide_in_reports=False)
    else:

        total_pages = round(ticketCount / count)
        if page < total_pages:
            end_page = count * (page+1)
        else:
            end_page = total_pages * count

        if page == 0 or page == 1:
            end_page = count
            page = 1
            start_page = 0
        else:
            start_page = count * page
        # print(page,start_page,end_page)
        ticketObjs = Wager.objects.filter(vhost=request.vhost, account=request.account, status__in=["P", "M"],
                                          gdl_ticket=True, bet_data__root_wager=True, grade_outcome__isnull=False,hide_in_reports=False)[start_page:end_page]
    tickets = []
    for r in ticketObjs:
        tickets.append(get_gdl_ticket(r))

    return JsonResponse({"res":"ok","msg":f"Retrieved {len(tickets)} open tickets!","tickets":tickets,"total_records":ticketCount,"curr_page":page,"page_size":count,"total_pages":total_pages},safe=False)

@csrf_protect
@account_login
def get_open_tickets_table_handle(request,page_size=50,page=1):

    ticketObjs = Wager.objects.filter(vhost=request.vhost, account=request.account, status__in=["P", "M"], gdl_ticket=True,
                                      bet_data__root_wager=True, grade_outcome__isnull=True,hide_in_reports=False)
    if "srt" in request.GET and request.GET["srt"] != "":
        sorters = request.GET["srt"].split(";")
        for sorter in sorters:
            ticketObjs = ticketObjs.order_by(sorter)
    else:
        ticketObjs = ticketObjs.order_by("-created")
    add_cols = {
        # "ticket_details":{"type":"modal_view",
        #                   "url":"/ticket/active/details/viewer/",
        #                   "text":"Ticket Details",
        #                   "onclick":"gdl_backend.show_ticket_modal"}
    }
    ttl_data = ticketObjs.all().aggregate(total_risk=Sum('risk'), total_win=Sum('win'))
    totals = [
        {"name":"","value":""},
        {"name": "", "value": ""},
        {"name": "Total:", "value": ttl_data["total_risk"]},
        {"name": "Total:", "value": ttl_data["total_win"]},
    ]
    return paginator_paginate_and_serialise(ticketObjs,page=page,page_size=page_size,filter_cols=["uuid","created","risk","win"],additional_col_names={},additional_cols=add_cols,totals=totals)


@account_login
def get_previous_tickets_table_handle(request,page_size=50,page=1):
    ticketObjs =  Wager.objects.filter(
            vhost=vhost,
            account=account,
            gdl_ticket=True,
            bet_data__root_wager=True,
            hide_in_reports=False,
        ).annotate(
            win_amount=Case(
                When(grade_outcome='W', then=F('win')),
                default=Value(0),
                output_field=DecimalField(max_digits=10, decimal_places=2),
            )
        )

    if "srt" in request.GET and request.GET["srt"] != "":
        sorters = request.GET["srt"].split(";")
        for sorter in sorters:
            ticketObjs = ticketObjs.order_by(sorter)
    else:
        ticketObjs = ticketObjs.order_by("-created")
    add_cols = {
        # "ticket_details":{"type":"modal_view",
        #                   "url":"/ticket/active/details/viewer/",
        #                   "text":"Ticket Details",
        #                   "onclick":"gdl_backend.show_ticket_modal"}
    }

    return paginator_paginate_and_serialise(ticketObjs,page=page,page_size=page_size,filter_cols=["uuid","created","grade_outcome","risk","win"],additional_col_names={"grade_outcome":"Outcome","risk":"Risk","win":"Result"},additional_cols=add_cols)

@account_login
def get_previous_tickets_table_handle_ranged(request,start,end,type,page_size=50,page=1):


        startDate = datetime.strptime(start, "%Y-%m-%d").date()
        endDate = datetime.strptime(end, "%Y-%m-%d").date()

        tz = pytz.timezone(settings.TIME_ZONE)

        start_dt = timezone.make_aware(
            datetime.combine(startDate, time.min),
            tz
        )

        end_dt = timezone.make_aware(
            datetime.combine(endDate + timedelta(days=1), time.min),
            tz
        )
        # print(start_dt,end_dt)
        ticketObjs = Wager.objects.filter(
            vhost=request.vhost,
            account=request.account,
            gdl_ticket=True,
            bet_data__root_wager=True,
            hide_in_reports=False,
            graded_at__gte=start_dt,
            graded_at__lt=end_dt
        ).annotate(
            win_amount=Case(
                When(grade_outcome='W', then=F('win')),
                default=Value(0),
                output_field=DecimalField(max_digits=10, decimal_places=2),
            )
        )
        if type == "W":
            ticketObjs = ticketObjs.filter(grade_outcome="W")
        elif type == "L":
            ticketObjs = ticketObjs.filter(grade_outcome="L")
        if "srt" in request.GET and request.GET["srt"] != "":
            sorters = request.GET["srt"].split(";")
            for sorter in sorters:
                ticketObjs = ticketObjs.order_by(sorter)
        else:
            ticketObjs = ticketObjs.order_by("-graded_at")

        add_cols = {
            # "ticket_details":{"type":"modal_view",
            #                   "url":"/ticket/active/details/viewer/",
            #                   "text":"Ticket Details",
            #                   "onclick":"gdl_backend.show_ticket_modal"}
        }
        # print(ticketObjs)
        ttl_data = ticketObjs.aggregate(total_risk=Sum('risk'), total_win=Sum('win_amount'))

        totals = [
            {"name": "", "value": ""},
            {"name": "", "value": ""},
            {"name": "Total:", "value": ttl_data["total_risk"]},
            {"name": "Total:", "value": ttl_data["total_win"]},
            {"name": "", "value": ""},
        ]
        return paginator_paginate_and_serialise(ticketObjs,page=page,page_size=page_size,filter_cols=["uuid","grade_outcome","risk","win_amount","graded_at"],set_columns=["uuid","grade_outcome","risk","win_amount","graded_at"],additional_col_names={"grade_outcome":"Outcome","win_amount":"Result","graded_at":"Graded At"},additional_cols=add_cols,totals=totals)


@account_login
def get_previous_tickets_handle(request):

    count = int(request.POST["count"])
    page = int(request.POST["page"])
    total_pages = 1
    if page == 0: page = 1
    ticketCount = Wager.objects.filter(vhost=request.vhost,account=request.account,graded=True,gdl_ticket=True,bet_data__root_wager=True).count()
    if ticketCount < count:
        ticketObjs = Wager.objects.filter(vhost=request.vhost,account=request.account,graded=True,gdl_ticket=True,bet_data__root_wager=True)
    else:
        total_pages = math.ceil(ticketCount / count)
        if page < total_pages:
            end_page = count * (page + 1)
        else:
            end_page = total_pages * count

        if page == 0 or page == 1:
            end_page = count
            page = 1
            start_page = 0
        else:
            start_page = count * page
        # print(page,start_page,end_page)
        ticketObjs = Wager.objects.filter(vhost=request.vhost, account=request.account,graded=True,
                                          gdl_ticket=True, bet_data__root_wager=True)[start_page:end_page]

    tickets = []
    for r in ticketObjs:
        tickets.append(get_gdl_ticket(r))
    return JsonResponse({"res":"ok","msg":f"Retrieved {len(tickets)} previous tickets!","tickets":tickets,"total_records":ticketCount,"curr_page":page,"page_size":count,"total_pages":total_pages},safe=False)

@account_login
def get_winning_tickets_handle(request):
    ticketObjs = Wager.objects.filter(vhost=request.vhost,account=request.account,status__in=["W"],gdl_ticket=True,bet_data__root_wager=True,closed=False,executed=False)

    tickets = []
    for r in ticketObjs:
        tickets.append(get_gdl_ticket(r))
    return JsonResponse({"res":"ok","msg":f"Retrieved {len(tickets)} winning tickets!","tickets":tickets},safe=False)

