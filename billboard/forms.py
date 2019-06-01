#-*-coding:utf-8-*- 
__author__ = 'Nirvana'
from django import forms
from billboard.models import Notice


class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'content']

class UpdateForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'content']