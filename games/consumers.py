import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import Game

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_id = f'game_{self.room_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_id,
            self.channel_name
        )
        
        await self.accept()
        
        # Send current game state to new connection
        game_data = await self.get_game_data()
        if game_data:
            await self.send(text_data=json.dumps({
                'type': 'game_state',
                'game_data': game_data
            }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_id,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'make_move':
                # Handle move logic
                position = data.get('position')
                user_id = data.get('user_id')
                
                success, message, game_data = await self.process_move(position, user_id)
                
                if success:
                    # Broadcast updated game state to room group
                    await self.channel_layer.group_send(
                        self.room_group_id,
                        {
                            'type': 'game_update',
                            'game_data': game_data,
                            'message': message
                        }
                    )
                else:
                    # Send error only to this client
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': message
                    }))
                    
            elif message_type == 'join_game':
                # Handle player joining
                user_id = data.get('user_id')
                success, message, game_data = await self.process_join(user_id)
                
                if success:
                    await self.channel_layer.group_send(
                        self.room_group_id,
                        {
                            'type': 'game_update',
                            'game_data': game_data,
                            'message': message
                        }
                    )
                else:
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': message
                    }))
                    
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON data'
            }))

    async def game_update(self, event):
        """Receive game update from room group and send to WebSocket"""
        game_data = event['game_data']
        message = event.get('message', '')
        
        await self.send(text_data=json.dumps({
            'type': 'game_update',
            'game_data': game_data,
            'message': message
        }))

    @database_sync_to_async
    def get_game_data(self):
        """Get current game data from database"""
        try:
            game = Game.objects.get(id=self.room_id)
            return game.get_game_data()
        except Game.DoesNotExist:
            return None

    @database_sync_to_async
    def process_move(self, position, user_id):
        """Process a move - game logic moved from views.py"""
        try:
            from django.contrib.auth.models import User
            
            game = Game.objects.get(id=self.room_id)
            user = User.objects.get(id=user_id)
            
            # Verify user is a player
            if not game.is_player(user):
                return False, "You are not a player in this game", None
            
            # Make the move
            success, message = game.make_move(position, user)
            
            if success:
                return True, message, game.get_game_data()
            else:
                return False, message, None
                
        except (Game.DoesNotExist, User.DoesNotExist, ValueError):
            return False, "Invalid game or user", None

    @database_sync_to_async
    def process_join(self, user_id):
        """Process player joining the game"""
        try:
            from django.contrib.auth.models import User
            
            game = Game.objects.get(id=self.room_id)
            user = User.objects.get(id=user_id)
            
            success, message = game.join_game(user)
            
            if success:
                return True, message, game.get_game_data()
            else:
                return False, message, None
                
        except (Game.DoesNotExist, User.DoesNotExist):
            return False, "Invalid game or user", None