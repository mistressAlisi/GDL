import {AbstractApp} from "/static/minerve/js/core/AbstractApp.js";
import {
    ElementCheckboxInput,
    ElementForm,
    ElementHiddenInput,
    ElementInput,
    ElementModal, ElementSubmit,
    ElementA
} from "../dashboards/DashboardApp/Elements/Elements.js";


export class AbstractTableApp extends AbstractApp {
    settings = {
        "table_class":"table table-striped table-hover table-responsive",
        "tr_class":"",
        "pagination_size":15,
        "navigation_pill_count_box_break":10,
        "navigation_display_count":true,
        "navigation_display_status":true,
        "navigation_display_pbar":true,
        "disable_normal_toasts":false,
        "totals_div": false,
        "select_all_enabled":false,
        "toast_class":"",
        "display_cols": [],
        "filter_form_fields":[],
        "col_actions": {},
    }
    urls = {
        "_api_prefix":"/api/v1/",
        "_prefix":"/",
        "paginator_endpoint":"change/me",
        "detail_endpoint":"change/me/",
        "edit_endpoint":"change/me/",
        "save_endpoint":"change/me/",
        "delete_endpoint":"change/me/",
        "internal_modal_ajax_url":"change/me/",
        "internal_details_ajax_url":"change/me/",
        "delete_all_endpoint":"change/me/",
        "search_endpoint":"change/me",
        "save_all_endpoint":"change/me"

    }
    texts =  {
        "navigation_aria": "Table Navigation Range",
        "previous":"Previous",
        "next":"Next",
        "viewing":"Viewing ",
        "records":"records",
        "ready":"<i class=\"fa-regular fa-signal-stream\"></i> Ready!",
        "loading":"<i class=\"fa-solid fa-spinner fa-spin-pulse text-primary\"></i> Loading...",
        "error":"<i class=\"fa-duotone fa-solid fa-circle-exclamation text-red\"></i> Error!",
        "sort_by":"<i class=\"fa-duotone fa-solid fa-sort\"></i> Sort by:",
        "sort_none":"<i class=\"fa-duotone fa-solid fa-circle-0\"></i> None",
        "sort_asc":"<i class=\"fa-duotone fa-solid fa-up-to-dotted-line\"></i> Ascending",
        "sort_desc":"<i class=\"fa-duotone fa-solid fa-down-to-dotted-line\"></i> Descending",
        "search":"<i class=\"fa-duotone fa-solid fa-radar\"></i> Search",
        "go_search":"<i class=\"fa-duotone fa-solid fa-magnifying-glass\"></i>",
        "all_records":"Viewing all records.",
        "detail_column_name":"Detail Name",
        "detail_column_value":"Detail Value",
        "edit_modal_title":"Edit Record",
        "detail_modal_title":"Record Details",
        "edit_header":"Success!",
        "edit_body":"Record updated successfully.",
        "empty_table":"",
        "filter_modal_title":"Filter Settings",
        "select_col":"Select",
        "select_all":"(De)Select All",
        "delete_sel":"Delete Sel.",
        "delete_confirm":"Delete all selected records?",
        "add_sel":"Add Selected",
        "save_confirm":"Create/Save selected records?"

    }

    navigation = {
        "container":false,
        "previous": false,
        "next": false,
        "box": false,
        "buttons": {}
    }
    sorters = {

    }
    searchers = {

    }

    display_cols = []
    col_names = {}
    row_data = []
    total_records = 0
    total_pages = 0
    current_page = 0
    tag = false
    props = {}
    table = false
    dom_con = false
    header = false
    body = false
    header_div = false
    footer = false
    footer_div = false
    header_set = false
    filter_modal = false
    filter_form = false
    filter_string = false
    filter_fields = []
    del_all_btn = false
    select_checkboxes = []
    last_detail_modal = false
    dom_factory() {
        let dom_el = $("<"+this.tag+"/>",this.props);
        return dom_el;
    }
    get_el() {
        return this.table;
    }
    get_container() {
        return this.dom_con;
    }

    normalToast(header, body) {
        if (this.settings["disable_normal_toasts"] !== true) {
            new bs5.Toast({
                body: body,
                header: header,
                className: this.settings.toast_class,

            }).show();
        }
    }
    _handle_filter_form_post(event) {
        event.preventDefault();
        event.stopPropagation();
        this.filter_modal.bs_modal.hide()
        this.filter_fields = this.filter_form.get_el().serializeArray()
        this.filter_string = ""
        for (let f in this.filter_fields) {
            let fd = this.filter_fields[f];
            this.filter_string = this.filter_string+fd["name"]+"_eql_"+fd["value"]+";;"
        }
        console.log(this.filter_string)
        this.load(this.current_page)
        $(this).trigger('filter_change',this.filter_fields);

    }

