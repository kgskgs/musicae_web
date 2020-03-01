from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about', views.about, name='about'),
    path('members', views.MemberList.as_view(), name='members_lst'),
    path('members/<int:pk>', views.MemberDetail.as_view(), name='members_det'),
    path('rules', views.rules, name='rules'),
    path('seminars', views.seminars, name='seminars'),
    path('news', views.NewsList.as_view(), name='news'),
]
