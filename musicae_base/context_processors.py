from .models import UrlItem

def header_processor(request):
    menuItems = UrlItem.objects.raw(
        "SELECT * FROM musicae_base_urlitem WHERE id NOT IN (SELECT to_urlitem_id FROM musicae_base_urlitem_children) ORDER BY position"
        )
    context = {'menuItems': menuItems, 'showBanner': True}

    return context