    open_filter_form() {
        if (this.filter_modal === false) {
            this.filter_modal = new ElementModal(this.texts.filter_modal_title, "", true, false, $(document.body))
            this.filter_form = new ElementForm("#", "POST", "#")
            this.filter_form.texts["submit"] = "Set filter"
            this.filter_form.get_el().on("submit", this._handle_filter_form_post.bind(this));
            this.filter_modal.modalBody.empty();
            this.filter_modal.modalBody.append(this.filter_form.get_el())
            this.filter_form.load_fields(this.settings.filter_form_fields)
        }
        this.filter_modal.bs_modal.show()

    }

    _handle_imf_post(edit_modal,res) {
        this.normalToast(this.texts.edit_header,this.texts.edit_body);
        edit_modal.bs_modal.hide()
        this.load(this.current_page)
    }
    _handle_internal_modal_form(edit_modal,event) {
        this.generic_post_form_v2({"event":event,"callback":this._handle_imf_post.bind(this,edit_modal)})
    }
    _internal_modal_edit_handle(res) {
        let edit_modal = new ElementModal(this.texts.edit_modal_title,"",true,false,$(document.body));
        let form = new ElementForm(this.urls.save_endpoint);
        this.elements["form"] = form.dom_el
        edit_modal.modalBody.empty()
        edit_modal.modalBody.append(form.dom_el);
        form.dom_el.on("submit",this._handle_internal_modal_form.bind(this,edit_modal));
        // console.warn(res.data.rows);
        form.load_fields(res.data.rows);
        edit_modal.bs_modal.show();

    }


    _internal_modal_detail_render(res) {
        let detail_modal = new ElementModal(this.texts.detail_modal_title,"",true,false,$(document.body));
        let rowkeys = Object.keys(res.data.values)
        this.tag = "table"
        this.props = {"class":"table table-striped table-hover table-responsive",}
        let table = this.dom_factory();
        detail_modal.modalBody.empty();
        detail_modal.modalBody.append(table);
        this.tag = "thead"
        let theadc = this.dom_factory();
        this.tag = "tbody"
        let tbody = this.dom_factory();

        this.table.append(theadc);
        this.tag = "tr";
        this.props = {};
        let thead = this.dom_factory();
        this.tag = "td";
        this.props = {"html":this.texts.detail_column_name};
        let thd1 = this.dom_factory();
        thead.append(thd1);
        this.props = {"html":this.texts.detail_column_value};
        thd1 = this.dom_factory();
        thead.append(thd1);
        theadc.append(thead);
        table.append(theadc);
        table.append(tbody);
        for (let i in rowkeys) {
            let key = rowkeys[i];
            this.tag = "tr";
            this.props = {};
            let ltr = this.dom_factory();
            tbody.append(ltr);
            this.tag = "td";
            if (key in res.data.names) {
                this.props = {"text":res.data.names[key]+":"}
            } else {
                this.props = {"text":key+":"}
            }
            let ltd = this.dom_factory();
            ltr.append(ltd);
            this.props = {"text":res.data.values[key]}
            ltd = this.dom_factory();
            ltr.append(ltd);

        }
        detail_modal.bs_modal.show()
    }
    _internal_modal_ajax_handle(event) {
            let uuid = $(event.target).data("uuid");
            let detail_modal = new ElementModal(this.texts.detail_modal_title,"95%",true,false,$(document.body));
            let url = this.urls["_prefix"] + this.urls["internal_modal_ajax_url"] + uuid;
            detail_modal.modalBody.load(url)
            detail_modal.dialog.addClass('modal-dialog-scrollable');
            detail_modal.bs_modal.show()
            this.last_detail_modal = detail_modal;
    }
    _internal_modal_detail_handle(event) {
            let uuid = $(event.target).data("uuid");
            this.generic_api_getreq(this.urls.detail_endpoint+uuid,false,this._internal_modal_detail_render.bind(this));

    }
    _internal_edit_handle(event) {
            let uuid = $(event.target).data("uuid");
            this.generic_api_getreq(this.urls.edit_endpoint+uuid,false,this._internal_modal_edit_handle.bind(this));

    }
    _internal_details_view_handle(event) {
        event.preventDefault();
        event.stopPropagation();
        let uuid = $(event.target).data("uuid");
        let rowid = "__internal_det-"+uuid;
        let parent_tbody =this._parent_walker($(event.target)[0],"TBODY")
        let fres = parent_tbody.find("#"+rowid)
        if (fres.length > 0) {
            fres[0].remove();
        } else {
            let parent_tr = this._parent_walker($(event.target)[0], "TR")
            window.ptr = parent_tr;
            this.tag = "tr"
            this.props = {
                "id": rowid,
                "colspan": parent_tr.children().length,
            }
            let new_tr = this.dom_factory();
            parent_tr.after(new_tr)
            let url = this.urls["_prefix"] + this.urls["internal_details_ajax_url"] + uuid;
            this.tag = "td"
            this.props = {
                "html": "Loading....",
                "colspan": parent_tr.children().length
            }
            let new_td = this.dom_factory();
            new_tr.append(new_td);
            new_td.load(url)
            this.tag = "tr"
            this.props = {}
        }
    }

