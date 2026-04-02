from django.urls import path
from game.gdlgdlagent.views import filters as views
urlpatterns = [
    path("view",views.filter_settings_view_handle,name="filter_settings_view_handle"),
    path("view/user",views.user_filter_settings_view_handle,name="user_filter_settings_view_handle")
]