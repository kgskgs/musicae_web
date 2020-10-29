from modeltranslation.translator import register, TranslationOptions
from .models import *


@register(UrlItem)
class NewsTranslationOptions(TranslationOptions):
    fields = ('text',)


@register(Page)
class PageTranslationOptions(TranslationOptions):
    fields = ('content', 'description', 'keywords')