    _add_row(data,additional_cols=false) {

        this.tag = "tr"
        this.props = {}
        let row_data = {
            "tr":this.dom_factory(),
            "tds":[]
        }
        this.tag = "td"
        let pk = ''
        for (let key in data) {
            if (key === "__pk") {
                pk = data[key]
            } else if (key in this.settings.col_actions) {
                // Dynamic Actions for the Columns:
                switch (this.settings.col_actions[key]) {
                    case "inline_details_view":
                        this.props = {
                                "id": "td_" + key,
                        }
                        let td = this.dom_factory()
                        this.tag = "a"
                        this.props = {
                            "href":"#",
                            "html":data[key],
                            "data-uuid":data[key]
                        }
                        let a = this.dom_factory()
                        td.append(a);
                        a.on("click",this._internal_details_view_handle.bind(this))
                        row_data["tds"].push(td)
                        row_data["tr"][0].append(td[0])
                        this.tag = "td"
                    break;
                }
            } else {
                // console.log(key,data[key],typeof(data[key]))
                switch (typeof (data[key])) {
                    case "object":
                        if (data[key] !== null) {
                            this.props = {
                                "html": data[key].name,
                                "id": "td_" + key,
                                "data_id": data[key].id,
                            }
                        } else {
                            this.props = {
                                "html": "",
                                "id": "td_" + key,
                                "data_id":""
                            }
                        }
                        break;

                    default:
                        this.props = {
                            "html": data[key],
                            "id": "td_" + key
                        }
                        break;
                }
                let td = this.dom_factory()
                row_data["tds"].push(td)

                row_data["tr"][0].append(td[0])
            }
        }
        if (additional_cols !== false) {
            for (let key in additional_cols) {
                let element = false
                let addcol = additional_cols[key]
                // Additional column feature support being initated here:
                // First type: Modal Link!
                if (addcol["type"] === "modal_view") {
                    element = new ElementA("#", addcol["text"], {"onclick": addcol["onclick"] + "('" + pk + "');"})
                } else if (addcol["type"] === "internal_modal_detail") {
                    element = new ElementA("#", addcol["text"], {"data-uuid": pk})
                    element.dom_el.on("click", this._internal_modal_detail_handle.bind(this))
                } else if (addcol["type"] === "internal_modal_ajax") {
                    element = new ElementA("#", addcol["text"], {"data-uuid": pk})
                    element.dom_el.on("click", this._internal_modal_ajax_handle.bind(this))
                } else if (addcol["type"] === "internal_modal_edit") {
                    element = new ElementA("#", addcol["text"], {"data-uuid":pk})
                    element.dom_el.on("click",this._internal_edit_handle.bind(this))
                }
                // console.log(element);
                if (element !== false) {
                    this.props = {"id": "td_" + key}
                    let td = this.dom_factory()
                    td[0].append(element.get_el()[0])
                    row_data["tds"].push(td)
                    row_data["tr"][0].append(td[0])
                }
            }
        }
        if (this.settings["select_all_enabled"] === true) {
                let element = new ElementCheckboxInput("sel_"+pk, false,{"data-uuid":pk})
                this.props = {"id": "select"}
                let td = this.dom_factory()
                this.select_checkboxes.push(element.input)
                td[0].append(element.input[0])
                row_data["tds"].push(td)
                row_data["tr"][0].append(td[0])
        }
        this.row_data.push(row_data)
        this.body[0].append(row_data["tr"][0])
        this.row_count++
    }

    _update_record_modal(options,res) {
      let modal = new ElementModal(options);
      let form = new ElementForm({"post_url":res.post_url});
      for (var i in res.fields) {
          var field = res.fields[i];
          var field_obj = false;
          // console.log(field);
          var type = field.type;
          delete field.type;
          switch (type) {
              case "uuid":
                 field_obj = new ElementHiddenInput(field.name,field.value,field);
              break;
              default:
                  field_obj = new ElementInput(field.name,field.type,field)
          }
          // console.warn(field_obj);
          if (field_obj != false) {
              form.append(field_obj.get_el());
          }
      }
      var submit = new ElementSubmit({"label":"Update Record"});
      form.append(submit.get_el());
      form.get_el().on("submit", this._handle_generic_ajax_update_form.bind(this))
      modal.modalBody.empty();
      modal.modalBody.append(form.get_el());
      modal.modalDiv.on("hidden.bs.modal", function (event) {
           $(event.target).remove();
      });
      modal.bs_modal.show();
      if ("refresh" in options) {
          modal.refresh = true;
      }
      this.last_modal_created = modal
     // console.log(res,options);

    }

