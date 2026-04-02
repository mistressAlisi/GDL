import {AbstractTableApp} from "./AbstractTableApp.js";

export class DynamicTableApp extends AbstractTableApp {
    _handle_config_start(res) {
        $.extend(this.settings, res.data.settings);
        $.extend(this.urls, res.data.urls);
        $.extend(this.texts, res.data.texts);
        this.generic_api_getreq(this.urls["paginator_endpoint"]+this.settings["pagination_size"],"filter="+this.filter_string,this._start_handle.bind(this));
    }
    start(config_url) {
        this.generic_api_getreq(config_url,false,this._handle_config_start.bind(this))

    }
}
export default DynamicTableApp;