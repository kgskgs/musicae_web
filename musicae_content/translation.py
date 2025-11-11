from modeltranslation.translator import register, TranslationOptions
from .models import *


@register(Person)
class PersonTranslationOptions(TranslationOptions):
    fields = ('bio', 'name', 'currentResearch', "title", "short_description",)


@register(Publication)
class PublicationTranslationOptions(TranslationOptions):
    fields = ('title', 'abstract',)


@register(pTopic)
class pTopicTranslationOptions(TranslationOptions):
    fields = ('text',)


@register(pKeyword)
class pKeywordTranslationOptions(TranslationOptions):
    fields = ('text',)

@register(Link)
class LinkTranslationOptions(TranslationOptions):
    fields = ('text',)

@register(ResearchSection)
class ResearchSectionTR(TranslationOptions):
    fields = ('title', 'body')
