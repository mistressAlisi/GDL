from django.urls import path

from .. import api_views
urlpatterns = [
    path("open/meta",api_views.open_tickets_table_meta,name="open_tickets_table_meta"),
    path("open/table/data", api_views.tickets_table_data_handle, name="rules_table_data_handle"),
    path("open/table/data/<int:page_size>", api_views.tickets_table_data_handle, name="rules_table_data_handle"),
    path("open/table/data/<int:page_size>/<int:page>", api_views.tickets_table_data_handle, name="rules_table_data_handle"),
    path("open/table/data/detail/<uuid:ruuid>",api_views.tickets_table_detail_handle,name="rules_table_detail_handle"),
    path("closed/meta",api_views.closed_tickets_table_meta,name="closed_tickets_table_meta"),
    path("closed/table/data", api_views.tickets_table_closed_data_handle, name="rules_table_data_handle"),
    path("closed/table/data/<int:page_size>", api_views.tickets_table_closed_data_handle, name="rules_table_data_handle"),
    path("closed/table/data/<int:page_size>/<int:page>", api_views.tickets_table_closed_data_handle, name="rules_table_data_handle"),
    path("open/matches/meta",api_views.open_matches_table_meta,name="open_matches_table_meta"),
    path("open/matches/table/data/",api_views.tickets_open_match_table_handle,name="tickets_open_match_table_handle"),
    path("open/matches/table/data/<int:page_size>", api_views.tickets_open_match_table_handle, name="tickets_open_match_table_handle"),
    path("open/matches/table/data/<int:page_size>/<int:page>", api_views.tickets_open_match_table_handle, name="tickets_open_match_table_handle"),
    path("open/matches/table/data/detail/<uuid:ruuid>",api_views.tickets_table_detail_handle,name="tickets_table_detail_handle"),

]

