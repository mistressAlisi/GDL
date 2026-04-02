import {AbstractDashboardApp} from "/static/minerve/js/dashboards/DashboardApp/AbstractDashboardApp.js";
import {ElementGDLCartEntry} from "/static/gdlfront/js/GDLAPP/Elements/GDLElements.js";
import {ElementGDLConfirmTktModal} from "/static/gdlfront/js/GDLv2/Elements/GDLElements.js";

export class CartHandler extends AbstractDashboardApp {
    settings = {
        "cart_container":"#cart_container",
        "cart_offcanvas":"#offCanvasCart",
        "cart_bttn":"#gdl_buy_now",
        "purchase_btn":"#gdl_purchase_btn",
        "gdl_active_cnt":"#gdl_active_cnt",
        "modal_counter":".modal_counter",
        "modal_stake":".modal_stake",
        "modal_wins":".modal_wins",
        "save_form": "#confirm_form",
        "avail_balance": ".avail_bal",
        "bonus_balance":".bonus_balance",
        "balance":"#balance",
        "pending":".pending_bal",



    }
    urls = {
        "_api_prefix": "/api/v1/game/",
        "cart":"tickets/cart/",
        "accept_ticket":"tickets/accept/",
        "reject_ticket":"tickets/reject/",
        "ticket_viewer": "/game/ticket/details/viewer/",
        "delete_cart":"tickets/cart/empty"
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

    constructor(settings,urls) {
        super(settings,urls);
        $.extend(this.settings, settings);
        $.extend(this.urls, urls);

        this.elements["cart_container"] = $(this.settings["cart_container"])
        this.elements["gdl_active_cnt"] = $(this.settings["gdl_active_cnt"])
        this.elements["cart_offcanvas"] = $(this.settings["cart_offcanvas"])
        this.elements["cart_offc_control"] = new bootstrap.Offcanvas(this.elements["cart_offcanvas"]);
        this.elements["modal_counter"] = $(this.settings["modal_counter"])
        this.elements["modal_stake"] = $(this.settings["modal_stake"])
        this.elements["modal_wins"] = $(this.settings["modal_wins"])
        this.elements["cart_bttn"] = $(this.settings["cart_bttn"])
        this.elements["purchase_btn"] = $(this.settings["purchase_btn"]);
        this.elements["save_form"] = $(this.settings["save_form"])
        this.elements["cart_bttn"].on('click',this._show_cart.bind(this));
        this.elements["purchase_btn"].on('click',this._handle_buy_event.bind(this));
        this.elements["avail_balance"] = $(this.settings.avail_balance)
        this.elements["bonus_balance"] = $(this.settings.bonus_balance)
        this.elements["balance"] = $(this.settings.balance)
        this.elements["pending"] = $(this.settings.pending)
        this.get_cart();

    }


    _save_tickets(event) {
          this.generic_post_form(event,false,this._reset_after_save.bind(this))
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
            // console.log("CartEntry",cartEntry)
            this.elements["cart_container"].append(cartEntry.get_el());
            cartEntry.remove_btn.on("click", this._handle_reject_ticket.bind(this,false));
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
        if (this.elements["save_form"]) {
            this.elements["save_form"].submit();
        } else {
            $('#gdl_save_form').submit();
        }
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
    _handle_remove_cart(event) {
        event.stopPropagation();
        event.preventDefault();
        let btn = $(this._parent_walker(event.target,"A"));
        let tuuid = btn.data("uuid");
        let url = this.urls["reject_ticket"]+tuuid+"?ng=1";
        this.generic_post_form_v2({"form":this.form[0],"callback":this.get_cart_post_remove.bind(this),"url":url})
    }

}