"""tillweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from tillweb_infra import views

admin.autodiscover()
admin.site.site_header = "Till administration"

import quicktill.tillweb.urls

urlpatterns = [
    url(r'^accounts/', include([
        url(r'^login/$', auth_views.LoginView.as_view(), name="login-page"),
        url(r'^logout/$', auth_views.LogoutView.as_view(), name="logout-page"),
        url(r'^profile/$', views.userprofile, name="user-profile-page"),
        url(r'^change-password/$', views.pwchange, name="password-change-page"),
        url(r'^users/$', views.users, name="userlist"),
        url(r'^users/(?P<userid>\d+)/$', views.userdetail, name="userdetail"),
    ])),
    url(r'^admin/', admin.site.urls),
    url(r'^detail/', include(quicktill.tillweb.urls.tillurls),
        {"pubname": "detail"}),
    url(r'^$', views.frontpage, name="frontpage"),
    url(r'^locations.json$', views.locations_json, name="locations-json"),
    url(r'^location/(?P<location>[\w\- ]+).json$', views.location_json,
        name="location-json"),
    url(r'^stock.json$', views.stock_json, name="stock-json"),
    url(r'^progress.json$', views.progress_json, name="progress-json"),
    url(r'^refusals/$', views.refusals, name="refusals"),
    url(r'^display/on-tap.html$', views.display_on_tap, name="display-on-tap"),
    url(r'^display/cans-and-bottles.html$', views.display_cans_and_bottles,
        name="display-cans-and-bottles"),
    url(r'^display/wines-and-spirits.html$', views.display_wines_and_spirits,
        name="display-wines-and-spirits"),
    url(r'^display/club-mate.html$', views.display_club_mate,
        name="display-club-mate"),
    url(r'^display/soft-drinks.html$', views.display_soft_drinks,
        name="display-soft-drinks"),
    url(r'^display/progress.html$', views.display_progress,
        name="display-progress"),
]
