# linkme/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('connect/', views.connection_view, name="connect"),

    # add more patterns as needed
]
