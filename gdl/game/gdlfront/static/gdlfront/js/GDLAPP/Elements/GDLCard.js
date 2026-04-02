import {_elementProto} from "/static/minerve/js/dashboards/DashboardApp/Elements/prototype.js";

export class ElementGDLCard extends _elementProto {
  settings = {
    "active_class":"flipped active",
    "render_as_active":false,
  }
  detail_btn = false
  accept_btn = false
  reject_btn = false
  accept_btn_frnt = false
  reject_btn_frnt = false
  bt1 = false
  bt2 = false
  bt3 = false

  data = {}
  props = {}
  texts = {
      up_to: "Ticket Wins",
      return_to: "Returns",
      return_str: " returns ",
      returns: "$0",
      stake_str: "0 wins: 0",
      sports: "0 Events:",
      selected: " ",
      possible_win: "Click to reveal details!",
  }
  form = false
  accept_evt(modal,event) {
      // console.log("AAEE",this)
      this.accept_btn.trigger("click");
      modal.bs_modal.hide()
  }
  reject_evt(modal,event) {
    // console.log("RREE",this)
    this.reject_btn.trigger("click");
    modal.bs_modal.hide()
  }
  constructor(id, texts = {}, data = {},props={},settings={}) {
  super(id, texts, data);
    this.id = id;
    this.props = props;
    $.extend(this.texts,texts)
    $.extend(this.data,data);
    $.extend(this.texts,texts);
    $.extend(this.settings,settings);
    // console.warn(this.data);
    // console.warn(this.texts);
    this.el = this._render();
  }

  _render() {
    let tkclass = `ticket-variant-${this.props.variant_number || 0}`;
    if (window.hasOwnProperty("theme_switcher")) {
      let tsp = window.theme_switcher.get_current_ticket_theme()
      if (tsp !== false) {
        tkclass = tsp
      }
    }
     if (this.data["status"] == "L") {
        tkclass = tkclass + "ticket-variant-lost";
    } else if (this.data["status"] == "W") {
        tkclass = tkclass +  "ticket-variant-won";
    } else if ((this.data["status"] == "P")||(this.data["status"] == "M"))  {
        tkclass = tkclass + "ticket-in-prog"
    }
    let ltkclass = "col-9 col-md-5 col-lg-4 col-xl-2  flip-card m-2 gdl-ticket-card text-dark "
    if (this.settings["render_as_active"]) {

      ltkclass +=" "+this.settings["active_class"]+" "
    }
    const col = $("<div/>", {
      class: ltkclass+tkclass,
      id: this.id
    });
    const inner = $("<div/>", { class: "flip-card-inner" });
    col.append(inner);
    this.col = col;

    const front = this._render_front();
    const back = this._render_back();

    inner.append(front, back);
    return col;
  }

  _render_front() {
    const front = $("<div/>", { class: "flip-card-front" });

    if ((this.data.depth <= 3) && (this.data.total_stake >= 10)) {
      front.append($("<h6/>", {class: "up-to-subtitle", text: this.texts.return_to}));
    } else {
      front.append($("<h6/>", {class: "up-to-subtitle", text: this.texts.up_to}));
    }
    front.append($("<h3/>", { class: "to-win mt-5", text: this.texts.returns }));
    front.append($("<p/>", { class: "to-win-subtitle", html: this.texts.possible_win }));
    if (this.settings["render_as_active"] === false) {
      this.accept_btn_frnt = $("<button/>",{"class":"btn accept-btn","html":"<i class=\"fa-duotone fa-solid  fa-circle-check \"></i>","data-bs-placement":"top","data-bs-toggle":"tooltip","title":"Accept Ticket!","data-uuid":this.id});
      this.reject_btn_frnt = $("<button/>",{"class":"btn  reject-btn","html":"<i class=\"fa-duotone fa-solid fa-circle-xmark \"></i>","data-bs-placement":"top","data-bs-toggle":"tooltip","title":"Reject Ticket!","data-uuid":this.id});
      const front_btnContainer = $("<p/>", {class:''});
      front_btnContainer.append(this.reject_btn_frnt,this.accept_btn_frnt);
      front.append(front_btnContainer);
      this.bt4 = new bootstrap.Tooltip(this.accept_btn_frnt);
      this.bt5 = new bootstrap.Tooltip(this.reject_btn_frnt);

    }
    return front;
  }

