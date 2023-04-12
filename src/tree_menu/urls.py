from django.shortcuts import redirect
from django.urls import path

from .views import *


urlpatterns = [
    path(r'<str:name>/', index, name='index'),
    path('', lambda request: redirect('/1/')),
]
