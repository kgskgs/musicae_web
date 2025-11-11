from .models import UrlItem
from musicae_content.models import ResearchPage 
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

def research_pages_processor(request):
    return {"research_pages": ResearchPage.objects.all()}

def about_pages_processor(request):
    # local import avoids app-registry order issues
    from musicae_content.models import ResearchPage

    about_root = ResearchPage.objects.filter(slug="about").first()
    children = []
    if about_root:
        children = list(
            ResearchPage.objects.filter(parent=about_root, show_in_menu=True)
            .order_by("menu_order", "name")
        )
    return {
        "about_root_page": about_root,
        "about_children": children,
    }