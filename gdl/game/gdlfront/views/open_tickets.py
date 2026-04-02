import itertools
from datetime import datetime

from django.shortcuts import render, redirect
from django.utils.timezone import localdate, now

from frontend.lobby.forms import AccountSignupForm, AccountLoginForm
from game.gdlgdlcore.toolkit.tickets import get_gdl_ticket, get_gdl_ticket_matches
from parameters.models import VHostUserMenuEntry, VHostUserSideBarEntry
from toolkit.contexts import default_account_dashboard_context
from toolkit.decorators import account_login
from wager.models import Wager

@account_login
def open_tickets_view_handle(request):
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")

    signup_form = AccountSignupForm()
    login_form = AccountLoginForm()
    if "tz" in request.session:
        tz = request.session["tz"]
    else:
        tz = False
    context.update({

        "signup_form":signup_form,
        "login_form":login_form,

    })
    return render(request,"gdlfront/dashboard/tickets/index.html",context)

@account_login
def open_tickets_table_view_handle_old(request):
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")

    signup_form = AccountSignupForm()
    login_form = AccountLoginForm()
    context.update({

        "signup_form":signup_form,
        "login_form":login_form,

    })
    if vdomain.frontend == "kio":
        return render(request,"gdlfront/kiosk/tickets/index_table_kiosk.html",context)
    else:
        return render(request,"gdlfront/dashboard/tickets/index_table.html",context)


@account_login
def open_tickets_details_view_handle(request,payload):
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    rootWagerObj = Wager.objects.get(uuid=payload,vhost=vhost,account=context["account"])
    ticketObj = get_gdl_ticket(rootWagerObj,False,True)
    matches_batches = get_gdl_ticket_matches(rootWagerObj,20)
    context.update({
        "ticket":ticketObj,
        "matches_batches": matches_batches,
        "rootWagerObj":rootWagerObj,
    })
    # print(matches_batches)
    return render(request,"gdlfront/dashboard/tickets/ticket_viewer.html",context)

@account_login
def prev_tickets_view_handle(request):
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")

    signup_form = AccountSignupForm()
    login_form = AccountLoginForm()
    context.update({

        "signup_form":signup_form,
        "login_form":login_form,

    })
    return render(request,"gdlfront/dashboard/tickets/previous.html",context)


@account_login
def winning_tickets_view_handle(request):
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")

    signup_form = AccountSignupForm()
    login_form = AccountLoginForm()
    context.update({

        "signup_form":signup_form,
        "login_form":login_form,

    })
    return render(request,"gdlfront/dashboard/tickets/winners.html",context)

@account_login
def previous_tickets_table_view_handle(request):
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")

    signup_form = AccountSignupForm()
    login_form = AccountLoginForm()
    today = localdate().isoformat()
    context.update({

        "signup_form":signup_form,
        "login_form":login_form,
        "today":today
    })
    if vdomain.frontend == "kio":
        return render(request,"gdlfront/kiosk/tickets/prev_table_kiosk.html",context)
    else:
        return render(request,"gdlfront/dashboard/tickets/previous_table.html",context)


@account_login
def open_tickets_table_view_handle(request):
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    if vdomain.frontend == "kio":
        return render(request,"gdlfront/kiosk/tickets/index_table_kiosk.html",context)
    else:
        return render(request,"gdlfront/dashboard/tickets/index_table.html",context)
