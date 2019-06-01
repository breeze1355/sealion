from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.cache import cache_control

import os
import hashlib
import face_recognition as fr
import numpy as np
from datetime import datetime

from SeaLion import settings
from activity.models import Activity
from activity.utils import Pagintor
from user import forms
from user.forms import ImageForm, AvatarUploadForm, UpdateForm, ForgetForm, LoginForm
from user.models import UserModel, PhotoModel, UserAvatar


# Create your views here.
def userlogin(request):
    """
    用户登录
    :param request:POST
    :return:登录成功返回主页  失败返回提示信息
    """
    if request.session.get('is_login', None):
        return redirect("/index/")
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            if '@' not in username:
                # 不是邮箱 则认为使用手机号登录
                username = hash_code(username)
            password = login_form.cleaned_data['password']
            password = hash_code(password)
            try:
                user = authenticate(username=username, password=password)
                if user and user.is_active:
                    login(request, user)
                    if 'error' in request.session:
                        # 删除之前缓存的登录失败提示信息
                        del request.session['login_error']
                    request.session['is_login'] = True
                    request.session['nick_name'] = user.nick_name
                    return HttpResponseRedirect(reverse('activityApp:index', ))
                login_error = '用户名密码错误'
            except:
                login_error = '用户不存在'
            request.session['login_error'] = login_error
            forget_form = ForgetForm()
        return render(request, 'login/login.html', locals())

    login_form = LoginForm()
    forget_form = ForgetForm()
    return render(request, 'login/login.html', locals())


def register(request):
    """
    用户注册
    :param request:POST
    :return: 注册成功返回登陆页面 注册失败返回提示信息
    """
    if request.method == 'POST':
        register_form = forms.RegisterForm(request.POST)
        register_error = "请检查填写的内容！"
        if register_form.is_valid():
            nick_name = register_form.cleaned_data['nick_name']
            password = register_form.cleaned_data['password']
            tel = register_form.cleaned_data['tel']
            email = register_form.cleaned_data['email']
            username = register_form.cleaned_data['username']
            std_num = register_form.cleaned_data['std_num']
            std_class = register_form.cleaned_data['std_class']
            same_tel = UserModel.objects.filter(tel=tel)
            nick_name_only = UserModel.objects.filter(nick_name=nick_name)
            if same_tel:
                register_error = '该手机号已被注册，请使用别的手机号码！'
                return render(request, 'login/register.html', locals())
            if nick_name_only:
                register_error = '此昵称已存在！'
                return render(request, 'login/register.html', locals())
            new_user = UserModel()
            new_user.nick_name = nick_name
            new_user.username = username
            new_user.password = hash_code(password)
            new_user.tel = hash_code(tel)
            new_user.email = email
            new_user.std_num = std_num
            new_user.std_class = std_class
            new_user.save()
            avatar = UserAvatar(user=new_user)
            avatar.save()
            return redirect("userApp:login")
        else:
            return render(request, 'login/register.html', locals())
    register_form = forms.RegisterForm()
    return render(request, 'login/register.html', locals())


def forget(request):
    """
    忘记密码
    :param request:
    :return:
    """
    if request.method == 'POST':
        forget_form = forms.ForgetForm(request.POST)
        if forget_form.is_valid():
            tel = forget_form.cleaned_data['tel']
            email = forget_form.cleaned_data['email']
            new_password = forget_form.cleaned_data['new_password']
            try:
                user = UserModel.objects.get(Q(tel=tel) | Q(email=email))
                if not user.is_staff:
                    user.password = hash_code(new_password)
                    user.save()
            except:
                request.session['login_error'] = "验证信息错误，请检查输入的手机号或电子邮箱是否正确"
    login_form = LoginForm()
    return render(request, 'login/login.html', locals())



def userlogout(request):
    """
    退出登录
    :param request:
    :return: 活动主页
    """
    if not request.session.get('is_login', None):
        return HttpResponseRedirect(reverse('activityApp:index', ))
    request.session.flush()     # 清空缓存
    logout(request)
    return HttpResponseRedirect(reverse('activityApp:index', ))


@login_required(login_url=settings.LOGIN_URL)
@cache_control(must_revalidate=True, max_age=3600)
def userProfile(request):
    """
    个人主页
    :param request: GET
    :return: 个人主页页面
    """
    update_form = UpdateForm(instance=request.user)
    image_form = ImageForm()
    avatar_form = AvatarUploadForm()
    updateInfoMessage = request.session.get('updateInfoMessage')
    if 'updateInfoMessage' in request.session:
        del request.session['updateInfoMessage']
    return render(request, 'user/personal.html', locals())

