from modeltranslation.translator import register, TranslationOptions
from .models import *


@register(Member)
class NewsTranslationOptions(TranslationOptions):
    fields = ('bio', 'name', 'currentResearch', "title", "short_description",)


@register(Publication)
class NewsTranslationOptions(TranslationOptions):
    fields = ('title', 'abstract',)


@register(pTopic)
class NewsTranslationOptions(TranslationOptions):
    fields = ('text',)
