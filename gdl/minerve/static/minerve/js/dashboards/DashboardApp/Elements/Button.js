import {_elementProto} from "./prototype.js";

export class ElementButton extends _elementProto {

    constructor(text,props) {
        super()
        this.tag = "button"
        this.props = {
            "html":text
        }
        $.extend(this.props, props);
        this.dom_el = this.dom_factory();

    }
}
export default ElementButton;