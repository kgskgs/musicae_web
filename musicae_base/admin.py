from django.contrib import admin
from .models import UrlItem


class UrlItemAdmin(admin.ModelAdmin):
    fields = ['text', 'target', 'position',  'children']
    list_display = ['text', 'target', 'position']

admin.site.register(UrlItem, UrlItemAdmin)
