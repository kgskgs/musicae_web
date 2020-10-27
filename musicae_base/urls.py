from django.urls import path, re_path
from . import views
from .models import Page


urlpatterns = [
    path('contacts/', views.contact, name='contacts'),
]

extraPages = Page.objects.all()

for page in extraPages:
    target = page.link.target.replace('/', '')
    urlpatterns.append(
        re_path(target + r"\/?", views.PageView, {'link': page.link}, name=target)
    )
