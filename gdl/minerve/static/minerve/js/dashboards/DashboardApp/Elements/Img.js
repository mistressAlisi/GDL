import {_elementProto} from "./prototype.js";

export class ElementImg extends _elementProto {

    constructor(src,props) {
        super()
        this.tag = "img"
        this.props = {
            "src":src,
            "alt":src
        }
        $.extend(this.props, props);
        this.dom_el = this.dom_factory();

    }
}
export default ElementImg;