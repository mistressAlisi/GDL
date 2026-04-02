export class Paginator {
    settings = {
        "table_placeholder_div": "#table_placeholder",
        "table_loading_div": "#table_loading",
        "table_container": "#table_container",
        "paginator_url_el": "#paginator_url",
        "paginator_murl_el": "#paginator_murl",

    }
    urls = {
        "_prefix": "/agent/dashboard/",
        "_api_prefix": "/api/v1/agent/",
        "paginator_url": "",
        "paginator_meta_url": "",
    }
    parent = false
    elements = {}
    search_params = {}
    current_page = 0
    total_pages = 0
    _handleTableLoad(res) {

        this.hide_load();
    }
    _handleMeta(res) {
        if (res.res == "ok") {
            this.total_pages = res.paginator.total_pages;
            this.current_page = res.paginator.current_page;
            this.load_page(this.current_page);
            try {
                this.parent.elements["form"] = $(this.parent.settings["edit_form_id"]);
                this.parent._edit_form_loader(res.values);
            } catch (e) {
                console.warn("Unable to execute _edit_form_loader after HandleMeta:");
                console.warn(e);
            }

        }

    }

    load_page(page) {
            this.show_load();
            let url = this.urls["_prefix"]+this.urls["paginator_url"]
            this.elements["container"].load(url,this.search_params+"&p="+page,this._handleTableLoad.bind(this))
    }
    reload_page() {
        this.load_page(this.current_page);
    }
    hide_load() {
        this.elements["loading"].hide();
        this.elements["container"].show();
    }

    show_load() {
        this.elements["placeholder"].hide();
        this.elements["container"].hide();
        this.elements["loading"].show();
    }
    start(event) {
        this.search_params = $(event.target).serialize();
        this.urls["paginator_url"] = $(this.settings["paginator_url_el"])[0].value;
        this.urls["paginator_meta_url"] = $(this.settings["paginator_murl_el"])[0].value;
        let url = this.urls["_api_prefix"]+this.urls["paginator_meta_url"]
        this.elements["placeholder"] = $(this.settings["table_placeholder_div"])
        this.elements["loading"] = $(this.settings["table_loading_div"])
        this.elements["container"] = $(this.settings["table_container"])
        $.get(url,this.search_params,this._handleMeta.bind(this))




    }
    pre_start() {
        this.elements["loading"] = $(this.settings["table_loading_div"])
        this.elements["loading"].hide();
    }
    constructor(parent,settings, urls, elements) {
        $.extend(this.settings, settings);
        $.extend(this.urls, urls);
        $.extend(this.elements, elements);
        this.parent = parent;

        console.log("Paginator(tm) Ready");




    }
}