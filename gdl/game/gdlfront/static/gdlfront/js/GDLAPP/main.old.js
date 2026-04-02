import {AbstractDashboardApp} from "/static/minerve/js/dashboards/DashboardApp/AbstractDashboardApp.js";
import {ElementButton,ElementP} from "/static/minerve/js/dashboards/DashboardApp/Elements/Elements.js";
import {ElementGDLCard,ElementGDLCartEntry,ElementGDLConfirmTktModal} from "./Elements/GDLElements.js";

import {DetailView} from "/static/minerve/js/dashboards/DashboardApp/DetailView.js";
import {Paginator} from "/static/minerve/js/dashboards/DashboardApp/Paginator.js";

export class GDLApp extends AbstractDashboardApp {

    urls = {
        "_api_prefix": "/api/v1/game/",
        "submit_step1": "run_step1",
        "ticket_viewer": "/game/ticket/details/viewer/",
        "accept_ticket":"tickets/accept/",
        "reject_ticket":"tickets/reject/",
        "cart":"tickets/cart/"

    }

    /** must be loaded from ruleset in form! **/
    ruleset = {}
    /** Fixes for Safari: **/
    safari_new_grp = [18.3,17.6]
    settings = {
        "gdl_div": "#gdl_play_area",
        "loading_div": "#gdl_loading_message",
        "setup_area": "#gdl_setup_card",
        "flip_card_css": ".flip-card",
        // "ticket_button": "#ticket_button",
        "ticket_class": ".gdl-ticket-card",
        "ticket_counter": "#ticket_counter",
        "confirm_slider": "#confirmSlider",
        "confirm_slider_label": "#confirmLabel",
        "modal": "#confirm_ticket_modal",
        "modal_counter": "#modal_counter",
        "modal_stake": "#modal_stake",
        "modal_wins": "#modal_wins",
        "param_form": "#parameter_form",
        "advanced_form":"#adv_parameter_form",
        "param_form_div":"#basic_settings",
        "advanced_form_div":"#advanced_settings",
        "mode_switch_btn":"#advanced_switch_btn",
        "quick_picks_div":"#quick-picks",
        "quick_picks_form":"#quick_pick_form",
        "quick_picks_btn":"#quick_pick_btn",
        "save_form": "#confirm_form",
        "save_form_contents": "#gdl_data",
        "avail_balance": ".avail_balance",
        "ticket_settings_div": "#ticket_settings_div",
        "gdl_play_controls":"#gdl_play_controls",
        "gdl_to_win":"#gdl_to_win",
        "gdl_risking":"#gdl_risking",
        "gdl_events":"#gdl_events",
        "gdl_active_cnt":"#gdl_active_cnt",
        "gdl_total":"#gdl_total",
        "gdl_buy_now":"#gdl_buy_now",
        "gdl_main_content":"#main-content",
        "gdl_cashier_now":"#gdl_cashier_now",
        "gdl_refresh_now":"#gdl_refresh_now",
        "gdl_settings_now":"#gdl_settings_now",
        "gdl_settings_ntk":"#gdl_settings_ntk",
        "gdl_more_now":"#gdl_more_now",
        "gdl_view_mode":"#gdl_view_mode",
        "gdl_empty_message":"#gdl_empty_message",
        "main_sidebar":"#mainSidebar",
        "events": "#id_events",
        "stake": "#id_stake",
        "minwin": "#id_minwin",
        "ruleset": "#ruleset",
        "ticket_count":"#id_count",
        "ticket_anim_delay": 50,
        "viewer_modal_width": "100%",
        "bet_scaler": 1.401,
        "max_bet": 100000,
        "viewport_area_percentage_factor": 0.36,
        "viewport_area_percentage_factor_mobile": 0.17,
        "viewport_area_percentage_factor_iphone": 0.15,
        "focus_tooltip_anim":"bounce animate__slow",
        "viewport_area_padding_top_dpx21":"",
        "card_render_as_active":false,
        "past_tickets_mode":false,
        "gdl_current_page":"#gdl_current_page",
        "gdl_total_pages":"#gdl_total_pages",
        "gdl_progressbar":"#gdl_progressbar",
        "gdl_total_tickets":"#gdl_total_tickets",
        "gdl_paginator_ctl":"#id_page",
        "extra_cards_buffer":1,
        "cart_offcanvas":"#offCanvasCart",
        "cart_container":"#cart_container",

        "bonus_balance":".bonus_balance",
        "card_skip_accept_btn":false,
        "disable_success_toasts":true


    }
    current_cards = {

    }
    to_win = 0
    stake = 0
    ticket_data = []
    viewport_area = 0
    card_area = 0
    recommended_cards = 0
    active_cards = 0
    current_page = 0
    total_pages = 0
    save_modal = false
    _randomInt(min, max) {
        const range = max - min + 1;
        const maxUint = 256;
        const array = new Uint8Array(1);

        // Reject values that would cause modulo bias
        const maxAcceptable = maxUint - (maxUint % range);

        let value;
        do {
            crypto.getRandomValues(array);
            value = array[0];
        } while (value >= maxAcceptable);

        return min + (value % range);
    }

