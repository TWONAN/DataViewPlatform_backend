"""
我们的文章视图函数
"""
import os
import logging
from datetime import datetime
from bs4 import BeautifulSoup
from django.db import transaction
from django.http import JsonResponse, QueryDict
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from api import models
from utils.code import ResMsg, GeneralCode

logger = logging.getLogger("error")


# 文章序列化
class Articleserializers(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    content = serializers.CharField(source='articledetail.content')
    avatar = serializers.FileField(source='user.avatar')

    class Meta:
        model = models.Article
        fields = ['username', 'aid', 'title', 'desc', 'create_time', 'content', 'avatar', "status"]


class ArticleAPI(APIView):

    def __init__(self):
        super(ArticleAPI).__init__()
        self.res = ResMsg()

    def get(self, request, *args, **kwargs):
        """
        获取所有用户文章，进行展示
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        page = int(request.GET.get("page"))
        username = request.GET.get("username")
        usertoken = request.GET.get("usertoken")
        size = 5  # 默认5条每页
        if username and usertoken:
            user = models.UserInfo.objects.filter(username=username, token=usertoken)
            aobj = models.Article.objects.all().filter(status=1, user=user).order_by("-create_time")
        else:
            aobj = models.Article.objects.all().filter(status=1).order_by("-create_time")
        count = aobj.count()
        aobj = aobj[(page - 1) * size:page * size]
        ser = Articleserializers(instance=aobj, many=True)
        for item in ser.data:
            item["create_time"] = datetime.strptime(item["create_time"], "%Y-%m-%dT%H:%M:%S.%f").strftime(
                "%Y-%m-%d %H:%M:%S")
        self.res.update(data=ser.data)
        self.res.add_field("total_page", count)
        return Response(self.res.data)

    def post(self, request, *args, **kwargs):
        """
        用户上传文章
        TODO:未完善
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        title = request.POST.get('title')  # *-* 文章标题 -*-
        content = request.POST.get('content')  # *-* 文章内容 -*-
        img_obj = request.FILES.get('imgFile')  # *-* 上传的图片 -*-
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
        # *-* 如果上传了图片 -*-
        if img_obj:
            path = os.path.join('static', 'img', img_obj.name)
            with open(path, 'wb') as f:
                for line in img_obj:
                    f.write(line)
            self.res.add_field("errors", 0)
            self.res.add_field("url", "/static/img/" + img_obj.name)
            return JsonResponse(self.res.data)
        # *-* 如果用户添加的有文章内容 -*-
        if content:
            bp = BeautifulSoup(content, 'lxml')
            desc = bp.text[0:150] + '...'
            for tag in bp.find_all():
                if tag.name in ['script', 'link']:
                    tag.decompose()
            try:
                with transaction.atomic():  # *-* 事务回滚 -*-
                    article_obj = models.Article.objects.create(user=user, desc=desc, title=title)
                    models.ArticleDetail.objects.create(content=str(bp), article=article_obj)
            except Exception as e:
                logger.error(e)
                self.res.update(code=GeneralCode.FAIL)
                return Response(self.res.data)
        return Response(self.res.data)

    def delete(self, request, *args, **kwargs):
        """
        删除文章接口，不过是软删除哦~
        :param request:
        :param aid:
        :return:
        """
        data = QueryDict(request.body)
        aid = data.get("aid")
        del_obj = models.Article.objects.filter(aid=aid)
        if del_obj:
            try:
                del_obj.update(status=0)
            except Exception as e:
                logger.error(e)
                self.res.update(code=GeneralCode.FAIL)
        return Response(self.res.data)
