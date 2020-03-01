from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import *

import datetime


def index(request):
    return render(request, "musicae_content/index.html")


def about(request):
    return render(request, "musicae_content/about.html")


def rules(request):
    return render(request, "musicae_content/rules.html")


class MemberList(ListView):
    model = Member


class MemberDetail(DetailView):
    model = Member


def seminars(request):

    today = datetime.date.today()

    context = {
        "ongoing": Seminar.objects.filter(start_date__lte=today, end_date__gte=today),
        "upcoming": Seminar.objects.filter(start_date__gt=today),
        "past": Seminar.objects.filter(end_date__lt=today),
    }

    return render(request, 'musicae_content/seminars.html', context)


class NewsList(ListView):
    model = News
