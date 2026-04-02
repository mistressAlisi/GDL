export class Modal {
    modalId = null;
    modalDiv = null;
    modalBody = null;
    dialog = null;
    content = null;
    header = null;
    title = null;
    footer = null;
    xbtn = null;
    clsbtn = null;
    bs_modal = null;
    append_to = null;
    get_el() {
        return this.modalDiv;
    }
    _cleanup_el() {
        // console.log("Destroying modal.");
        this.modalDiv.remove();
    }
    constructor(title_str, max_width, dismissable = true, css_class = false,append_to=false) {
        // console.warn(title_str, max_width, dismissable, css_class,rest);
        this.modalId = Math.floor(Date.now() / 1000);
        this.modalDiv = $("<div>", {class: "modal", id: this.modalId});
        if (css_class !== false) {
            this.modalDiv.addClass(css_class);
        }
        this.modalBody = $("<div>", {class: "modal-body", text: "...Loading..."});
        this.dialog = $("<div>", {class: "modal-dialog modal-dialog-scrollable", css: {"max-height": "95%", "overflow-y": "auto"}});
        if (max_width !== false) {
            this.dialog.css({'width': max_width, 'max-width': max_width});
        }
        this.content = $("<div>", {class: "modal-content"});
        this.header = $("<div>", {class: "modal-header"});
        this.title = $("<div>", {class: "modal-title h4", html: title_str});

        this.footer = $("<div>", {class: "modal-footer"});
        this.header.append(this.title);
        if (append_to) {
            this.append_to = append_to;
        }

        if (dismissable == true) {
            this.xbtn = $("<button>", {
                class: "btn-close",
                type: "button",
                "data-bs-dismiss": "modal",
                "data-bs-target": "#" + this.modalId
            });
            this.clsbtn = $("<button>", {
                class: "btn btn-secondary",
                type: "button",
                text: "Close",
                "data-bs-dismiss": "modal",
                "data-bs-target": "#" + this.modalId
            });
            this.header.append(this.xbtn);
            this.footer.append(this.clsbtn);
            this.clsbtn.on("click",this._cleanup_el.bind(this));

        } else {
            this.modalDiv.attr('data-bs-backdrop', 'static');
            this.modalDiv.attr('data-bs-keyboard', 'false');
        }

        this.content.append(this.header);
        this.content.append(this.modalBody);
        this.content.append(this.footer);
        this.dialog.append(this.content);

        this.modalDiv.append(this.dialog);


        if (this.append_to === null || this.append_to === false) {
            $(document.body).append(this.modalDiv);
        } else {
            $(this.append_to).append(this.modalDiv);
        }
        this.bs_modal = new bootstrap.Modal(this.modalDiv);


    }

}
export default Modal;