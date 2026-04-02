from django.urls import path
from . import api_views
urlpatterns = [
    path("webhooks/<str:provider>/",api_views.webhook_handle,name="webhook_handle"),
    path("deposit/start", api_views.start_deposit_handle, name="deposit_start"),
    path("deposit/validate", api_views.validate_deposit, name="validate_deposit"),
    path("deposit/ionblock/status", api_views.check_ionblock_status, name="check_ionblock_status"),

    path("withdraw/validate", api_views.validate_withdrawal, name="validate_withdrawal"),
]