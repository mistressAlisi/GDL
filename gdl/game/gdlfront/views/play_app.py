
import json
from datetime import timezone

from django.shortcuts import render, redirect
from django.utils.timezone import localdate, localtime
from django.utils.translation import gettext as _

from account.models import Account
from game.gdlgdlcore.models import GDLTypeSettingsEntry

from game.gdlfront.models import GDLTicketCartCache, GDLFilterSettingsGroup, GDLFilterSettingsSportEntry
from cashier.engine import Cashier
from cashier.models import ParlayPayoutRulesetEntry
from game.gdlfront.forms.play_setup import SetupGDL_FullForm, SetupGDL_FilteredForm, SetupGDL_AdvInlineForm
from frontend.lobby.forms import AccountSignupForm, AccountLoginForm

from matches.models import Match
from sports.models import Sport, Group

from toolkit.contexts import default_account_dashboard_context
from toolkit.decorators import account_login

from toolkit.wagers.rule_tools import parlay_leg_ruleset_builder



# Create your views here.
@account_login
def play_app_configure_index(request):
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    signup_form = AccountSignupForm()
    login_form = AccountLoginForm()
    setup_form = SetupGDL_FilteredForm()
    inline_form = SetupGDL_AdvInlineForm()
    filter_settings = GDLFilterSettingsGroup.objects.filter(vhost=vhost,domain=vdomain,active=True).first()
    # print(filter_settings.group_filter.all())
    filter_sports = GDLFilterSettingsSportEntry.objects.filter(parent=filter_settings,sport__active=True,sport__group__active=True)
    quick_picks_choices = GDLTypeSettingsEntry.objects.filter(vhost=vhost,active=True)
    if filter_settings:

        filter_sports = filter_settings.sport_filter.all()
        filter_groups = filter_settings.group_filter.all()
    else:
        filter_sports = None
        filter_groups = None
    rule_set,min_legs,max_legs = parlay_leg_ruleset_builder(account)
    gdl_count = GDLTicketCartCache.objects.filter(vhost=vhost, account=account, selected=True).count()
    context.update({
        "signup_form":signup_form,
        "login_form":login_form,
        "min_legs":min_legs,
        "max_legs":max_legs,
        "ruleset":json.dumps(rule_set,separators=(',', ':')),
        "setup_form": setup_form,
        "inline_form": inline_form,
        "filter_sports":filter_sports,
        "filter_groups":filter_groups,
        "quick_picks_choices":quick_picks_choices,
        "gdl_count":gdl_count

    })
    # print(context)
    if vdomain.frontend == "kio":
        return render(request,"gdlfront/kiosk/play_app/home.html",context)
    else:
        return render(request, "gdlfront/dashboard/play_app/home.html", context)


@account_login
def play_app_qp_index(request,filter=False,fstr=False):
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request, "player")
    signup_form = AccountSignupForm()
    login_form = AccountLoginForm()
    setup_form = SetupGDL_FilteredForm()
    inline_form = SetupGDL_AdvInlineForm()
    filter_settings = GDLFilterSettingsGroup.objects.filter(vhost=vhost, domain=vdomain, active=True).first()
    quick_picks_choices = GDLTypeSettingsEntry.objects.filter(vhost=vhost,active=True)
    # print(filter_settings.group_filter.all())
    if filter_settings:

        filter_sports = filter_settings.sport_filter.all()
        filter_groups = filter_settings.group_filter.all()
    else:
        filter_sports = None
        filter_groups = None
    quick_pick_name = False
    if filter == "sport":
        slug = fstr.upper()
        filter_groups = Group.objects.filter(vhost=vhost,slug=slug)
        gn = filter_groups.first()
        quick_pick_name = f"{gn.icon} {gn.name}"

    rule_set, min_legs, max_legs = parlay_leg_ruleset_builder(account)
    gdl_count = GDLTicketCartCache.objects.filter(vhost=vhost,account=account,selected=True).count()
    context.update({
        "signup_form": signup_form,
        "login_form": login_form,
        "min_legs": min_legs,
        "max_legs": max_legs,
        "ruleset": json.dumps(rule_set, separators=(',', ':')),
        "setup_form": setup_form,
        "inline_form": inline_form,
        "filter_groups": filter_groups,
        "quick_pick_name":quick_pick_name,
        "quick_picks_choices": quick_picks_choices,
        "gdl_count":gdl_count

    })
    return render(request, "gdlfront/dashboard/play_app/quickpicks_form.html", context)

@account_login
def play_app_qp_dynamic_index(request,quuid):
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request, "player")
    signup_form = AccountSignupForm()
    login_form = AccountLoginForm()
    setup_form = SetupGDL_FilteredForm()
    inline_form = SetupGDL_AdvInlineForm()
    gdl_count = GDLTicketCartCache.objects.filter(vhost=vhost, account=account, selected=True).count()
    quick_picks_choices = GDLTypeSettingsEntry.objects.get(vhost=vhost,active=True,uuid=quuid)
    filter_sports = quick_picks_choices.sport_filter.all()
    filter_groups = quick_picks_choices.group_filter.all()
    for fs in filter_sports:
        print(f"fs: {fs}, {fs.uuid}")
    translated_name = ""
    if quick_picks_choices.name == "Basketball":
        translated_name = _("Basketball")
    if quick_picks_choices.name == "Football":
        translated_name = _("Football")
    if quick_picks_choices.name == "Baseball":
        translated_name = _("Baseball")
    if quick_picks_choices.name == "Soccer":
        translated_name = _("Soccer")
    quick_pick_name = f"{quick_picks_choices.icon} {translated_name}"
    rule_set, min_legs, max_legs = parlay_leg_ruleset_builder(account)
    context.update({
        "signup_form": signup_form,
        "login_form": login_form,
        "min_legs": min_legs,
        "max_legs": max_legs,
        "ruleset": json.dumps(rule_set, separators=(',', ':')),
        "setup_form": setup_form,
        "inline_form": inline_form,
        "filter_groups": filter_groups,
        "filter_sports":filter_sports,
        "quick_pick_name":quick_pick_name,
        "quick_picks_choices": quick_picks_choices,
        "gdl_count":gdl_count

    })
    return render(request, "gdlfront/dashboard/play_app/quickpicks_form.html", context)


