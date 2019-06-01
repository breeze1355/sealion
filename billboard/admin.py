from django.contrib import admin

# Register your models here.
from billboard.models import Notice


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    """
    Notice admin
    """
    list_display = [
        'id', 'announcer', 'title', 'content',  'c_time',
    ]
    search_fields = ['title', 'announcer']
    list_filter = ['announcer']
    list_per_page = 10