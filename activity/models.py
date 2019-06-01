from django.db import models

# Create your models here.
from SeaLion import settings


class Activity(models.Model):
    """
    活动表
    """
    title = models.CharField(verbose_name="活动名称", max_length=100, db_index=True)
    address = models.CharField(verbose_name='活动地点', max_length=50)
    start_time = models.DateTimeField(verbose_name='开始时间')
    isActive = models.BooleanField(verbose_name="是否开始签到", default=False)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='创建者', related_name='activities_creator',
                                on_delete=models.CASCADE)
    guests = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name='嘉宾', related_name='activities_guest',
                                    blank=True)
    signed_in_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='activities_signed_in',
                                             verbose_name='已签到嘉宾')
    c_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    desc = models.TextField(verbose_name='活动描述', max_length=50, blank=True)
    notice = models.TextField(verbose_name='活动公告', max_length=50, blank=True)

    class Meta:
        ordering = ['-c_time', ]
        verbose_name = 'Activity'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title
