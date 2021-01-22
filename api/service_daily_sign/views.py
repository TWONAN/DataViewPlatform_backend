"""
处理每日签到
"""
import logging
from datetime import datetime
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, QueryDict
from rest_framework.response import Response
from rest_framework.views import APIView
from api import models
from utils.code import ResMsg, GeneralCode

logger = logging.getLogger("error")


class DailySign(APIView):
    def __init__(self, *args, **kwargs):
        super(DailySign).__init__(*args, **kwargs)
        self.res = ResMsg()

    def get(self, request, *args, **kwargs):
        """
        获取签到数
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        username = request.GET.get("username")
        usertoken = request.GET.get("usertoken")

        user = models.UserInfo.objects.get(username=username, token=usertoken)
        # *-* 验证用户 -*-
        if not user:
            self.res.update(code=GeneralCode.AUTHORITY_FAIL)
            return Response(self.res.data)

        sobj = models.DailySign.objects.filter(user=user).first()
        sign_num = sobj.sign_num
        self.res.update(data={"sign_num": sign_num})
        return Response(self.res.data)

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
        try:
            with transaction.atomic():  # *-* 事务回滚 -*-
                sobj.update_time = new_time
                sobj.sign_num += 1
                sobj.save()
        except Exception as e:
            logger.error(e)
            self.res.update(code=GeneralCode.FAIL)
            return Response(self.res.data)

        return Response(self.res.data)
