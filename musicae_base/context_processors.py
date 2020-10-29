from .models import UrlItem
import re
from django.conf import settings

def header_processor(request):
    menuItems = UrlItem.objects.raw(
        "SELECT * FROM musicae_base_urlitem WHERE "
        "id NOT IN (SELECT to_urlitem_id FROM musicae_base_urlitem_children) AND showOnBar = 1 "
        "ORDER BY position"
    )
    #lang_next = '/'.join(request.path.split('/')[1:])
    langs = [fr'\/{x[0]}' for x in settings.LANGUAGES]
    sub_langs = '|'.join(langs) #request.path
    lang_next = re.sub(sub_langs, '', request.path)
    context = {'menuItems': menuItems, 'showBanner': True, "lang_next": lang_next}

    return context
