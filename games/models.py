from django.db import models
from django.contrib.auth.models import User

class Game(models.Model):
    # Player choices
    PLAYER_X = 'X'
    PLAYER_O = 'O'
    PLAYER_CHOICES = [
        (PLAYER_X, 'Player X'),
        (PLAYER_O, 'Player O'),
    ]
    
    # Game state choices
    STATE_ACTIVE = 'active'
    STATE_WON = 'won'
    STATE_TIE = 'tie'
    STATE_CHOICES = [
        (STATE_ACTIVE, 'Active'),
        (STATE_WON, 'Won'),
        (STATE_TIE, 'Tie'),
    ]
    
    # Fields as required by Task 10 & 11
    room_name = models.CharField(max_length=100, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_owned')
    player_o = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='games_as_player_o')  # NEW: Second player
    board = models.CharField(max_length=9, default=' ' * 9)
    current_player = models.CharField(max_length=1, choices=PLAYER_CHOICES, default=PLAYER_X)
    game_state = models.CharField(max_length=10, choices=STATE_CHOICES, default=STATE_ACTIVE)
    winner = models.CharField(max_length=1, choices=PLAYER_CHOICES, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.room_name} - {self.get_game_state_display()}"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('games:game_detail', kwargs={'game_id': self.id})
    
    def is_player(self, user):
        """Check if user is a player in this game"""
        return user == self.owner or user == self.player_o
    
    def get_player_symbol(self, user):
        """Get the symbol (X/O) for a player"""
        if user == self.owner:
            return self.PLAYER_X
        elif user == self.player_o:
            return self.PLAYER_O
        return None
    
    def get_board_display(self):
        """Return board as a 3x3 list for template rendering"""
        board_list = list(self.board.ljust(9))
        return [
            board_list[0:3],
            board_list[3:6],
            board_list[6:9]
        ]
    
    def check_winner(self):
        """Check if there's a winner or tie"""
        board = self.board
        lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]              # Diagonals
        ]
        
        for line in lines:
            if board[line[0]] != ' ' and board[line[0]] == board[line[1]] == board[line[2]]:
                return board[line[0]]  # Return the winning player
        
        if ' ' not in board:
            return 'tie'
        
        return None
    
    def make_move(self, position, player):
        """Make a move at the given position - verify player"""
        if self.game_state != self.STATE_ACTIVE:
            return False, "Game is not active"
        
        # Verify it's the correct player's turn
        player_symbol = self.get_player_symbol(player)
        if player_symbol != self.current_player:
            return False, "It's not your turn"
        
        if position < 0 or position > 8:
            return False, "Invalid position"
        
        board_list = list(self.board)
        
        if board_list[position] != ' ':
            return False, "Position already taken"
        
        # Make the move
        board_list[position] = self.current_player
        self.board = ''.join(board_list)
        
        # Check for winner
        result = self.check_winner()
        if result:
            if result == 'tie':
                self.game_state = self.STATE_TIE
                self.save()
                return True, "Game ended in a tie!"
            else:
                self.game_state = self.STATE_WON
                self.winner = result
                self.save()
                return True, f"Player {result} wins!"
        else:
            # Switch to next player
            self.current_player = self.PLAYER_O if self.current_player == self.PLAYER_X else self.PLAYER_X
            self.save()
            return True, "Move made successfully"
    
    def join_game(self, user):
        """Allow a second player to join the game"""
        if self.player_o is None and user != self.owner:
            self.player_o = user
            self.save()
            return True, "Successfully joined the game"
        return False, "Cannot join this game"
    
    def get_game_data(self):
        """Return game data for WebSocket communication"""
        return {
            'id': self.id,
            'room_name': self.room_name,
            'board': self.board,
            'current_player': self.current_player,
            'game_state': self.game_state,
            'winner': self.winner,
            'owner': self.owner.username,
            'player_o': self.player_o.username if self.player_o else None,
        }