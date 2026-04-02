from django.urls import path

from game.gdlgdlagent.api_views import rules as api_views
urlpatterns = [
    path("filters/save",api_views.gdl_core_filters_save_handle,name="gdl_core_filters_save_handle"),
    path("filters/users/save",api_views.gdl_core_user_filters_save_handle,name="gdl_core_filters_save_handle"),
]