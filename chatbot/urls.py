from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_view, name='chat_view'),
    path('api/chat/', views.get_ai_response, name='get_ai_response'),
]