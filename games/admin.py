from django.contrib import admin
from .models import Game

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['room_name', 'owner', 'current_player', 'game_state', 'created_at']
    list_filter = ['game_state', 'current_player']
    search_fields = ['room_name', 'owner__username']

# REMOVE THIS LINE: admin.site.register(Game) - DELETE THIS LINE