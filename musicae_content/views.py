from django.shortcuts import render

def index(request):
    return render(request, "musicae_content/index.html")

def about(request):
    return render(request, "musicae_content/about.html")
