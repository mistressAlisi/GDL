from django.urls import include, path

urlpatterns = [
    path("tickets/",include("game.gdlgdlagent.urls.tickets"),name="tickets"),
    path("settings/",include("game.gdlgdlagent.urls.settings"),name="settings"),
]