    _set_header(column_obj = []) {
        let columns = Object.values(column_obj)
        let keys = Object.keys(column_obj)
        this.header.empty()
        this.tag = "tr"
        this.props = {}
        let tr = this.dom_factory();
        this.header.append(tr[0])
        console.log("Columns",columns)
        for (let key in columns) {
            this.tag = "td"
            this.props = {"id":"col_"+key,"class":this.settings["tr_class"]}
            let td = this.dom_factory();
            tr[0].append(td[0])
            this.tag = "div"
            this.props = {"class":"dropdown"}
            let drpdn = this.dom_factory()
            this.tag = "a"
            this.props = {"class":"dropdown-toggle dropdown-toggle-split","href":"#","data-bs-toggle":"dropdown","data-bs-auto-close":"outside","role":"button","text":columns[key]}
            let a = this.dom_factory()
            drpdn[0].append(a[0])
            this.tag = "ul"
            this.props = {"class":"dropdown-menu"}
            let ul = this.dom_factory()
            drpdn[0].append(ul[0])
            this.tag = "li"
            this.props = {"class":"dropdown-item"}
            let li = this.dom_factory()
            this.tag = "a"
            this.props = {"class":"dropdown-item","html":this.texts["sort_by"]+" "+this.texts["sort_none"],"href":"#"}
            this.sorters[key] = this.dom_factory()
            this.sorters[key].on("click", this._handle_sort_event.bind(this))
            this.sorters[key].data("sort_target",keys[key]);
            this.sorters[key].data("sort_key",key);
            this.sorters[key].data("sort_mode","none");
            li[0].append(this.sorters[key][0])
            ul[0].append(li[0])
            this.tag = "li"
            this.props = {"class":"dropdown-item mb-3 p-2 input-group"}
            let li2 = this.dom_factory()
            this.tag = "label"
            this.props = {"class":"form_label","html":this.texts["search"]}
            let label = this.dom_factory()
            li2[0].append(label[0])
            this.tag = "div"
            this.props = {"class":"input-group mb-3"}
            let div = this.dom_factory()
            this.tag = "input"
            this.props = {"class":"form-control p-1","type":"text"}
            this.searchers[key] = this.dom_factory()
            div[0].append(this.searchers[key][0])
            this.tag = "button"
            this.props = {"class":"btn btn-sm btn-primary btn-sm","html":this.texts["go_search"]}
            let btn = this.dom_factory()
            div[0].append(btn[0])
            li2[0].append(div[0])

            ul[0].append(li2[0])
            td.append(drpdn[0])
        }
        if (this.settings["select_all_enabled"] == true) {

            this.tag = "td"
            this.props = {"text":this.texts["select_col"]}
            let td = this.dom_factory();
            tr[0].append(td[0])

        }
        this.col_names = columns;
    }

    _handle_sort_event(event) {
        event.preventDefault()
        event.stopPropagation()
        let trgt = $(event.target)
        let key = trgt.data("sort_key")
        let col = trgt.data("sort_target")
        let srt = trgt.data("sort_mode")
        switch (srt) {
            case "none":
                trgt.data("sort_mode","ASC")
                trgt.html(this.texts["sort_by"]+" "+this.texts["sort_asc"])
            break;
            case "ASC":
                trgt.data("sort_mode","DESC")
                trgt.html(this.texts["sort_by"]+" "+this.texts["sort_desc"])
            break;
            case "DESC":
                trgt.data("sort_mode","none")
                trgt.html(this.texts["sort_by"]+" "+this.texts["sort_none"])
            break;

        }
        this.load(this.current_page)
        // console.log(trgt,col,key,srt)
    }

    _build_sort_qrystring() {
        let srt = "&srt="
        for (let key in this.sorters) {
            let trgt = $(this.sorters[key])
            let col = trgt.data("sort_target")
            let mode = trgt.data("sort_mode")
            if (mode == "ASC") {
                srt = srt + col+";"
            } else if (mode == "DESC") {
                srt = srt + "-"+col+";"
            }
        }
        return srt.slice(0,-1)
    }

