import {_elementProto} from "./prototype.js";

export class ElementSubmit extends _elementProto {

    constructor({label,...rest}) {
        super()
        this.tag = "button";
        this.props = {
            "type": "submit",
            "class":"input-btn btn",
            "html":label
        }
        $.extend(this.props, rest);
        this.dom_el = this.dom_factory();

    }
}
export default ElementSubmit;