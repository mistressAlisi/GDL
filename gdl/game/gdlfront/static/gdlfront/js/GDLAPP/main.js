import {AbstractDashboardApp} from "/static/minerve/js/dashboards/DashboardApp/AbstractDashboardApp.js";
import {ElementGDLCard,ElementGDLCartEntry,ElementGDLConfirmTktModal,ElementGDLViewTktModal} from "./Elements/GDLElements.js";
import {WSManager} from "/static/minerve/js/core/WSManager.js";

$.getJSON('/jsi18n/', function(translations) {
    // Define a function for convenience
    window.gettext = function(msgid) {
        return translations[msgid] || msgid; // Fallback to original if not found
    };
    // Use translations in your JavaScript code
    console.log(translations);
});

export class GDLApp extends AbstractDashboardApp {

    urls = {
        "_api_prefix": "/api/v1/game/",
        "submit_step1": "run_step1",
        "ticket_viewer": "/game/ticket/details/viewer/",
        "accept_ticket":"tickets/accept/",
        "reject_ticket":"tickets/reject/",
        "cart":"tickets/cart/",
        "ticket_stream":"/game/stream_tickets",
        "quickpicks_stream":"/game/stream_quickpicks"

    }

    /** must be loaded from ruleset in form! **/
    ruleset = {}
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
        "modal_counter": ".modal_counter",
        "modal_stake": ".modal_stake",
        "modal_wins": ".modal_wins",
        "param_form": "#parameter_form",
        "custom_settings":"#custom_settings",
        "param_form_div":"#basic_settings",
        "custom_settings_div":"#custom_settings",
        "mode_switch_btn":"#custom_switch_btn",
        "quick_picks_div":"#quick-picks",
        "quick_picks_form":"#quick_pick_form",
        "quick_picks_btn":"#quick_pick_btn",
        "save_form": "#confirm_form",
        "save_form_contents": "#gdl_data",
        "avail_balance": ".avail_bal",
        "balance":"#balance",
        "pending":".pending_bal",
        "ticket_settings_div": "#ticket_settings_div",
        "gdl_play_controls":"#gdl_play_controls",
        "gdl_to_win":"#gdl_to_win",
        "gdl_risking":"#gdl_risking",
        "gdl_events":"#gdl_events",
        "gdl_active_cnt":"#gdl_active_cnt",
        "gdl_total":"#gdl_total",
        "gdl_buy_now":"#gdl_buy_now",
        "gdl_buy_now_alt":"#gdl_buy_now_alt",
        "gdl_main_content":"#main-content",
        "gdl_cashier_now":"#gdl_cashier_now",
        "gdl_refresh_now":"#gdl_refresh_now",
        "gdl_settings_now":"#gdl_settings_now",
        "gdl_settings_ntk":"#gdl_settings_ntk",
        "gdl_more_now":"#gdl_more_now",
        "gdl_view_mode":"#gdl_view_mode",
        "gdl_empty_message":"#gdl_empty_message",
        "main_sidebar":"#mainSidebar",
        "events": "#id_depth",
        "stake": "#id_stake",
        // "minwin": "#id_minwin",
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
        "disable_success_toasts":true,
        "disable_normal_toasts":false,
        "min_payout":"#id_min_payout",
        "qp_mul":20,
        // "ws_domain":"wss.sportslotto.net",
        // "ws_domain":"127.0.0.1",
        // "ws_port":"443"
        // "ws_port":"8000"
    }

    current_cards = {

    }
    old_card = false
    to_win = 0
    stake = 0
    ticket_data = []
    viewport_area = 0
    card_area = 0
    recommended_cards = 0
    active_cards = 0
    current_page = 0
    total_pages = 0
    /** Websockets workers: **/
    wsw = false
    wsw_qp = false
    save_modal = false

    /** New Websocket: Manager **/
    ws_manager = new WSManager(this);

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

    _randUUID() {
          return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
            const r =
              (crypto.getRandomValues(new Uint8Array(1))[0] & 15) >>
              (c === 'x' ? 0 : 3);
            return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16);
          });
    }
    _set_ticket_btns(tuuid) {
        // console.warn("Set Ticket Buttons",rejctBtn,acceptBtn)
        this.last_modal.dialog.addClass("modal-dialog-scrollable");
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
                    "html": "<i class=\"fa-duotone fa-solid  fa-circle-check \"></i> Accept",
                    "data-bs-placement": "top",
                    "data-bs-toggle": "tooltip",
                    "title": "Accept Ticket!",
                    "data-uuid": tuuid
                });
                this.last_modal.footer.prepend(acceptBtn);
                acceptBtn.on("click", this._handle_accept_card.bind(this, true));
            }
            this.last_modal.footer.prepend(rejectBtn);
             let closeBtn = $("<button/>", {
                 "class": "btn",
                 "html": "Close Dialogue",
                 "title": "Close Dialogue",
             })
            this.last_modal.footer.append(closeBtn);
            closeBtn.on("click",this.last_modal.bs_modal.hide.bind(this.last_modal.bs_modal));
            rejectBtn.on("click", this._handle_reject_card.bind(this, true));
        }
        // console.warn("Set Ticket Buttons",rejctBtn,acceptBtn)
    }

    _handle_ticket_details(is_a,event) {
        let btn = null
        if (is_a == false) {
            btn = $(this._parent_walker(event.target, "BUTTON"));
        } else{
            btn = $(this._parent_walker(event.target, "A"));
        }
        let uuid = btn.data("uuid")
        this.generic_ajax_modal_dialogue("Ticket Details", this.urls["ticket_viewer"] + uuid, false, "", false, this._set_ticket_btns.bind(this,uuid), false, true)
    }

    _render_ticket_details(data,card,event) {

        let dataModal = new ElementGDLViewTktModal({},data.risk,data.wins,data.events,data.legs,card);
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
                        stake_str: "Risking " + data["total_stake"] + " returns " + data["total_returns"],
                        return_str: "" + data["total_stake"]+" returns : " + data["returns"],
                        selected: "<i class=\"fa-solid fa_square-exclamation\"></i> Better Luck Next Time!",
                    }
                    break;
                case "W":
                    texts = {
                        stake_str: "" + data["total_stake"] + " won: " + data["total_returns"],
                        return_str: "" + data["total_stake"]+" returns : " + data["total_returns"],
                        selected: "<i class=\"fa-dutone fa-solid fa-stars\"></i> You're a Winner!!",
                    }
                    break;
                case "P":
                case "M":
                    texts = {
                        selected: "<i class=\"fa-dutone fa-solid fa-hourglass\"></i> In Play - Good Luck!",
                        returns: "" + data["total_returns"],
                        stake_str: "" + data["total_stake"] + " to win: " + data["total_returns"],
                        return_str: "" + data["total_stake"]+" returns : " + data["total_returns"],
                        sports: ` ${data["sports"] || 0} Events`
                    };
                    break;
                case "C":
                    texts = {
                    selected: "",
                    returns: "" + data["total_returns"],
                    stake_str: "" + data["total_stake"] + " returns : " + data["total_returns"]+"",
                    return_str: "" + data["total_stake"]+" returns : " + data["total_returns"],
                    sports: ` ${data["depth"] || 0} Events`
                }
                break;
            }

        let cuuid = this._randUUID()
        const card = new ElementGDLCard(cuuid, texts, data, props, {"render_as_active":this.settings["card_render_as_active"]});
        this.current_cards[cuuid] = card;
        card.reject_btn.on("click", this._handle_reject_card.bind(this,false));
        card.accept_btn.on("click", this._handle_accept_card.bind(this,card.form,false));
        card.reject_btn_frnt.on("click", this._handle_reject_card.bind(this,false));
        card.accept_btn_frnt.on("click", this._handle_accept_card.bind(this,card.form,false));
        let detail_data = {
            "legs":data["legs"],
            "status":data["status"],
            "events":data["depth"],
            "risk":data["total_stake"],
            "wins":data["total_returns"],
        }
        card.detail_btn.on("click", this._render_ticket_details.bind(this, detail_data,card));
        card.get_el().on("click",this._render_ticket_details.bind(this, detail_data,card));
        // Add animation class and inline delay:
        let delay = `${ticket_count * this.settings["ticket_anim_delay"]}ms`;
        card.el.css({
        opacity: 0,
        animation: 'slideFadeIn 0.6s ease-out forwards',
        'animation-delay': delay
        });

        return card.get_el();
    }

    _handle_accept_card(form_data,close_modal,event) {
        event.stopPropagation();
        event.preventDefault();
        let btn = $(this._parent_walker(event.target,"BUTTON"));
        this.generic_post_form_v2({"form":form_data[0],"callback":this._card_replace.bind(this),"url":this.urls["accept_ticket"],"skip_modal":true})

    }
    _gen_ticket_req(count=false,form=false) {
        let settings = {}
        let fda = false;
        if (form === false) {
            fda = new FormData(this.elements["param_form"][0])
        } else {
            fda = new FormData(form)
        }
        for (const pair of fda.entries()) {
          settings[pair[0]] = pair[1];
        }
        if (count !== false) {
            settings["count"] = count
        }
        let payload = {
            action: "generate",
            settings: settings,
        }
        return payload;
    }
    _handle_reject_card(close_modal,event) {
        event.stopPropagation();
        event.preventDefault();
        let btn = $(this._parent_walker(event.target,"BUTTON"));
        let tuuid = btn.data("uuid");
        this.old_card = tuuid;
        if (close_modal) {
            this.last_modal.bs_modal.hide()
        }
        let payload = this._gen_ticket_req(1)
        // this.wsw.send(JSON.stringify(payload));
        this.ws_manager.send("wsw", payload);


    }
    _handle_remove_cart(event) {
        event.stopPropagation();
        event.preventDefault();
        let btn = $(this._parent_walker(event.target,"A"));
        let tuuid = btn.data("uuid");
        let url = this.urls["reject_ticket"]+tuuid+"?ng=1";
        this.generic_post_form_v2({"form":this.elements["param_form"],"callback":this.get_cart_post_remove.bind(this),"url":url})
    }

    _card_replace(res) {
        this.old_card = res["data"]["old"]
        let payload = this._gen_ticket_req(1)
        // console.log("Payload",payload)
        // this.wsw.send(JSON.stringify(payload));
        this.ws_manager.send("wsw", payload);

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
        let detail_data = {
            "legs":data["legs"],
            "status":data["status"],
            "events":data["depth"],
            "risk":data["total_stake"],
            "wins":data["total_returns"],
        }
        card.detail_btn.on("click", this._render_ticket_details.bind(this, detail_data,card));
        this._render_ticket_details()
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
        this.elements["balance"].text(res.balance)
        this.elements["pending"].text(res.pending)
        if (this.elements["bonus_balance"] !== false) {
            this.elements["bonus_balance"].text(res.bonus)
        }
        this.normalToast("Purchase Complete!","Your ticket(s) have been purchased! Good luck!")
        // this.elements["param_form"].submit();
        this.active_cards = 0

        this.get_cart();
        this.toggle_settings();
        // this.elements["ticket_button"].prop('disabled', true);
        // this.elements["ticket_counter"].text(0)_set_ticket_btns
        // this.elements["gdl_active_cnt"].text(0)

    }
    _save_tickets(event) {
        this.generic_post_form(event,false,this._reset_after_save.bind(this))
    }
    _execute_ticket_order() {




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

        sv = this.elements["min_payout"][0].value;
        // this.elements["minwin"].attr({"max":max_bet,"step":250});
        if (sv > max_bet) {
            this.elements["min_payout"][0].value = max_bet;
        }


    }


    _handle_ajax_error(res) {
        if ("cashier" in res) {
            if (res.cashier === true) {
                cashier.start_deposit_modal();
            }
        }
    }
    update_qp(event) {
        event.stopPropagation();
        event.preventDefault();
        let value = $(event.target)[0].value * this.settings["qp_mul"];
        $("#min_payout")[0].value = value;

    }
    start_qp(event) {
        event.stopPropagation();
        event.preventDefault();
        // console.log(this.elements["quick_picks_form"][0]);
        let tickets_req = this._gen_ticket_req(false,this.elements["quick_picks_form"][0])
        // console.log(tickets_req);
        // this.wsw_qp.send(JSON.stringify(tickets_req));
        // this._safeWsSend("wsw_qp", tickets_req);
        this.ws_manager.send("wsw_qp", tickets_req);

    }
    start(event) {
        event.preventDefault();
        event.stopPropagation();
        this.active_cards = 0;
        this.elements["loading_div"].fadeIn();
        this.elements["gdl_div"].fadeOut();
        this.elements["gdl_empty_message"].hide();
        this.elements["setup_area"].hide();
        this.elements["quick_picks_div"].hide();
        // console.log(JSON.stringify(payload))
        this.elements["gdl_div"].empty();
        this.elements["gdl_div"].fadeIn();
        this.elements["loading_div"].hide();
        let payload = this._gen_ticket_req(false,event.target)
        console.warn("Payload",payload);
        // this._safeWsSend("wsw", payload);
        this.ws_manager.send("wsw", payload);


        // this.generic_post_form_v2({"event":event,"modal":false,"callback":this._handle_start.bind(this)});

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
                "wins":gettext("Ticket Wins ")+entrc["returns"]+gettext(" for ")+entrc["risk"],
                "events":entrc["events"]+gettext(" events")
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
    get_cart_post_remove() {
        this.normalToast("Success","Ticket Deleted!")
        this.get_cart();
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
         const div = this.elements["custom_settings_div"];

    if (div.is(":visible")) {
        div.hide();
    } else {
        div.show();
    }


    }

    _reset_mode() {
        this.elements["advanced_form_div"].hide()
        // this.elements["quick_picks_div"].hide()
        this.elements["param_form_div"].show()

    }

    websocket_onmessage_qp(event) {
        const msg = JSON.parse(event.data);

         if (msg.type === "ticket") {
             let texts = {
                 "wins": gettext("Ticket Wins ") + msg["total_returns"] + gettext(" for ") + msg["total_stake"],
                 "events": msg["depth"] + gettext(" events")
             }
             let euuid = this._randUUID()
             // console.warn(msg)
             let cartEntry = new ElementGDLCartEntry(euuid, texts, {"uuid": msg["uuid"]})
             this.elements["cart_container"].append(cartEntry.get_el());
            cartEntry.remove_btn.on("click", this._handle_remove_cart.bind(this));
            cartEntry.details_btn.on("click", this._handle_ticket_details.bind(this,true));

         } else if (msg.type === "complete") {
            this.elements["gdl_active_cnt"].text(msg.ticket_count);
            this.active_cards = msg.ticket_count*1;
            this.elements["modal_counter"].text(this.active_cards);
            this.elements["modal_stake"].text(msg.total_risk);
            this.elements["modal_wins"].text(msg.total_wins);
            this.stake = msg.total_risk;
            this.to_win = msg.total_wins;
            this._show_cart()
        } else if (msg.type === "empty") {
             this.elements["gdl_empty_message"].show();
        }
    }
    websocket_onmessage(event) {
        // try {
        const msg = JSON.parse(event.data);
        // console.log("MSG incoming",msg);
        if (msg.type === "ticket") {
            var tktDv = this._card_factory(msg,1)
                if (this.old_card === false) {
                    this.elements["gdl_div"].append(tktDv);
                    tktDv.on("click", this._handle_card_flip.bind(this, tktDv))
                } else {
                    let oldCard = this.current_cards[this.old_card];
                    console.log(oldCard,this.old_card);
                    oldCard.replace_and_destroy(tktDv);
                    delete this.current_cards[this.old_card];
                    tktDv.on("click", this._handle_card_flip.bind(this, tktDv))
                    this.get_cart()
                    this.old_card = false;
                }

        } else if (msg.type === "complete" || msg.type === "error") {
          // console.log("Command Finished.");
          // ws.close();
        } else if (msg.type === "empty") {

                    this.elements["gdl_empty_message"].fadeIn();
        } else if (msg.type === "error") {
            console.error("Websocket Protocol Error!!")
            console.error(msg);
        }
      // } catch (err) {
      //   console.log("⚠️ Invalid JSON: " + event.data);
      // }
    }


   getWssEndpoint() {
    const hostname = window.location.hostname;
    const parts = hostname.split(".");

    // Reduce foof.yourapp.com → yourapp.com
    const baseDomain =
        parts.length > 2
            ? parts.slice(-2).join(".")
            : hostname;

    return `wss://wss.${baseDomain}`;
    }

    websocket_setup() {

    // const wsp = "ws://"
    console.log("[GDLApp]: Websockets Initialising...")
        let fullUrl = ""
        function build_url(url) {
            if (this.settings["ws_domain"]) {
                const wsp = window.location.protocol === "https:" ? "wss://" : "ws://";
                fullUrl = wsp + this.settings["ws_domain"] + ":" + this.settings["ws_port"] + url;
            } else {
                fullUrl = this.getWssEndpoint() + url;
            }
            return fullUrl;
        }
        this.ws_manager.initStream("wsw",build_url.bind(this,this.urls["ticket_stream"])(),this.websocket_onmessage.bind(this))
        this.ws_manager.initStream("wsw_qp",build_url.bind(this,this.urls["quickpicks_stream"])(),this.websocket_onmessage_qp.bind(this))
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
        this.elements["balance"] = $(this.settings.balance)
        this.elements["pending"] = $(this.settings.pending)
        this.elements["ticket_settings_div"] = $(this.settings["ticket_settings_div"]);
        this.elements["ruleset"] = $(this.settings.ruleset);
        this.elements["stake"] = $(this.settings.stake);
        this.elements["events"] = $(this.settings.events);
        // this.elements["minwin"] = $(this.settings.minwin);
        this.elements["gdl_empty_message"].css("opacity", "1.0");
        this.elements["loading_div"].css("opacity", "1.0");
        this.elements["loading_div"].hide();
        this.elements["gdl_empty_message"].hide()
        this.elements["setup_area"] = $(this.settings.setup_area);
        this.elements["gdl_play_controls"] = $(this.settings.gdl_play_controls);
        this.elements["gdl_settings_now"] = $(this.settings.gdl_settings_now);
        this.elements["gdl_settings_ntk"] = $(this.settings.gdl_settings_ntk);
        this.elements["gdl_buy_now"] = $(this.settings.gdl_buy_now);
        this.elements["gdl_buy_now_alt"] = $(this.settings.gdl_buy_now_alt);
        this.elements["gdl_total"] = $(this.settings.gdl_total);
        this.elements["gdl_active_cnt"] = $(this.settings.gdl_active_cnt);
        this.elements["gdl_to_win"] = $(this.settings.gdl_to_win);
        this.elements["gdl_events"] = $(this.settings.gdl_events);
        this.elements["basic_ticket_count"] = $(this.settings.param_form + " " + this.settings.ticket_count);
        // this.elements["adv_ticket_count"] = $(this.settings.advanced_form + " " + this.settings.ticket_count);
        this.elements["gdl_cashier_now"] = $(this.settings.gdl_cashier_now);
        this.elements["gdl_more_now"] = $(this.settings.gdl_more_now);
        // this.elements["custom_settings_div"] = $(this.settings.custom_settings_div);
        this.elements["param_form_div"] = $(this.settings.param_form_div);
        this.elements["custom_settings_div"] = $(this.settings.custom_settings_div);
        this.elements["quick_picks_div"] = $(this.settings.quick_picks_div);
        this.elements["quick_picks_form"] = $(this.settings.quick_picks_form);
        this.elements["mode_switch_btn"] = $(this.settings.mode_switch_btn);
        this.elements["gdl_main_content"] = $(this.settings.gdl_main_content);
        this.elements["gdl_settings_now"].on("click", this.toggle_settings.bind(this))
        this.elements["gdl_settings_ntk"].on("click", this.toggle_settings.bind(this))
        this.elements["gdl_buy_now"].on("click", this._show_cart.bind(this));
        this.elements["gdl_buy_now_alt"].on("click", this._show_cart.bind(this));
        this.elements["cart_offcanvas"] = $(this.settings.cart_offcanvas);
        this.elements["cart_container"] = $(this.settings.cart_container);
        this.elements["cart_offc_control"] = new bootstrap.Offcanvas(this.elements["cart_offcanvas"]);
        this.elements["custom_settings_div"].hide()
        this.elements["mode_switch_btn"].on("click", this._switch_mode.bind(this));
        this.elements["min_payout"] = $(this.settings.min_payout);
        try {
            this.elements["bonus_balance"] = $(this.settings.bonus_balance);
        } catch (e) {
            this.elements["bonus_balance"] = false
        }

        try {
            this.ruleset = JSON.parse(this.elements["ruleset"][0].value);
        } catch (e) {
            console.info("Notice: Unable to parse/load ruleset.")
        }
        this.elements["param_form"].on("change", this._handle_form_change.bind(this));
        // this.elements["setup_area"].hide();
        // Calibrate maximum object count based on display size:
        this.elements["gdl_div"].empty();

        this.recommended_cards = 10;
        // console.log(this.user_agent.name);
        if (this.user_agent.name.match("Safari")) {
            // console.log("Is Safari");
            // alert("is Safari");
            if ((this.user_agent.isTablet) || (this.user_agent.platform == "IPad")) {
                // console.log("Lamatch")
                // this.elements["gdl_play_controls"].css("top", "-35px");
                this.recommended_cards = 6;
            } else if (this.user_agent.platform.match("Macintosh")) {
                this.recommended_cards = 10;
            } else {
                this.recommended_cards = 3;
                if (this.safari_new_grp.includes(this.user_agent.shortVersion)) {
                    // this.elements["gdl_play_controls"].css("top","-120px");
                } else {
                    // this.elements["gdl_play_controls"].css("top", "-25px");
                    this.elements["gdl_main_content"].css("top", "30px");
                    this.elements["gdl_main_content"].css("left", "0px");
                    this.elements["gdl_main_content"].css("position", "fixed");

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
            } else if (this.user_agent.platform.match("IPad")) {
                this.recommended_cards = 6
            } else if (this.user_agent.platform.match("Mac")) {
                this.recommended_cards = 10
            } else if (this.user_agent.platform.match("iPhone")) {
                this.recommended_cards = 3
            }
        } else if (this.user_agent.name.match("Firefox")) {
            if (this.user_agent.isAndroid) {
                if (this.user_agent.isMobile) {
                    this.recommended_cards = 3;
                }
            }
        }
        // if (window.devicePixelRatio > 2.1) {
        //
        //         this.elements["gdl_div"].attr("style",this.settings["viewport_area_padding_top_dpx21"]);
        // }
        console.log("Card Area", this.card_area, "Viewport Area", this.viewport_area, "Card count set to", this.recommended_cards);
        try {
            this.elements["basic_ticket_count"][0].value = this.recommended_cards;
        } catch (DOMException) {}
        // this.elements["adv_ticket_count"][0].value = this.recommended_cards;
        this.elements["gdl_div"].hide();
        this.elements["gdl_div"].empty();
        this.elements["gdl_div"].css("opacity", 100);
        this.on_ajax_error_func = this._handle_ajax_error

        this.get_cart()
        this.websocket_setup()

    }
}
