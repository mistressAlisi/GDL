from django.contrib.auth.decorators import login_required
from django.db.models import Q, OuterRef, Exists

from licensemanager.models import ApplicationStudio, AvailableApplication
from matches.models import Match
from minerve.toolkit.paginator import paginator_paginate_and_serialise
from minerve.toolkit.responses import generic_json_success
from minerve.toolkit.serialisers import edit_row_serialiser, simple_serialiser
from toolkit.vhosts import get_vhost_and_apperance
from wager.models import Wager


@login_required
def open_tickets_table_meta(request):
    vhost, vdomain, apperance = get_vhost_and_apperance(request)
    data = {
        "settings": {

        },
        "urls": {
            "paginator_endpoint":"agent/game/tickets/open/table/data/",
            "detail_endpoint":"agent/game/tickets/open/table/data/detail/",
        },
        "texts": {

        }
    }
    return generic_json_success("ok",data=data)


@login_required
def tickets_table_data_handle(request,page_size=20,page=1):
    vhost, vdomain, apperance = get_vhost_and_apperance(request)
    appTypeObj = AvailableApplication.objects.get(slug='gamedaylotto')
    wagerObjs = Wager.objects.filter(vhost=vhost,status__in=["P","M"],application_type=appTypeObj,parlay_closed=False)
    if "srt" in request.GET and request.GET["srt"] != "":
        sorters = request.GET["srt"].split(",")
        for sorter in sorters:
            wagerObjs = wagerObjs.filter(level=sorter)
    add_cols = {
        "_details":{"type":"internal_modal_detail",
                          "text":"Details"},
        # "_edit": {"type": "internal_modal_edit",
        #                   "text": "Edit"},
    }
    return paginator_paginate_and_serialise(wagerObjs, page=page, page_size=page_size,
                                            filter_cols=["uuid","account","status","match","team_1","for_draw","current_ip","risk","win"],
                                            additional_col_names={"_details":"Details","uuid":"ID","account":"Account #",
                                                                  "status":"Status","match":'Match',"team_1":"On Team","for_draw":"Draw","current_ip":"IP",
                                                                  "risk":"Risk","win":"Returns"},
                                            relation_names={"match": "get_match_name", "team_1": "get_name", "account": "acctnum"},
                                            additional_cols=add_cols)


@login_required
def closed_tickets_table_meta(request):
    data = {
        "settings": {

        },
        "urls": {
            "paginator_endpoint":"agent/game/tickets/closed/table/data/",
            "detail_endpoint":"agent/game/tickets/open/table/data/detail/",
        },
        "texts": {

        }
    }
    return generic_json_success("ok",data=data)


@login_required
def tickets_table_closed_data_handle(request,page_size=20,page=1):
    vhost, vdomain, apperance = get_vhost_and_apperance(request)
    appTypeObj = AvailableApplication.objects.get(slug='gamedaylotto')
    wagerObjs = Wager.objects.filter(vhost=vhost,application_type=appTypeObj).filter(Q(status__in=["L","W","D"])|Q(parlay_closed=True))
    if "srt" in request.GET and request.GET["srt"] != "":
        sorters = request.GET["srt"].split(",")
        for sorter in sorters:
            wagerObjs = wagerObjs.filter(level=sorter)
    add_cols = {
        "_details":{"type":"internal_modal_detail",
                          "text":"Details"},
        # "_edit": {"type": "internal_modal_edit",
        #                   "text": "Edit"},
    }
    return paginator_paginate_and_serialise(wagerObjs, page=page, page_size=page_size,
                                            filter_cols=["uuid","account","status","match","team_1","for_draw","current_ip","risk","win","parlay_closed"],
                                            additional_col_names={"_details":"Details","uuid":"ID","account":"Account #",
                                                                  "status":"Status","match":'Match',"team_1":"On Team","for_draw":"Draw","current_ip":"IP",
                                                                  "risk":"Risk","win":"Returns","parlay_closed":"Parlay Lost"},
                                            relation_names={"match": "get_match_name", "team_1": "get_name", "account": "acctnum"},
                                            additional_cols=add_cols)

@login_required
def tickets_table_detail_handle(request,ruuid):
    vhost, vdomain, apperance = get_vhost_and_apperance(request)
    ruleObj = Wager.objects.get(uuid=ruuid)
    values,names,help = simple_serialiser(ruleObj,)
    return generic_json_success("Loaded Ticket Details",data={"values":values,"names":names,"help":help})


@login_required
def tickets_open_match_table_handle(request,page_size=20,page=1):
    vhost, vdomain, apperance = get_vhost_and_apperance(request)
    appTypeObj = AvailableApplication.objects.get(slug='gamedaylotto')
    wagers_subq = Wager.objects.filter(
        match=OuterRef("pk"),
        grade_outcome__isnull=True
    ).filter(
        Q(status="P") | Q(status="M"),
        application_type=appTypeObj,
    )

    # main query
    match_qs = (
        Match.objects.filter(
            finished=False,
            # commence_time__gte=localtime()
        )
        .annotate(has_wagers=Exists(wagers_subq))
        .filter(has_wagers=True)
    )
    if "srt" in request.GET and request.GET["srt"] != "":
        sorters = request.GET["srt"].split(",")
        for sorter in sorters:
            match_qs = match_qs.filter(level=sorter)
    add_cols = {
        "_details": {"type": "internal_modal_detail",
                     "text": "Details"},
        "_outcomes": {"type": "modal_view",
                  "text": "View",
                  "onclick": "match_tool.show_match_outcomes"
                  },
        "_data": {"type": "modal_view",
                          "text": "View",
                          "onclick":"match_tool.show_match"
                  },
    }
    return paginator_paginate_and_serialise(match_qs, page=page, page_size=page_size,
                                            filter_cols=["uuid", "home_team", "away_team", "commence_time",
                                                         "status_short", "status_long","sport"],
                                            additional_col_names={"_details": "Details", "uuid": "ID",
                                                                  "home_team": "Home Team", "away_team": "Away Team",
                                                                  "commence_time": "Commence Time",
                                                                  "status_short": "Status (S)",
                                                                  "status_long": "Status (L)",
                                                                  "sport": "Sport","_outcomes":"Outcome(s)","_data":"Data Sources"},
                                            relation_names={"match": "get_match_name", "home_team": "get_name",
                                                            "away_team": "get_name","sport":"title"},
                                            additional_cols=add_cols)


@login_required
def tickets_table_detail_handle(request,ruuid):
    vhost, vdomain, apperance = get_vhost_and_apperance(request)
    ruleObj = Match.objects.get(uuid=ruuid)
    values,names,help = simple_serialiser(ruleObj,)
    # print(values)
    return generic_json_success("Loaded Match Details",data={"values":values,"names":names,"help":help})

@login_required
def open_matches_table_meta(request):
    data = {
        "settings": {

        },
        "urls": {
            "paginator_endpoint":"agent/game/tickets/open/matches/table/data/",
            "detail_endpoint":"agent/game/tickets/open/matches/table/data/detail/",
        },
        "texts": {

        }
    }
    return generic_json_success("ok",data=data)