  _render_back() {
    const back = $("<div/>", { class: "flip-card-back" });

    back.append($("<span/>", { html: this.texts.selected }));
    if ((this.data.depth <= 3) && (this.data.total_stake >= 10)) {
      back.append($("<h5/>", { class: "to-win", html: this.texts.return_str }));
    } else {
      back.append($("<h5/>", { class: "to-win", html: this.texts.stake_str }));
    }


    const mlen = this.data?.depth || this.text?.sports || 0;
    const sportsTitle = `<strong><i class=\"fa-duotone fa-solid fa-medal\"></i> ${mlen} Events.</strong>`;
    back.append($("<span/>", { html: sportsTitle }));

    // Icons container
    const iconContainer = $("<p/>", {class:'d-none d-md-none d-sm-none d-lg-block d-xl-block d-xxl-block'});
    if (Array.isArray(this.data.matches) && Array.isArray(this.data.sports)) {
      // this.data.matches.forEach((_, i) => {
      //   const sportMeta = this.data.sports[i];
      //   if (Array.isArray(sportMeta) && sportMeta.length >= 4 && sportMeta[3]) {
      //     const icon = $("<span/>", {
      //       class: "p-1",
      //       html: `<i class='${sportMeta[3]}'></i>`,
      //       title: sportMeta[2],
      //       "data-bs-placement": "top",
      //       "data-bs-toggle": "tooltip"
      //     });
      //     iconContainer.append(icon);
      //     new bootstrap.Tooltip(icon[0]);
      //   }
      // });
    }

    back.append(iconContainer);
    const btnContainer = $("<p/>", {class:''});

    this.reject_btn = $("<button/>",{"class":"btn  reject-btn","html":"<i class=\"fa-duotone fa-solid fa-circle-xmark \"></i>","data-bs-placement":"top","data-bs-toggle":"tooltip","title":"Reject Ticket!","data-uuid":this.id});
    this.detail_btn = $("<button/>",{"class":"btn details-btn ms-1 me-1 pt-2 pb-2 ","html":"<i class=\"fa-duotone fa-solid fa-magnifying-glass-waveform\"></i> <span class=\"d-inline d-md-inline d-sm-none d-lg-inline d-xxl-inline d-xl-inline\">Details</span>","data-bs-placement":"bottom","data-bs-toggle":"tooltip","title":"View this ticket's full details","data-uuid":this.data["uuid"]});
    this.accept_btn = $("<button/>",{"class":"btn accept-btn","html":"<i class=\"fa-duotone fa-solid  fa-circle-check \"></i>","data-bs-placement":"top","data-bs-toggle":"tooltip","title":"Accept Ticket!","data-uuid":this.id});
    if (this.settings["render_as_active"] === false) {

      btnContainer.append(this.reject_btn);
      back.append(this.detail_btn);
      back.append(btnContainer);
      btnContainer.append(this.accept_btn);
      this.bt1 = new bootstrap.Tooltip(this.detail_btn);
      this.bt2 = new bootstrap.Tooltip(this.reject_btn);


      this.bt3 = new bootstrap.Tooltip(this.accept_btn);
    } else {

      back.append(this.detail_btn);
      this.bt1 = new bootstrap.Tooltip(this.detail_btn);
    }



    this.form = $("<form/>",{"method":"POST",action:"#","id":"ticket-form"})
    this.col.append(this.form)
    this.form.append($("<input/>",{"type":"hidden","id":"matches","name":"matches","value":this.data["muuids"].join(",")}))
    this.form.append($("<input/>",{"type":"hidden","id":"types","name":"type","value":this.data["outcomes"].join(",")}))
    this.form.append($("<input/>",{"type":"hidden","id":"stake","name":"stake","value":this.data["total_stake"]}))
    this.form.append($("<input/>",{"type":"hidden","id":"returns","name":"returns","value":this.data["total_returns"]}))
    this.form.append($("<input/>",{"type":"hidden","id":"lines","name":"lines","value":this.data["lines"].join(",")}))
    this.form.append($("<input/>",{"type":"hidden","id":"uuid","name":"uuid","value":this.id}))
    return back;
  }

  get_el() {
    return this.el;
  }

  replace_and_destroy(new_element) {
    this.bt1.hide()
    if (this.bt2) {
      this.bt2.hide()
    }
    if (this.bt3) {
      this.bt3.hide()
    }
    if (this.bt4) {
      this.bt4.hide()
    }
    if (this.bt5) {
      this.bt5.hide()
    }
    let old_el = this.el.replaceWith(new_element);
    old_el.empty()

  }
}

export default ElementGDLCard;
