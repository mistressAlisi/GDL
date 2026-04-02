import {BaseForm} from "./main.js";
import {GDLWSSCore} from "./gdlwss_core.js";
import {ElementGDLCartEntry,ElementGDLConfirmTktModal,ElementGDLCard,ElementGDLViewTktModal} from "/static/gdlfront/js/GDLv2/Elements/GDLElements.js";



export class QuickPicksForm extends BaseForm {
    settings = {
        "gdl_active_cnt":"#gdl_active_cnt",
        "modal_counter":".modal_counter",
        "modal_stake":".modal_stake",
        "modal_wins":".modal_wins",
        "gdl_empty_message":"#gdl_empty_message",
        "cart_container":"#cart_container",
        "cart_offcanvas":"#offCanvasCart",
        "cart_bttn":"#gdl_buy_now",
        "purchase_btn":"#gdl_purchase_btn",
        "balance_prefix":"",
        "save_form": "#confirm_form",
        "save_form_contents": "#gdl_data",
        "avail_balance": ".avail_bal",
        "bonus_balance":".bonus_balance",
        "balance":"#balance",
        "pending":".pending_bal",
        "min_payout":"#min_payout",
        "count_input":"#count",
        "stake_input":"#stake",
        "debug":false,
        // "ws_domain":"wss.sportslotto.net",
        // "ws_domain":"127.0.0.1",
        // "ws_port":"443"
        // "ws_port":"8000",


    }
    elements = {}
    urls = {
    "_api_prefix": "/api/v1/game/",
    "quickpicks_stream":"/game/stream_quickpicks",
    "cart":"tickets/cart/",
    "balance":"get/curr_balance"
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
      this.elements["gdl_active_cnt"].text(0)
      this.normalToast("Purchase Complete!","Your ticket(s) have been purchased! Good luck!")
      // this.elements["param_form"].submit();
      this.active_cards = 0
      this.elements["count_input"][0].value = 5
      this.elements["stake_input"][0].value = 1
      this.calculateReturn();
      this.animateBalanceCounters();
      // this.get_cart();


    }

    _save_tickets(event) {
          this.generic_post_form(event,false,this._reset_after_save.bind(this))
    }

    _card_replace(event) {
        // Stub for fun.
    }
    websocket_onmessage_qp(event) {

        const msg = JSON.parse(event.data);
        if (this.settings["debug"] === true) {
            console.log("MSG incoming",msg);
        }
         if ("incomplete" in msg) {
             if (msg["incomplete"] === true) {
                  LoadingModal.hide();
                  NotEnoughEventsModal.show()
                 return false
             }
         }
         if (msg.type === "ticket") {
             let texts = {
                 "wins": "Ticket Wins " + msg["total_returns"] + " for " + msg["total_stake"],
                 "events": msg["depth"] + " events"
             }
             let euuid = this.wss_core._randUUID()
             // console.warn(msg)
             let cartEntry = new ElementGDLCartEntry(euuid, texts, {"uuid": msg["uuid"]})
             this.elements["cart_container"].append(cartEntry.get_el());
            cartEntry.remove_btn.on("click", this._handle_remove_cart.bind(this));
            cartEntry.details_btn.on("click", this.wss_core._handle_ticket_details.bind(this.wss_core,true));

         } else if (msg.type === "complete") {
            this.elements["gdl_active_cnt"].text(msg.ticket_count);
            this.active_cards = msg.ticket_count*1;
            this.elements["modal_counter"].text(this.active_cards);
            this.elements["modal_stake"].text(msg.total_risk);
            this.elements["modal_wins"].text(msg.total_wins);
            this.stake = msg.total_risk;
            this.to_win = msg.total_wins;
            this._show_cart()
            LoadingModal.hide();
        } else if (msg.type === "empty") {
             this.elements["gdl_empty_message"].show();
        }
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


    get_cart_post_remove() {
        // this.normalToast("Success","Ticket Deleted!")
        // this.get_cart();
    }

    _handle_remove_cart(event) {
        event.stopPropagation();
        event.preventDefault();
        let btn = $(this._parent_walker(event.target,"A"));
        let tuuid = btn.data("uuid");
        let url = this.urls["reject_ticket"]+tuuid+"?ng=1";
        this.generic_post_form_v2({"form":this.form[0],"callback":this.get_cart_post_remove.bind(this),"url":url})
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
            cartEntry.remove_btn.on("click", this.wss_core._handle_reject_ticket.bind(this.wss_core,false));
            cartEntry.details_btn.on("click", this.wss_core._handle_ticket_details.bind(this.wss_core,true));
        }
        this.elements["gdl_active_cnt"].text(res["data"]["count"]);
        this.active_cards = 1*(res["data"]["count"]);
        this.elements["modal_counter"].text(this.active_cards);
        this.elements["modal_stake"].text(tot_risk);
        this.elements["modal_wins"].text(tot_wins);
        this.stake = tot_risk;
        this.to_win = tot_wins;
        this._show_cart()
    }

