from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import *

import datetime
import shlex
import operator
from functools import reduce
from django.db.models import Q


def index(request):
    return render(request, "musicae_content/index.html")


def about(request):
    return render(request, "musicae_content/about.html")


def rules(request):
    return render(request, "musicae_content/rules.html")


class PersonList(ListView):
    model = Person

    def get_queryset(self):
        queryset = Person.objects.filter(member=True)
        return queryset


class PersonDetail(DetailView):
    model = Person

    def get_queryset(self):
        queryset = Person.objects.filter(member=True)
        return queryset


def PublicationList(request, internal):
    context = {}

    context['types'] = Publication.ptypes

    context['ystart'] = 1900
    context['yend'] = datetime.date.today().year
    context['yrange'] = range(context['ystart'] + 1, context['yend'] - 1)
    context['searchMax'] = 15
    context['serachRange'] = range(context['searchMax'])

    if request.method == 'GET':
        context["publications"] = Publication.objects.filter(internal=internal)

    elif request.method == 'POST':
        search_terms = request.POST

        pub_set = Publication.objects.filter(internal=internal)

        detailed = int(search_terms['detailed'])
        print(detailed)

        if detailed == 0:
            print(search_terms['title'])
            pub_set = pub_set.filter(
                title__icontains=search_terms['title'])
        else:
            if 'types' in search_terms:
                pub_set = pub_set.filter(
                    ptype__in=search_terms.getlist('types')).distinct()
            sdate, edate = int(search_terms['sdate']), int(search_terms['edate'])
            if edate >= sdate:
                pub_set = pub_set.filter(published_year__gte=sdate)
                pub_set = pub_set.filter(published_year__lte=edate)

            for s in range(detailed):
                if not search_terms[f'srch-txt-{s}']:
                    continue
                # https://stackoverflow.com/questions/4824759/django-query-using-contains-each-value-in-a-list
                # https://stackoverflow.com/questions/2932648/how-do-i-use-a-string-as-a-keyword-argument
                search_txts = shlex.split(search_terms[f'srch-txt-{s}'])

                tmp_set = Publication.objects.filter(
                    reduce(operator.or_,
                           (Q(**{f"{search_terms[f'srch-type-{s}']}__icontains": x}) for x in search_txts))
                ).distinct()

                if search_terms[f'srch-logic-{s}'] == '1':
                    pub_set = pub_set & tmp_set
                if search_terms[f'srch-logic-{s}'] == '0':
                    pub_set = pub_set | tmp_set
                if search_terms[f'srch-logic-{s}'] == '-1':
                    pub_set = pub_set.exclude(id__in=tmp_set)

        print(pub_set.query)
        context["publications"] = pub_set

    return render(request, 'musicae_content/publication_list.html', context)


class PublicationDetail(DetailView):
    model = Publication


def seminars(request):
    todayMonth = datetime.date.today().month

    fall = [8, 9, 10, 11, 12, 1]

    sem = -1 if todayMonth in fall else 1

    active = Seminar.objects.filter(active=True)

    context = {
        "ongoing": active.filter(semester=sem),
        "upcoming": active.filter(semester=-sem),
    }

    return render(request, 'musicae_content/seminars.html', context)


def seminars_archive(request):

    context = {
        "sems": Seminar.objects.filter(active=False),
    }

    return render(request, 'musicae_content/seminars_archive.html', context)


class NewsList(ListView):
    model = News


class NewsDetail(DetailView):
    model = News
