from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from sympy.physics.units import volts

from game.gdlgdlagent.forms.filters import GDLCoreSportFilterForm, GDLFilterSettingsForm
from game.gdlgdlcore.models import GDLCoreSportGroupFilters
from game.gdlfront.models import GDLFilterSettingsGroup
from game.gdlgdlmanagement.forms.quickpicks import GDLTypeSettingsEntryForm
from toolkit.contexts import default_agent_dashboard_context


@login_required(login_url="/agent/login")
@permission_required("gdlcore.gdl_view_filter_settings")
def gdl_quickpicks_config_table(request):
    vhost, vdomain, apperance, agent, context = default_agent_dashboard_context(request)
    newForm = GDLTypeSettingsEntryForm()
    context.update({
        "new_form": newForm,
    })
    return render(request, "solstic.gdl/gdlmanagement/quickpicks/table.html", context)

