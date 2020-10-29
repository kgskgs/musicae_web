from django.contrib.sitemaps import Sitemap
from musicae_base.models import Page
from musicae_content.models import Person, Publication, News, File
from itertools import chain
from django.urls import reverse


class DynamicPageSitemap(Sitemap):
    priority = 0.8
    i18n = True

    def items(self):
        return Page.objects.all()

    def location(self, item):
        return reverse(item.link.target.replace('/', ''))


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
        return ['index', 'members_lst', 'publication_lst']

    def location(self, item):
        return reverse(item)


class FilesSitemap(Sitemap):
    priority = 0.3

    def items(self):
        files = list(chain(
            Publication.objects.filter(file__endswith=".pdf"),
            File.objects.filter(file__endswith=".pdf")
        ))
        return files

    def location(self, item):
        return item.get_file_url()
