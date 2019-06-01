# -*-coding:utf-8-*-
__author__ = 'Nirvana'
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from activity.utils import Pagintor
from billboard.models import Notice
from billboard.forms import UpdateForm,NoticeForm

from SeaLion import settings

# Create your views here.
@login_required(login_url=settings.LOGIN_URL)
def billboard_display(request):
    """
    展示活动公告列表
    :param request: GET
    :return: 公告列表
    """
    if request.method == 'GET':
        notices = Notice.objects.all()
        insert_form = NoticeForm()
        Billboard = Pagintor(request=request, ac_list=notices, acount=10)
        notice_insert_message = request.session.get('notice_insert_message')
        if 'notice_insert_message' in request.session:
            del request.session['notice_insert_message']
        message = request.session.get('message')
        if 'message' in request.session:
            del request.session['message']
    return render(request, 'notice/billboard.html', locals())


@login_required(login_url=settings.LOGIN_URL)
def notice_detail(request, nid):
    """
    公告详情
    :param request: GET
    :param nid: 公告id
    :return: 公告详情页面
    """
    if request.method == 'GET':
        notice = get_object_or_404(Notice,id=nid)
        update_form = UpdateForm(instance=notice)
        notice_update_message = request.session.get('notice_update_message')
        if 'notice_update_message' in request.session:
            del request.session['notice_update_message']
    return render(request, "notice/detail.html", locals())


@login_required(login_url=settings.LOGIN_URL)
def notice_insert(request):
    """
    创建公告
    :param request: POST
    :return: 公告列表
    """
    if request.method == "POST":
        insert_form = NoticeForm(request.POST)
        message = '请检查填写内容！'
        if insert_form.is_valid():
            new_notice = insert_form.save(commit=False)
            try:
                new_notice.announcer = request.user
                new_notice.save()
                message = '公告发布成功'
            except:
                message = '公告发布失败，请重试'
        request.session['notice_insert_message'] = message
    return HttpResponseRedirect(reverse('noticeApp:billboard',))

@login_required(login_url=settings.LOGIN_URL)
def billboard_delete(request, nid):
    """
    删除公告
    :param request: POST
    :param nid: 公告id
    :return: 公告列表
    """
    notice = get_object_or_404(Notice, id=nid)
    try:
        notice.delete()
        message = '删除公告成功'
    except BaseException:
        message = '删除失败，请重试'
    request.session['message'] = message
    return HttpResponseRedirect(reverse('noticeApp:billboard',))


def billboard_update(request, nid):
    """
    更改公告
    :param request: POST
    :param nid: 公告id
    :return: 公告详情
    """
    notice = get_object_or_404(Notice, id=nid)
    update_form = UpdateForm(instance=notice, data=request.POST)
    if update_form.is_valid():
        update_form.save(commit=False)
        try:
            update_form.save()
            message = '修改成功'
        except:
            message = '修改失败，请重试'
        request.session['notice_update_message'] = message
    return HttpResponseRedirect(reverse('noticeApp:detail', args=(nid,)))