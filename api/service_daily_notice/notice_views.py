"""
每日小提示
"""
from django.db import transaction
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from api import models
from utils.code import ResMsg, GeneralCode


class NoticeDailyserializers(serializers.ModelSerializer):
    class Meta:
        model = models.DailyNotice
        fields = '__all__'


class NoticeDaily(APIView):
    def __init__(self, *args, **kwargs):
        super(NoticeDaily).__init__(*args, **kwargs)
        self.res = ResMsg()

    def get(self, request, *args, **kwargs):
        notice_obj = models.DailyNotice.objects.all().filter(user=1).order_by("-update_time")
        notice_first = notice_obj.first()
        ser = NoticeDailyserializers(instance=notice_first)
        self.res.update(data=ser.data)
        return Response(self.res.data)

    def post(self, request, *args, **kwargs):
        username = request.POST.get("username")  # *-* 用户名 -*-
        usertoken = request.POST.get("usertoken")  # *-* 用户token -*-
        content = request.POST.get("content")  # *-* 提示 -*-

        user = models.UserInfo.objects.filter(username=username, token=usertoken)
        # *-* 验证用户 -*-
        if not user:
            self.res.update(code=GeneralCode.AUTHORITY_FAIL)
            return Response(self.res.data)

        if content:
            try:
                with transaction.atomic():  # *-* 事务回滚 -*-
                    models.DailyNotice.objects.create(user=user.first(), content=content)

            except Exception as e:
                print(e)
                self.res.update(code=GeneralCode.FAIL)
                return Response(self.res.data)
        return Response(self.res.data)
