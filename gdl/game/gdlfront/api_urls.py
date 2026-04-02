from django.urls import path

from . import api_views
urlpatterns = [

    path("generate/tickets", api_views.play_app_generate_tickets, name="play_app_generate_tickets"),
    path("generate/quickpick", api_views.play_app_get_quick_picks, name="play_app_get_quick_picks"),
    path("tickets/confirm",api_views.play_app_confirm_tickets,name="play_app_confirm_tickets"),
    path("tickets/open",api_views.get_open_tickets_handle,name="get_open_tickets_handle"),
    path("tickets/open/table/",api_views.get_open_tickets_table_handle,name="get_open_tickets_handle"),
    path("tickets/open/table/<int:page_size>",api_views.get_open_tickets_table_handle,name="get_open_tickets_handle"),
    path("tickets/open/table/<int:page_size>/<int:page>",api_views.get_open_tickets_table_handle,name="get_open_tickets_handle"),
    path("tickets/table",api_views.get_open_tickets_handle,name="get_open_tickets_handle"),
    path("tickets/winners",api_views.get_winning_tickets_handle,name="get_winning_tickets_handle"),
    path("tickets/previous", api_views.get_previous_tickets_handle, name="get_historic_tickets_handle"),
    path("tickets/previous/table/", api_views.get_previous_tickets_table_handle, name="get_previous_tickets_handle"),
    path("tickets/previous/table/<int:page_size>", api_views.get_previous_tickets_table_handle, name="get_previous_tickets_handle"),
    path("tickets/previous/table/<int:page_size>/<int:page>", api_views.get_previous_tickets_table_handle,
         name="get_previous_tickets_handle"),
    path("tickets/accept/",api_views.accept_ticket,name="accept_ticket"),
    path("tickets/reject/<uuid:tuuid>",api_views.reject_ticket,name="reject_ticket"),
    path("tickets/cart/",api_views.get_ticket_cart,name="ticket_cart"),
    path("tickets/cart/empty",api_views.empty_cart,name="empty_cart"),
    path("tickets/previous/table/<str:start>/<str:end>/<str:type>", api_views.get_previous_tickets_table_handle_ranged, name="get_previous_tickets_handle"),
    path("tickets/previous/table/<str:start>/<str:end>/<str:type>/<int:page_size>", api_views.get_previous_tickets_table_handle_ranged,
         name="get_previous_tickets_handle"),
    path("tickets/previous/table/<str:start>/<str:end>/<str:type>/<int:page_size>/<int:page>", api_views.get_previous_tickets_table_handle_ranged),
    path("get/curr_balance",api_views.get_acct_balances,name="get_acct_balances"),
    path("get/winners",api_views.get_winners_data_handle,name="get_winners_data_handle"),
]