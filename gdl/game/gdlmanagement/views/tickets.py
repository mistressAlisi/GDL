from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render

from toolkit.contexts import default_agent_dashboard_context


@login_required(login_url="/agent/login")
@permission_required("gdlcore.gdl_view_open_tickets")
def open_tickets_table_handle(request):
    vhost, vdomain, apperance, agent, context = default_agent_dashboard_context(request)
    # user_ping(request)
    return render(request, "solstic.gdl/gdlagent/open_tickets_table.html", context)


@login_required(login_url="/agent/login")
@permission_required("gdlcore.gdl_view_open_tickets")
def closed_tickets_table_handle(request):
    vhost, vdomain, apperance, agent, context = default_agent_dashboard_context(request)
    # user_ping(request)
    return render(request, "solstic.gdl/gdlagent/closed_tickets_table.html", context)




@login_required(login_url="/agent/login")
@permission_required("gdlcore.gdl_view_open_tickets")
def open_tickets_matches_table_handle(request):
    vhost, vdomain, apperance, agent, context = default_agent_dashboard_context(request)
    # user_ping(request)
    return render(request, "solstic.gdl/gdlagent/open_matches_table.html", context)

