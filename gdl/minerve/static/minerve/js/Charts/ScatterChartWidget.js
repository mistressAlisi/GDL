import {AbstractApp} from "/static/minerve/js/core/AbstractApp.js";

export class ScatterChartWidget extends AbstractApp {
    urls = {
        "_api_prefix":"",
        "source":"/path/to/chart/data"
    }

    settings = {
        "chart_js": {
            "responsive": true,

             "plugins": {
                "legend": {
                    "display": false,
                }
            }
        }
    }

    chart_js = false
    chart_builder(res) {
          this.chart_js = new Chart(this.canvas, {
                type: 'scatter',
                data: res.data,
                options: this.settings["chart_js"]
          });

    }
    start(url) {
        this.generic_api_getreq(url, false, this.chart_builder.bind(this));
    }
    constructor(settings, urls, elements) {
        super(settings, urls, elements);
        $.extend(this.settings, settings);
        $.extend(this.urls, urls);
        this.canvas = $("<canvas></canvas>");
    }

}
export default ScatterChartWidget;