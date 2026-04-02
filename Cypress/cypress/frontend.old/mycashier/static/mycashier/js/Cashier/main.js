import {AbstractDashboardApp} from "/static/minerve/js/dashboards/DashboardApp/AbstractDashboardApp.js";
import {ElementH} from "/static/minerve/js/dashboards/DashboardApp/Elements/H.js";
import {ElementP} from "/static/minerve/js/dashboards/DashboardApp/Elements/P.js";
import {ElementA} from "/static/minerve/js/dashboards/DashboardApp/Elements/A.js";
import {ElementImg} from "/static/minerve/js/dashboards/DashboardApp/Elements/Img.js";
import {ElementDiv} from "/static/minerve/js/dashboards/DashboardApp/Elements/Div.js";

import {ElementSpan} from "/static/minerve/js/dashboards/DashboardApp/Elements/Span.js";
import {ElementInput} from "/static/minerve/js/dashboards/DashboardApp/Elements/Input.js";
import {Modal} from "/static/minerve/js/dashboards/DashboardApp/Elements/Modal.js";

export class CashierApp extends AbstractDashboardApp {

    urls = {
        "_prefix":"/cashier/",
        "_api_prefix":"/api/v1/cashier/",
        "deposit_modal":"deposit/start/",
        "withdraw_modal":"withdraw/start/",
        "launch_modal":"/cashier/deposit/modal",
        "application_limit_modal":"/cashier/limits/applications/modal/",
        "losses_limit_modal":"/cashier/limits/losses/modal/"

    }
    settings = {
        "confirm_slider":"#confirmSlider",
        "confirm_slider_label":"#confirmLabel",
        "confirm_form":"#payment_amount_form",
        "amount":"#amount",
        "total_fees":"#total_fees",
        "final_amount":"#final_amount",
        "exchange_rate":" #exchange_rate",
        "avail_balance":"#balance-link .avail_balance",
    }
    deposit_modal = false
    _handle_validate_deposit(data) {
        this.form_target.find("input,select").attr("disabled",false);
        if ("further_steps" in data) {
                if (data["further_steps"][0]["type"] === "capture_payment") {
                        this.last_modal_created_bso.hide()
                        this.last_modal_created.remove();
                        this.start_crypto_payment_capture(data["further_steps"][0]["data"]);
                }
        } else if ("status" in data) {

            if ((data["status"] == "pending")||(data["status"] == "external"))  {
                this.last_modal.modalBody.empty()
                let msg = new ElementH(4,data["title"]);
                this.last_modal.modalBody.append(msg.get_el());
                msg = new ElementP(data["body_msg"])
                this.last_modal.modalBody.append(msg.get_el());
            }

        } else {
            this.last_modal_created_bso.hide()
            this.last_modal_created.remove();
            if ("avail_balance" in data) {
                $(this.settings["avail_balance"]).text(data["avail_balance"]);
            }
        }
    }
    _validate_deposit(event) {
        this.form_target = $(event.target)

        this.generic_post_form(event,false,this._handle_validate_deposit.bind(this));
        this.form_target.find("input,select").attr("disabled","disabled");
    }
    _validate_withdrawal(event) {
        this.generic_post_form(event,false,this._handle_validate_deposit.bind(this));
    }
    start_deposit(provider) {
        try {
            this.last_modal_created_bso.hide()
        } catch (e) {}
        // Use larger modal for Majestic payment providers (apl, pyl, crd)
        let modal_width = "80%";
        if (provider === "apl" || provider === "pyl" || provider === "crd") {
            modal_width = "90%";
        }
        this.generic_ajax_modal_dialogue("Deposit Funds",this.urls["deposit_modal"]+provider,true,modal_width,true,false,"cashier-modal");
    }

