from django.urls import path
from game.gdlgdlmanagement.views import quickpicks as views
urlpatterns = [
    path("table",views.gdl_quickpicks_config_table,name="filter_settings_view_handle"),
    # path("view/user",views.user_filter_settings_view_handle,name="user_filter_settings_view_handle")
]