from django.urls import path
from . import views

urlpatterns = [
    path('members', views.PersonList.as_view(), name='members_lst'),
    path('members/<int:pk>', views.PersonDetail.as_view(), name='members_det'),
    path('seminars', views.seminars, name='seminars'),
    #path('news', views.NewsList.as_view(), name='news'),
    path('news/<int:pk>', views.NewsDetail.as_view(), name='news_det'),
    path('publications', views.PublicationList, {'internal': True}, name='publication_lst'),
    path('publications/<int:pk>', views.PublicationDetail.as_view(), name='publications_det'),
    path('library', views.PublicationList, {'internal': False}, name='library_lst'),
    path('lib', views.PublicationList, {'internal': False}, name='library_lst'),
    path('', views.index, name='index'),
    #path('seminars/archive', views.seminars_archive, name='seminars_archive'),
]
