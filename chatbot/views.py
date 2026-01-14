from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
from google import genai
from dotenv import load_dotenv
from .forms import ChatForm

load_dotenv()

def chat_view(request):
    form = ChatForm()
    return render(request, 'chatbot/chat.html', {'form': form})

@csrf_exempt
def get_ai_response(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        prompt = data.get('prompt', '')
        
        # Call API as required
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )
        
        return JsonResponse({'response': response.text})