@account_login
def play_app_cst_index(request):
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    signup_form = AccountSignupForm()
    login_form = AccountLoginForm()
    setup_form = SetupGDL_FilteredForm()
    inline_form = SetupGDL_AdvInlineForm()
    gdl_count = GDLTicketCartCache.objects.filter(vhost=vhost, account=account, selected=True).count()
    filter_settings = GDLFilterSettingsGroup.objects.filter(vhost=vhost,domain=vdomain,active=True).first()
    # print(filter_settings.group_filter.all())
    if filter_settings:
        _fsg = GDLFilterSettingsSportEntry.objects.filter(parent=filter_settings)
        filter_sports = []
        index = 0
        for fsg in _fsg:
            if fsg.group.active == True:
                filter_sports.append(fsg)
                # print(f"{index} {fsg.group.name}")
                if fsg.group and fsg.group.name == "Basketball":
                    filter_sports[index].group.name = _("Basketball")
                if fsg.group and fsg.group.name == "American Football":
                    filter_sports[index].group.name = _("American Football")
                if fsg.group and fsg.group.name == "Soccer":
                    filter_sports[index].group.name = _("Soccer")
                if fsg.group and fsg.group.name == "Ice Hockey":
                    filter_sports[index].group.name = _("Ice Hockey")
                if fsg.group and fsg.group.name == "Tennis":
                    filter_sports[index].group.name = _("Tennis")
                index += 1
        filter_groups = filter_settings.group_filter.all()
    else:
        filter_sports = None
        filter_groups = None
    rule_set,min_legs,max_legs = parlay_leg_ruleset_builder(account)
    context.update({
        "signup_form":signup_form,
        "login_form":login_form,
        "min_legs":min_legs,
        "max_legs":max_legs,
        "ruleset":json.dumps(rule_set,separators=(',', ':')),
        "setup_form": setup_form,
        "inline_form": inline_form,
        "filter_sports":filter_sports,
        "filter_groups":filter_groups,
        "qp":False,
        "cst":True,
        "gdl_count":gdl_count

    })
    # print(context)
    if vdomain.frontend == "kio":
        return render(request,"gdlfront/kiosk/play_app/custom_tickets_form.html",context)
    else:
        return render(request, "gdlfront/dashboard/play_app/custom_tickets_form.html", context)



@account_login
def play_app_configure_step1(request):
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    signup_form = AccountSignupForm()
    login_form = AccountLoginForm()
    setup_form = SetupGDL_FullForm()
    rule_set,min_legs,max_legs = parlay_leg_ruleset_builder(account)
    context.update({
        "signup_form":signup_form,
        "login_form":login_form,
        "min_legs":min_legs,
        "max_legs":max_legs,
        "ruleset":json.dumps(rule_set,separators=(',', ':')),
        "setup_form": setup_form,

    })
    # print(context)
    return render(request,"gdlfront/dashboard/play_app/step1.html",context)


@account_login
def ticket_viewer_handle(request,tuuid):
    try:
        vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    except  Account.DoesNotExist:
        return redirect('/?login=True&target=game/viewer')

    ticketObj = GDLTicketCartCache.objects.get(uuid=tuuid)
    payload_decode = ticketObj.ticket_data
    # print(payload_decode)
    matches = []
    # print(payload_decode)
    i = 0
    for match in payload_decode["matches"]:
        matchObj = Match.objects.get(uuid=match)
        matches.append({"match":matchObj,"type":payload_decode["types"][i]})
        i += 1
    # print(matches)
    # matches_batches = list(itertools.batched(matches,5))
    #  WE KNOW the no loss rule, payout is 100% (or should be), so skip those objects, make our life easier:
    rules_obj = ParlayPayoutRulesetEntry.objects.filter(ruleset=account.parlay_rules,parlay_legs=i,max_losses__gt=0).order_by('max_losses')
    context.update({
        "stake":payload_decode["stake"],
        "returns":payload_decode["returns"],
        "length":i,
        # "matches_batches":matches_batches,
        "matches":matches,
        "rules":rules_obj,
        "ticket":ticketObj
    })
    if "ict" in request.GET:
        context.update({
            "skip_accept":True,
            "current_time": localtime()
        })
    # print("Here i am, sonny",matches_batches)

    return render(request,"gdlfront/dashboard/play_app/ticket_viewer.html",context)

@account_login
def kiosk_landing(request):
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    cashier = Cashier(vhost,account)
    context.update({
        "cashier": cashier,
    })
    return render(request,"gdlfront/kiosk/gdl_landing.html",context)