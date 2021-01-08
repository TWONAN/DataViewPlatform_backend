"""
我们想一起做的事的视图
"""
from datetime import datetime
from django.db import transaction
from django.http import QueryDict
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from api import models
from utils.code import ResMsg, GeneralCode


# 我们想做的事序列化
class OurWannaToDoserializers(serializers.ModelSerializer):
    class Meta:
        model = models.OurWannaToDo
        fields = '__all__'


class OurWannaTodo(APIView):

    def __init__(self):
        super(OurWannaTodo).__init__()
        self.res = ResMsg()

    def get(self, request, *args, **kwargs):
        """
        直接获取数据进行展示
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        boy = models.UserInfo.objects.filter(uid=3)
        girl = models.UserInfo.objects.filter(uid=2)

        if boy and request.GET.get("page_right"):
            page_right = int(request.GET.get("page_right"))
            page_right_size = 5
            boy_obj = models.OurWannaToDo.objects.filter(user=boy.first()).order_by("create_time")
            boy_count = boy_obj.count()
            boy_ser = OurWannaToDoserializers(
                instance=boy_obj.all()[(page_right - 1) * page_right_size:page_right * page_right_size], many=True)
            for item in boy_ser.data:
                item["create_time"] = datetime.strptime(item["create_time"], "%Y-%m-%dT%H:%M:%S.%f").strftime(
                    "%Y-%m-%d %H:%M:%S")
                if item.get("weather") == 0:
                    weather = "晴天"
                elif item.get("weather") == 1:
                    weather = "多云"
                elif item.get("weather") == 2:
                    weather = "雨天"
                elif item.get("weather") == 3:
                    weather = "大风"
                elif item.get("weather") == 4:
                    weather = "雾天"
                else:
                    weather = "雪天"
                item["weather"] = weather

                if item.get("status") == 0:
                    status = "未完成"
                else:
                    status = "完成"
                item["status"] = status

            self.res.add_field("right", boy_ser.data)
            self.res.add_field("total_right", boy_count)
        else:
            self.res.add_field("right", [])
            self.res.add_field("total_right", 0)

        if girl and request.GET.get("page_left"):
            page_left = int(request.GET.get("page_left"))
            page_left_size = 5
            girl_obj = models.OurWannaToDo.objects.filter(user=girl.first()).order_by("create_time")
            girl_count = girl_obj.count()
            girl_ser = OurWannaToDoserializers(
                instance=girl_obj.all()[(page_left - 1) * page_left_size:page_left * page_left_size], many=True)
            for item in girl_ser.data:
                item["create_time"] = datetime.strptime(item["create_time"], "%Y-%m-%dT%H:%M:%S.%f").strftime(
                    "%Y-%m-%d %H:%M:%S")
                if item.get("weather") == 0:
                    weather = "晴天"
                elif item.get("weather") == 1:
                    weather = "多云"
                elif item.get("weather") == 2:
                    weather = "雨天"
                elif item.get("weather") == 3:
                    weather = "大风"
                elif item.get("weather") == 4:
                    weather = "雾天"
                else:
                    weather = "雪天"
                item["weather"] = weather

                if item.get("status") == 0:
                    status = "未完成"
                else:
                    status = "完成"
                item["status"] = status
            self.res.add_field("left", girl_ser.data)
            self.res.add_field("total_left", girl_count)
        else:
            self.res.add_field("left", [])
            self.res.add_field("total_left", 0)

        return Response(self.res.data)

    def post(self, request, *args, **kwargs):
        """
        上传想做的事情
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        content = request.POST.get('content')  # *-* 内容 -*-
        weather = int(request.POST.get('weather')) if request.POST.get('weather') else 0  # *-* 天气 -*-
        status = int(request.POST.get('status')) if request.POST.get('status') else 0  # *-* 状态 -*-
        username = request.POST.get("username")  # *-* 用户名 -*-
        usertoken = request.POST.get("usertoken")  # *-* 用户token -*-
        change_status = request.POST.get("changeStatus")  # *-* 修改完成度 -*-
        wid = request.POST.get("wid")  # *-* 想做事id -*-

        user = models.UserInfo.objects.filter(username=username, token=usertoken)
        # *-* 验证用户 -*-
        if not user:
            self.res.update(code=GeneralCode.AUTHORITY_FAIL)
            return Response(self.res.data)

        user = user.first()  # *-* 获取到用户对象 -*-

        try:
            with transaction.atomic():
                # 修改完成状态
                if change_status and wid:
                    models.OurWannaToDo.objects.filter(w_id=wid).update(status=int(change_status))
                else:
                    wanna_obj = models.OurWannaToDo.objects.filter(user=user).order_by("-create_time").first()
                    if wanna_obj:
                        models.OurWannaToDo.objects.create(user=user,
                                                           content=content,
                                                           weather=weather,
                                                           status=status,
                                                           serial_number=wanna_obj.serial_number + 1)
                    else:
                        models.OurWannaToDo.objects.create(user=user,
                                                           content=content,
                                                           weather=weather,
                                                           status=status,
                                                           serial_number=1)
        except Exception as e:
            print(e)
            self.res.update(code=GeneralCode.FAIL)
            return Response(self.res.data)
        return Response(self.res.data)

    def delete(self, request, *args, **kwargs):
        data = QueryDict(request.body)
        w_id = data.get("w_id")
        w_obj = models.OurWannaToDo.objects.filter(w_id=w_id)
        if w_obj:
            try:
                with transaction.atomic():  # *-* 事务回滚 -*-
                    w_obj.update(status=0)
            except Exception as e:
                print(e)
                self.res.update(code=GeneralCode.FAIL)
                return Response(self.res.data)
            return Response(self.res.data)