    _set_navigation(parent) {

        this.tag = "nav"
        this.props = {"aria-label":this.texts["navigation_aria"]}
        let foot_root = this.dom_factory()
        parent.append(foot_root[0])
        this.tag = "ul"
        this.props = {"class":"pagination"}
        this.navigation.container = this.dom_factory()
        foot_root[0].append(this.navigation.container[0])
        this.tag = "li"
        this.props = {"class":"page-item"}
        let prev = this.dom_factory()
        this.tag = "btn"
        this.props = {"class":"btn btn-primary me-1","text":this.texts["previous"],"data-page":"prev"}
        this.navigation.previous = this.dom_factory()
        this.navigation.previous.on("click",this._nav_btn_handle.bind(this));
        prev[0].append(this.navigation.previous[0])
        this.navigation.container.append(prev[0])
        this.tag = "li"
        this.props = {"class":"page-item"}
        let next = this.dom_factory()
        // Simple pill navigation below:
        var effective_total_pages = Math.max(
        1,
        Math.ceil(this.total_records / this.settings["pagination_size"])
        );
        if (effective_total_pages < this.settings["navigation_pill_count_box_break"]) {
            let i = 1;

            while (i <= effective_total_pages) {
                this.tag = "li"
                this.props = {"class":"page-item"}
                let lli = this.dom_factory()
                this.tag = "btn"
                let btn_class ="btn-success"
                if (i%2 != 0) {
                    btn_class="btn-primary"
                }
                this.props = {"class":"btn ps-2 pe-2 ms-1 me-1 "+btn_class,"text":i,"data-page":i}
                let lah = this.dom_factory()
                lli[0].append(lah[0])
                this.navigation.container.append(lli[0])
                this.navigation.buttons[i] = lah;
                lah.on("click",this._nav_btn_handle.bind(this));
                i++;
            }
        // Too long! Interactive Input and multibutton support below:
        } else {
            let i = 1;
            while (i <= 3) {
                this.tag = "li"
                this.props = {"class":"page-item"}
                let lli = this.dom_factory()
                this.tag = "btn"
                let btn_class ="btn-success"
                if (i%2 != 0) {
                    btn_class="btn-primary"
                }
                this.props = {"class":"btn ps-2 pe-2 ms-1 me-1 "+btn_class,"text":'-',"data-page":i}
                let lah = this.dom_factory()
                lli[0].append(lah[0])
                this.navigation.container.append(lli[0])
                this.navigation.buttons[i] = lah;
                lah.on("click",this._nav_btn_handle.bind(this));
                i++;
            }
            this.tag = "input"
            this.props ={"type":"number","class":"form-control pt-0 pb-0 mt-0 mb-0","id":"current_nav","style":"max-width: 10vh;","max":effective_total_pages, "min":1}
            this.navigation.box = this.dom_factory()
            this.navigation.box.on("change",this._nav_btn_handle.bind(this));
            this.navigation.container.append(this.navigation.box[0])
            while (i <= 6) {
                this.tag = "li"
                this.props = {"class":"page-item"}
                let lli = this.dom_factory()
                this.tag = "btn"
                let btn_class ="btn-success"
                if (i%2 != 0) {
                    btn_class="btn-primary"
                }
                this.props = {"class":"btn ps-2 pe-2 ms-1 me-1 "+btn_class,"text":'-',"data-page":i}
                let lah = this.dom_factory()
                lli[0].append(lah[0])
                this.navigation.container.append(lli[0])
                this.navigation.buttons[i] = lah;
                lah.on("click",this._nav_btn_handle.bind(this));
                i++;
            }
        }

        this.tag = "btn"
        this.props = {"class":"btn btn-primary ms-1","text":this.texts["next"],"data-page":"next"}
        this.navigation.next = this.dom_factory()
        this.navigation.next.on("click",this._nav_btn_handle.bind(this));
        next[0].append(this.navigation.next[0])
        this.navigation.container.append(next[0])


    }

