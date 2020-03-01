from modeltranslation.translator import register, TranslationOptions
from .models import *


@register(Member)
class MemberTranslationOptions(TranslationOptions):
    fields = ('bio', 'name', 'currentResearch', "title", "short_description",)


@register(Publication)
class PublicationTranslationOptions(TranslationOptions):
    fields = ('title', 'abstract',)


@register(pTopic)
class pTopicTranslationOptions(TranslationOptions):
    fields = ('text',)


@register(Seminar)
class SeminarTranslationOptions(TranslationOptions):
    fields = ('title', 'time_and_place', 'description',)


@register(News)
class NewsTranslationOptions(TranslationOptions):
    fields = ('title', 'content',)
