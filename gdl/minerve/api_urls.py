from django.urls import path
from minerve.api_views import model_data

urlpatterns = [
    path("model_data/<str:model_name>",model_data.get_model_data_handle,name="get_model_data_handle"),
]
