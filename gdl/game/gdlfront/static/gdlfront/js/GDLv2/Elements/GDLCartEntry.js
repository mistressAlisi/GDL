import {_elementProto} from "/static/minerve/js/dashboards/DashboardApp/Elements/prototype.js";

export class ElementGDLCartEntry extends _elementProto {
    settings = {
        "li_class":"list-group-item d-flex justify-content-between align-items-start",
        "badge_class":"badge text-bg-primary rounded-pill"
    }
    data = {}
    props = {}
    texts = {
        wins: "Ticket Wins 5000 for 1",
        details: "<i class=\"fa-duotone fa-solid fa-magnifying-glass-chart\"></i> Details",
        remove: "<i class=\"fa-solid fa-xmark\"></i> Remove",
        events: "7 events",
    }
    details_btn = false
    remove_btn = false

    constructor(id, texts = {}, data = {}, props = {}, settings = {}) {
        super(id, texts, data);
        this.id = id;
        this.props = props;
        $.extend(this.texts, texts)
        $.extend(this.data, data);
        $.extend(this.texts, texts);
        $.extend(this.settings, settings);
        // console.warn(this.data);
        // console.warn(this.texts);
        this.dom_el = this._render();
    }
    _remove_itm() {
        this.dom_el.destroy();
    }
    _render() {
        this.tag = "li"
        this.props = {"class":this.settings["li_class"]};
        let dom_el = this.dom_factory()
        this.tag = "div"
        this.props = {"class":"ms-2 me-auto"};
        let container = this.dom_factory()
        dom_el.append(container);
        this.props = {"class":"fw-bold","text":this.texts["wins"]};
        let text = this.dom_factory()
        container.append(text);
        this.tag = "a"
        this.props = {"class":"text-info pe-1","href":"#","html":this.texts["details"],"data-uuid":this.data["uuid"]};
        this.details_btn = this.dom_factory()
        container.append(this.details_btn);
        this.props = {"class":"text-danger pe-1","href":"#","html":this.texts   ["remove"],"data-uuid":this.data["uuid"]};
        this.remove_btn = this.dom_factory()
        container.append(this.remove_btn);
        this.tag = "span"
        this.props = {"class":this.settings["badge_class"],"html":this.texts["events"]};
        let badge = this.dom_factory()
        dom_el.append(badge);
        return dom_el;


    }
}
export default ElementGDLCartEntry;