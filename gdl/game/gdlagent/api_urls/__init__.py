from django.urls import include, path

urlpatterns = [
    path("tickets/",include("game.gdlgdlagent.api_urls.tickets"),name="tickets"),
    path("rules/",include("game.gdlgdlagent.api_urls.rules"),name="rules"),

]