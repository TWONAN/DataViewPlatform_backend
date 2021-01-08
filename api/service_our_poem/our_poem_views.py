"""
我们的诗歌视图函数
"""
from datetime import datetime

from bs4 import BeautifulSoup
from django.db import transaction
from django.http import QueryDict
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from api import models

# 我们的诗歌序列化
from utils.code import ResMsg, GeneralCode


class OurPoemSerializers(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    content = serializers.CharField(source='poem_detail.content')

    class Meta:
        model = models.OurPoem
        fields = ['username', 'p_id', 'update_time', 'title', 'content']


# 处理我们诗歌
class OurPoemAPI(APIView):
    def __init__(self):
        super(OurPoemAPI).__init__()
        self.res = ResMsg()

    def get(self, request, *args, **kwargs):
        """
        获取所有诗歌
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        page = int(request.GET.get("page"))
        size = 5  # 默认5条一页
        p_obj = models.OurPoem.objects.all().filter(status=1).order_by("-update_time")
        count = p_obj.count()
        p_obj = p_obj[(page - 1) * size:page * size]
        ser = OurPoemSerializers(instance=p_obj, many=True)
        for item in ser.data:
            item["update_time"] = datetime.strptime(item["update_time"], "%Y-%m-%dT%H:%M:%S.%f").strftime(
                "%Y-%m-%d %H:%M:%S")
        self.res.update(data=ser.data)
        self.res.add_field("total_page", count)
        return Response(self.res.data)

    def post(self, request, *args, **kwargs):
        """
        上传诗歌
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        title = request.POST.get('title')  # *-* 诗歌标题 -*-
        content = request.POST.get('content')  # *-* 诗歌内容 -*-
        username = request.POST.get("username")  # *-* 用户名 -*-
        usertoken = request.POST.get("usertoken")  # *-* 用户token -*-

        user = models.UserInfo.objects.filter(username=username, token=usertoken)
        # *-* 验证用户 -*-
        if not user:
            self.res.update(code=GeneralCode.AUTHORITY_FAIL)
            return Response(self.res.data)
        # *-* 验证参数 -*-
        if not title or not content:
            self.res.update(code=GeneralCode.INVALID_PARAMS)
            return Response(self.res.data)
        user = user.first()  # *-* 获取到用户对象 -*-

        # *-* 如果用户添加的有诗歌内容 -*-
        if content:
            bp = BeautifulSoup(content, 'lxml')
            for tag in bp.find_all():
                if tag.name in ['script', 'link']:
                    tag.decompose()
            try:
                with transaction.atomic():  # *-* 事务回滚 -*-
                    p_obj = models.OurPoem.objects.create(user=user, title=title)
                    models.OurPoemDetail.objects.create(content=str(bp), poem=p_obj)
            except Exception as e:
                print(e)
                self.res.update(code=GeneralCode.FAIL)
                return Response(self.res.data)
        return Response(self.res.data)

    def delete(self, request, *args, **kwargs):
        """
        删除，软删除
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        data = QueryDict(request.body)
        pid = data.get("pid")
        p_obj = models.OurPoem.objects.filter(p_id=pid)
        if p_obj:
            try:
                with transaction.atomic():  # *-* 事务回滚 -*-
                    p_obj.update(status=0)
            except Exception as e:
                print(e)
                self.res.update(code=GeneralCode.FAIL)
                return Response(self.res.data)
            return Response(self.res.data)
