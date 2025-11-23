from django import forms
from .models import Game

class GameCreationForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['room_name']
        widgets = {
            'room_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter room name...'
            })
        }
    
    def clean_room_name(self):
        room_name = self.cleaned_data['room_name']
        if Game.objects.filter(room_name=room_name).exists():
            raise forms.ValidationError("A game with this room name already exists.")
        return room_name