    _set_status(text) {
        if (this.navigation.status_display) {
            $(this.navigation.status_display).html(text);
        }
    }
    _set_display_count_html(nhtml) {
        if (this.navigation.display_count) {
            this.navigation.display_count.html(nhtml);
        }
    }
    _set_display_count(page) {
        if (this.navigation.display_count) {
            let ntext = this.texts["viewing"]+" "+page*this.settings["pagination_size"]+"/"+this.total_records+" "+this.texts["records"]
            this.navigation.display_count.text(ntext);
        }
        if (this.navigation.display_pbar_bar) {
            let progress = ((page*this.settings["pagination_size"]) / this.total_records)*100;
            this.navigation.display_pbar_bar[0].style.width = progress+"%";
        }
    }
    _set_footer() {
        this.footer_div.empty()
        this.tag = "div"
        this.props = {"class":"d-flex justify-content-between"}
        let nav_box = this.dom_factory()
        this.props = {}
        let nav_ctrls = this.dom_factory()
        this.footer_div[0].append(nav_box[0])
        nav_box[0].append(nav_ctrls[0])
        this._set_navigation(nav_ctrls[0]);
        if (this.settings["navigation_display_count"] == true) {
            this.tag = "div"
            this.props = {"text":this.texts["viewing"]+" "+this.current_page*this.settings["pagination_size"]+"/"+this.total_records+" "+this.texts["records"]}
            this.navigation.display_count = this.dom_factory()
            nav_box[0].append(this.navigation.display_count[0])
        }
        if (this.settings["navigation_display_pbar"] == true) {
            this.tag = "div"
            this.props = {"class":"progress col-2","role":"progressbar","aria-label":"Table row record progress","aria-valuenow":this.current_page*this.settings["pagination_size"],"aria-valuemin":0,"aria-valuemax":this.total_records}
            this.navigation.display_pbar = this.dom_factory()
            this.props = {"class":"progress-bar progress-bar-striped progress-bar-success","style":"width: 50%"}
            this.navigation.display_pbar_bar = this.dom_factory()
            this.navigation.display_pbar[0].append(this.navigation.display_pbar_bar[0])
            nav_box[0].append(this.navigation.display_pbar[0])
        }
        if (this.settings["navigation_display_status"] == true) {
            this.tag = "div"
            this.props = {}
            this.navigation.status_display = this.dom_factory()
            this._set_status(this.texts["ready"])
            nav_box[0].append(this.navigation.status_display[0])
        }
        if (this.settings["select_all_enabled"] == true) {
            this.tag = "div"
            this.props = {}
            let select_all_div = this.dom_factory()
            this.tag = "button"
            this.props = {"html":this.texts["delete_sel"],"class":"btn  btn-danger ms-1"}
            this.del_all_btn = this.dom_factory()
            this.del_all_btn.on("click",this._del_all_toggle.bind(this))
            this.props = {"html":this.texts["add_sel"],"class":"btn  btn-success ms-1"}
            this.add_sel_btn = this.dom_factory()
            this.add_sel_btn.on("click",this._save_all_toggle.bind(this))
            this.add_sel_btn.hide();
            nav_box[0].append(select_all_div[0])
            select_all_div[0].append(this.del_all_btn[0],this.add_sel_btn[0])
            this.props = {"html":this.texts["select_all"],"class":"btn  btn-primary ms-1"}
            this.sel_all_btn = this.dom_factory()
            nav_box[0].append(select_all_div[0])
            select_all_div[0].append(this.sel_all_btn[0])
            select_all_div.on("click",this._select_all_toggle.bind(this))
        }
        this.tag = "tr"
        this.props = {}
        this.totals_area = this.dom_factory()
        this.footer.append(this.totals_area[0])
    }
    _select_all_toggle(event) {
        event.preventDefault()
        event.stopPropagation()
        for (var k in this.select_checkboxes) {
            if (this.select_checkboxes[k][0].checked === true) {
                this.select_checkboxes[k][0].checked = false
            } else {
                this.select_checkboxes[k][0].checked = true
            }
        }
    }
    _save_all_done(res) {
        this.reset();
        this.table.trigger("save_all_complete")
    }

    _del_all_done(res) {
        // this.load(this.current_page)
        this.start(this.urls["paginator_endpoint"])
        this.table.trigger("del_all_complete")
    }
    _del_all_toggle(event) {
        event.preventDefault()
        event.stopPropagation()
        let deletes = []
        for (var k in this.select_checkboxes) {
            if (this.select_checkboxes[k][0].checked === true) {
                    deletes.push(this.select_checkboxes[k].data("uuid"))
            }
        }
        let delstr = deletes.join("||")
        if (confirm(this.texts["delete_confirm"])) {
                this.generic_api_getreq(this.urls["delete_all_endpoint"],"uuids="+delstr,this._del_all_done.bind(this))
        }
    }

    _save_all_toggle(event) {
        event.preventDefault()
        event.stopPropagation()
        let saves = []
        for (var k in this.select_checkboxes) {
            if (this.select_checkboxes[k][0].checked === true) {
                    saves.push(this.select_checkboxes[k].data("uuid"))
            }
        }
        let savestr = saves.join("||")
        if (confirm(this.texts["save_confirm"])) {
                this.generic_api_getreq(this.urls["save_all_endpoint"],"uuids="+savestr,this._save_all_done.bind(this))
        }
    }

    _nav_btn_handle(event) {
        // console.log("nav_btn_handle")
        event.preventDefault()
        event.stopPropagation()
        let btn = $(event.target);
        // console.warn(btn,btn[0].value);
        if (btn[0].getAttribute("disabled") == "disabled") {
            return false;
        }
        let trgt = ""
        if (btn[0].value != undefined) {
            trgt = btn[0].value;
        } else {
            trgt = btn.data("page");
        }
        if (trgt >= this.total_pages+1) {
            console.warn("Exceeding total pages is prohibited.")
            btn[0].value = this.total_pages;
            trgt = this.total_pages;
        }

        let page = this.current_page;
         if ((trgt == "prev") && (this.current_page > 1)){
            page = this.current_page - 1;
        } else if ((trgt == "next") && (this.current_page < this.total_pages )) {
             console.log("Next")
             page = this.current_page + 1;
            } else if (trgt*1>=1) {
            page = trgt * 1
        }
        this.load(page);
    }

