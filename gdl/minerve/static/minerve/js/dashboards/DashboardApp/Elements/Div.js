import {_elementProto} from "./prototype.js";

export class ElementDiv extends _elementProto {

    constructor(props) {
        super()
        this.tag = "div"
        $.extend(this.props, props);
        this.dom_el = this.dom_factory();

    }
}
export default ElementDiv;