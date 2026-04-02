from account import api_views
from django.urls import path

urlpatterns = [
    path("login",api_views.account_login_handle,name="account_login_handle"),
]