from django.urls import path
from . import views as content_views

urlpatterns = [
    path("", content_views.home, name="home"),

    path("members/", content_views.PersonList.as_view(), name="members_lst"),
    path("members/<int:pk>/", content_views.PersonDetail.as_view(), name="members_det"),

    path("library/", content_views.PublicationList.as_view(), {"internal": True}, name="library_lst"),

    path("publications/<int:pk>/", content_views.PublicationDetail.as_view(), name="publications_det"),

    path("about/", content_views.about, name="about"),
    path("about/<slug:slug>/", content_views.about_detail, name="about_detail"),

    path("research/", content_views.research_list, name="research_list"),
    path("research/<slug:slug>/", content_views.research_detail, name="research_detail"),
]
