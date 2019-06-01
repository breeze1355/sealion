import os
import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser,User

from SeaLion import settings


def user_directory_path(instance, filename):
    """
    自定义用户头像保存路径
    :param instance: 用户实例
    :param filename: 文件名
    :return: 路径
    """
    ext = filename.split('.')[-1]
    formal = filename.split('.')
    if formal is not 'default':
        filename = '{}.{}'.format(uuid.uuid4().hex[:10], ext)
    else:
        filename = 'default.png'
    return os.path.join("avatar",str(instance.user.id), filename)


class UserModel(AbstractUser):
    """
    拓展用户模型
    """
    nick_name = models.CharField(max_length=25, verbose_name='昵称', blank=False, unique=True)
    std_num = models.CharField(max_length=12, verbose_name='学号', unique=True, blank=True)
    std_class = models.CharField(max_length=25, verbose_name='班级', blank=True)
    tel = models.CharField(max_length=255, verbose_name='手机号', blank=False)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['-std_class']
        verbose_name = 'User Info'
        verbose_name_plural = verbose_name


class UserAvatar(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to=user_directory_path, verbose_name='用户头像',  default=os.path.join("avatar", "default.png"))

    class Meta:
        ordering = ['-user']
        verbose_name = 'User Avatar'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}'s avatar".format(self.user.username)


class PhotoModel(models.Model):
    """
    用户照片编码模型
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='用户', related_name='user', on_delete=models.CASCADE)
    user_img = models.ImageField(upload_to='user_photos', verbose_name='用户照片', blank=True)
    img_code = models.CharField(max_length=255, verbose_name='图像编码', blank=True)

    def __str__(self):
        return self.user.username

    class Meta:
        ordering = ["id"]
        verbose_name = "User Image Code File"
        verbose_name_plural = verbose_name
