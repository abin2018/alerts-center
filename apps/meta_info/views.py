from django.http import request
from django.shortcuts import redirect


# admin 重定向
def admin_redirect(request):
    return redirect('/admin/')