    _time_delta(end_date) {
        let start = Date.now()
        let tdm = end_date-start
        let sec_delta =  Math.floor((tdm / 1000) % 60);
        let min_delta = Math.floor((tdm / (1000 * 60)) % 60);
        let hour_delta = Math.floor((tdm / (1000 * 60 * 60)) % 24);
        let day_delta = Math.floor(tdm / (1000 * 60 * 60 * 24));
        let retr = {"delta":tdm,"sec":sec_delta,"min":min_delta,"hour":hour_delta,"day":day_delta}
        return retr
    }
    _set_time_delta_str(date_ts,element) {
        $(element)[0].innerHTML = "<strong>Time Left: </strong>"+date_ts["day"]+" days, "+("0" + date_ts["hour"]).slice(-2)+":"+("0" + date_ts["min"]).slice(-2)+":"+("0" + date_ts["sec"]).slice(-2)
    }
    _update_qr_timeout() {
         let date_ts = this._time_delta(this.last_modal_created.expires);
         this._set_time_delta_str(date_ts,this.last_modal_created.timer_div.get_el()[0]);
         if (date_ts["delta"] > 0) {
             this.last_modal_created.last_timeout = setTimeout(this._update_qr_timeout.bind(this),1000)
         }
    }
    start_crypto_payment_capture(parameters) {
        let crypto_modal = new Modal("Complete your Crypto Transaction","30%")

        this.last_modal_created = crypto_modal;
        crypto_modal.modalBody.empty();
        let elm = new ElementDiv({"class":"text-bg-primary w-100"})
        let elm1 = new ElementImg(parameters["currency_logo"],{"class":"img img-fluid pt-1 pb-1 me-2","style":"max-width:40px; max-height:40px;"});
        elm.append(elm1.get_el());
        elm1 = new ElementSpan(parameters["currency_name"]+" Payment")
        elm.append(elm1.get_el());
        crypto_modal.header.prepend(elm.get_el());
        elm1 = new ElementH(6,parameters["amount"]+" "+parameters["currency_name"],{"class":"pt-2 pb-0 m-0"});
        crypto_modal.modalBody.append(elm1.get_el());
        let contents = ""
        switch (parameters["currency_name"]) {
            case 'Bitcurrency SV':
                contents= `bitcurrency:${parameters["hot_wallet"]}?sv&amount=${parameters["amount"]}`;
            case 'Tether USD (Omni)':
                contents= `bitcurrency:${parameters["hot_wallet"]}?amount=${parameters["amount"]}&req-asset=${parameters["currency_id"]}`;
            case 'BinanceCoin':
                contents= `bnb:${parameters["hot_wallet"]}?sv&amount=${parameters["amount"]}&req-asset=${parameters["currency_id"]}`;
            case 'Tether USD (ERC20)':
                contents= `ethereum:${parameters["hot_wallet"]}?value=${parameters["amount"]}&req-asset=${parameters["currency_id"].slice(parameters["currency_id"].indexOf(':') + 1)}`;
            case 'Tether USD (TRC20)':
                contents= `tron:${parameters["hot_wallet"]}?value=${parameters["amount"]}&req-asset=${parameters["currency_id"].slice(parameters["currency_id"].indexOf(':') + 1)}`;
            default:
                contents= `${parameters["currency_name"].toLowerCase().replace(/ /g, '')}:${parameters["hot_wallet"]}?amount=${parameters["amount"]}${parameters["currency_tag"] ? `&tag=${parameters["currency_tag"]}` : ""}`;
        }

        let qrc = $("<qr-code id=\"qr_cashier1\" contents=\""+contents+"\" module-color=\"var(--bs-success)\" position-ring-color=\"var(--bs-success)\" position-center-color=\"var(--bs-success)\" mask-x-to-y-ratio=\"1\" style=\"width: 230px; height: 230px; margin: 0.05em auto; background-color: var(--bs-gray-900);\"><img src=\""+parameters["currency_logo"]+"\" slot=\"icon\"/></qr-code>");
        crypto_modal.modalBody.append(qrc);
         document.getElementById('qr_cashier1').addEventListener('codeRendered', () => {
                  document.getElementById('qr_cashier1').animateQRCode('RadialRippleIn');
         });
         elm1 = new ElementDiv({"class":"d-flex justify-content-center"});
         let elm2 = new ElementInput("total_amount","text",{"verbose_name":"Total Amount:","value":parameters["amount"],"readonly":"readonly","container_class":"w-75 align-middle"});
         elm1.get_el().append(elm2.get_el());
         crypto_modal.modalBody.append(elm1.get_el());
         elm1 = new ElementDiv({"class":"d-flex justify-content-center"});
         elm2 = new ElementInput("address","text",{"verbose_name":"Payment Address:","value":parameters["hot_wallet"],"readonly":"readonly","container_class":"w-75 align-middle"});
         elm1.get_el().append(elm2.get_el());
         crypto_modal.modalBody.append(elm1.get_el());
         crypto_modal.bs_modal.show();
         elm1 = new ElementDiv({"class":"d-flex justify-content-center"});
         crypto_modal.expires =  new Date(parameters["tx_expires"])
         // console.log(date_ts);
         crypto_modal.timer_div =  new ElementH(5,"foof");
         let date_ts = this._time_delta(crypto_modal.expires);
         this._set_time_delta_str(date_ts,crypto_modal.timer_div.get_el()[0]);
         crypto_modal.footer.prepend(crypto_modal.timer_div.get_el());
         crypto_modal.modalBody.append(elm1.get_el());
         elm1 = new ElementDiv({"class":"d-flex justify-content-center"});

         elm2 = new ElementSpan("1 "+parameters["currency_symbol"]+" = "+parseFloat(parameters["rate"]).toFixed(7)+" "+parameters["original_currency"])
         elm1.get_el().append(elm2.get_el());

         elm1 = new ElementDiv({"class":"d-flex justify-content-between ps-2 pe-2 mt-1 mb-1"});
         elm2 = new ElementH(6,"Subtotal: ");
         elm1.get_el().append(elm2.get_el());
         elm2 = new ElementP(parameters["subtotal"]+" "+parameters["currency_symbol"]);
         elm1.get_el().append(elm2.get_el());
         crypto_modal.modalBody.append(elm1.get_el());

         elm1 = new ElementDiv({"class":"d-flex justify-content-between ps-2 pe-2 mt-1 mb-1"});
         elm2 = new ElementH(6,"Network Costs: ");
         elm1.get_el().append(elm2.get_el());
         elm2 = new ElementP(parameters["network"]+" "+parameters["currency_symbol"]);
         elm1.get_el().append(elm2.get_el());
         crypto_modal.modalBody.append(elm1.get_el());

         elm1 = new ElementDiv({"class":"d-flex justify-content-between ps-2 pe-2 mt-1 mb-1"});
         elm2 = new ElementH(6,"Total Amount: ");
         elm1.get_el().append(elm2.get_el());
         elm2 = new ElementH(6,parameters["amount"]+" "+parameters["currency_symbol"]);
         elm1.get_el().append(elm2.get_el());
         crypto_modal.modalBody.append(elm1.get_el());

         elm1 = new ElementDiv({"class":"d-flex justify-content-between ps-2 pe-2 mt-1 mb-1"});
         elm2 = new ElementH(6,"External Payment Provider: ");
         elm1.get_el().append(elm2.get_el());
         elm2 = new ElementA(parameters["url"],"<i class=\"fa-duotone fa-solid fa-up-right-from-square pe-2\"></i>Open in new Tab",{"target":"_blank","rel":"noopener noreferrer"});
         elm1.get_el().append(elm2.get_el());
         crypto_modal.modalBody.append(elm1.get_el());

         crypto_modal.modalBody.append(elm1.get_el());
         crypto_modal.bs_modal.show();
         this._update_qr_timeout();

    }

