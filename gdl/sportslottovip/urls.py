"""
URL configuration for SportslottoEngine project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("how-to-play", views.how_to_play, name="how_to_play"),
    path("about_us", views.about_us, name="about_us"),
    path("terms_conditions", views.terms_conditions, name="terms_conditions"),
    path("faq", views.faq, name="faq"),
    path("consolation_payout_table", views.consolation_payout_table, name="consolation_payout_table"),
    path("refer_a_friend", views.refer_a_friend, name="refer_a_friend"),
    path('login-widget/', views.login_widget, name='login_widget'),
    path('hero_rows_json/', views.hero_rows_json, name='hero_rows_json'),
    path('home', views.index, name='home'),
    path('glossary', views.glossary, name='glossary'),
    path('responsible_gaming', views.responsible_gaming, name='responsible_gaming'),
    path('privacy', views.privacy, name='privacy'),
    path('differences', views.differences, name='differences'),
    path('what_is_sportslotto', views.what_is_sportslotto, name='what_is_sportslotto'),
    path('how_to_win', views.how_to_win, name='how_to_win'),
    path('login-widget/', views.login_widget_proxy, name='login_widget_proxy'),
    path("register", views.register, name="register"),




]
