from django.contrib import admin
from .models import *


class MemberAdmin(admin.ModelAdmin):
    ordering = ('position',)
    list_display = ['name', 'pk', 'position']
    filter_horizontal = ['publications']


class PublicationAdmin(admin.ModelAdmin):
    ordering = ('pk',)
    list_display = ['title', 'ptype', 'pk', 'published']


class NewsAdmin(admin.ModelAdmin):
    ordering = ('-added',)
    list_display = ['title', 'added']


admin.site.register(Member, MemberAdmin)
admin.site.register(Publication, PublicationAdmin)
admin.site.register(pTopic)
admin.site.register(Seminar)
admin.site.register(News, NewsAdmin)
admin.site.register(Publisher)
