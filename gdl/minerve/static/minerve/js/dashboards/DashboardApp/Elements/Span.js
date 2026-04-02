import {_elementProto} from "./prototype.js";

export class ElementSpan extends _elementProto {

    constructor(text,props) {
        super()
        this.tag = "span"
        this.props = {
            "html":text
        }
        $.extend(this.props, props);
        this.dom_el = this.dom_factory();

    }
}
export default ElementSpan;