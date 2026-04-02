from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse

from game.gdlgdlagent.forms.filters import GDLCoreSportFilterForm, GDLFilterSettingsForm
from game.gdlgdlcore.models import GDLCoreSportGroupFilters, GDLTypeSettingsEntry
from game.gdlfront.models import GDLFilterSettingsGroup
from game.gdlgdlmanagement.forms.quickpicks import GDLTypeSettingsEntryForm
from minerve.toolkit.errors import generic_json_error
from minerve.toolkit.paginator import paginator_paginate_and_serialise
from minerve.toolkit.responses import generic_json_success
from minerve.toolkit.serialisers import edit_row_serialiser
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



@login_required
def gdl_quickpicks_settings_table_meta_handle(request):
    vhost, vdomain, apperance = get_vhost_and_apperance(request)
    data = {
        "settings": {

        },
        "urls": {
            "paginator_endpoint":"management/game/quickpicks/table/data/",
            "detail_endpoint":"management/game/quickpicks/table/data/detail/",
            "edit_endpoint": "management/game/quickpicks/table/data/detail/load/",
            "save_endpoint": "management/game/quickpicks/table/data/save",
        },
        "texts": {

        }
    }
    return generic_json_success("ok",data=data)



@login_required
def gdl_quickpicks_settings_table_data_handle(request,page_size=20,page=1):
    vhost, vdomain, apperance = get_vhost_and_apperance(request)

    typeObjs = GDLTypeSettingsEntry.objects.filter(vhost=vhost)
    if "srt" in request.GET and request.GET["srt"] != "":
        sorters = request.GET["srt"].split(",")
        for sorter in sorters:
            typeObjs = typeObjs.filter(level=sorter)
    add_cols = {
        # "_details":{"type":"internal_modal_detail",
        #                   "text":"Details"},
        "_edit": {"type": "internal_modal_edit",
                          "text": "Edit"},
    }
    return paginator_paginate_and_serialise(typeObjs, page=page, page_size=page_size,
                                            filter_cols=["uuid","domain","name","icon","class_name","group_filter","sport_filter","order_by","active"],
                                            additional_col_names={"_edit":"Edit","uuid":"ID","domain":"VDomain",
                                                                  "icon":"Icon","class_name":'CSS Class',"group_filter":"Sports","sport_filter":"Leagues","order_by":"Ordering","active":"Active"},
                                            # relation_names={"match": "get_match_name", "team_1": "get_name", "account": "acctnum"},
                                            additional_cols=add_cols)



@login_required
def gdl_create_quickpicks_entry(request):
    vhost, vdomain, apperance = get_vhost_and_apperance(request)
    inputForm = GDLTypeSettingsEntryForm(request.POST)
    if inputForm.is_valid():
        inputForm.instance.vhost = vhost
        inputForm.instance.vdomain = vdomain
        inputForm.save()

        return generic_json_success("GDL Quickpicks Created!")
    else:
        return JsonResponse({"res": "err", "err": "Form Errors", "data": {"e": inputForm.errors}})


@login_required
def gdl_quickpicks_edit_handle(request,ruuid):
    vhost, vdomain, apperance = get_vhost_and_apperance(request)
    ruleObj = GDLTypeSettingsEntry.objects.get(uuid=ruuid)

    values,hex = edit_row_serialiser(ruleObj,)
    return generic_json_success("Editing Settings Group",data={"rows":values,"hex":hex})


@login_required
def gdl_quickpicks_save_handle(request):
    vhost, vdomain, apperance = get_vhost_and_apperance(request)
    if "uuid" in request.POST:
        ruleObj = GDLTypeSettingsEntry.objects.get(vhost=vhost,uuid=request.POST["uuid"])
        input_form = GDLTypeSettingsEntryForm(request.POST,instance=ruleObj)
        if input_form.is_valid():
            input_form.save()
            return generic_json_success("ok")
        else:
            return JsonResponse({"res":"err","err":input_form.errors},safe=False)
    # values,hex = edit_row_serialiser(ruleObj,)
    else:
        return generic_json_error("UUID not supplied.")