@login_required(login_url=settings.LOGIN_URL)
def avatar_upload(request):
    """
    用户头像上传
    :param request:POST
    :return:
    """
    user = request.user
    user_profile = get_object_or_404(UserAvatar, user=user)

    if request.method == "POST":
        a_form = AvatarUploadForm(request.POST, request.FILES)
        if a_form.is_valid():
            current_avatar = user_profile.avatar
            if not current_avatar == os.path.join("avatar", "default.png"):
                current_avatar_path = os.path.join("media", "avatar" ,str(user.id), os.path.basename(current_avatar.url))
                os.remove(current_avatar_path)

            avatar = a_form.cleaned_data['avatar']
            user_profile.avatar = avatar # 将图片路径修改到当前数据库
            user_profile.save()
            return HttpResponseRedirect(reverse('userApp:profile'))

        request.session['updateInfoMessage'] = "头像上传失败"
    return HttpResponseRedirect(reverse('userApp:profile'))

@login_required(login_url=settings.LOGIN_URL)
def updateProfile(request):
    """
    修改个人信息
    :param request:POST
    :return:个人主页
    """
    if request.method == 'POST':
        updateInfoMessage = '修改信息已存在，请重试'
        user = request.user
        update_form = UpdateForm(instance=user, data=request.POST, files=request.FILES)
        if update_form.is_valid():
            update_form.save(commit=False)
            try:
                nick_name = update_form.cleaned_data['nick_name']
                std_num = update_form.cleaned_data['std_num']
                if not nick_name == user.nick_name:
                    nick_name_same = UserModel.objects.filter(nick_name=nick_name)
                    if nick_name_same:
                        updateInfoMessage = '修改信息已存在，无法更新'
                if not std_num == user.std_num:
                    std_num_same = UserModel.objects.filter(std_num=std_num)
                    if std_num_same:
                        updateInfoMessage = '修改信息已存在，无法更新'
                else:
                    updateInfoMessage = '保存成功'
                    update_form.save()
            except:
                updateInfoMessage = '保存失败请重试'

        request.session['updateInfoMessage'] = updateInfoMessage
    return HttpResponseRedirect(reverse('userApp:profile', ))


@login_required(login_url=settings.LOGIN_URL)
def upload_image(request):
    """
    照片上传处理
    :param request:POST
    :return: 个人主页
    """
    if request.method == 'POST':
        new_photo = PhotoModel(user=request.user)
        image_form = ImageForm(instance=new_photo, data=request.POST, files=request.FILES)
        if image_form.is_valid():
            image_form = image_form.save(commit=False)
            try:
                img_code = fr.face_encodings(
                    fr.load_image_file(image_form.user_img))    # 加载文件、编码
                save_path = os.path.join("media", "user_image_code", str(request.user.id))  # 文件保存路径
                if not os.path.exists(save_path):
                    # 不存在则创建
                    os.mkdir(save_path)
                file_path = os.path.join(save_path,datetime.now().strftime('%Y%m%d_%H%M%S'))
                np.save(file_path, img_code[0])
                image_form.user_img = None
                image_form.img_code = file_path
                image_form.save()
                request.session['uploaded'] = True
                if 'nav_msg' in request.session:
                    del request.session['nav_msg']
                return HttpResponseRedirect(reverse('userApp:profile'))
            except:
                request.session['updateInfoMessage'] = "照片上传失败"
        return HttpResponseRedirect(reverse('userApp:profile'))


@login_required(login_url=settings.LOGIN_URL)
@cache_control(must_revalidate=True, max_age=3600)
def created_activities(request):
    """
    获取我创建的所有活动的列表
    :param request:GET
    :return:
    """
    if request.method == 'GET':
        ac_list = Activity.objects.filter(creator=request.user)
        my_activities_list = Pagintor(request=request, ac_list=ac_list,acount=4)
        return render(request, 'user/myActivity.html', locals())
    return render(request, 'user/myActivity.html')


@login_required(login_url=settings.LOGIN_URL)
@cache_control(must_revalidate=True, max_age=3600)
def joined_activities(request):
    """
    获取我加入的所有活动的列表
    :param request:GET
    :return:
    """
    if request.method == 'GET':
        joined_list = []
        ac_list = Activity.objects.all()
        for ac in ac_list:
            guest_list = ac.guests.all()
            if request.user in guest_list:
                joined_list.append(ac)
        joined_activities_list = Pagintor(request=request, ac_list=joined_list, acount=4)
        return render(request, 'user/joined.html', locals())
    return render(request, 'user/joined.html')


class CustomBackend(ModelBackend):
    """
    自定义登录认证
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 验证用户名、手机号或邮箱
            user = UserModel.objects.get(Q(username=username) | Q(tel=username) | Q(email=username))
            if user.check_password(password) or user.password == password:
                return user
        except Exception as e:
            return e


def hash_code(s, salt='helloworld'):
    """
    加密函数
    :param s:
    :param salt: 盐
    :return: h:加密字符串
    """
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()



