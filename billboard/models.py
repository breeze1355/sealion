from django.db import models
from SeaLion import settings
# Create your models here.
class Notice(models.Model):
    """
    公告表
    """
    announcer = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='创建者', related_name='notice_creator',
                                on_delete=models.CASCADE, blank=True)
    title = models.CharField(verbose_name='公告标题', max_length=50, blank=True)
    content = models.TextField(verbose_name='公告内容', blank=True)
    c_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    def __unicode__(self):
        return u'%s' % self.title

    class Meta:
        ordering = ['-c_time']
        verbose_name = 'Billboard'
        verbose_name_plural = verbose_name
