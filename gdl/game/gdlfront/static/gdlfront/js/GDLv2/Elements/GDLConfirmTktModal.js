import {ElementModal,ElementDiv,ElementH,ElementP,ElementButton} from "/static/minerve/js/dashboards/DashboardApp/Elements/Elements.js";

export class ElementGDLConfirmTktModal extends ElementModal {
    texts= {
        "title":"Purchase Tickets!",
        "body":" You've picked {0} tickets: Risking {1} returns {2}.",
        "confirm":"Press the button below to complete your purchase:",
        "btn_label":"Complete Purchase",
        "bonus_label":"Use Free Play Balance"
    }

    useBonusCheckbox = null;
    bonus_balance = 0;

    process_start() {
         this.spinner.show();
         this.confirmBtn.get_el().attr("disabled","disabled");
    }

    get use_bonus() {
       if (this.bonus_balance > 0) {
           this.useBonusCheckbox = $('#use_bonus_toggle');
           return this.useBonusCheckbox[0].checked
       } else {
           return false;
       }
    }

    constructor(texts, ticket_count, ticket_risk, ticket_wins, bonus_balance, confirm_evt) {
        super("Loading...",false,true,false,"#__modal_area");
        $.extend(this.texts,texts);
        this.bonus_balance = bonus_balance || 0;

        this.title.html(this.texts["title"]);
        let tktDiv = new ElementDiv();
        this.modalBody.empty()

        this.modalBody.append(tktDiv.get_el()[0]);
        let text = new ElementP(this.texts["body"].replace('{0}', ticket_count).replace('{1}', ticket_risk).replace('{2}', ticket_wins))
        this.modalBody.append(text.get_el()[0]);

        // Add bonus toggle if bonus available
        if (this.bonus_balance > 0) {
            let bonusDiv = $('<div class="bonus-toggle-section my-3 p-3 border rounded" style="background-color: var(--bs-success-bg-subtle, #d1e7dd); color: var(--bs-success-text-emphasis, #0a3622);"></div>');
            let bonusCheck = $('<div class="form-check form-switch">' +
                '<input class="form-check-input" type="checkbox" id="use_bonus_toggle" style="cursor: pointer;">' +
                '<label class="form-check-label" for="use_bonus_toggle" style="cursor: pointer; color: inherit;">' +
                '<i class="fa-solid fa-gift me-2 text-success"></i>' +
                this.texts["bonus_label"] + ': <strong>$' + this.bonus_balance.toFixed(2) + '</strong>' +
                '</label></div>');
            bonusDiv.append(bonusCheck);
            this.modalBody.append(bonusDiv[0]);

        }

        let confirmHead = new ElementH(6,this.texts["confirm"]);
        this.modalBody.append(confirmHead.get_el()[0]);
        this.confirmBtn = new ElementButton(this.texts["btn_label"],{"class":"btn btn-primary"});
        this.spinner = $("<i class=\"fa-sharp fa-solid fa-spinner-third fa-spin\" id='spinner_id'></i>")
        this.confirmBtn.get_el().prepend(this.spinner);
        this.footer.empty();
        this.spinner.hide();
        this.footer.append(this.confirmBtn.get_el()[0]);
        this.confirmBtn.get_el().on("click",confirm_evt);
        this.confirmBtn.get_el().on("click",this.process_start.bind(this));
        this.bs_modal.show();
    }
}
export default ElementGDLConfirmTktModal;