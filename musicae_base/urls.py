# musicae_base/urls.py
from django.urls import path
from musicae_base import views as base_views          # 👈 for contact
from musicae_content import views as content_views    # 👈 for about pages

app_name = "musicae_base"

urlpatterns = [
    # Static / specific routes first
    path("contact/", base_views.contact, name="contact"),  # ✅ fixed import
    path("about/", content_views.about, name="about"),
    path("about/<slug:slug>/", content_views.about_detail, name="about_detail"),
]