    _load_handle(res) {
        if ((res.data.paginator.current_page == 1)&&(this.header_set === false)) {
            this.header_set = true;
            this.header.empty()
            console.log(res.data.column_names)
            this._set_header(res.data.column_names)
        }
        this.body.empty()
        for (let key in res.data.rows) {
            this._add_row(res.data.rows[key],res.data.additional_cols);
        }
        if ("totals" in res.data) {
            var tstr = false;
            var ltdiv = false;
            this.totals_area.empty();
            for (var key in res.data.totals) {
                 tstr = res.data.totals[key]["name"]+" "+res.data.totals[key]["value"]+" ";
                 ltdiv = $("<td/>",{"html":tstr})
                 this.totals_area[0].append(ltdiv[0])

            }

        }
        this.navigation.container.find("btn").removeClass('disabled');
        this.navigation.container.find("btn").attr('disabled',false);
        this.current_page = res.data.paginator.current_page;
        if (this.total_pages > 1) {
        // Simple Pill based navigation below:
        if (this.total_pages < this.settings["navigation_pill_count_box_break"]) {
        this.navigation.buttons[this.current_page].attr("disabled","disabled");
        this.navigation.buttons[this.current_page].addClass("disabled");
        if (this.current_page == 1) {
            this.navigation.previous.attr("disabled", "disabled");
            this.navigation.previous.addClass("disabled");
        }
        if (this.current_page == this.total_pages) {
            this.navigation.next.attr("disabled","disabled");
            this.navigation.next.addClass("disabled");
        }
        // console.log("Page is now",this.current_page)
        } else {
            // Interactive Box and Pill navigation:
            this.navigation.box[0].value = this.current_page;
            this.navigation.container.find("btn").addClass('disabled');
            this.navigation.container.find("btn").attr('disabled','disabled');
            if (this.current_page == 1) {
                this.navigation.previous.attr("disabled", "disabled");
                this.navigation.previous.addClass("disabled");
            } else {
                this.navigation.previous.attr("disabled",false);
                this.navigation.previous.removeClass("disabled");
            }
            if (this.current_page == this.total_pages) {
                this.navigation.next.attr("disabled","disabled");
                this.navigation.next.addClass("disabled");
            } else {
                this.navigation.next.attr("disabled",false);
                this.navigation.next.removeClass("disabled");
            }
            let btn1 = $(this.navigation.buttons[1][0]);
            if (this.current_page  <= 3) {
                btn1.attr("disabled","disabled");
                btn1.addClass("disabled");
                btn1.text("-");

            } else {
                btn1.attr("disabled",false);
                btn1.removeClass("disabled");
                btn1.text(this.current_page-3);
                btn1.data("page",this.current_page-3);
            }
            let btn2 = $(this.navigation.buttons[2][0]);
            if (this.current_page  <= 2) {
                btn2.attr("disabled","disabled");
                btn2.addClass("disabled");
                btn2.text("-");
            } else {
                btn2.attr("disabled",false);
                btn2.removeClass("disabled");
                btn2.text(this.current_page-2);
                btn2.data("page",this.current_page-2);
            }
            let btn3 = $(this.navigation.buttons[3][0]);
            if (this.current_page  <= 1) {
                btn3.attr("disabled","disabled");
                btn3.addClass("disabled");
                btn3.text("-");
            } else {
                btn3.attr("disabled",false);
                btn3.removeClass("disabled");
                btn3.text(this.current_page-1);
                btn3.data("page",this.current_page-1);
            }
            let btn4 = $(this.navigation.buttons[4][0]);
            if (this.current_page + 1 >= this.total_pages) {
                btn4.attr("disabled","disabled");
                btn4.addClass("disabled");
                btn4.text("-");
            } else {
                btn4.attr("disabled",false);
                btn4.removeClass("disabled");
                btn4.text(this.current_page+1);
                btn4.data("page",this.current_page+1);
            }
            let btn5 = $(this.navigation.buttons[5][0]);
            if (this.current_page + 2 >= this.total_pages) {
                btn5.attr("disabled","disabled");
                btn5.addClass("disabled");
                btn5.text("-");
            } else {
                btn5.attr("disabled",false);
                btn5.removeClass("disabled");
                btn5.text(this.current_page+2);
                btn5.data("page",this.current_page+2);
            }
            let btn6 = $(this.navigation.buttons[6][0]);
            if (this.current_page + 3 >= this.total_pages) {
                btn6.attr("disabled","disabled");
                btn6.addClass("disabled");
                btn6.text("-");
            } else {
                btn6.attr("disabled",false);
                btn6.removeClass("disabled");
                btn6.text(this.current_page+3);
                btn6.data("page",this.current_page+3);
            }
        }
            this._set_display_count(this.current_page);
        } else {
            this._set_display_count_html(this.texts["all_records"])
            if (this.navigation.display_pbar_bar) {
                this.navigation.display_pbar.hide();
            }
        }

        this._set_status(this.texts["ready"])

    }

