from django import forms
from .models import SystemConfigure


class SystemConfigureForm(forms.ModelForm):
    send_on_call_info_reminder_webhook = forms.CharField(required=True, label='通知Webhook',
                                                         widget=forms.TextInput(attrs={"style": "width:800px;"}))
    unresolved_alerts_reminder_webhook = forms.CharField(required=True, label='通知Webhook',
                                                         widget=forms.TextInput(attrs={"style": "width:800px;"}))

    class Meta:
        model = SystemConfigure
        fields = ('send_on_call_info_reminder_webhook', 'unresolved_alerts_reminder_webhook',)
