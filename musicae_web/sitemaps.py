from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from itertools import chain
from musicae_content.models import Page, Person, Publication, News

class DynamicPageSitemap(Sitemap):
    priority = 0.8
    i18n = True

    def items(self):
        return Page.objects.all()

class ModelObjSitemap(Sitemap):
    priority = 0.5
    i18n = True

    def items(self):
        objs = list(chain(
            Person.objects.all(),
            Publication.objects.all(),
            News.objects.all(),
        ))
        return objs

class StaticPageSitemap(Sitemap):
    priority = 0.9
    i18n = True

    def items(self):
        return [
            'home',
            'members_lst',
            'library_lst',
            'about',
            'research_list'
        ]

    def location(self, item):
        return reverse(item)