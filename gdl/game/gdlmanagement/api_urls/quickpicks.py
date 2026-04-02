from django.urls import path

from game.gdlgdlmanagement.api_views import rules as views
urlpatterns = [
    path("table/meta",views.gdl_quickpicks_settings_table_meta_handle),
    path("table/data",views.gdl_quickpicks_settings_table_data_handle),
    path("table/data/",views.gdl_quickpicks_settings_table_data_handle),
    path("table/data/<int:page_size>",views.gdl_quickpicks_settings_table_data_handle),
    path("table/data/<int:page_size>/<int:page>/",views.gdl_quickpicks_settings_table_data_handle),
    # path("table/data/detail/<uuid:tuuid>", views.gdl_quickpicks_settings_table_detail_handle),
    path("table/data/detail/load/<uuid:ruuid>", views.gdl_quickpicks_edit_handle),
    path("table/data/save", views.gdl_quickpicks_save_handle),
    path("create",views.gdl_create_quickpicks_entry)

]