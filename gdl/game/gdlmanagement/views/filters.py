from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from sympy.physics.units import volts

from game.gdlgdlagent.forms.filters import GDLCoreSportFilterForm, GDLFilterSettingsForm
from game.gdlgdlcore.models import GDLCoreSportGroupFilters
from game.gdlfront.models import GDLFilterSettingsGroup
from toolkit.contexts import default_agent_dashboard_context


@login_required(login_url="/agent/login")
@permission_required("gdlcore.gdl_view_filter_settings")
def filter_settings_view_handle(request):
    vhost, vdomain, apperance, agent, context = default_agent_dashboard_context(request)
    filterObj,fcc = GDLCoreSportGroupFilters.objects.get_or_create(vhost=vhost,domain=vdomain)
    if fcc: filterObj.save()
    sport_form = GDLCoreSportFilterForm(instance=filterObj)
    # user_ping(request)
    context.update({
        "sport_form":sport_form
    })
    return render(request, "game/gdlagent/filters_setting_view.html", context)


@login_required(login_url="/agent/login")
@permission_required("gdlcore.gdl_view_filter_settings")
def user_filter_settings_view_handle(request):
    vhost, vdomain, apperance, agent, context = default_agent_dashboard_context(request)
    filterObj,c = GDLFilterSettingsGroup.objects.get_or_create(vhost=vhost,domain=vdomain)
    if c: filterObj.save()
    sport_form = GDLFilterSettingsForm(instance=filterObj)
    # user_ping(request)
    context.update({
        "sport_form":sport_form
    })
    return render(request, "game/gdlagent/user_filters_setting_view.html", context)

