from django.contrib import admin
from .models import *

class MemberAdmin(admin.ModelAdmin):
    ordering = ('pk',)
    list_display = ['name', 'pk']
    filter_horizontal = ['publications']

class PublicationAdmin(admin.ModelAdmin):
    ordering = ('pk',)
    list_display = ['title', 'pk', 'published']


admin.site.register(Member, MemberAdmin)
admin.site.register(Publication, PublicationAdmin)
admin.site.register(pTopic)
