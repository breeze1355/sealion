from django.contrib import admin

# Register your models here.
from activity.models import Activity


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    """
    activity admin
    """
    list_display = [
        'id', 'title', 'creator', 'c_time', 'address', 'start_time', 'isActive',
    ]
    search_fields = ['title', 'address', 'creator', 'isActive']
    list_filter = ['isActive']
    list_per_page = 10


