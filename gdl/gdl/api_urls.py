
from django.urls import path, include

urlpatterns = [

    path("account/",include("account.api_urls")),
    path("cashier/",include("cashier.api_urls")),
    path("game/",include("game.gdlfront.api_urls")),

]