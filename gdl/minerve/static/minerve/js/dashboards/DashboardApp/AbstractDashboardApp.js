import {AbstractApp} from "/static/minerve/js/core/AbstractApp.js";
import {ElementForm,ElementInput,ElementHiddenInput,ElementSubmit,ElementModal,ElementH} from "./Elements/Elements.js";
import {BrowserDetector} from '/static/browser-dtector/dist/browser-dtector.js';

export class    AbstractDashboardApp extends AbstractApp {
    settings = {
        "loading_toast": "#loading_toast",
        "nav-link-cls": [".nav-link", ".nav-dlink"],
        "on_submit_complete": false,
        "toastSuccessCls": "toast-success text-bg-success",
        "disable_success_toasts": false,
        "disable_normal_toasts": false,

    }
    urls = {}
    elements = {}
    modal = false
    last_modal = false
    last_modal_created = false
    last_modal_created_bso = false
    on_ajax_error_func = false
    user_agent = null
    _animateCSS(node, animation, prefix = 'animate__') {
        // We create a Promise and return it
        new Promise((resolve, reject) => {
            const animationName = `${prefix}${animation}`;
            //     const node = document.querySelector(element);

            node.addClass(`${prefix}animated  ${animationName}`);

            // When the animation ends, we clean the classes and resolve the Promise
            function handleAnimationEnd(event) {

                event.stopPropagation();
                node.removeClass(`${prefix}animated ${animationName}`);
                resolve('Animation ended');
            }

            node.on('animationend', handleAnimationEnd);
        });
    }

    _isMobile() {
        let isMobile = window.orientation > -1;
        return isMobile;
    }


    _getModal() {
        this.modal = new bootstrap.Modal(this.elements["modal"]);
    }

    _showModal() {
        if (this.modal == false) {
            this._getModal();
        }
        this.modal.show();
    }

    _hideModal() {
        if (this.modal == false) {
            this._getModal();
        }
        this.modal.hide();
    }

    _edit_form_loader(data) {
        var data_keys = Object.keys(data.data);
        for (var i in data_keys) {
            // console.log("Edit Form Loader:", i,data_keys[i]);
            var dk = data_keys[i];
            var update_el = $(this.elements["form"]).find("#id_" + dk);
            // console.log(data.data[dk]);
            if (update_el.length > 0) {
                if (update_el[0].type == "checkbox") {
                    update_el[0].checked = data.data[dk];
                } else {
                    update_el[0].value = data.data[dk];
                }

            }
        }
    }

    edit_handle(data, edit_function = false) {
        this.hideLoading();
        if (data.res == "ok") {
            this._edit_form_loader(data);
            this._showModal();

        } else {
            var errStr = this._parse_ajax_error(data.data);
            this.errorToast('<h6><i class="fa-solid fa-xmark"></i>&#160;Error!', 'An Error Occured! ' + errStr);
            console.error("Unable to execute Operation: ", errStr)
            return false;
        }
    }

    edit_record(uuid) {
        console.info("Loading Data for Edit Mode for '" + uuid + "'");
        this.showLoading();
        this.elements["modal"] = $(this.settings["modal_id"]);
        this.elements["form"] = $(this.settings["edit_form_id"]);
        $(this.settings["edit_form_id"])[0].reset();
        let url = this.urls["_api_prefix"] + this.elements["form"].data("get-url") + "/" + uuid;
        this._clear_invalid();
        console.log(this.elements["modal"], this.elements["form"], this.settings["modal_id"], this.settings["modal_id"]);
        $.ajax({
            url: url,
            method: 'GET',
            context: this
        }).done(this.edit_handle.bind(this));

    }

    _delete_handle(callback, data) {
        this.hideLoading();
        if (data.res == "ok") {
            this.successToast("Complete!", "Record Deleted!")
            $(this.settings.dashboard_panel).load(this._current_url);
            if (callback != false) {
                callback();
            }
        } else {
            this.errorToast("Error!", data.err)
        }
    }

    delete_record(uuid, form_element = false, callback = false) {
        if (confirm("Are you sure you want to delete this record?")) {
            this.showLoading();
            if (form_element == false) {
                this.elements["form"] = $(this.settings["edit_form_id"]);
            } else {
                this.elements["form"] = form_element
            }

            let url = this.urls["_api_prefix"] + this.elements["form"].data("delete-url") + "/" + uuid;
            $.ajax({
                url: url,
                method: 'GET',
                context: this
            }).done(this._delete_handle.bind(this, callback));
        }
    }


