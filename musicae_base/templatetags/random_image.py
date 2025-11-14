import random
from django import template
from django.templatetags.static import static

register = template.Library()

SESSION_KEY = 'used_banners'

GENERIC_BANNERS = [
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

def get_random_banner_path(request):
    used_banners = request.session.get(SESSION_KEY, [])
    
    available_banners = [
        banner for banner in GENERIC_BANNERS 
        if banner not in used_banners
    ]

    if not available_banners:
        available_banners = GENERIC_BANNERS
        used_banners = []
        
    random_path = random.choice(available_banners)
    
    used_banners.insert(0, random_path)
    
    history_size = 5 
    request.session[SESSION_KEY] = used_banners[:history_size]
    
    request.session.modified = True
    
    return random_path


@register.simple_tag(takes_context=True)
def random_banner_static(context):
    request = context['request']
    
    random_path = get_random_banner_path(request)
    
    return static(random_path)