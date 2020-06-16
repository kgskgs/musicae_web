from django.urls import path, re_path
from . import views
from .models import Page


#index_item = Page.objects.get(link__target='/')

urlpatterns = [
#    path('', views.PageView, {'link': index_item}, name='index'),
    path('contact/', views.contact, name='contact'),
]

#extraPages = Page.objects.exclude(link=index_item)
#
#for page in extraPages:
#    target = page.link.target.replace('/', '')
#    urlpatterns.append(
#        re_path(target+r"\/?", views.PageView, {'link': page.link}, name=target)
#    )
