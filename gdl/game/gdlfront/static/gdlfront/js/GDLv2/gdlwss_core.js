import {AbstractDashboardApp} from "/static/minerve/js/dashboards/DashboardApp/AbstractDashboardApp.js";
import {ElementGDLConfirmTktModal,ElementGDLViewTktModal} from "./Elements/GDLElements.js";
import {WSManager} from "/static/minerve/js/core/WSManager.js";

export class GDLWSSCore extends AbstractDashboardApp {
        urls = {
        "_api_prefix": "/api/v1/",
        "submit_step1": "run_step1",
        "ticket_viewer": "/game/ticket/details/viewer/",
        "accept_ticket":"tickets/accept/",
        "reject_ticket":"tickets/reject/",
        "cart":"tickets/cart/",
        "ticket_stream":"/game/stream_tickets",
        "quickpicks_stream":"/game/stream_quickpicks",
        "delete_cart":"tickets/cart/empty"

    }

    /**
     * Derive API prefix from current URL path
     */
    _getApiPrefix() {
        const pathParts = window.location.pathname.split('/').filter(p => p);
        if (pathParts.length > 0) {
            return `/api/v1/${pathParts[0]}/`;
        }
        return '/api/v1/';
    }
    pendingTicketTimers = {};
    TICKET_TIMEOUT_MS = 10000
    _startTicketTimeout(oldUuid, resendFn) {
        this._clearTicketTimeout(oldUuid);

        this.pendingTicketTimers[oldUuid] = setTimeout(() => {
            console.warn("⏱ Ticket timeout for", oldUuid, "— resending generate");

            resendFn();

        }, this.TICKET_TIMEOUT_MS);
    }

        _clearTicketTimeout(oldUuid) {
        if (this.pendingTicketTimers[oldUuid]) {
            clearTimeout(this.pendingTicketTimers[oldUuid]);
            delete this.pendingTicketTimers[oldUuid];
        }
    }
    ruleset = {}
    settings = {
        "gdl_div": "#gdl_play_area",
        "loading_div": "#gdl_loading_message",
        "setup_area": "#gdl_setup_card",
        "flip_card_css": ".flip-card",
        // "ws_domain":"wss.sportslotto.net",
        // "ws_domain":"127.0.0.1",
        // "ws_port":"443"
        // "ws_port":"8000",
        "gdl_empty_btn":"#gdl_empty_btn"
    }

    current_cards = {}
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
    ws_manager = new WSManager(this);
    parent = false



    enqueueCartRequest(fn) {
        return new Promise((resolve, reject) => {
            this.cartQueue.push({ fn, resolve, reject });
            this._runCartQueue();
        });
    }

    async _runCartQueue() {
        if (this.cartBusy) return;

        const job = this.cartQueue.shift();
        if (!job) return;

        this.cartBusy = true;

        try {
            const result = await job.fn();
            job.resolve(result);
        } catch (err) {
            job.reject(err);
        } finally {
            this.cartBusy = false;
            this._runCartQueue();
        }
    }

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

    _handle_cart_clear_handle(res) {
        this.normalToast("Cart Emptied!")
        this.parent._hide_cart()
    }
    _clearCart(event) {
        event.preventDefault()
        event.stopPropagation()
        if (confirm("Empty Cart?")) {
            this.generic_api_getreq(this.urls["delete_cart"],false,this._handle_cart_clear_handle.bind(this))
        }
    }



    _execute_ticket_order() {
        // Set use_bonus hidden input before form submission
        let use_bonus = this.save_modal ? this.save_modal.use_bonus : false;
        $('#use_bonus_input').val(use_bonus ? 'true' : 'false');
        this.elements["save_form"].submit();
    }

    _handle_confirm(e) {
        this._execute_ticket_order();
    }

    _handle_ajax_error(res) {
        if ("cashier" in res) {
            if (res.cashier === true) {
                cashier.start_deposit_modal();
            }
        }
    }
    _set_ticket_btns(tuuid,active=true) {
        // console.warn("Set Ticket Buttons",rejctBtn,acceptBtn)
        this.last_modal.dialog.addClass("modal-dialog-scrollable");

            let rejectBtn = $("<button/>", {
                "class": "btn  reject-btn",
                "html": "<i class=\"fa-duotone fa-solid fa-circle-xmark \"></i> Reject Ticket",
                "data-bs-placement": "top",
                "data-bs-toggle": "tooltip",
                "title": "Reject Ticket!",
                "data-uuid": tuuid
            });
            if (active === true) {
                let acceptBtn = $("<button/>", {
                    "class": "btn accept-btn btn-success",
                    "html": "<i class=\"fa-duotone fa-solid  fa-circle-check \"></i> Accept",
                    "data-bs-placement": "top",
                    "data-bs-toggle": "tooltip",
                    "title": "Accept Ticket!",
                    "data-uuid": tuuid
                });
                this.last_modal.footer.prepend(acceptBtn);
                acceptBtn.on("click", this.parent._handle_accept_card.bind(this.parent, true));
            }
             let closeBtn = $("<button/>", {
                 "class": "btn btn-outline-danger",
                 "html": "Close Dialogue",
                 "title": "Close Dialogue",
             })
            this.last_modal.footer.append(closeBtn);
            this.last_modal.footer.append(rejectBtn);

            closeBtn.on("click",this.last_modal.bs_modal.hide.bind(this.last_modal.bs_modal));
            rejectBtn.on("click", this._handle_reject_ticket.bind(this, true));

        // console.warn("Set Ticket Buttons",rejctBtn,acceptBtn)
    }
     _handle_buy_event() {
        if ($("#cart_container").children().length  > 0) {
            if (this._isMobile())
            {
                this._hide_cart()
            }
            // Get bonus balance from page element or parent
            let bonus = this.parent.bonus_balance || parseFloat($('#bonus_balance')[0].value) || 0;
            this.save_modal = new ElementGDLConfirmTktModal({},this.active_cards,this.stake,this.to_win,bonus,this._handle_confirm.bind(this));
        } else {
            alert("Accept some Tickets first!")
        }
    }


