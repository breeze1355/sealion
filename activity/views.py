# -*-coding:utf-8-*-
__author__ = 'Nirvana'

import base64
import os

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import View

from SeaLion import settings
from activity.forms import ActivityForm, UpdateForm
from activity.models import Activity
from user.models import PhotoModel
from billboard.models import Notice
from activity.utils import Pagintor

from datetime import datetime
import face_recognition as fr
import numpy as np

# Create your views here.

# 全局变量
known_face_encodings = []   # 活动嘉宾面部图像缓存列表
know_std_num= []            # 活动嘉宾学号缓存列表
msg = ''                    # 签到结果
result = ''                 # 签到人员信息


# 登陆限制装饰器类
class LoginRequiredMixin(object):
 @classmethod
 def as_view(cls, **initkwargs):
    view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
    return login_required(view)

def display_activity(request):
    """
    分页展示活动
    :param request: GET
    :return: 活动列表
    """
    if request.method == 'GET':
        ac_list = Activity.objects.all()
        Billboard = Notice.objects.all()[:3]
        apply_form = ActivityForm()                 # 给一个 创建活动 的空白表单
        activities_list = Pagintor(request=request, ac_list=ac_list, acount=4)
        if request.user.is_authenticated:
            if request.session.get('uploaded') is None:
                image_code = PhotoModel.objects.filter(user=request.user)
                if len(image_code) > 0:
                    # 如果用户照片不为空
                    request.session['uploaded'] = True
                else:
                    request.session['nav_msg'] = True
            message = request.session.get('message')    # 获取其他操作的提示信息
            if 'message' in request.session:
                del request.session['message']
    return render(request, 'activity/index.html', locals())


def search_activity(request):
    """
    活动查找
    :param request: GET
    :return: 查询结果列表
    """
    if request.method == 'GET':
        activity_msg = request.GET.get("activity_msg", "")
        activities_list = Activity.objects.all()
        apply_form = ActivityForm()
        if len(activity_msg) > 0:
            # 如果查询信息不为空
            activities_list = Activity.objects.filter(Q(title__contains=activity_msg) |
                                                      Q(address__contains=activity_msg) |
                                                      Q(creator__username__contains=activity_msg) |
                                                      Q(creator__nick_name__contains=activity_msg))
        activities_list = Pagintor(request=request, ac_list=activities_list, acount=4)
        Billboard = Notice.objects.all()[:3]
    return render(request, "activity/index.html", locals())


class Activity_Rec(LoginRequiredMixin, View):
    """
    活动签到功能控制类
    """
    def get(self,request,aid):
        """
        获取活动详情 如果request user是活动创建者 则获取该活动嘉宾列表
        :param request: 请求信息 GET
        :param aid: 活动id
        :return: 活动详情页面
        """
        global  known_face_encodings
        global  know_std_num
        activity= get_object_or_404(Activity, id=aid)
        update_form = UpdateForm(instance=activity)
        message = request.session.get('message')
        if 'message' in request.session:
            del request.session['message']
        if 'joined' in request.session:
            del request.session['joined']
        guests = activity.guests.all()
        if request.user == activity.creator:
            for gue in guests:
                gue_files = PhotoModel.objects.filter(user=gue)
                for file in gue_files:
                    img_code = np.load(file.img_code + '.npy')
                    known_face_encodings.append(img_code)
                    know_std_num.append(gue.std_num)
        sum_guest = guests.count()                          # 总人数
        signed_guest_list = activity.signed_in_users.all()  # 已签到嘉宾列表
        signed_guest_count = 0                              # 签到人数
        unsigned_guest_count = 0                            # 未签到人数
        sign_rate = 0.00                                    # 签到率
        if request.user in guests:
            # 如果请求者在嘉宾列表中，保存状态
            joined = True
            request.session['joined'] = joined
        if sum_guest > 0:
            signed_guest_count = signed_guest_list.count()
            unsigned_guest_count = sum_guest - signed_guest_count
            sign_rate = round((signed_guest_list.count() / sum_guest) * 100, 2)
        return render(request, "activity/detail.html", locals())

    def post(self,request):
        """
        获取前端发送的图像进行比对并返回结果
        :param request: 请求信息 POST
        :return: 识别结果
        """
        global known_face_encodings
        global know_std_num
        global msg
        global result
        # 获取base64格式的图片
        aid = request.POST.get('aid')
        activity = get_object_or_404(Activity, id=aid)
        faceImage = request.POST.get('faceImg')
        # 提取出base64格式，并进行转换为图片
        index = faceImage.find('base64,')
        base64Str = faceImage[index + 6:]
        bytes_img = base64.b64decode(base64Str)
        # 将文件保存
        backupDate = datetime.now().strftime("%Y%m%d_%H%M%S")
        fileName = "Img_%s.jpg" % (backupDate)
        file_path = os.path.join("media", "image_cache",str(activity.title)+'_'+str(activity.id))   # 文件保存路径
        if not os.path.exists(file_path):
            # 不存在则创建
            os.mkdir(file_path)
        _file = os.path.join(file_path,fileName)
        file = open(_file, 'wb')
        file.write(bytes_img)
        file.close()
        # 删除多余的图片
        files = os.listdir(file_path)
        files.sort()
        ImgCount = files.__len__()
        if ImgCount > 100:
            # 图片超过100个，删除一个
            os.unlink(file_path + files[0])

        unknown_face_tmp_encoding = []
        try:
            unknown_face = fr.load_image_file(_file)
            unknown_face_tmp_encoding = fr.face_encodings(unknown_face)
        except IndexError:
            pass  # 图片中未发现人脸
        except IOError:
            pass  # 图片中未发现人脸

        # 对图片进行人脸识别比对
        for face_encoding in unknown_face_tmp_encoding:
            matches = fr.compare_faces(known_face_encodings, face_encoding, 0.45)
            face_distances = fr.face_distance(known_face_encodings, face_encoding)
            try:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    match = know_std_num[int(best_match_index)]
                    result = activity.guests.get(std_num=match)
                    msg = 'ok'
                    if result in activity.signed_in_users.all():
                        pass
                    else:
                        activity.signed_in_users.add(result)
                        activity.save()
            except:
                msg = ''
        return JsonResponse({'guest':str(result),'msg': msg})


