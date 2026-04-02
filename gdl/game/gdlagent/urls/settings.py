from django.urls import path, include
from game.gdlgdlagent.views import filters as views
urlpatterns = [
    path("filters/",include("game.gdlgdlagent.urls.filters"),name="filters")
]