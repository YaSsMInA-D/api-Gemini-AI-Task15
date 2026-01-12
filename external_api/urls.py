# external_api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.show_api_data, name='show_api'),
]