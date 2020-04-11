from modeltranslation.translator import register, TranslationOptions
from .models import *


@register(Person)
class PersonTranslationOptions(TranslationOptions):
    fields = ('bio', 'name', 'currentResearch', "title", "short_description",)


@register(Publication)
class PublicationTranslationOptions(TranslationOptions):
    fields = ('title', 'abstract', 'published_place', "bib_info",)


@register(pTopic)
class pTopicTranslationOptions(TranslationOptions):
    fields = ('text',)


@register(pKeyword)
class pKeywordTranslationOptions(TranslationOptions):
    fields = ('text',)


@register(Seminar)
class SeminarTranslationOptions(TranslationOptions):
    fields = ('title', 'time', 'place', 'description',)


@register(News)
class NewsTranslationOptions(TranslationOptions):
    fields = ('title', 'content',)


@register(Publisher)
class PublisherTranslationOptions(TranslationOptions):
    fields = ('name',)
