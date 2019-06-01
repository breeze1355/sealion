from django import forms
from activity.models import Activity


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['title', 'address', 'start_time', 'desc', 'isActive']
        widgets = {
            'start_time': forms.TimeInput,
            'desc': forms.Textarea(attrs={'cols': 50, 'rows': 10}),  # 关键是这一行
        }
        help_texts = {
            'start_time': 'eg. 1900/01/01 00:00'
        }


class UpdateForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['title', 'address', 'start_time', 'desc', 'notice']
        widgets = {
            'desc': forms.Textarea(attrs={'cols': 50, 'rows': 10}),
            'notice': forms.Textarea(attrs={'cols': 50, 'rows': 10}),
        }