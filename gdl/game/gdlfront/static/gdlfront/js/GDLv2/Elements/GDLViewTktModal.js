import {ElementModal,ElementDiv,ElementH,ElementP,ElementButton,ElementUl,ElementLi} from "/static/minerve/js/dashboards/DashboardApp/Elements/Elements.js";

export class ElementGDLViewTktModal extends ElementModal {
    texts= {
        "title":"Ticket Details",
        "header":"Risking {0} returns {1}:",
        "subheader":"(Across {2} events)",
        "confirm":"Press the button below to confirm your ticket(s):",
        "btn_accept_label":"Accept!",
        "btn_reject_label":"Reject!",
        "btn_dismiss_label":"Close",
        "match_label": "<span class=\"pick\">{0}</span> vs {1}",
        "draw_label":"<span class=\"draw\">{0} vs {1}</span>",
    }
    accept_btn = false
    reject_btn = false
    card = false
    constructor(texts,ticket_risk, ticket_wins,event_count,legs,card) {
        super("Loading...",false,false,false,"#__modal_area");
         $.extend(this.texts,texts);
         this.title.html(this.texts["title"]);
         let tktDiv = new ElementDiv();
         this.modalBody.empty()
         this.modalDiv.attr("data-bs-backdrop","static");
         this.dialog.addClass("modal-dialog-scrollable")


         this.card = card;
         let header = new ElementH(5,this.texts["header"].replace('{0}', ticket_risk).replace('{1}', ticket_wins).replace('{2}', event_count))
         let subheader = new ElementP(this.texts["subheader"].replace('{0}', ticket_risk).replace('{1}', ticket_wins).replace('{2}', event_count))
         let list = new ElementUl({"class":"list-group list-group-flush"})
         this.modalBody.append(header.get_el()[0]);
         this.modalBody.append(subheader.get_el()[0]);
         this.modalBody.append(list.get_el()[0]);
         for (let leg in legs) {
             let legdata = legs[leg];
             let legli = new ElementLi("",{"class":"mb-2"});
             // console.warn(legdata)
             legli.dom_el.empty()
             list.dom_el.append(legli.get_el()[0]);
             let matchText = ""
             if (legdata["outcome"] == "away") {
               matchText = this.texts["match_label"].replace("{0}",legdata["away_team"]["name"]).replace("{1}", legdata["home_team"]["name"]);
             } else if (legdata["outcome"] == "home") {
               matchText = this.texts["match_label"].replace("{1}",legdata["away_team"]["name"]).replace("{0}", legdata["home_team"]["name"]);
             } else {

             }
             let matchH = new ElementH(5,matchText,{"class":"pb-0 mb-0"});
             let matchSport = new ElementP(legdata["sport_name"],{"class":"text-muted p-0 m-0"})

             let matchTime = new ElementP(legdata["match_time"],{"class":"badge rounded-pill text-bg-success mb-2"})
             legli.dom_el.append(matchH.get_el()[0]);
             legli.dom_el.append(matchSport.get_el()[0]);
             legli.dom_el.append(matchTime.get_el()[0]);
         }
         this.footer.empty();
         this.accept_btn = new ElementButton(this.texts["btn_accept_label"],{"class":"btn btn-accept"});
         this.reject_btn = new ElementButton(this.texts["btn_reject_label"],{"class":"btn btn-reject"});
         this.dismiss_btn = new ElementButton(this.texts["btn_dismiss_label"],{"class":"btn btn-success"});
         this.footer.append(this.reject_btn.get_el()[0]);
         this.footer.append(this.dismiss_btn.get_el()[0]);
         this.footer.append(this.accept_btn.get_el()[0]);
         this.accept_btn.get_el().on("click",this.card.accept_evt.bind(this.card,this));
         this.reject_btn.get_el().on("click",this.card.reject_evt.bind(this.card,this));
         this.dismiss_btn.get_el().on("click",this.bs_modal.hide.bind(this.bs_modal));
         // this.reject_btn.get_el().on("click",reject_evt);
         // this.footer.append(confirmBtn.get_el()[0]);
         // confirmBtn.get_el().on("click",confirm_evt);

         this.dialog.css({"max-width":"95%","min-width":"50%","width":"95%"})
         this.bs_modal.show();
    }
}
export default ElementGDLViewTktModal;