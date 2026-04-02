import {_elementProto} from "./prototype.js";

export class ElementLi extends _elementProto {

    constructor(text,props) {
        super()
        this.tag = "p"
        this.props = {
            "html":text
        }
        $.extend(this.props, props);
        this.dom_el = this.dom_factory();

    }
}
export default ElementLi;