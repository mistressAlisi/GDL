from django.urls import path
from game.gdlgdlagent import views
urlpatterns = [
    path("open",views.open_tickets_table_handle,name="open_tickets_table_handle"),
    path("closed",views.closed_tickets_table_handle,name="closed_tickets_table_handle"),
    path("open_matches",views.open_tickets_matches_table_handle,name="open_tickets_matches_table_handle"),
]