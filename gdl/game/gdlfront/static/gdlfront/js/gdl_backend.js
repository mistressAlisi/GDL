import {GDLBackendApp} from "./GDLAPP/main_backend.js";

window.gdl_backend = new GDLBackendApp({},{"_paginator_endpoint":"tickets/open/table/"});
window.gdl_backend.start();