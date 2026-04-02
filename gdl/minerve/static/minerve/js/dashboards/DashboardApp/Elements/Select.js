import {_elementProto} from "./prototype.js";

export class ElementSelect extends _elementProto {
    container = false;
    label = false;
    input = false;
    help = false;

    get_el() {
        return this.container;
    }

    create_option(value,label,curr_val=false) {
        this.tag = "option";
        this.props = {"value": value,"text": label};
        if (curr_val == value) {
            this.props["selected"] = "selected";
        }
        let option = this.dom_factory()
        this.input.append(option);
        return option;
    }

    set_options(rows,value) {
        for (let i in rows) {
            let row = rows[i];
            this.create_option(row.value,row.label,value);
        }
    }
    constructor(id,{...props}) {
        super()
        /** Build the container first: **/
        this.tag = "div"
        this.props = {"class": "mb-3 row"}
        if ("container_class" in props) {
            this.props["class"] = this.props["class"]+" "+props["container_class"];
        }
        this.container = this.dom_factory();
        this.props = {"class":"col-auto pt-2 mt-1 text-info"}
        let div1 = this.dom_factory();
        this.props = {"class":"col-auto"}
        let div2 = this.dom_factory();
        this.container.append(div1,div2)
        /** Now the label: **/
        this.tag = "label"
        this.props = {
            "for": id,
            "class": "form-label"
        }
        if ("verbose_name" in props){
            this.props["text"] = props["verbose_name"]+": ";
        } else {
            this.props["text"] = id+": ";
        }
        this.label = this.dom_factory();
        // console.warn(this.label,this.props);
        // this.container.append(this.label);
        div1.append(this.label);
        this.tag = "select";
        this.props = {
            "id": "id_"+id,
            "name":id,
            "class":"select",
            "aria-describedby": id+"help"
        }

        $.extend(this.props, props);
        if ("input_class" in props) {
            this.props["class"] = this.props["class"] + " " + props["input_class"]
        }
        this.input = this.dom_factory();
        // this.container.append(this.input);
        div2.append(this.input);
        this.tag = "div"
        this.props = {
            "id":id+"help",
            "class":"form-text",
            "text":""
        }
        if ("help_text" in props){
            this.props["text"] = props["help_text"];
        }
        this.help = this.dom_factory();
        // this.container.append(this.help);
        div2.append(this.help);
        if ('on_submit' in props) {
            this.dom_el.on("submit", props["on_submit"]);
        };
        if ('on_change' in props) {
            this.dom_el.on("change", props["on_change"]);
        }
        this.create_option("","---")
        let value = false;
        if ("values" in props) {
            let values = props["values"];
            if ("value" in props) {
                value = props["value"];
            }
            this.set_options(values,value);
        }


    }

}
export default ElementSelect;