# -*-coding:utf-8-*-
__author__ = 'Nirvana'

from django.conf.urls import url
from django.urls import re_path

from user import views

app_name = 'userApp'
urlpatterns = [
    url(r'^login/$', views.userlogin, name='login'),
    url(r'^register/$', views.register, name='register'),
    url(r'^forget/$', views.forget, name='forget'),
    url(r'^logout/$', views.userlogout, name='logout'),
    url(r'^created/$', views.created_activities, name='created'),
    url(r'^joined/$', views.joined_activities, name='joined'),
    url(r'^update//$', views.updateProfile, name='update'),
    url(r'^upload/$', views.upload_image, name='upload'),
    url(r'^avatar/$', views.avatar_upload, name='avatar'),
    re_path(r'^profile/$', views.userProfile, name='profile'),

]
