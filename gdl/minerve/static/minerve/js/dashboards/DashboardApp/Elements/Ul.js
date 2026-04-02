import {_elementProto} from "./prototype.js";

export class ElementUl extends _elementProto {

    constructor(props) {
        super()
        this.tag = "ul"
        $.extend(this.props, props);
        this.dom_el = this.dom_factory();

    }
}
export default ElementUl;