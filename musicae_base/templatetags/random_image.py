import random
from django import template
from django.templatetags.static import static

register = template.Library()

@register.simple_tag
def random_banner_static():
    """
    Randomly selects a banner image path from a predefined list.
    The paths must start with 'musicae_base/' to access files 
    in the app's static directory.
    """
    # Paths are relative to the STATICFILES_DIRS/static/ root.
    # 'musicae_base/' is the namespace, 'banners/' is the subfolder.
    generic_banners = [
        'musicae_base/banners/1.jpg',
        'musicae_base/banners/2.jpg',
        'musicae_base/banners/3.jpg',
        'musicae_base/banners/4.jpg',
        'musicae_base/banners/6.webp',
        # Add all your generic fallback images here
    ]
    
    # Select one path randomly and resolve it using the static file finder
    random_path = random.choice(generic_banners)
    return static(random_path)