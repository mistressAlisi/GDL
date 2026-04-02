from django.urls import path
from . import views
urlpatterns = [
    path("kiosk",views.kiosk_landing,name="kiosk_landing"),
    path("play",views.play_app_configure_index,name="play_app_configure_index"),
    path("play/quickpicks",views.play_app_qp_index,name="play_app_qp_index"),
    path("play/quickpicks/dynamic/<uuid:quuid>", views.play_app_qp_dynamic_index, name="play_app_qp_dynamic_index"),
    path("play/quickpicks/<str:filter>/<str:fstr>",views.play_app_qp_index,name="play_app_qp_index"),
    path("play/custom",views.play_app_cst_index,name="play_app_qp_index"),
    path("active",views.open_tickets_view_handle,name="open_tickets_view_handle"),
    path("active/table",views.open_tickets_table_view_handle,name="open_tickets_table_view_handle"),
    path("previous",views.prev_tickets_view_handle,name="prev_tickets_view_handle"),
    path("previous/table",views.previous_tickets_table_view_handle,name="previous_tickets_table_view_handle"),
    path("winners",views.winning_tickets_view_handle,name="winning_tickets_view_handle"),
    path("ticket/details/viewer/<uuid:tuuid>",views.ticket_viewer_handle,name="ticket_viewer_handle"),
    path("ticket/active/details/viewer/<uuid:payload>",views.open_tickets_details_view_handle,name="open_tickets_details_view_handle"),
]