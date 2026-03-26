from urllib.parse import urlparse

from django import template
from django.templatetags.static import static
from django.urls import translate_url as django_translate_url


register = template.Library()


def _is_absolute(value):
    if not value:
        return False
    parsed = urlparse(value)
    return bool(parsed.scheme and parsed.netloc)


@register.simple_tag
def absolute_url(request, value=None):
    target = value or request.path
    if _is_absolute(target):
        return target
    return request.build_absolute_uri(target)


@register.simple_tag
def absolute_lang_url(request, lang_code, path=None):
    translated = django_translate_url(path or request.path, lang_code)
    if _is_absolute(translated):
        return translated
    return request.build_absolute_uri(translated)


@register.simple_tag
def absolute_static(request, path):
    return request.build_absolute_uri(static(path))
