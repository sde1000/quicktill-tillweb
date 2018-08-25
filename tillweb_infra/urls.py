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
    url(r'^$', views.index, name="frontpage"),
    url(r'^refusals/$', views.refusals, name="refusals"),
]
