import {BaseForm} from "./main.js";
import {GDLWSSCore} from "./gdlwss_core.js";
import {ElementGDLCartEntry,ElementGDLConfirmTktModal,ElementGDLCard,ElementGDLViewTktModal} from "/static/gdlfront/js/GDLv2/Elements/GDLElements.js";



export class CustomTicketsForm extends BaseForm {
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
        "setup_area": "#setup_area",
        "balance_prefix":"",
        "save_form": "#confirm_form",
        "save_form_contents": "#gdl_data",
        "avail_balance": ".avail_bal",
        "bonus_balance":".bonus_balance",
        "balance":"#balance",
        "pending":".pending_bal",
        "loading_div": "#gdl_loading_message",
        "flip_card_css": ".flip-card",
        "ticket_class": ".gdl-ticket-card",
        "ticket_counter": "#ticket_counter",
        "basic_ticket_count":"#count",
        "gdl_div": "#gdl_play_area",a
        "gdl_main_content":"#gdl_main_content",
        "debug":false,
        // "ws_domain":"wss.sportslotto.net",
        // "ws_domain":"127.0.0.1",
        // "ws_port":"443"
        // "ws_port":"8000",


    }
    elements = {}
    urls = {
    // _api_prefix is inherited from BaseForm and set dynamically
    "ticket_stream":"/game/stream_tickets",
    "cart":"tickets/cart/",
    "balance":"get/curr_balance",
    "submit_step1": "run_step1",
    "ticket_viewer": "/game/ticket/details/viewer/",
    "accept_ticket":"tickets/accept/",
    "reject_ticket":"tickets/reject/",

    }
    first_run = true
    get_cart_post_remove() {
    // this.normalToast("Success","Ticket Deleted!")
        this.get_cart();
    }
    _handle_remove_cart(event) {
        event.stopPropagation();
        event.preventDefault();
        let btn = $(this._parent_walker(event.target,"A"));
        let tuuid = btn.data("uuid");
        let url = this.urls["reject_ticket"]+tuuid+"?ng=1";
        this.generic_post_form_v2({"form":this.form[0],"callback":this.get_cart_post_remove.bind(this),"url":url})
    }

    _gen_ticket_req(count=false,form=false,old=false) {
        let settings = {}
        let fda = false;
        if (form === false) {
            fda = new FormData(this.form[0])
        } else {
            fda = new FormData(form)
        }
        for (const pair of fda.entries()) {
          settings[pair[0]] = pair[1];
        }
        if (count !== false) {
            settings["count"] = count
        }
        let old_uuid = false
        if (old !== false) {
            old_uuid = old;
        }
        let payload = {
            action: "generate",
            settings: settings,
            old_uuid: old_uuid,
        }
        return payload;
    }
    _reset_after_save(res) {
      this.save_modal.bs_modal.hide()
      this._hide_cart();
      this.elements["gdl_active_cnt"].text(0)
      this.elements["avail_balance"].text(res.available)
      this.elements["balance"].text(res.balance)
      this.elements["pending"].text(res.pending)
      this.elements["bonus_balance"].text(res.bonus)
      // if (this.elements["bonus_balance"] !== false) {

      // }
      this.normalToast("Purchase Complete!","Your ticket(s) have been purchased! Good luck!")
      // this.elements["param_form"].submit();
      this.active_cards = 0
      this.animateBalanceCounters();
      // this.get_cart();


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
        card.detail_btn.on("click", this.wss_core._render_ticket_details.bind(this.wss_core, detail_data,card));
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
    _to_win_counter(a,b) {
        this.to_win = this.to_win + (b.value*1)
    }
    _stake_counter(a,b) {
        this.stake = this.stake + (b.value*1)
    }
    websocket_onmessage(event) {
        // try {
        // if (this.settings["debug"]) {
        //     console.log("Raw Incoming Event", event)
        // }
        const msg = JSON.parse(event.data);
        // console.warn("Ze Message",msg)
        if (this.settings["debug"] === true) {
            console.log("MSG incoming",msg);
        }
        if (msg.incomplete) {
             if (msg["incomplete"] === true) {
                 LoadingModal.hide();
                 NotEnoughEventsModal.show()
                 return false
             }
         }
        if (msg.type === "ticket") {
            if (this.settings.debug) {
                console.info("Incoming Ticket Message", msg)
            }
            if (msg.old_uuid) {
                this.wss_core._clearTicketTimeout(msg.old_uuid);
            }
            // if (this.first_run) {
                LoadingModal.hide();
                // this.first_run = false;

            // }
            var tktDv = this._card_factory(msg,1)
                if (msg.old_uuid) {
                    let oldCard = $("#"+msg.old_uuid);
                    // console.log(msg.old_uuid,oldCard)
                    oldCard.replaceWith(tktDv);
                    delete this.wss_core.current_cards[this.old_card];

                } else {
                    this.elements["gdl_div"].append(tktDv);

                }
                tktDv.on("click", this._handle_card_flip.bind(this, tktDv))

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
    _save_tickets(event) {
          this.generic_post_form(event,false,this._reset_after_save.bind(this))
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

    _card_factory(data,ticket_count) {
        const variant = this.wss_core._randomInt(0, 20);

        const props = {
            variant_number: variant
        };
        let texts = {}
            // console.log("Data to render:", data);
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

        let cuuid = this.wss_core._randUUID()
        const card = new ElementGDLCard(cuuid, texts, data, props, {"render_as_active":this.settings["card_render_as_active"]});
        this.wss_core.current_cards[cuuid] = card;
        card.reject_btn.on("click", this.wss_core._handle_reject_card.bind(this.wss_core,false));
        card.accept_btn.on("click", this.wss_core._handle_accept_card.bind(this.wss_core,card.form,false));
        card.reject_btn_frnt.on("click", this.wss_core._handle_reject_card.bind(this.wss_core,false));
        card.accept_btn_frnt.on("click", this.wss_core. _handle_accept_card.bind(this.wss_core,card.form,false));
        // card.accept_btn_frnt.on("click", card.el.hide.bind(card));
        // card.accept_btn.on("click", card.el.hide.bind(card));
        let detail_data = {
            "legs":data["legs"],
            "status":data["status"],
            "events":data["depth"],
            "risk":data["total_stake"],
            "wins":data["total_returns"],
        }
        card.detail_btn.on("click", this.wss_core._render_ticket_details.bind(this.wss_core, detail_data,card));
        card.get_el().on("click",this.wss_core._render_ticket_details.bind(this.wss_core, detail_data,card));
        // Add animation class and inline delay:
        let delay = `${ticket_count * this.settings["ticket_anim_delay"]}ms`;
        card.el.css({
        opacity: 0,
        animation: 'slideFadeIn 0.6s ease-out forwards',
        'animation-delay': delay
        });
        // console.log(card)
        return card.get_el();
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
    _execute_ticket_order() {
        // Set use_bonus hidden input before form submission
        let use_bonus = this.save_modal ? this.save_modal.use_bonus : false;
        $('#use_bonus_input').val(use_bonus ? 'true' : 'false');
        this.elements["save_form"].submit();
    }
    constructor(formId,settings,urls) {
        super(formId);
        // Re-set dynamic API prefix (child class fields override parent's after super() returns)
        this.urls["_api_prefix"] = this._getApiPrefix();
        $.extend(this.settings, settings);
        $.extend(this.urls, urls);
        this.riskInput = $('#stake');
        this.ticketCountInput = $('#count');
        this.possibleReturnDisplay = $('#possible-return');
        this.wss_core = new GDLWSSCore(settings,urls,this)
        this.selectedSports = new Set(['basketball', 'football', 'baseball']);
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
        this.elements["loading_div"] = $(this.settings.loading_div);
        this.elements["gdl_div"] = $(this.settings.gdl_div);
        this.elements["setup_area"] = $(this.settings.setup_area);
        this.elements["ticket_counter"] = $(this.settings.ticket_counter);
        this.elements["cart_bttn"].on('click',this.get_cart.bind(this));
        this.elements["view_cart_btn"] = $("#view_cart_btn");
        this.elements["view_cart_btn"].on('click',this.get_cart.bind(this));
        this.elements["purchase_btn"].on('click',this._handle_buy_event.bind(this));
        this.elements["gdl_main_content"] = $(this.settings.gdl_main_content)
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
        this.wss_core.setup_wss_socket("tkt",build_url.bind(this,this.urls["ticket_stream"])(),this.websocket_onmessage.bind(this))
        this.bindEvents();

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
                // if (this.safari_new_grp.includes(this.user_agent.shortVersion)) {
                //     this.elements["gdl_play_controls"].css("top", "-120px");
                // } else {
                //     this.elements["gdl_play_controls"].css("top", "-25px");
                    this.elements["gdl_main_content"].css("top", "30px");
                    this.elements["gdl_main_content"].css("left", "0px");
                    this.elements["gdl_main_content"].css("position", "fixed");

                // }
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
        console.log("Card count set to", this.recommended_cards);
        try {
            this.elements["basic_ticket_count"][0].value = this.recommended_cards;
        } catch (DOMException) {}

    }



    bindEvents() {
        // Sport checkbox toggle
        $('.sport-checkbox').on('click', (e) => {
            const $checkbox = $(e.currentTarget);
            const sport = $checkbox.data('sport');
            const $input = $checkbox.find('input[type="checkbox"]');

            // Toggle checkbox
            $input.prop('checked', !$input.prop('checked'));

            // Toggle selected class
            $checkbox.toggleClass('selected');

            // Update selected sports set
            if ($input.prop('checked')) {
                this.selectedSports.add(sport);
            } else {
                this.selectedSports.delete(sport);
            }

            // Prevent default to avoid double-toggle
            e.preventDefault();
        });

        // Prevent checkbox click from triggering parent
        $('.sport-checkbox input[type="checkbox"]').on('click', (e) => {
            e.stopPropagation();
        });

        // Add focus effects to inputs
        $('.input-enhanced').on('focus', function() {
            $(this).parent('.input-container').addClass('focused');
        }).on('blur', function() {
            $(this).parent('.input-container').removeClass('focused');
        });

        // Form submission validation
        this.form.on('submit', (e) => {
            if (this.selectedSports.size === 0) {
                e.preventDefault();
                this.showError('Please select at least one sport.');
                return false;
            }

            if (!this.validateForm()) {
                e.preventDefault();
                this.showError('Please fill in all required fields correctly.');
                return false;
            }
        });
    }
    _card_replace(oldUuid) {
        // const oldUuid = res["data"]["old"];

        this.wss_core.old_card = oldUuid;

        const payload = this._gen_ticket_req(1, false, oldUuid);

        if (this.settings.debug) {
            console.log("Sending Payload", payload);
        }

        // 🔥 SEND
        this.wss_core.send("tkt", payload);

        // 🔥 START 10s WATCHDOG
        this.wss_core._startTicketTimeout(oldUuid, () => {
            console.warn("Retrying ticket request for", oldUuid);
            this.wss_core.send("tkt", payload);
        });

        // this._handle_cart(res);
    }


    start(event) {
        event.preventDefault();
        event.stopPropagation();
        this.active_cards = 0;
        this.elements["loading_div"].fadeIn();
        this.elements["gdl_div"].fadeOut();
        this.elements["gdl_empty_message"].hide();
        this.elements["setup_area"].hide();
        // if (this.first_run) {
        //     console.log("Showing loading modal...")
        //     LoadingModal.show();
        // }
        // } else {
        //     console.log("Not Showing loading modal...")
        // }
        // console.log(JSON.stringify(payload))
        this.elements["gdl_div"].empty();
        this.elements["gdl_div"].fadeIn();
        this.elements["loading_div"].hide();
        let payload = this.wss_core._gen_ticket_req(false,event.target)
        // console.warn("Payload",payload);
        this.wss_core.send("tkt", payload);

    }

}