    successToast(header, body) {
        if (this.settings["disable_success_toasts"] !== true) {
            new bs5.Toast({
                body: body,
                header: header,
                placement: 'bottom-right',
                className: this.settings.toastSuccessCls,
            }).show();
        }
    }

    errorToast(header, body) {
        new bs5.Toast({
            body: body,
            header: header,
            placement: 'bottom-right',
            className: this.settings.toastErrorCls,

        }).show();
    }

    normalToast(header, body) {
        if (this.settings["disable_normal_toasts"] !== true) {
            new bs5.Toast({
                body: body,
                header: header,
                placement: 'bottom-right',
                className: this.settings.toastCls,

            }).show();
        }
    }

    // Loading Toast:
    showLoading() {
        if (this.elements["loading_toast"]) {
            this.elements["loading_toast"].show();
        }
    }

    hideLoading(callback) {
        if (this.elements["loading_toast"]) {
            this.elements["loading_toast"].hide();
            if (typeof (callback) == "function") {
                callback();
            }
        }
    }

    refresh() {
        $(this.settings.dashboard_panel).load(this._current_url);
    }

    load_page(event) {
        // console.warn(event.target,event.target.href)
        if (event.target.href !== "#theme_switcher") {
            return true
        }
        else if (event.target.href.slice(-1) === "#") {
            event.preventDefault();
            event.stopPropagation();
            // console.log("Event Catch Load Page",event,event.target)
            var trgturl = $(event.target).data("target-url");
            if (trgturl == undefined) {
                return false;
            }
            this.showLoading();

            let target_url = this.urls["_prefix"] + trgturl;

            this._current_url = target_url;
            if ($(event.target).data("target-form-url") !== undefined) {
                let form_target_url = this.urls["_prefix"] + $(event.target).data("target-form-url");
                $(this.settings.dashboard_form_area).load(form_target_url);
                this.elements["form"] = $(this.settings.dashboard_form_area);
            }
            $(this.settings.dashboard_panel).load(target_url, false, this.hideLoading.bind(this));
            try {
                $(this._parent_walker($(event.target)[0])[0].parentNode).offcanvas('hide');
            } catch (e) {
            }
        }
    }

    _submit_form_handle(data) {
        this.hideLoading();
        if (data.res == "ok") {
            if (!"silent" in data) {
                this.successToast("Complete!", "Operation Complete!");
            }
            $(this.settings["edit_form_id"])[0].reset();
            try {
                this.elements["modal"].hide();
            } catch (e) {
                console.info("Could not close modal dialog.");
            }
            if (this.settings.on_submit_complete === false) {
                $(this.settings.dashboard_panel).load(this._current_url);
            } else {
                this.settings.on_submit_complete();
            }
        } else {
            var errstr = this._parse_ajax_error(data.data);
            this.errorToast("Error!", errstr)
        }


    }

    submit_form(event, handler) {
        event.stopPropagation();
        event.preventDefault();
        this.showLoading();
        this.elements["modal"] = $(this.settings["modal_id"]);
        this.elements["form"] = $(this.settings["edit_form_id"]);
        try {
            this._getModal();
        } catch (e) {
            console.info("No Modal Detected during submit_form.");
        }
        let url = this.urls["_api_prefix"] + this.elements["form"].data("post-url");
        $.ajax({
            url: url,
            data: new FormData(this.elements["form"][0]),
            method: 'POST',
            context: this,
            cache: false,
            contentType: false,
            processData: false
        }).done(this._submit_form_handle.bind(this));
    }

    load_detail_view(event,on_complete=false) {
        event.preventDefault();
        event.stopPropagation();
        let form = $(event.target);
        // let loadval = $(this.settings.detail_item_select)[0].value;
        let url = form.data("detail-url");
        let loadformval = form.serialize()
        $(this.settings.detail_item_card).load(url,loadformval,on_complete);
        $(this.settings.detail_view_modal_sel).modal('hide')
    }

