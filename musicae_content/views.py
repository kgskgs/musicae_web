from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.conf import settings
from django.db.models import Q, Min, Max
from django.db import models

from .models import (
    Person,
    Publication,
    ResearchPage,
    ResearchSection,
)

import datetime
import shlex
import operator
from functools import reduce
import re


def mobile(request):
    """Return True if the request comes from a mobile device."""

    MOBILE_AGENT_RE = re.compile(r".*(iphone|mobile|androidtouch)", re.IGNORECASE)

    if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
        return True
    else:
        return False

def home(request):
    publications = (
        Publication.objects
        .order_by('-published_year', 'title')[:5]   # latest 5 by year
    )
    members = Person.objects.all()[:12]
    return render(request, "home.html", {
        "publications": publications,
        "members": members,
    })


class PersonList(ListView):
    model = Person
    template_name = "musicae_content/members.html"
    context_object_name = "persons"
    paginate_by = 24

    def get_queryset(self):
        # Order by position (NULLs last), then by name
        return (
            Person.objects.filter(member=True)
            .annotate(
                _pos_null=models.Case(
                    models.When(position__isnull=True, then=1),
                    default=0,
                    output_field=models.IntegerField(),
                )
            )
            .order_by("_pos_null", "position", "name")
        )

class PersonDetail(DetailView):
    model = Person
    template_name = "musicae_content/person_detail.html"  # create this template
    context_object_name = "person"

def about(request):
    page = get_object_or_404(ResearchPage, slug="about")
    sections = page.sections.all()
    return render(request, page.get_template_name(), {
        "page": page,
        "sections": sections,
    })

def about_detail(request, slug):
    # show a child page under About (or any page really)
    page = get_object_or_404(ResearchPage, slug=slug)
    sections = page.sections.all()
    return render(request, page.get_template_name(), {
        "page": page,
        "sections": sections,
    })

def research_list(request):
    """Main research landing page."""
    pages = ResearchPage.objects.all()
    return render(request, "musicae_content/research_list.html", {"pages": pages})

def research_detail(request, slug):
    """Single research page detail."""
    page = get_object_or_404(ResearchPage, slug=slug)
    sections = page.sections.all()
    return render(request, page.get_template_name(), {
        "page": page,
        "sections": sections,
    })

def PublicationList(request, internal=False):
    context = {}
    context['types'] = Publication.ptypes
    context['searchMax'] = 15
    context['serachRange'] = range(context['searchMax'])

    year_data = Publication.objects.aggregate(
        min_year=Min('published_year'),
        max_year=Max('published_year')
    )
    context['ystart'] = year_data.get('min_year') or datetime.date.today().year - 20
    context['yend'] = year_data.get('max_year') or datetime.date.today().year

    if not isinstance(context['ystart'], int):
        context['ystart'] = int(context['ystart'])
    if not isinstance(context['yend'], int):
        context['yend'] = int(context['yend'])

    context['yrange'] = range(context['ystart'] + 1, context['yend'])

    # These base names have *_bg, *_en, etc. in your model.
    LOCAL_TRANSLATED_FIELDS = ['title', 'abstract']
    langs = [x[0] for x in settings.LANGUAGES]

    # Map old form field choices to actual model fields
    FIELD_MAP = {
        'keywords__text': 'keywords_txt',   # old: related keywords model; now: text field
        'publisher__name': 'publisher_txt'  # old: related publisher model; now: text field
    }

    base_qs = Publication.objects.filter(internal=True) if internal else Publication.objects.all()

    if request.method == 'GET':
        context["publications"] = base_qs

    elif request.method == 'POST':
        search_terms = request.POST
        pub_set = base_qs

        detailed = int(search_terms.get('detailed', '0'))

        # ---------- SIMPLE SEARCH ----------
        if detailed == 0:
            simple_query = search_terms.get('q', '').strip()
            if simple_query:
                terms = shlex.split(simple_query)
                q_obj = Q()
                for term in terms:
                    # title (base)
                    q_obj |= Q(title__icontains=term)
                    # title translations
                    for lang_code in langs:
                        field = f"title_{lang_code}"
                        if hasattr(Publication, field):
                            q_obj |= Q(**{f"{field}__icontains": term})
                    # authors
                    q_obj |= Q(authors__name__icontains=term)
                    # topic (assuming Topic has `text`)
                    q_obj |= Q(topic__text__icontains=term)
                    # keywords stored as text
                    q_obj |= Q(keywords_txt__icontains=term)
                    # publisher stored as text
                    q_obj |= Q(publisher_txt__icontains=term)

                pub_set = pub_set.filter(q_obj).distinct()

        # ---------- DETAILED SEARCH ----------
        else:
            selected_types = search_terms.getlist('types')
            if selected_types:
                pub_set = pub_set.filter(ptype__in=selected_types)

            sdate = int(search_terms.get('sdate', context['ystart']))
            edate = int(search_terms.get('edate', context['yend']))

            if edate >= sdate:
                pub_set = pub_set.filter(
                    published_year__gte=sdate,
                    published_year__lte=edate
                )

            for i in range(context['searchMax']):
                search_txt = search_terms.get(f'srch-txt-{i}', '').strip()
                if not search_txt:
                    continue

                field_type = search_terms.get(f'srch-type-{i}')
                if not field_type:
                    continue

                # Normalize to real model field if needed
                field_type = FIELD_MAP.get(field_type, field_type)

                logic_op = search_terms.get(f'srch-logic-{i}', '1')
                terms = shlex.split(search_txt)

                # Build row Q
                if field_type in LOCAL_TRANSLATED_FIELDS:
                    row_q = reduce(
                        operator.or_,
                        (
                            Q(**{f"{field_type}_{lang_code}__icontains": term})
                            for term in terms
                            for lang_code in langs
                            if hasattr(Publication, f"{field_type}_{lang_code}")
                        )
                    )
                else:
                    row_q = reduce(
                        operator.or_,
                        (Q(**{f"{field_type}__icontains": term}) for term in terms)
                    )

                tmp_set = base_qs.filter(row_q).distinct()

                if logic_op == '1':          # AND
                    pub_set = pub_set & tmp_set
                elif logic_op == '0':        # OR
                    pub_set = (pub_set | tmp_set).distinct()
                elif logic_op == '-1':       # AND NOT
                    pub_set = pub_set.exclude(id__in=tmp_set.values('id'))

        context["publications"] = pub_set

    return render(request, 'musicae_content/publication_list.html', context)

class PublicationList(ListView):
    model = Publication
    template_name = 'musicae_content/publication_list.html'  # adjust if needed
    context_object_name = 'publications'

class PublicationDetail(DetailView):
    model = Publication