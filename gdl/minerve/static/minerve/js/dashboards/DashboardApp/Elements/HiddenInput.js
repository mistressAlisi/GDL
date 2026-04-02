import {_elementProto} from "./prototype.js";

export class ElementHiddenInput extends _elementProto {

    constructor(id,value,props) {
        super()
        this.tag = "input";
        this.props = {
            "id": "id_"+id,
            "name":id,
            "type": "hidden",
            "value":value
        }
        $.extend(this.props, props);
        this.dom_el = this.dom_factory();

    }
}
export default ElementHiddenInput;