    // _ui_element_focus_tooltip(el) {
    //     let bts = bootstrap.Tooltip.getInstance(el)
    //     bts.show();
    //     el.one("animationend",function(e){
    //       bts = bootstrap.Tooltip.getInstance(e.target);
    //       bts.hide();
    //     })
    //     this._animateCSS(el,this.settings["focus_tooltip_anim"])
    // }

    _set_ticket_btns(tuuid) {
        if (this.settings["card_render_as_active"] === false) {
            let rejectBtn = $("<button/>", {
                "class": "btn  reject-btn",
                "html": "<i class=\"fa-duotone fa-solid fa-circle-xmark \"></i> Reject Ticket",
                "data-bs-placement": "top",
                "data-bs-toggle": "tooltip",
                "title": "Reject Ticket!",
                "data-uuid": tuuid
            });
            if (this.settings["card_skip_accept_btn"] !== true) {
                let acceptBtn = $("<button/>", {
                    "class": "btn accept-btn",
                    "html": "<i class=\"fa-duotone fa-solid  fa-circle-check \"></i> Accept Ticket",
                    "data-bs-placement": "top",
                    "data-bs-toggle": "tooltip",
                    "title": "Accept Ticket!",
                    "data-uuid": tuuid
                });
                this.last_modal.footer.prepend(acceptBtn);
                acceptBtn.on("click", this._handle_accept_card.bind(this, true));
            }
            this.last_modal.footer.prepend(rejectBtn);

            rejectBtn.on("click", this._handle_reject_card.bind(this, true));
        }
    }

    _handle_ticket_details(is_a,event) {
        let btn = null
        if (is_a == false) {
            btn = $(this._parent_walker(event.target, "BUTTON"));
        } else{
            btn = $(this._parent_walker(event.target, "A"));
        }
        let uuid = btn.data("uuid")
        this.generic_ajax_modal_dialogue("Ticket Details", this.urls["ticket_viewer"] + uuid, false, this.settings["viewer_modal_width"], true, this._set_ticket_btns.bind(this,uuid), false, true)
    }

