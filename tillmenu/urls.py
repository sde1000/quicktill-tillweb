from django.conf.urls import include, url
from .views import *

urlpatterns = [
    url(r'^$', index, name="tillmenu-index"),
    url(r'^(?P<menuid>\d+)/$', menu, name="tillmenu-detail"),
]
