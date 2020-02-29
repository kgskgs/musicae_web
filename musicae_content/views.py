from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import *


def index(request):
    return render(request, "musicae_content/index.html")


def about(request):
    return render(request, "musicae_content/about.html")


class MemberList(ListView):
    model = Member


class MemberDetail(DetailView):
    model = Member
