from django.contrib import admin
from .models import UrlItem, Page


class UrlItemAdmin(admin.ModelAdmin):
    list_display = ['text', 'target', 'position']


admin.site.register(UrlItem, UrlItemAdmin)
admin.site.register(Page)