    start_detail_view() {
        $(this.settings.detail_view_modal_sel).modal('show');
    }
    // Deprecated
    // _alert_div_factory(alert_str, css_class, fa_icon = false) {
    //     let alertId = Math.floor(Date.now() / 1000);
    //     let alertDiv = $("<div>", {class: "alert", id: alertId});
    //     if (css_class !== false) {
    //         alertDiv.addClass(css_class);
    //     }
    //     if (fa_icon !== false) {
    //         let fa_icon_el = $("<i>", {class: fa_icon});
    //         alertDiv.append(fa_icon_el);
    //     }
    //     let text_span = $("<div>", {html: alert_str});
    //     alertDiv.append(text_span);
    //     return alertDiv;
    // }

    _handle_generic_ajax_update_form_res(res) {
        this.hideLoading();
        let ref = false;
        if ("refresh" in this.last_modal_created) {
            ref = true;
        }
        this.last_modal_created.bs_modal.hide();
        this.last_modal_created.modalDiv.remove();
        if (ref === true) {
            location.reload();
        }
    }
    _handle_generic_ajax_update_form(event) {
        this.generic_post_form(event,false,this._handle_generic_ajax_update_form_res.bind(this));
    }
    _handle_generic_ajax_modal_update(options,res) {
      this.hideLoading();
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

    generic_ajax_modal_update(url,{...options}) {
        if ('destroy_old_modal' in options) {
            if (this.last_modal_created !== false) {
                this.last_modal_created.modalDiv.remove();
            }
        }
        if (!'skip_prefix' in options) {
            url = this.urls["_api_prefix"] + url;
        }
        this.generic_api_getreq(url,false,this._handle_generic_ajax_modal_update.bind(this,options),false);

    }

    generic_ajax_modal_dialogue(title, url, add_prefix = true, max_width = "100%", dismissable = true, load_callback = false, modal_css_class = false, destroy_old_modal = false,append_to=false) {
        if (destroy_old_modal === true) {
            if (this.last_modal_created !== false) {
                if (this.last_modal_created.modalDiv !== undefined) {
                    this.last_modal_created.modalDiv.remove();
                }
            }
        }
        let options = {
            "title":title,
            "max_width":max_width,
            "dismissable":dismissable,
            "modal_css_class":modal_css_class
        }
        let modal = new ElementModal(title,max_width,dismissable,modal_css_class,append_to);
        if (url !== false) {
            let turl = url;
            if (add_prefix===true) {
                turl = this.urls["_prefix"] + turl;
            }
            this.showLoading();
            modal.modalBody.load(turl, false, this.hideLoading.bind(this, load_callback));
        }
        modal.modalDiv.on("hidden.bs.modal", function (event) {
            $(event.target).remove();

        });
        modal.bs_modal.show();

        /** You might need these two things later :) **/
        this.last_modal_created = modal.modalDiv;
        this.last_modal_created_bso = modal.bs_modal;
        this.last_modal = modal;
        return [modal.modalDiv, modal.bs_modal];
    }

    generic_post_form_handle(modal, callback, res) {
        if (res.res == "ok") {
            if (modal !== false) {
                $(modal).modal('hide');
            }
            if (!("silent" in res)) {
                let hdr = "<i class=\"fa-duotone fa-solid fa-check text-success pe-2\"></i> Success!";
                if ("header" in res) {
                    hdr = res.header;
                }
                if (res.msg !== false) {
                    this.successToast(hdr, res.msg);
                } else {
                    this.successToast(hdr, "Operation Complete!");
                }
            }
            if (callback !== false) {
                callback(res);
            }
        } else {
            let hdr = "<i class=\"fa-duotone fa-solid fa-circle-exclamation text-error pe-2\"></i> Error: "+res.err+"!";
            try {
                var errstr = this._parse_ajax_error(res.data)
                this.errorToast(hdr, errstr);
            } catch (e) {
                console.warn("Unable to Parse data inside _parse_ajax_error:",e)
                this.errorToast(hdr, res.err);
            }
            if (this.on_ajax_error_func) {
                console.warn(this.on_ajax_error_func);
                this.on_ajax_error_func(res);
            }
        }
    }

    bind_links() { 
        for (let clsName of this.settings["nav-link-cls"]) {
            $(clsName).on("click", this.load_page.bind(this));
        }
    }

    constructor(settings, urls, elements) {
        super(settings, urls, elements);
        this.elements["loading_toast"] = new bootstrap.Toast($(this.settings.loading_toast));
        $(document).bind('loading', this.showLoading.bind(this));
        $(document).bind('loaded', this.hideLoading.bind(this));
        let bdetect = new BrowserDetector()
        this.user_agent = bdetect.parseUserAgent()

    }
}
