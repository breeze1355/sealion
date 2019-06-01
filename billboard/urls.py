#-*-coding:utf-8-*- 
__author__ = 'Nirvana'
from django.conf.urls import url

from billboard import views

app_name = 'noticeApp'
urlpatterns = [
    url(r'^billboard/$', views.billboard_display, name='billboard'),
    url(r'^detail/(?P<nid>[0-9]+)/$', views.notice_detail, name='detail'),
    url(r'^insert/$', views.notice_insert, name='insert'),
    url(r'^delete/(?P<nid>[0-9]+)/$', views.billboard_delete, name='delete'),
    url(r'^update/(?P<nid>[0-9]+)/$', views.billboard_update, name='update'),
]