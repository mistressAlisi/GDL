export class _elementProto {
    dom_el = false
    dom_con = false;
    tag = false
    props = {}

    append(element) {
        // console.log("DOM EL",this.dom_el);
        // console.log("element",element);
        if (("dom_el" in element) && (element["dom_el"] != false)) {
            return this.dom_el[0].append(element.dom_el);
        } else {

            return this.dom_el[0].append(element[0]);
        }
    }

    dom_factory() {
        let dom_el = $("<"+this.tag+"/>",this.props);
        return dom_el;
    }
    get_el() {
        return this.dom_el;
    }
    get_container() {
        if (this.dom_con) {
            return this.dom_con;
        } else {
            return this.dom_el;
        }
    }

}