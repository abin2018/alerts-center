from django.urls import path
from .views import CommonAlertView
from .views import AliyunAlertView
from .views import TingyunAlertView
from .views import CommonEventView


urlpatterns = [
    path('common/<str:source_id>/', CommonAlertView.as_view(), name='common'),
    path('aliyun/<str:source_id>/', AliyunAlertView.as_view(), name='aliyun'),
    path('tingyun/<str:source_id>/', TingyunAlertView.as_view(), name='tingyun'),
    path('event/<str:source_id>/', TingyunAlertView.as_view(), name='event'),
]