    start_deposit_modal(provider) {
        this.generic_ajax_modal_dialogue("Deposit Funds",this.urls["launch_modal"],false,"100%",true,false,"",false,"#__modal_area");
    }
    start_withdraw(provider) {
        this.generic_ajax_modal_dialogue("Withdraw Funds",this.urls["withdraw_modal"]+provider);
    }
    _execute_deposit() {
        console.log("Deposit Funds");
    }

    _handle_dep_change(event) {
        let amount = $(this.settings["amount"])[0].value * $(this.settings["exchange_rate"])[0].value;
        let final = amount  - (amount * $(this.settings["total_fees"])[0].value);
        $(this.settings["final_amount"])[0].value = final;
    }

    _handle_wdl_change(event) {
        let amount = $(this.settings["amount"])[0].value / $(this.settings["exchange_rate"])[0].value;
        let final = amount  - (amount * $(this.settings["total_fees"])[0].value);
        $(this.settings["final_amount"])[0].value = final;
    }
    _set_application_limit_handler(data) {
        this.last_modal_created_bso.hide()
        location.reload();

    }

    set_application_limit(event) {
        // console.warn(event);
        event.preventDefault();
        event.stopPropagation();
        this.generic_post_form_v2({"event":event,"callback":this._set_application_limit_handler.bind(this)});
    }
    start_app_limit_modal(auuid) {
        this.generic_ajax_modal_dialogue("Application Limits",this.urls["application_limit_modal"]+auuid,false);
    }


    start_loss_limit_modal(auuid) {
        this.generic_ajax_modal_dialogue("Losses Limits",this.urls["losses_limit_modal"],false);
    }

    _set_lockout_handler(data) {
        alert("The Account has been locked out.\n You will now be logged out.")


    }
    set_lockout(event) {
        // console.warn(event);
        event.preventDefault();
        event.stopPropagation();
        this.generic_post_form_v2({"event":event,"callback":this._set_lockout_handler.bind(this)});
    }


    constructor(settings,urls) {
        super(settings, urls)
        $.extend(this.settings, settings);
        $.extend(this.urls, urls);
        console.log("Starting Cashier App");

    }
}
