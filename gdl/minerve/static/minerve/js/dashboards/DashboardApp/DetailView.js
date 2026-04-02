export class DetailView {
    settings= {
        "detail_view_select_modal":"#select_detail_modal",
        "detail_view_select":"#select_detail",
        "detail_view_container":"#detail_view_container",
    }
    urls = {
        "_prefix":"/agent/dashboard/",
        "_api_prefix":"/api/v1/agent/",
        "detail_selector_url":"",
        "detail_page_url":""
    }
    elements = {

    }
    _current_url = ""
    load_details(event) {

        event.preventDefault();
        event.stopPropagation();
        let currval = $(this.settings.detail_view_select)[0].value;
        if (currval == "") {
            agent.errorToast("Select an item!","Invalid selection.");
        } else {
            this._current_url = this.urls["_prefix"]+$(event.target).data("get-url")+"/"+currval;
            $(this.settings.detail_view_container).show();
            $(document).trigger("loading");
            $(this.settings.detail_view_container).load(this._current_url)
            $(this.settings.detail_view_select_modal).modal('hide');
        }
    }
    refresh() {
        $(this.settings.detail_view_container).load(this._current_url);
    }

    switch_detail() {
        $(this.settings.detail_view_container).hide();
        this.start();
    }

    start() {

        $(this.settings.detail_view_select).selectize({});
        $(this.settings.detail_view_select_modal).modal('show');
    }

    constructor(settings,urls,elements) {
        $.extend(this.settings,settings);
        $.extend(this.urls,urls);
        $.extend(this.elements,elements);
    }
}