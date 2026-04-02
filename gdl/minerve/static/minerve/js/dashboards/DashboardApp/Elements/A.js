import {_elementProto} from "./prototype.js";

export class ElementA extends _elementProto {

    constructor(href,text,props) {
        super()
        this.tag = "a"
        this.props = {
            "html":text,
            "href":href
        }
        $.extend(this.props, props);
        this.dom_el = this.dom_factory();

    }
}
export default ElementA;
