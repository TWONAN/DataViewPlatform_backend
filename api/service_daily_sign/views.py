"""
处理每日签到
"""
from datetime import datetime

from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, QueryDict
from rest_framework.response import Response
from rest_framework.views import APIView

from api import models
from utils.code import ResMsg, GeneralCode


class DailySign(APIView):
    def __init__(self, *args, **kwargs):
        super(DailySign).__init__(*args, **kwargs)
        self.res = ResMsg()

    def post(self, request, *args, **kwargs):
        """
        通过时间判断当日是否签到
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        current_date = request.POST.get("currentDate")  # 获取前端传的当前时间
        username = request.POST.get("username")
        usertoken = request.POST.get("usertoken")

        user = models.UserInfo.objects.get(username=username, token=usertoken)
        # *-* 验证用户 -*-
        if not user:
            self.res.update(code=GeneralCode.AUTHORITY_FAIL)
            return Response(self.res.data)

        sobj = models.DailySign.objects.filter(user=user).first()
        update_time = sobj.update_time
        nyr = update_time.strftime("%Y-%m-%d")
        if nyr == current_date:
            self.res.update(code=GeneralCode.FAIL)
            return Response(self.res.data)
        new_time = datetime.strptime(current_date, "%Y-%m-%d")
        sobj.update_time = new_time
        sobj.sign_num += 1
        sobj.save()
        return Response(self.res.data)