    _card_factory(data,ticket_count) {
        const variant = this._randomInt(0, 20);

        const props = {
            variant_number: variant
        };
        let texts = {}
        // console.log(data);
            switch (data["status"]) {
                case "L":
                    texts = {
                        stake_str: "Risking $" + data["stake"] + " to win $" + data["returns"],
                        selected: "<i class=\"fa-solid fa-square-exclamation\"></i> Better Luck Next Time!",
                    }
                    break;
                case "W":
                    texts = {
                        stake_str: "$" + data["stake"] + " won: $" + data["returns"],
                        selected: "<i class=\"fa-dutone fa-solid fa-stars\"></i> You're a Winner!!",
                    }
                    break;
                case "P":
                case "M":
                    texts = {
                        selected: "<i class=\"fa-dutone fa-solid fa-hourglass\"></i> In Play - Good Luck!",
                        returns: "$" + data["returns"],
                        stake_str: "$" + data["stake"] + " to win: $" + data["returns"],
                        sports: ` ${data["sports"] || 0} Events`
                    };
                    break;
                case "C":
                    texts = {
                    selected: "",
                    returns: "$" + data["returns"],
                    stake_str: "$" + data["stake"] + " to win: $" + data["returns"]+"",
                    sports: ` ${data["sports"] || 0} Events`
                }
            }


        let cuuid = data["uuid"];
        const card = new ElementGDLCard("card_" + cuuid, texts, data, props, {"render_as_active":this.settings["card_render_as_active"]});
        this.current_cards[cuuid] = card;
        if (this.settings["card_render_as_active"] == false) {
            card.reject_btn.on("click", this._handle_reject_card.bind(this,false));
            card.accept_btn.on("click", this._handle_accept_card.bind(this,false));
            card.reject_btn_frnt.on("click", this._handle_reject_card.bind(this,false));
            card.accept_btn_frnt.on("click", this._handle_accept_card.bind(this,false));
        }
        card.detail_btn.on("click", this._handle_ticket_details.bind(this,false));

        // Add animation class and inline delay:
        let delay = `${ticket_count * this.settings["ticket_anim_delay"]}ms`;
        card.el.css({
        opacity: 0,
        animation: 'slideFadeIn 0.6s ease-out forwards',
        'animation-delay': delay
        });
        return card.get_el();
    }

    _handle_accept_card(close_modal,event) {
        event.stopPropagation();
        event.preventDefault();
        let btn = $(this._parent_walker(event.target,"BUTTON"));
        let tuuid = btn.data("uuid");
        let url = this.urls["accept_ticket"]+tuuid;
        if (close_modal) {
            this.last_modal.bs_modal.hide()
        }
        this.generic_post_form_v2({"form":this.elements["param_form"],"callback":this._card_replace.bind(this),"url":url,"skip_modal":true})

    }

    _handle_reject_card(close_modal,event) {
        event.stopPropagation();
        event.preventDefault();
        let btn = $(this._parent_walker(event.target,"BUTTON"));
        let tuuid = btn.data("uuid");
        let url = this.urls["reject_ticket"]+tuuid;
        if (close_modal) {
            this.last_modal.bs_modal.hide()
        }
        this.generic_post_form_v2({"form":this.elements["param_form"],"callback":this._card_replace.bind(this),"url":url})
    }
    _handle_remove_cart(event) {
        event.stopPropagation();
        event.preventDefault();
        let btn = $(this._parent_walker(event.target,"A"));
        let tuuid = btn.data("uuid");
        let url = this.urls["reject_ticket"]+tuuid+"?ng=1";
        this.generic_post_form_v2({"form":this.elements["param_form"],"callback":this.get_cart.bind(this),"url":url})
    }

    _card_replace(res) {
        let ouuid = res["data"]["old"]
        let newCard = this._card_factory(res["data"]["new_tickets"][0])
        let oldCard = this.current_cards[ouuid]
        oldCard.replace_and_destroy(newCard);
        delete this.current_cards[ouuid];
        newCard.on("click", this._handle_card_flip.bind(this, newCard))
        this.get_cart()

    }

    toggle_settings() {
        this.elements["loading_div"].hide();
        this.elements["gdl_div"].hide();
        this.elements["gdl_empty_message"].hide();
        // this.elements["gdl_play_controls"].hide();
        // this.elements["gdl_play_controls"].removeClass('d-flex')
        this.elements["setup_area"].fadeIn();
        this.elements["quick_picks_div"].fadeIn();
    }

    toggle_ticket_settings() {
        this.elements["ticket_settings_div"].toggleClass('open')
    }
    _to_win_counter(a,b) {
        this.to_win = this.to_win + (b.value*1)
    }
    _stake_counter(a,b) {
        this.stake = this.stake + (b.value*1)
    }
    _handle_card_flip(card,event) {
        if (event.target.tagName === "BUTTON") {
            return true;
        }
        let cards = $(this.settings["ticket_class"])

        card.toggleClass("active")
        card.toggleClass("flipped")
       if (card.hasClass("active")) {
           // console.log(card,card[0])

       }
        let active_cards = $(this.settings["ticket_class"]+".active");
        let stakes = $(this.settings["ticket_class"]+".active form #stake");
        let returns = $(this.settings["ticket_class"]+".active form #returns");
        this.to_win = 0;
        this.stake = 0;
        returns.each(this._to_win_counter.bind(this))
        stakes.each(this._stake_counter.bind(this))
        let actives = active_cards.length
        let inactives = cards.length - actives;
        this.elements["ticket_counter"].text(actives)
        this.elements["modal_counter"].text(actives)
        this.elements["modal_stake"].text(this.stake)
        this.elements["modal_wins"].text(this.to_win)
        // if (actives > 0) {
        //
        //     this.elements["gdl_buy_now"].prop("disabled",false)
        // } else {
        //     this.elements["gdl_buy_now"].prop("disabled",true)
        // }
        // this.elements["gdl_active_cnt"].text(actives);
        this.active_cards = actives

    }

