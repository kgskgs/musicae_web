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
   
    generic_banners = [
        'musicae_base/banners/1.jpg',
        'musicae_base/banners/2.jpg',
        'musicae_base/banners/3.jpg',
        'musicae_base/banners/4.jpg',
        'musicae_base/banners/6.webp',
        'musicae_base/banners/7.jpg',
        'musicae_base/banners/8.jpg',
        'musicae_base/banners/9.jpg',  
        'musicae_base/banners/10.jpg',
        'musicae_base/banners/11.jpg',
        'musicae_base/banners/12.jpg',
        'musicae_base/banners/13.jpg',
        'musicae_base/banners/14.jpg',
        'musicae_base/banners/15.jpg',
        'musicae_base/banners/16.jpg',
        
    ]
    
    random_path = random.choice(generic_banners)
    return static(random_path)