from django import template
from django.urls import translate_url as dj_translate_url

register = template.Library()

@register.filter
def translate_url(path, lang_code):
    """
    Use in templates like:
    {{ request.get_full_path|translate_url:'de' }}
    It returns the same URL but with the language switched.
    """
    return dj_translate_url(path, lang_code)