    start(event) {
        event.stopPropagation();
        event.preventDefault();

        let tickets_req = this.wss_core._gen_ticket_req(false,this.form[0])
        LoadingModal.show();
        this.wss_core.send("qp", tickets_req);

    }

 _execute_ticket_order() {
     // Set use_bonus hidden input before form submission
     let use_bonus = this.save_modal ? this.save_modal.use_bonus : false;
     $('#use_bonus_input').val(use_bonus ? 'true' : 'false');
     this.elements["save_form"].submit();
 }

 _handle_buy_event() {
     if ($("#cart_container").children().length  > 0) {
         if (this._isMobile())
         {
             this._hide_cart()
         }
         // Get bonus balance
         let bonus = this.bonus_balance || parseFloat($('#bonus_balance')[0].value) || 0;
         this.save_modal = new ElementGDLConfirmTktModal({},this.active_cards,this.stake,this.to_win,bonus,this._execute_ticket_order.bind(this));
     } else {
         alert("Accept some Tickets first!")
     }
 }

    constructor(formId,settings,urls) {
        super(formId);
        $.extend(this.settings, settings);
        $.extend(this.urls, urls);
        this.riskInput = $('#stake');
        this.ticketCountInput = $('#count');
        this.possibleReturnDisplay = $('#possible-return');
        this.wss_core = new GDLWSSCore(settings,urls,this)
        this.elements["cart_container"] = $(this.settings["cart_container"])
        this.elements["gdl_active_cnt"] = $(this.settings["gdl_active_cnt"])
        this.elements["modal_counter"] = $(this.settings["modal_counter"])
        this.elements["modal_stake"] = $(this.settings["modal_stake"])
        this.elements["modal_wins"] = $(this.settings["modal_wins"])
        this.elements["cart_bttn"] = $(this.settings["cart_bttn"])
        this.elements["gdl_empty_message"] = $(this.settings["gdl_empty_message"])
        this.elements["purchase_btn"] = $(this.settings["purchase_btn"]);
        this.elements["cart_offcanvas"] = $(this.settings["cart_offcanvas"])
        this.elements["cart_offc_control"] = new bootstrap.Offcanvas(this.elements["cart_offcanvas"]);
        this.elements["save_form"] = $(this.settings["save_form"]);
        this.elements["save_form_contents"] = $(this.settings["save_form_contents"]);
        this.elements["avail_balance"] = $(this.settings.avail_balance)
        this.elements["bonus_balance"] = $(this.settings.bonus_balance)
        this.elements["balance"] = $(this.settings.balance)
        this.elements["pending"] = $(this.settings.pending)
        this.elements["min_payout"] = $(this.settings.min_payout)
        this.elements["count_input"] = $(this.settings.count_input)
        this.elements["stake_input"] = $(this.settings.stake_input)

        let fullUrl = ""
        function build_url(url) {
            if (this.settings["ws_domain"]) {
                const wsp = window.location.protocol === "https:" ? "wss://" : "ws://";
                fullUrl = wsp + this.settings["ws_domain"] + ":" + this.settings["ws_port"] + url;
            } else {
                fullUrl = this.wss_core.getWssEndpoint() + url;
            }
            return fullUrl;
        }
        this.wss_core.setup_wss_socket("qp",build_url.bind(this,this.urls["quickpicks_stream"])(),this.websocket_onmessage_qp.bind(this))
        this.bindEvents();
        this.calculateReturn();

        // this.get_cart()
    }

    bindEvents() {
        // Real-time calculation on risk amount change
        this.riskInput.on('input', () => {
            this.calculateReturn();
        });

        // Add smooth transition on focus
        this.riskInput.on('focus', function() {
            $(this).parent('.input-container').addClass('focused');
        }).on('blur', function() {
            $(this).parent('.input-container').removeClass('focused');
        });

        this.ticketCountInput.on('focus', function() {
            $(this).parent('.input-container').addClass('focused');
        }).on('blur', function() {
            $(this).parent('.input-container').removeClass('focused');
        });

        // Form submission
        this.form.on('submit', (e) => {
            if (!this.validateForm()) {
                e.preventDefault();
                this.showError('Please fill in all required fields correctly.');
            }
        });
        this.elements["cart_bttn"].on('click',this.get_cart.bind(this));
        this.elements["purchase_btn"].on('click',this._handle_buy_event.bind(this));

    }

    calculateReturn() {
        const risk = parseFloat(this.riskInput.val()) || 0;
        const possibleReturn = risk * 20; // 20 to 1 odds

        this.possibleReturnDisplay.text(this.settings.balance_prefix+`${possibleReturn.toFixed(2)}`);
        this.elements["min_payout"][0].value = possibleReturn;
        // Add animation effect
        this.possibleReturnDisplay.addClass('pulse-animation');
        setTimeout(() => {
            this.possibleReturnDisplay.removeClass('pulse-animation');
        }, 300);
    }
}
