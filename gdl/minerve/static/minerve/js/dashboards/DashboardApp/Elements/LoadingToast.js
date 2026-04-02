import {_elementProto} from "./prototype.js";

export class ElementLoadingToast extends _elementProto {
    container = false;
    constructor({message="Loading",icon="fa-spinner"}) {
        super();
        this.tag = "div";
        this.props = {
            "class": "toast-container top-0 end-0 p-3 float-right",
        }
        this.container = this.dom_factory();
        this.props = {
            "id":"loading_toast",
            "class":"toast toast-top-right bg-dark",
            "role":"alert",
            "aria-live":"assertive",
            "aria-atomic":"true",
        }
        this.dom_el  = this.dom_factory()
        this.container.append(this.dom_el);
        this.props = {
            "class": "toast-header bg-dark text-primary border-primary border-2",
            "html":"<i class='fa-solid fa-gauge'></i>",
        }
        let header = this.dom_factory()
        this.dom_el.append(header);
        this.props = {
            "class": "toast-body bg-dark bg-opacity-50 text-white",
            "html":"<i class='"+icon+" pe-1'></i> "+message,
        }
        let body = this.dom_factory()
        this.dom_el.append(body);
    }
}