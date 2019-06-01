# -*-coding:utf-8-*-
from django.views.generic import RedirectView

__author__ = 'Nirvana'

from django.conf.urls import url
from django.views.static import serve

from SeaLion.settings import MEDIA_ROOT
from activity import views
from activity.views import Activity_Rec

app_name = 'activityApp'

urlpatterns = [

    url(r'^$', views.display_activity, name='index'),
    url(r'^index/$', views.display_activity, name='index'),
    url(r'^search/$', views.search_activity, name='search'),
    url(r'^create/$', views.create_activity, name='apply'),
    url(r'^delete/(?P<aid>[0-9]+)/$', views.delete_activity, name='delete'),
    url(r'^detail/(?P<aid>[0-9]+)/$', Activity_Rec.as_view(), name='detail'),
    url(r'^update/(?P<aid>[0-9]+)/$', views.update_activity, name='update'),
    url(r'^join/(?P<aid>[0-9]+)/$', views.join_activity, name='join'),
    url(r'^sign_condition/(?P<aid>[0-9]+)/$', views.sign_condition, name='sign_condition'),
    url(r'^sign/$', Activity_Rec.as_view()),
    url(r'^guest/(?P<aid>[0-9]+)/(?P<gid>[0-9]+)/$', views.guest_condition, name='guest'),

]
