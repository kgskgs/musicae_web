"""musicae_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from .sitemaps import *
from django.conf.urls.i18n import i18n_patterns

sitemaps = {
    'staticPages': StaticPageSitemap(),
    'dynamicPages': DynamicPageSitemap(),
    'objects': ModelObjSitemap(),
    'files': FilesSitemap()
}

urlpatterns = [
    #path('', include('musicae_content.urls')),
    #path('', include('musicae_base.urls')),
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('captcha/', include('captcha.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
]


urlpatterns += i18n_patterns(
   path('', include('musicae_content.urls')),
   path('', include('musicae_base.urls')),

   prefix_default_language=False
)



urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
