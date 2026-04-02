import json
from datetime import timedelta, datetime

from asgiref.sync import sync_to_async
from django.db import transaction
from django.db.models import Sum, F
from django.http import JsonResponse
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_protect

from game.gdlfront.models import GDLTicketCartCache
from game.gdlfront.toolkit.gdl import gdl_get_tickets_caller
from cashier.engine import Cashier
from game.gdlcore.toolkit.tickets import create_gdl_ticket, prevalidate_all_tickets, \
    _play_app_confirm_tickets_tx

from minerve.toolkit.responses import generic_json_success, silent_json_success
from minerve.toolkit.serialisers import simple_serialiser, filtered_serialiser_many

from toolkit.decorators import account_login
from wager.models import Wager


# Create your views here.
def get_winners_data_handle(request):

    cutoff = now() - timedelta(days=60)
    winners = Wager.objects.filter(vhost=request.vhost,grade_outcome='W',hide_in_reports=False,graded_at__gte=cutoff).order_by('graded_at','win')[0:50]
    wagers_data,_,_ = filtered_serialiser_many(winners,["uuid","account","risk","win","graded_at","created_at"],date_isoformat=True)
    account_winners = ((Wager.objects.filter(
            vhost=request.vhost,
            grade_outcome='W',
            hide_in_reports=False,
            graded_at__gte=cutoff,
        ).values('account__uuid', 'account__acctnum','account__acctname','account__pronouns','account__avatar',"win").order_by('-graded_at')))


    account_data = []
    for aw in account_winners[0:50]:
        if aw['account__acctname']:
            name = aw['account__acctname']
        else:
            name = aw['account__acctnum']
        account_data.append({
            "uuid":str(aw['account__uuid']),
            "acctnum":aw['account__acctnum'],
            "pronouns":aw['account__pronouns'],
            "avatar":aw['account__avatar'],
            "total_win":aw['win'],
            "name":name,

        })

    return silent_json_success("ok",data={"winning_tickets":wagers_data,"top_winners":account_data})
