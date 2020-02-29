from modeltranslation.translator import register, TranslationOptions
from .models import UrlItem


@register(UrlItem)
class NewsTranslationOptions(TranslationOptions):
    fields = ('text',)
