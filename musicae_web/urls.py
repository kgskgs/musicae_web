from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.conf.urls.i18n import i18n_patterns
from .sitemaps import StaticPageSitemap, DynamicPageSitemap, ModelObjSitemap

sitemaps = {
    'staticPages': StaticPageSitemap(),
    'dynamicPages': DynamicPageSitemap(),
    'objects': ModelObjSitemap(),
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('captcha/', include('captcha.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
    path("ckeditor/", include("ckeditor_uploader.urls")),
]

urlpatterns += i18n_patterns(
   path('', include('musicae_content.urls')),
   path('', include('musicae_base.urls')),
   prefix_default_language=False
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)