    _reset_after_save(res) {
        this.save_modal.bs_modal.hide()
        this._hide_cart();

        this.elements["avail_balance"].text(res.available)
        if (this.elements["bonus_balance"] !== false) {
            this.elements["bonus_balance"].text(res.bonus)
        }
        this.successToast("Game's on!","Your ticket(s) have been placed! Good luck!")
        this.elements["param_form"].submit();
        this.active_cards = 0

        this.get_cart();
        // this.elements["ticket_button"].prop('disabled', true);
        // this.elements["ticket_counter"].text(0)
        // this.elements["gdl_active_cnt"].text(0)

    }
    _save_tickets(event) {
        this.generic_post_form(event,false,this._reset_after_save.bind(this))
    }
    _execute_ticket_order() {
        // console.log('Execute ticket_order');
        // let etv = this._encode_tickets();
        //
        // this.elements["save_form_contents"][0].value = JSON.stringify(etv);
        this.elements["save_form"].submit();


    }

    _handle_confirm(e) {
        this._execute_ticket_order();
    }
    _getMinWin(parlays, baseBet = 2) {
        return Math.round(baseBet * Math.pow(this.settings["bet_scaler"], parlays));
    }

    _handle_form_change(e) {
        let current_legs = this.elements["events"][0].value;
        let current_rules = this.ruleset[current_legs]
        this.elements["stake"].attr({"min":current_rules["min_bet"],"max":current_rules["max_bet"]})
        let sv = this.elements["stake"][0].value
        if (sv < current_rules["min_bet"]) {
            this.elements["stake"][0].value = current_rules["min_bet"]
        }
        if (sv > current_rules["max_bet"]) {
            this.elements["stake"][0].value = current_rules["max_bet"]
        }
        let max_bet = this.settings["max_bet"];
        if (max_bet > this.settings["absmax_bet"]) {
            max_bet = this.settings["absmax_bet"]
        }

        sv = this.elements["minwin"][0].value;
        // this.elements["minwin"].attr({"max":max_bet,"step":250});
        if (sv > max_bet) {
            this.elements["minwin"][0].value = max_bet;
        }


    }
    _handle_start(res) {

        if ("quick_pick" in res) {
            this.get_cart();
            this._show_cart();
            this.elements["loading_div"].hide();
            this.elements["setup_area"].fadeIn();
            this.elements["quick_picks_div"].fadeIn();
        } else {
            this.elements["gdl_div"].empty();
            if (res.tickets.length === 0) {
                this.elements["loading_div"].hide();
                this.elements["gdl_empty_message"].fadeIn();
            }
            for (let ticket in res.tickets) {
                var tktDv = this._card_factory(res.tickets[ticket], ticket)
                // Add animation classes and inline delay

                this.elements["gdl_div"].append(tktDv);
                this.elements["gdl_total"].text(res.tickets.length);
                // this.elements["gdl_risking"].text(res.stake)
                // this.elements["gdl_to_win"].text(res.towin);
                // this.elements["gdl_events"].text(res.events);
                // tktDv.on("click", $(this).toggleClass('active'))

                tktDv.on("click", this._handle_card_flip.bind(this, tktDv))


            }
            this.elements["loading_div"].fadeOut();
            this.elements["gdl_div"].fadeIn();
            // this.elements["gdl_play_controls"].show();
            // this.elements["gdl_play_controls"].addClass('d-flex')
            // this._enable_play_controls()
            this.elements["modal"] = $(this.settings.modal);
        }
    }


