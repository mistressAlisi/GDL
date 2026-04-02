import {GDLApp} from "./GDLAPP/main.js";

window.gdlapp = new GDLApp({
    "past_tickets_mode":true,
    "card_render_as_active":true,
    "viewport_area_percentage_factor_mobile":0.45,
    "viewport_area_percentage_factor_iphone":0.4,
    },{
    "ticket_viewer":"/game/ticket/active/details/viewer/",
});
