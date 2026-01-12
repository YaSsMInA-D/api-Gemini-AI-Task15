# external_api/views.py
from django.shortcuts import render
import requests

def show_api_data(request):
    """ view to show API data on webpage"""
    url = "https://jsonplaceholder.typicode.com/posts"
    
    try:
        response = requests.get(url)
        posts = response.json()[:3]  # 3 posts
    except:
        posts = []
    
    return render(request, 'external_api/show.html', {'posts': posts})