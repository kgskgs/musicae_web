from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.conf import settings
from django.db.models import Q
from .models import *

import datetime
import shlex
import operator
from functools import reduce
import re

def mobile(request):
    """Return True if the request comes from a mobile device."""

    MOBILE_AGENT_RE=re.compile(r".*(iphone|mobile|androidtouch)",re.IGNORECASE)

    if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
        return True
    else:
        return False

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


def index(request):
    news = News.objects.all()
    if request.user_agent.is_mobile:
        news_nested = [[news[i]] for i in range(len(news))]
    else:
        news_nested = [news[i:i+3] for i in range(0, len(news), 3)]
    context = {
        "news_nested": news_nested, 
        "show_arrows": len(news_nested) > 1,
        "show_news": len(news) > 0,
        "links": Link.objects.all(),
        "dev" : request.user_agent.device.family
    }
    return render(request, 'musicae_content/index.html', context)


def PublicationList(request, internal):
    context = {}

    context['types'] = Publication.ptypes

    context['ystart'] = 1900
    context['yend'] = datetime.date.today().year
    context['yrange'] = range(context['ystart'] + 1, context['yend'] - 1)
    context['searchMax'] = 15
    context['serachRange'] = range(context['searchMax'])

    # print()

    if request.method == 'GET':
        if internal:
            context["publications"] = Publication.objects.filter(internal=True)
        else:
            context["publications"] = Publication.objects.all()

    elif request.method == 'POST':
        search_terms = request.POST

        if internal:
            pub_set = Publication.objects.filter(internal=True)
        else:
            pub_set = Publication.objects.all()

        detailed = int(search_terms['detailed'])
        # print(detailed)
        langs = [x[0] for x in settings.LANGUAGES]

        if detailed == 0:
            print(search_terms['title'])
            search_txts = shlex.split(search_terms['title'])
            pub_set = pub_set.filter(
                reduce(operator.or_,
                       (Q(**{f"title_{lang}__icontains": term})
                        for term in search_txts for lang in langs)
                       )
            ).distinct()
        else:
            if 'types' in search_terms:
                pub_set = pub_set.filter(
                    ptype__in=search_terms.getlist('types')).distinct()
            sdate, edate = int(search_terms['sdate']), int(search_terms['edate'])
            if edate >= sdate:
                pub_set = pub_set.filter(published_year__gte=sdate)
                pub_set = pub_set.filter(published_year__lte=edate)
            for i in range(detailed):
                if not search_terms[f'srch-txt-{i}']:
                    continue
                # https://stackoverflow.com/questions/4824759/django-query-using-contains-each-value-in-a-list
                # https://stackoverflow.com/questions/2932648/how-do-i-use-a-string-as-a-keyword-argument
                search_txts = shlex.split(search_terms[f'srch-txt-{i}'])

                tmp_set = Publication.objects.filter(
                    reduce(operator.or_,
                           (Q(**{f"{search_terms[f'srch-type-{i}']}_{lang}__icontains": term})
                            for term in search_txts for lang in langs)
                           )
                ).distinct()

                if search_terms[f'srch-logic-{i}'] == '1':
                    pub_set = pub_set & tmp_set
                if search_terms[f'srch-logic-{i}'] == '0':
                    pub_set = pub_set | tmp_set
                if search_terms[f'srch-logic-{i}'] == '-1':
                    pub_set = pub_set.exclude(id__in=tmp_set)

        print(pub_set.query)
        context["publications"] = pub_set

    return render(request, 'musicae_content/publication_list.html', context)


class PublicationDetail(DetailView):
    model = Publication


def seminars(request):
    #todayMonth = datetime.date.today().month

    prof_id = request.GET['prof']
    active = Seminar.objects.filter(profs__id=prof_id)
    prof = Person.objects.get(pk=prof_id)

    context = {
        "seminars": active,
        "prof": prof
    }

    return render(request, 'musicae_content/seminars.html', context)


# def seminars_archive(request):

#     context = {
#         "sems": Seminar.objects.filter(active=False),
#     }

#     return render(request, 'musicae_content/seminars_archive.html', context)


class NewsList(ListView):
    model = News


class NewsDetail(DetailView):
    model = News
