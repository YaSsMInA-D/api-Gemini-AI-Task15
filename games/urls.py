from django.urls import path
from . import views

app_name = 'games'  # Make sure this line exists

urlpatterns = [
    path('', views.game_list, name='game_list'),
    path('create/', views.create_game, name='create_game'),
    path('<int:game_id>/', views.game_detail, name='game_detail'),
    path('<int:game_id>/delete/', views.delete_game, name='delete_game'),
    path('game/<int:game_id>/join/', views.join_game, name='join_game'),
]