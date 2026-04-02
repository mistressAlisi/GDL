from django.urls import path
from mycashier import api_views
urlpatterns = [
    path("cashier/limits/applications/set",api_views.set_application_limit,name="set_application_limit"),
    path("cashier/limits/losses/set",api_views.set_loss_limit,name="set_loss_limit"),
    path("cashier/lockout/execute",api_views.set_account_lockout,name="set_account_lockout"),

]
