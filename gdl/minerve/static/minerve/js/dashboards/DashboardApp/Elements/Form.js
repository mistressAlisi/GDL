import {_elementProto} from "./prototype.js";
import {ElementCheckboxInput, ElementHiddenInput, ElementInput, ElementSelect,ElementSubmit,ElementTextArea} from "./Elements.js";



export class ElementForm extends _elementProto {

    constructor(post_url,method="POST",target="#",on_submit=false,on_change=false,...rest) {
        // console.warn(post_url,method,rest);
        super();
        this.tag = "form";
        this.props = {
            "method": method,
            "data-post-url": post_url,
            "target": target,
        }
        this.texts = {
            "submit":"Save Record"
        }
        if ("texts" in rest) {
            console.warn(rest.texts)
            $.extend(this.texts, rest.texts);
        }
        // console.log(this.props);
        this.dom_el = this.dom_factory();
        if ("intro_str" in rest) {
            this.intro_str = $("<div>", {class: "p", html: rest.intro_str});
            this.content.append(this.intro_str);
        }
        if (on_submit != false) {
            this.dom_el.on("submit", on_submit);
        };
        if (on_change != false) {
            this.dom_el.on("change", on_change);
        };

    }

    load_fields(fields) {
          for (var i in fields) {
              var field = fields[i];
              var field_obj = false;

              var type = field.type;
              delete field.type;

              switch (type) {
                  case "uuid":
                     field_obj = new ElementHiddenInput(field.name,field.value);
                  break;
                  case "select":
                    field_obj = new ElementSelect(field.name,{"values":field.values,"value":field.value});
                  break;
                  case "boolean":
                      field_obj = new ElementCheckboxInput(field.name,field.value,{"verbose_name":field.verbose_name});
                  break;
                  case "json":
                      field_obj = new ElementTextArea(field.name,field.value,{"verbose_name":field.verbose_name});
                  break;
                  default:
                      field_obj = new ElementInput(field.name,type,{"text":field,"value":field.value,"verbose_name":field.verbose_name});
                  break;
              }

              if (field_obj != false) {
                  this.dom_el.append(field_obj.get_el());
              }
          }
          let field_btn = new ElementSubmit({"label":this.texts.submit,"class":"btn btn-accept"})
          this.dom_el.append(field_btn.dom_el);
    }
}
export default ElementForm;