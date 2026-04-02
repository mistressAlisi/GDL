import {_elementProto} from "./prototype.js";

export class ElementH extends _elementProto {

    constructor(size=1,text,props) {
        super()
        this.tag = "h"+size;
        this.props = {
            "html":text
        }
        $.extend(this.props, props);
        this.dom_el = this.dom_factory();

    }
}
export default ElementH;