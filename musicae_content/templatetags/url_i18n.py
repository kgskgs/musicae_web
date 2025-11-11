from django import template
from django.urls import translate_url as dj_translate_url

register = template.Library()

@register.filter
def translate_url(path, lang_code):
    return dj_translate_url(path, lang_code)
