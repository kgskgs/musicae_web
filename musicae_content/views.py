from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import *

import datetime
from calendar import monthrange


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


def PublicationList(request):
    context = {}

    context['authors'] = Member.objects.raw(
        "SELECT * from musicae_content_member WHERE id in (SELECT member_id FROM musicae_content_member_publications)")
    context['topics'] = pTopic.objects.raw(
        "SELECT * from musicae_content_ptopic WHERE id in (SELECT ptopic_id FROM musicae_content_publication_topics)")
    context['types'] = Publication.ptypes

    if request.method == 'GET':
        context["publications"] = Publication.objects.all

    elif request.method == 'POST':
        search_terms = request.POST

        pub_set = Publication.objects.filter(
            title__icontains=search_terms['title'])
        if search_terms['author'] and search_terms['author'] != '-1':
            pub_set = pub_set.filter(member__id=search_terms['author'])
        if 'topics' in search_terms:
            pub_set = pub_set.filter(
                topics__in=search_terms.getlist('topics')).distinct()
        if 'types' in search_terms:
            pub_set = pub_set.filter(
                ptype__in=search_terms.getlist('types')).distinct()

        sdate = datetime.date(1900, 1, 1)
        edate = datetime.date.today()
        if 'p_start' in search_terms and search_terms['p_start']:
            sdate = datetime.datetime.strptime(search_terms['p_start'], "%m.%Y")
        if 'p_end' in search_terms and search_terms['p_end']:
            edate = datetime.datetime.strptime(search_terms['p_end'], "%m.%Y")
            maxDay = monthrange(edate.year, edate.month)[1]
            edate = edate.replace(day=maxDay)
        if sdate and edate:
            if edate >= sdate:
                pub_set = pub_set.filter(published__gte=sdate)
                pub_set = pub_set.filter(published__lte=edate)

        context["publications"] = pub_set

    return render(request, 'musicae_content/publication_list.html', context)


class PublicationDetail(DetailView):
    model = Publication


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
