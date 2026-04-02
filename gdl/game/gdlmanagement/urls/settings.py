from django.urls import path, include
from game.gdlgdlagent.views import filters as views
urlpatterns = [
    path("filters/",include("game.gdlgdlmanagement.urls.filters"),name="filters"),

]