    _ajax_error_handler(event,data) {
        if ("status" in data) {
            alert("Abstract Table App: AJAX Layer Error: " + data.status+"\nURL: " + this._last_ajax_url);
        }
    }

    load(page=1) {
        let cols = this.columns.join(",")
        if (this.display_cols.length > 0) {
            cols = this.display_cols.join(",")
        }
        console.log("Loading Page: "+page);
        this._set_status(this.texts["loading"])
        this.generic_api_getreq(this.urls["paginator_endpoint"]+this.settings["pagination_size"]+"/"+page,"cols="+cols+this._build_sort_qrystring()+"&filter="+this.filter_string,this._load_handle.bind(this));
    }


    reset() {
        this.header.empty()
        this.body.empty()
        try {
            this.add_sel_btn.hide();
            this.del_all_btn.show();
            this.sel_all_btn.show();
        } catch(e) {}
        this.start(this.urls.paginator_endpoint)
    }

    search_for_new_record(qstr) {
        let cols = this.columns.join(",")
        if (this.display_cols.length > 0) {
            cols = this.display_cols.join(",")
        }
        console.log("Searching for: "+qstr+" on the search endpoint");
        this.add_sel_btn.show();
        this.del_all_btn.hide();
        this.sel_all_btn.hide();
        this._set_status(this.texts["loading"])
        this.generic_api_getreq(this.urls["search_endpoint"],"cols="+cols+this._build_sort_qrystring()+"&q="+qstr,this._load_handle.bind(this));
    }


    _start_handle(res) {
        // console.log("Table Data",data.paginator);
        // console.log(data);
        if  ((res === undefined)||("empty" in res.data)) {
            console.log("Received an Empty Table Set!");
            this.body.empty();
            this.total_records = 0;
            this.current_page = 0;
            this.total_pages = 0;
            this.columns = []
            console.log("Initialised a Table with " + this.total_records + " records across " + this.total_pages + " total pages of " + this.settings["pagination_size"] + " rows each.");
            // if (this.total_pages > 1) {
            this._set_footer()
            // }
            $(this.dom_con).trigger("table_start");
        } else {

            this.total_records = res.data.paginator.total_records;
            this.current_page = res.data.paginator.current_page;
            this.total_pages = res.data.paginator.total_pages;
            this.columns = res.data.columns;
            console.log("Initialised a Table with " + this.total_records + " records across " + this.total_pages + " total pages of " + this.settings["pagination_size"] + " rows each.");
            // if (this.total_pages > 1) {
            this._set_footer()
            // }
            this.load(1);

            $(this.dom_con).trigger("table_start");
        }

    }

    start(page_size) {
        if (page_size !== undefined) {
            this.settings["pagination_size"] = page_size;
            console.log("Setting Pagination Size: " + page_size);
        }
        this.select_checkboxes = []
        this.generic_api_getreq(this.urls["paginator_endpoint"]+this.settings["pagination_size"], "filter="+this.filter_string,this._start_handle.bind(this));
    }
    constructor(settings, urls, texts) {
        super(settings, urls);
        $.extend(this.settings, settings);
        $.extend(this.urls, urls);
        $.extend(this.texts, texts);
        $(this).on("ajax_error", this._ajax_error_handler.bind(this));
        this.display_cols = this.settings["display_cols"];
        this.tag = "div"
        this.props = {};
        this.dom_con = this.dom_factory();
        this.header_div = this.dom_factory();
        this.tag = "table"
        this.props = {
            "class": this.settings["table_class"],
        }

        this.table = this.dom_factory();
        this.dom_con[0].append(this.header_div[0],this.table[0]);
        this.props = {}
        this.tag = "thead"
        this.header = this.dom_factory();
        this.tag = "tbody"
        this.body = this.dom_factory();
        this.tag = "tfoot"
        this.footer = this.dom_factory();
        this.table[0].append(this.header[0],this.body[0],this.footer[0]);
        this.tag = "div"
        this.footer_div = this.dom_factory();
        this.dom_con[0].append(this.footer_div[0]);





    }

}