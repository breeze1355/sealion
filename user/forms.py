# -*-coding:utf-8-*-
__author__ = 'Nirvana'
from django import forms
from django.utils.translation import ugettext_lazy as _
from user.models import UserModel, PhotoModel


class LoginForm(forms.Form):
    """
    用户登录表单
    """
    username = forms.CharField(label="账号", max_length=128, required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': u"手机号/邮箱"}))
    password = forms.CharField(label="密码", max_length=256, required=True,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': u"密码"}))


class RegisterForm(forms.ModelForm):
    """
    用户注册表单
    """
    class Meta:
        model = UserModel
        fields = ['username', 'nick_name', 'tel', 'email', 'password', 'std_num', 'std_class']
        help_texts = {
            'nick_name': '150个字符或者更少，可包含字母，数字和仅有的@/./+/-/_符号',
            'username': '用户真实姓名',
            'email': '如xxx@163.com',
        }
        labels = {
            'email': _('电子邮箱'),
        }
        widgets = {
            'email': forms.EmailInput,
            'password':forms.PasswordInput()
        }

class ForgetForm(forms.Form):
    """
    更改密码信息提交表单
    """
    tel = forms.CharField(label="手机号码", max_length=256, required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': u"申请账号使用的手机号码"}))
    email = forms.CharField(label="电子邮箱", max_length=256, required=True,
                               widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': u"申请账号使用的电子邮箱"}))
    new_password = forms.CharField(label="新的密码", max_length=256, required=True,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': u"密码"}))


class UpdateForm(forms.ModelForm):
    """
    用户信息表单
    """
    class Meta:
        model = UserModel
        fields = ['nick_name', 'username', 'std_num', 'std_class', 'email']
        help_texts = {
            'nick_name': '必填。150个字符或者更少。可包含字母，数字和仅有的@/./+/-/_符号。',
            'username': '必填。用户真实姓名。',
        }


class ImageForm(forms.ModelForm):
    """
    用户照片表单
    """
    class Meta:
        model = PhotoModel
        fields = ['user_img']


class AvatarUploadForm(forms.Form):
    avatar = forms.ImageField(label=" ", max_length=256, required=True)
