from rest_framework.views import APIView
from django.http import JsonResponse
from .tasks import process_alerting_data
from .tasks import process_aliyun_alert_data
from .tasks import process_tingyun_alert_data


class CommonAlertView(APIView):
    def post(self, request, source_id):
        alert_data = request.data
        alert_data['alert_source'] = source_id
        process_alerting_data.delay(alert_data)
        return JsonResponse({'status': 'OK'})


class AliyunAlertView(APIView):
    def post(self, request, source_id):
        alert_data_raw = dict(request.data)
        alert_data_raw['alert_source'] = source_id
        alert_data = process_aliyun_alert_data(alert_data_raw)
        process_alerting_data.delay(alert_data)
        return JsonResponse({'status': 'OK'})


class TingyunAlertView(APIView):
    def post(self, request, source_id):
        alert_data_raw = dict(request.data)
        alert_data_raw['alert_source'] = source_id
        alert_data = process_tingyun_alert_data(alert_data_raw)
        process_alerting_data.delay(alert_data, False)
        return JsonResponse({'status': 'OK'})


class CommonEventView(APIView):
    def post(self, request, source_id):
        alert_data = request.data
        alert_data['alert_source'] = source_id
        process_alerting_data.delay(alert_data, False)
        return JsonResponse({'status': 'OK'})
