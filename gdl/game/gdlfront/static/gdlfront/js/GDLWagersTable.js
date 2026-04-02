import {AbstractTableApp} from "/static/minerve/js/TableApp/AbstractTableApp.js";
window.GDLWagersTable = new AbstractTableApp(
    {"display_cols": ["created","application_type","type","risk","win","match","team_1","status"]},
    {"paginator_endpoint":"game/tickets/open/table/"}
)

$("#anchor").append(window.GDLWagersTable.get_container());
window.GDLWagersTable.start();