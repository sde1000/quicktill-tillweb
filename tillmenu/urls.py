from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name="tillmenu-index"),
    path('<int:menuid>/', menu, name="tillmenu-detail"),
]
