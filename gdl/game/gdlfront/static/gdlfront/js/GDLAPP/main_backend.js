import {AbstractDashboardApp} from "/static/minerve/js/dashboards/DashboardApp/AbstractDashboardApp.js";
import {AbstractTableApp} from "/static/minerve/js/TableApp/AbstractTableApp.js";
import {ElementButton} from "/static/minerve/js/dashboards/DashboardApp/Elements/Button.js";
import {ElementGDLCard} from "./Elements/GDLCard.js";
import {ElementGDLCartEntry} from "./Elements/GDLCartEntry.js";
import {DetailView} from "/static/minerve/js/dashboards/DashboardApp/DetailView.js";
import {Paginator} from "/static/minerve/js/dashboards/DashboardApp/Paginator.js";

export class GDLBackendApp extends AbstractDashboardApp {

    urls = {
        "_api_prefix": "/api/v1/game/",
        "_prefix":"/game/ticket/",
        "submit_step1": "run_step1",
        "ticket_viewer": "active/details/viewer/",
        "_paginator_endpoint": "tickets/previous/table/",
        "internal_details_ajax_url":"active/details/viewer/",
        "delete_all_endpoint":"messages/delete/all"
    }
    settings = {
         "display_cols": ["created","application_type","type","risk","win","match","team_1","status"],
         "anchor":"#detail_item_card",
         "loading_toast":"#loading_toast",
        "outcome":"#id-outcome",
        "col_actions":{
             "uuid":"inline_details_view"
        },
        "start":"#id-start",
        "end":"#id-end",
        "submit_form":"#detail_select_form",
        "table_class":"table table-striped table-hover table-responsive table-dark",

    }
    elements = {}
    table = false

    show_ticket_modal(uuid) {
        this.generic_ajax_modal_dialogue("Ticket Details", this.urls["ticket_viewer"] + uuid, false, this.settings["viewer_modal_width"], true, false, false, true)
    }

    constructor(settings, urls) {
        super(settings, urls)
        $.extend(this.settings, settings);
        $.extend(this.urls, urls);
        this.elements["anchor"] = $(this.settings.anchor);
        this.elements["loading_toast"] = $(this.settings.loading_toast);
        this.elements["submit_form"] = $(this.settings.submit_form);
        this.elements["submit_form"].on("submit", this.start.bind(this));
    }

    start(event) {
        if (event != null) {
            event.stopPropagation()
            event.preventDefault()
        }
        this.elements["anchor"].empty();
        if ($(this.settings["start"]).length > 0) {
            var start = $(this.settings["start"])[0].value
            var end = $(this.settings["end"])[0].value
            var outc = $(this.settings["outcome"])[0].value
            this.urls["paginator_endpoint"] = this.urls["_paginator_endpoint"] + start + "/" + end + "/" + outc + "/"
        } else {
            this.urls["paginator_endpoint"] = this.urls["_paginator_endpoint"]
        }
        this.table = new AbstractTableApp({
            "display_cols":this.settings.display_cols,"col_actions":this.settings.col_actions,
            "table_class":this.settings.table_class,
            // "totals_div":"#totals_div",
            "select_all_enabled":false
        },this.urls);
        this.elements["anchor"].append(this.table.get_container());
        this.table.start(50)
    }
}
export default GDLBackendApp;