    _handle_ajax_error(res) {
        if ("cashier" in res) {
            if (res.cashier === true) {
                cashier.start_deposit_modal();
            }
        }
    }
    start(event) {
        event.preventDefault();
        event.stopPropagation();
        this.active_cards = 0;
        // this.elements["gdl_active_cnt"].text(this.active_cards);
        // console.log("Starting GDL run,",event);
        this.elements["loading_div"].fadeIn();
        this.elements["gdl_div"].fadeOut();
        this.elements["gdl_empty_message"].hide();
        // this._disable_play_controls()
        this.elements["setup_area"].hide();
        this.elements["quick_picks_div"].hide();
        // this.elements["gdl_play_controls"].removeClass('d-flex')
        // this.elements["gdl_play_controls"].hide();
        this.generic_post_form_v2({"event":event,"modal":false,"callback":this._handle_start.bind(this)});

    }


    _enable_play_controls() { 
        this.elements["gdl_cashier_now"].attr("disabled", false);
        // this.elements["gdl_buy_now"].attr("disabled", false);
        // this.elements["gdl_more_now"].attr("disabled", false);
        // this.elements["gdl_refresh_now"].attr("disabled", false);
        this.elements["gdl_settings_now"].attr("disabled", false);

    }
    
    _disable_play_controls() { 
        this.elements["gdl_cashier_now"].attr("disabled", true);
        // this.elements["gdl_buy_now"].attr("disabled", true);
        // this.elements["gdl_more_now"].attr("disabled", true);
        // this.elements["gdl_refresh_now"].attr("disabled", true);
        this.elements["gdl_settings_now"].attr("disabled", true);
    }


    _handle_buy_event() {
        if ($("#cart_container").children().length  > 0) {
            if (this._isMobile())
            {
                this._hide_cart()
            }
            this.save_modal = new ElementGDLConfirmTktModal({},this.active_cards,this.stake,this.to_win,this._handle_confirm.bind(this));
        } else {
            alert("Accept some Tickets first!")
        }
    }