    get_cart_post_remove() {
        this.normalToast("Success","Ticket Deleted!")
        this.parent.get_cart();
    }


    setup_wss_socket(stream_name,wss_url,on_message) {
      console.log("Adding Handler "+stream_name+" for WSS stream: "+wss_url);
      this.ws_manager.initStream(stream_name,wss_url,on_message)
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


  _handle_ticket_details(is_a,event) {
      let btn = null
      if (is_a == false) {
          btn = $(this._parent_walker(event.target, "BUTTON"));
      } else{
          btn = $(this._parent_walker(event.target, "A"));
      }
      let uuid = btn.data("uuid")
      this.generic_ajax_modal_dialogue("Ticket Details", this.urls["ticket_viewer"] + uuid, false, "50%", false, this._set_ticket_btns.bind(this,uuid,false), false, true)
  }
  _markCardOptimistic(uuid) {
    const $card = $("#" + uuid);

    if (!$card.length) return;

    $card
        .addClass("gdl-processing")
        .css({
            pointerEvents: "none",
        })
        .animate(
            {
                opacity: 0.25,
                transform: "scale(0.96)",
            },
            200
        );

    $card.find(".processing-overlay").fadeIn(500);
  }
  _unmarkCardOptimistic(uuid) {
    const $card = $("#" + uuid);

    if (!$card.length) return;

    $card
        .removeClass("gdl-processing")
        .css({
            pointerEvents: "",
            opacity: 1,
            transform: "",
        });

    $card.find(".gdl-processing-overlay").remove();
    }
    _update_cart_cnt(res) {
        // this.parent.elements["gdl_active_cnt"].text(res["data"]["count"]);
        var count = (this.parent.elements["gdl_active_cnt"].text()*1)+1
        this.parent.elements["gdl_active_cnt"].text(count)

    }
    _handle_accept_card(form_data, close_modal, event) {
        event.stopPropagation();
        event.preventDefault();

        let btn = $(this._parent_walker(event.target, "BUTTON"));
        btn.attr("disabled", "disabled");

        const $form = $(form_data[0]);

        // 👇 pull uuid immediately
        const tuuid = $form.find("input[name='uuid']").val();

        // 👇 optimistic fade immediately
        if (tuuid) {
            this._markCardOptimistic(tuuid);
        }

        const data = $form.serialize();
        const turl = this.urls["_api_prefix"] + this.urls["accept_ticket"];
        this.parent._card_replace(tuuid);
        this.enqueueCartRequest(() => {
            return new Promise((resolve, reject) => {
                $.ajax({
                    url: turl,
                    method: "POST",
                    data: data,
                    success: resolve,
                    error: reject,
                });
            });
        })
            .then(resolve => {
                this._update_cart_cnt(resolve);
            })
            .catch(err => {
                console.error("Cart error", err);

                // ❌ rollback optimistic UI
                if (tuuid) {
                    this._unmarkCardOptimistic(tuuid);
                }

                btn.removeAttr("disabled");
            });
    }

  _handle_reject_card(close_modal,event) {
        event.stopPropagation();
        event.preventDefault();
        let btn = $(this._parent_walker(event.target,"BUTTON"));
        let tuuid = btn.data("uuid");
        // console.log("TUUID",tuuid)
        this.old_card = tuuid;
        if (close_modal) {
            this.last_modal.bs_modal.hide()
        }
        let payload = this._gen_ticket_req(1,this.parent.form[0])
        // this.wsw.send(JSON.stringify(payload));
        this.ws_manager.send("tkt", payload);


    }

   _handle_reject_ticket(close_modal,event) {
        event.stopPropagation();
        event.preventDefault();
        // console.log("HRT",close_modal,event)
        let btn = $(event.target)
        let tuuid = btn.data("uuid");


        let url = this.urls["reject_ticket"]+tuuid+"?ng=1";
        this.generic_api_getreq(url,false,this.get_cart_post_remove.bind(this))
        if (close_modal) {
            this.last_modal.bs_modal.hide()
        }

   }



  _render_ticket_details(data,card,event) {

      let dataModal = new ElementGDLViewTktModal({},data.risk,data.wins,data.events,data.legs,card);
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
      // console.log("payload",payload)
      return payload;
    }

    send(name,request) {
      this.ws_manager.send(name,request)
    }



    constructor(settings,urls,parent) {
        super(settings, urls)
        this.parent = parent
        $.extend(this.settings, settings);
        $.extend(this.urls, urls);
        // Set dynamic API prefix based on current URL
        this.urls["_api_prefix"] = this._getApiPrefix();
        console.log("Starting WSS Core...",this.parent);
        this.on_ajax_error_func = this._handle_ajax_error
        $(this.settings["gdl_empty_btn"]).on('click',this._clearCart.bind(this))
        this.cartQueue = [];
        this.cartBusy = false;

    }

}