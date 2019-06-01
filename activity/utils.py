#-*-coding:utf-8-*- 
__author__ = 'Nirvana'
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

def Pagintor(request, ac_list, acount):
    """
    分页器
    :param request:
    :param ac_list: 需要分页的列表
    :return: 第page页的数据
    """
    paginator = Paginator(ac_list, acount)  # 创建每页4条数据的分页器
    page = request.GET.get('page')  # 通过get请求得到当前要显示的第几页数据
    try:
        data = paginator.page(page)  # 获取第page页的数据，如果没有抛出异常
    except PageNotAnInteger:
        # 如果page页不是整数，取第1页数据
        data = paginator.page(1)
    except EmptyPage:
        # 如果page不在范围，取最后1页数据
        data = paginator.page(paginator.num_pages)
    return data