    _handle_cart(res) {
        let tot_risk = 0
        let tot_wins = 0
        this.settings["card_skip_accept_btn"] = true;
        this.elements["cart_container"].empty()
        for (var entry in res["data"]["tickets"]) {
            var entrc = res["data"]["tickets"][entry];
            tot_risk += entrc["risk"]
            tot_wins += entrc["returns"]
            let texts = {
                "wins":"Ticket Wins "+entrc["returns"]+" for "+entrc["risk"],
                "events":entrc["events"]+" events"
            }
            let cartEntry = new ElementGDLCartEntry(entrc["uuid"],texts,{"uuid":entrc["uuid"]})
            this.elements["cart_container"].append(cartEntry.get_el());
            cartEntry.remove_btn.on("click", this._handle_remove_cart.bind(this));
            cartEntry.details_btn.on("click", this._handle_ticket_details.bind(this,true));
        }
        this.elements["gdl_active_cnt"].text(res["data"]["count"]);
        this.active_cards = 1*(res["data"]["count"]);
        this.elements["modal_counter"].text(this.active_cards);
        this.elements["modal_stake"].text(tot_risk);
        this.elements["modal_wins"].text(tot_wins);
        this.stake = tot_risk;
        this.to_win = tot_wins;
    }
    get_cart() {
        this.generic_api_getreq(this.urls["cart"],false,this._handle_cart.bind(this));
    }
    _show_cart() {

        this.elements["cart_offc_control"].show();
    }
    _hide_cart() {
        this.elements["cart_offc_control"].hide();
    }
    _switch_mode() {
        this.elements["advanced_form_div"].show()
        this.elements["param_form_div"].hide()
    }
    _switch_qp() {
        // this.elements["quick_picks_div"].show()
        this.elements["param_form_div"].hide()
    }
    _reset_mode() {
        this.elements["advanced_form_div"].hide()
        // this.elements["quick_picks_div"].hide()
        this.elements["param_form_div"].show()

    }
    constructor(settings,urls) {
        super(settings, urls)
        $.extend(this.settings, settings);
        $.extend(this.urls, urls);
        console.log("Starting GDL App");
        this.elements["gdl_div"] = $(this.settings.gdl_div);
        this.elements["loading_div"] = $(this.settings.loading_div);
        this.elements["gdl_empty_message"] = $(this.settings.gdl_empty_message);
        this.elements["confirm_slider"] = $(this.settings.confirm_slider);
        this.elements["ticket_counter"] = $(this.settings.ticket_counter);
        this.elements["confirm_slider_label"] = $(this.settings.confirm_slider_label);
        this.elements["modal_wins"] = $(this.settings.modal_wins);
        this.elements["modal"] = $(this.settings.modal);
        this.elements["modal_counter"] = $(this.settings.modal_counter);
        this.elements["modal_stake"] = $(this.settings.modal_stake);
        this.elements["param_form"] = $(this.settings.param_form);
        this.elements["save_form"] = $(this.settings.save_form);
        this.elements["save_form_contents"] = $(this.settings.save_form_contents)
        this.elements["avail_balance"] = $(this.settings.avail_balance)
        this.elements["ticket_settings_div"] = $(this.settings["ticket_settings_div"]);
        this.elements["ruleset"] = $(this.settings.ruleset);
        this.elements["stake"] = $(this.settings.stake);
        this.elements["events"] = $(this.settings.events);
        this.elements["minwin"] = $(this.settings.minwin);
        this.elements["gdl_empty_message"].css("opacity","1.0");
        this.elements["loading_div"].css("opacity","1.0");
        this.elements["loading_div"].hide();
        this.elements["gdl_empty_message"].hide()
        // this.elements["ticket_button"].prop('disabled', true);
        this.elements["setup_area"] = $(this.settings.setup_area);
        this.elements["gdl_play_controls"] = $(this.settings.gdl_play_controls);
        // this.elements["gdl_play_controls"].hide();
        this.elements["gdl_settings_now"] = $(this.settings.gdl_settings_now);
        this.elements["gdl_settings_ntk"] = $(this.settings.gdl_settings_ntk);
        this.elements["gdl_buy_now"] = $(this.settings.gdl_buy_now);
        this.elements["gdl_total"] = $(this.settings.gdl_total);
        this.elements["gdl_active_cnt"] = $(this.settings.gdl_active_cnt);
        // this.elements["gdl_risking"] = $(this.settings.gdl_risking);
        this.elements["gdl_to_win"] = $(this.settings.gdl_to_win);
        this.elements["gdl_events"] = $(this.settings.gdl_events);
        this.elements["basic_ticket_count"] = $(this.settings.param_form+" "+this.settings.ticket_count);
        this.elements["adv_ticket_count"] = $(this.settings.advanced_form+" "+this.settings.ticket_count);
        this.elements["gdl_cashier_now"] = $(this.settings.gdl_cashier_now);
        this.elements["gdl_more_now"] = $(this.settings.gdl_more_now);
        this.elements["advanced_form_div"] = $(this.settings.advanced_form_div);
        this.elements["param_form_div"] = $(this.settings.param_form_div);
        this.elements["advanced_form_div"] = $(this.settings.advanced_form_div);
        this.elements["quick_picks_div"] = $(this.settings.quick_picks_div);
        this.elements["quick_picks_form"] = $(this.settings.quick_picks_form);
        this.elements["mode_switch_btn"] = $(this.settings.mode_switch_btn);
        this.elements["gdl_main_content"] = $(this.settings.gdl_main_content);
        // this.elements["quick_picks_btn"] = $(this.settings.quick_picks_btn);


        this.elements["gdl_settings_now"].on("click",this.toggle_settings.bind(this))
        this.elements["gdl_settings_ntk"].on("click",this.toggle_settings.bind(this))
        // this.elements["gdl_refresh_now"].on("click",this.refresh_tickets.bind(this));
        // this.elements["gdl_buy_now"].attr("disabled", true);
        this.elements["gdl_buy_now"].on("click", this._show_cart.bind(this));
        this.elements["cart_offcanvas"] = $(this.settings.cart_offcanvas);
        this.elements["cart_container"] = $(this.settings.cart_container);
        this.elements["cart_offc_control"] = new bootstrap.Offcanvas(this.elements["cart_offcanvas"]);
        this.elements["advanced_form_div"].hide()
        // this.elements["quick_picks_div"].hide()
        this.elements["mode_switch_btn"].on("click",this._switch_mode.bind(this));
        // this.elements["quick_picks_btn"].on("click",this._switch_qp.bind(this));
        try {
            this.elements["bonus_balance"] = $(this.settings.bonus_balance);
        } catch(e) {
            this.elements["bonus_balance"] = false
        }

        try {
            this.ruleset = JSON.parse(this.elements["ruleset"][0].value);
        } catch (e) {
            console.info("Notice: Unable to parse/load ruleset.")
        }
        this.elements["param_form"].on("change",this._handle_form_change.bind(this));
        // this.elements["setup_area"].hide();
        // Calibrate maximum object count based on display size:
        this.elements["gdl_div"].empty();
        // First, create a GDLCard to inject into the invisible GDL div.
        const card = new ElementGDLCard("card_test");
        const cardel = card.get_el()[0];
        this.elements["gdl_div"].css("opacity",0)
        this.elements["gdl_div"].append(cardel);

        const card_width = cardel.offsetWidth;
        const card_height = cardel.offsetHeight;
        this.card_area = (card_width*card_height);
        this.viewport_area = window.visualViewport.width * window.visualViewport.height;
        // if ((navigator.platform == "iPhone")||(window.devicePixelRatio > 2.1)) {
        //     this.recommended_cards = Math.round((this.viewport_area * this.settings["viewport_area_percentage_factor_iphone"]) / this.card_area);
        //
        //
        //     console.log("Factor is",this.settings["viewport_area_percentage_factor_iphone"]);
        // } else if (this.user_agent.isMobile === false) {
        //     this.recommended_cards = Math.round((this.viewport_area * this.settings["viewport_area_percentage_factor"]) / this.card_area);
        //     console.log("Factor is",this.settings["viewport_area_percentage_factor"]);
        // } else {
        //     this.recommended_cards = Math.round((this.viewport_area * this.settings["viewport_area_percentage_factor_mobile"]) / this.card_area);
        //     console.log("Factor is",this.settings["viewport_area_percentage_factor_mobile"]);
        // }
        this.recommended_cards = 6;
        if (this.user_agent.isSafari) {
            if (this.user_agent.isTablet) {
                this.elements["gdl_play_controls"].css("top","-35px");
                this.recommended_cards = 6;
            } else {
                this.recommended_cards = 3;
                if (this.safari_new_grp.includes(this.user_agent.shortVersion)) {
                    this.elements["gdl_play_controls"].css("top","-120px");
                } else {
                    this.elements["gdl_play_controls"].css("top","-25px");
                    this.elements["gdl_main_content"].css("top","30px");
                    this.elements["gdl_main_content"].css("left","0px");
                    this.elements["gdl_main_content"].css("position","fixed");

                }
            }
        } else if (this.user_agent.isChrome) {
            if (this.user_agent.platform.match("Android")) {
                let vpsh = Math.round(window.visualViewport.height)
                if (vpsh >= 827) {
                    this.recommended_cards = 4
                } else if (vpsh >= 762) {
                    this.recommended_cards = 3
                } else if (vpsh <= 698) {
                    this.recommended_cards = 3
                }
            }
        }
        // if (window.devicePixelRatio > 2.1) {
        //
        //         this.elements["gdl_div"].attr("style",this.settings["viewport_area_padding_top_dpx21"]);
        // }
        console.log("Card Area",this.card_area,"Viewport Area",this.viewport_area,"Card count set to",this.recommended_cards);
        this.settings["disable_success_toasts"] = true
        this.settings["disable_normal_toasts"] = true
        this.elements["basic_ticket_count"][0].value = this.recommended_cards;
        this.elements["adv_ticket_count"][0].value = this.recommended_cards;
        this.elements["gdl_div"].hide();
        this.elements["gdl_div"].empty();
        this.elements["gdl_div"].css("opacity",100);
        this.on_ajax_error_func = this._handle_ajax_error
        this.get_cart()


    }
}

