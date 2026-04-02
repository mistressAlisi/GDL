from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse

from game.gdlgdlagent.forms.filters import GDLCoreSportFilterForm, GDLFilterSettingsForm
from game.gdlgdlcore.models import GDLCoreSportGroupFilters
from game.gdlfront.models import GDLFilterSettingsGroup
from minerve.toolkit.responses import generic_json_success
from toolkit.contexts import default_agent_dashboard_context
from toolkit.vhosts import get_vhost_and_apperance


@login_required
@permission_required("gdlcore.gdl_set_filter_settings")
def gdl_core_filters_save_handle(request):
    vhost, vdomain, apperance, agent, context = default_agent_dashboard_context(request)
    filterObj = GDLCoreSportGroupFilters.objects.get(vhost=vhost,domain=vdomain)
    sport_form = GDLCoreSportFilterForm(request.POST,instance=filterObj)
    if sport_form.is_valid():
        sport_form.save()
        return generic_json_success("Updated Filters!")
    else:
        return JsonResponse({"res":"err","error":sport_form.errors})

@login_required
@permission_required("gdlcore.gdl_set_filter_settings")
def gdl_core_user_filters_save_handle(request):
    vhost, vdomain, apperance, agent, context = default_agent_dashboard_context(request)
    filterObj = GDLFilterSettingsGroup.objects.get(vhost=vhost, domain=vdomain)
    sport_form = GDLFilterSettingsForm(request.POST, instance=filterObj)
    if sport_form.is_valid():
        sport_form.save()
        return generic_json_success("Updated Filters!")
    else:
        return JsonResponse({"res": "err", "error": sport_form.errors})