@login_required(login_url=settings.LOGIN_URL)
def create_activity(request):
    """
    创建活动
    :param request:POST
    :return: 活动列表
    """
    if request.method == "POST":
        activity_form = ActivityForm(request.POST)
        message = '请检查填写内容！'
        if activity_form.is_valid():
            new_activity = activity_form.save(commit=False)
            try:
                new_activity.creator = request.user
                new_activity.save()
                message = '活动创建成功'
            except:
                message = '创建活动失败，请重试'
        request.session['message'] = message
    return HttpResponseRedirect(reverse('activityApp:index',))


@login_required(login_url=settings.LOGIN_URL)
def delete_activity(request, aid):
    """
    删除活动
    :param request: POST
    :param aid: 活动id
    :return:
    """
    activity = get_object_or_404(Activity, id=aid)
    try:
        activity.delete()
        message = '删除活动成功'
    except BaseException:
        message = '删除失败，请重试'
    request.session['message'] = message
    return HttpResponseRedirect(reverse('activityApp:index',))


@login_required(login_url=settings.LOGIN_URL)
def update_activity(request, aid):
    """
    修改活动信息
    :param request:  POST
    :param aid: 活动id
    :return:
    """
    activity = get_object_or_404(Activity, id=aid)
    update_form = UpdateForm(instance=activity, data=request.POST)
    if update_form.is_valid():
        update_form.save(commit=False)
        try:
            update_form.save()
            message = '修改成功'
        except BaseException:
            message = '修改失败，请重试'
        request.session['message'] = message
    return HttpResponseRedirect(reverse('activityApp:detail', args=(aid,)))


@login_required(login_url=settings.LOGIN_URL)
def sign_condition(request, aid):
    """
    活动签到状态更改（活动创建者）
    :param request: GET
    :param aid: activity id
    :return:
    """
    if request.method == "GET":
        activity = get_object_or_404(Activity, id=aid)
        try:
            activity.isActive = not activity.isActive
            activity.save()
            message = '操作成功'
        except:
            message = '操作失败'
        request.session['message'] = message
    return HttpResponseRedirect(reverse('activityApp:detail', args=(aid,)))


@login_required(login_url=settings.LOGIN_URL)
def join_activity(request, aid):
    """
    加入活动/退出活动
    :param request: GET
    :param aid: 活动id
    :return:
    """
    nav_msg = request.session.get('nav_msg')
    if not nav_msg:
        activity = get_object_or_404(Activity, id=aid)
        if not activity.isActive:
            joined = request.session.get('joined')
            if joined is  None:
                try:
                    activity.guests.add(request.user)
                    message = '加入活动成功'
                except:
                    message = '加入活动失败'
            else:
                try:
                    activity.guests.remove(request.user)
                    message = '退出活动成功'
                    del request.session['joined']
                except:
                    message = '退出活动失败'
        else:
            message = '活动状态已更改'
        request.session['message'] = message
    return HttpResponseRedirect(reverse('activityApp:detail', args=(aid,)))


@login_required(login_url=settings.LOGIN_URL)
def guest_condition(request, aid, gid):
    """
    嘉宾签到状态更改
    :param request: GET
    :param aid: 活动id
    :param gid: 嘉宾id
    :return: 活动详情页面
    """
    activity = get_object_or_404(Activity, id=aid)
    if activity.isActive  and activity.creator == request.user:
        signed_guest = activity.signed_in_users.all()
        guest = activity.guests.get(id=gid)
        if not guest in signed_guest:
            activity.signed_in_users.add(guest)
        else:
            activity.signed_in_users.remove(guest)
    return HttpResponseRedirect(reverse('activityApp:detail', args=(aid,)))
