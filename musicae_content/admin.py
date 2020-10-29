from django.contrib import admin
from .models import *


class PersonAdmin(admin.ModelAdmin):
    ordering = ('position',)
    list_display = ['name', 'pk', 'position', 'member']
    #filter_horizontal = ['publications']


class PublicationAdmin(admin.ModelAdmin):
    ordering = ('pk',)
    save_as = True
    list_display = ['title', 'internal', 'ptype', 'published_year', 'pk']


class NewsAdmin(admin.ModelAdmin):
    ordering = ('-added',)
    list_display = ['title', 'ntype', 'added']



class SeminarsAdmin(admin.ModelAdmin):
    list_display = ['title', 'semester', 'active']

class LinkAdmin(admin.ModelAdmin):
    list_display = ['url']

class FileAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_file_url']

admin.site.register(Person, PersonAdmin)
admin.site.register(Publication, PublicationAdmin)
admin.site.register(pTopic)
admin.site.register(pKeyword)
admin.site.register(Seminar, SeminarsAdmin)
admin.site.register(News, NewsAdmin)
admin.site.register(Publisher)
admin.site.register(Journal)
admin.site.register(Link, LinkAdmin)
admin.site.register(File, FileAdmin)
