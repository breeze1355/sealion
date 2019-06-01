from django.contrib import admin

# Register your models here.
from user.models import UserModel, PhotoModel, UserAvatar


@admin.register(UserModel)
class UserModelAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'nick_name', 'username', 'std_num', 'std_class', 'c_time',
    ]
    search_fields = ['username', 'nick_name', 'std_num', 'std_class']
    list_filter = ['std_num']
    list_per_page = 10


@admin.register(PhotoModel)
class PhotoModelAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'img_code'
    ]
    search_fields = ['user']
    list_filter = ['user']
    list_per_page = 10


@admin.register(UserAvatar)
class UserAvatarAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'avatar'
    ]
    search_fields = ['user']
    list_filter = ['user']
    list_per_page = 10


admin.site.site_header = 'Sea Lion'
admin.site.site_title = '后台管理界面'
admin.site.index_title = '表单管理'

