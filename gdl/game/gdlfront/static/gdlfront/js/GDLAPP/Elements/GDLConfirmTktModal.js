import {ElementModal,ElementDiv,ElementH,ElementP,ElementButton} from "/static/minerve/js/dashboards/DashboardApp/Elements/Elements.js";

export class ElementGDLConfirmTktModal extends ElementModal {
    texts= {
        "title":"Purchase Tickets!",
        "body":" You've picked {0} tickets: Risking {1} returns {2}.",
        "confirm":"Press the button below to complete your purchase:",
        "btn_label":"Complete Purchase"
    }

    process_start() {
         this.spinner.show();
         this.confirmBtn.get_el().attr("disabled","disabled");

    }

    constructor(texts, ticket_count, ticket_risk, ticket_wins,confirm_evt) {
        super("Loading...",false,true,false,"#__modal_area");
        $.extend(this.texts,texts);
         this.title.html(this.texts["title"]);
         let tktDiv = new ElementDiv();
         this.modalBody.empty()

         this.modalBody.append(tktDiv.get_el()[0]);
         let text = new ElementP(this.texts["body"].replace('{0}', ticket_count).replace('{1}', ticket_risk).replace('{2}', ticket_wins))
         this.modalBody.append(text.get_el()[0]);
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