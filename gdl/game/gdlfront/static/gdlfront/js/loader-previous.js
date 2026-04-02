import {GDLApp} from "./GDLAPP/main.js";

window.gdlapp = new GDLApp({
    "card_render_as_active":true,
    "past_tickets_mode":true,
    "viewport_area_percentage_factor_mobile":0.45,
    "viewport_area_percentage_factor_iphone":0.4,
    "pagination_size":50,
    },{
    "ticket_viewer":"/game/ticket/active/details/viewer/",
});
