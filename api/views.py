import os

from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from api import models
from uuid import uuid4
from rest_framework import serializers
import requests
from lxml import html
from django.db.models import Count
from api import reg_form
from utils.code import GeneralCode, ResMsg
from bs4 import BeautifulSoup
from django.db import transaction
from geetest import GeetestLib
from datetime import datetime
from django.http import QueryDict

# Create your views here.

pc_geetest_id = 'b46d1900d0a894591916ea94ea91bd2c'
pc_geetest_key = '36fc3fe98530eea08dfc6ce76e3d24c4'


# 我们想做的事序列化
class OurWannaToDoserializers(serializers.ModelSerializer):
    class Meta:
        model = models.OurWannaToDo
        fields = '__all__'


# 数据处理详情序列化
class DataDetailserializers(serializers.ModelSerializer):
    class Meta:
        model = models.DataDetail
        fields = '__all__'


# 文章序列化
class Articleserializers(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    content = serializers.CharField(source='articledetail.content')
    avatar = serializers.FileField(source='user.avatar')

    class Meta:
        model = models.Article
        fields = ['username', 'aid', 'title', 'desc', 'create_time', 'content', 'avatar', "status"]


# 我们的诗歌序列化
class OurPoemSerializers(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    content = serializers.CharField(source='poem_detail.content')

    class Meta:
        model = models.OurPoem
        fields = ['username', 'p_id', 'update_time', 'title', 'content']


# 处理分页
class HandlePage(object):
    def __init__(self, current_page):
        self.current_page = int(current_page)

    # 处理当前页面下的开始数据
    @property
    def start(self):
        return (self.current_page - 1) * 20

    # 处理当前页面下的结束数据
    @property
    def end(self):
        return self.current_page * 20

    # 获取总数据，计算页数，生成按钮
    def page_str(self, all_item):
        all_page, y = divmod(all_item, 20)
        if y != 0:
            all_page += 1
        # 定义一个连接按钮的空字符串
        button_list = []
        if all_page <= 10:
            start_page = 1
            end_page = all_page
        else:
            if self.current_page < 6:
                start_page = 1
                end_page = 11
            elif self.current_page + 5 > all_page:
                start_page = all_page - 9
                end_page = all_page + 1

            else:
                start_page = self.current_page - 4
                end_page = self.current_page + 5
        for i in range(start_page, end_page):

            if i == self.current_page:
                button_list.append({"page": i, "tips": True})
            else:
                button_list.append({"page": i, "tips": False})
        return button_list


# 登录视图
class LoginAPI(APIView):
    def __init__(self):
        super(LoginAPI).__init__()
        self.res = ResMsg()

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        pwd = request.POST.get('password')

        # 极简验证开始
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        sobj = models.Session.objects.all().first()
        status = sobj.STATUS_SESSION_KEY
        user_id = sobj.USERID
        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        user = models.UserInfo.objects.filter(username=username, pwd=pwd).first()
        name_obj = models.UserInfo.objects.filter(username=username).first()
        if result:
            # 用户存在
            if user:
                uid = str(uuid4())
                models.UserInfo.objects.update_or_create(username=username, pwd=pwd, defaults={'token': uid})
                self.res.add_field("token", uid)
            # 不存在用户
            elif not name_obj:
                self.res.update(code=GeneralCode.USERNAME_ERROR)
            # 密码错误
            else:
                # 密码错误
                self.res.update(code=GeneralCode.PASSWORD_ERRPR)
        else:
            # 验证码错误
            self.res.update(code=GeneralCode.VERIFICATION_ERROR)

        ret = self.res.data
        return Response(ret)


# 注册视图函数
def reg(request):
    """
    TODO:暂时用的django自带的模板，需要进行跳转到注册页面
    :param request:
    :return:
    """
    res = ResMsg()
    form_obj = reg_form.Regform()
    if request.method == 'POST':
        form_obj = reg_form.Regform(request.POST)
        if form_obj.is_valid():
            form_obj.cleaned_data.pop('re_pwd')
            img = request.FILES.get('avatar')
            tmp_user = list()
            if img:
                user = models.UserInfo.objects.create(**form_obj.cleaned_data, avatar=img)
                for i in range(6):
                    tmp_user.append(models.DataDetail(num=1, title="未知%s" % i, user=user, exp_num=1))
                models.DataDetail.objects.bulk_create(tmp_user)
                res.update(msg="/login/")
                return JsonResponse(res.data)
            else:
                user = models.UserInfo.objects.create(**form_obj.cleaned_data, avatar="static/avatars/hmbb.png")
                for i in range(6):
                    tmp_user.append(models.DataDetail(num=1, title="未知%s" % i, user=user, exp_num=1))
                models.DataDetail.objects.bulk_create(tmp_user)
                res.update(msg="/login/")
                return JsonResponse(res.data)
        else:
            res.update(code=GeneralCode.FAIL, msg=form_obj.errors)
            return JsonResponse(res.data)
    return render(request, 'reg.html', {'form_obj': form_obj})


# 我们想一起做的事的视图
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
        boy = models.UserInfo.objects.get(uid=3)
        girl = models.UserInfo.objects.get(uid=2)
        boy_obj = models.OurWannaToDo.objects.filter(user=boy).order_by("create_time")
        boy_count = boy_obj.count()
        girl_obj = models.OurWannaToDo.objects.filter(user=girl).order_by("create_time")
        girl_count = girl_obj.count()

        if boy_obj:
            boy_ser = OurWannaToDoserializers(instance=boy_obj.all(), many=True)
            self.res.add_field("right", boy_ser.data)
            self.res.add_field("total_right", boy_count)
        else:
            self.res.add_field("right", [])
            self.res.add_field("total_right", 0)

        if girl_obj:
            girl_ser = OurWannaToDoserializers(instance=girl_obj.all(), many=True)
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
        weather = request.POST.get('weather')  # *-* 天气 -*-
        status = request.POST.get('status')  # *-* 状态 -*-
        username = request.POST.get("username")  # *-* 用户名 -*-
        usertoken = request.POST.get("usertoken")  # *-* 用户token -*-

        user = models.UserInfo.objects.filter(username=username, token=usertoken)
        # *-* 验证用户 -*-
        if not user:
            self.res.update(code=GeneralCode.AUTHORITY_FAIL)
            return Response(self.res.data)
        # *-* 验证参数 -*-
        if not content:
            self.res.update(code=GeneralCode.INVALID_PARAMS)
            return Response(self.res.data)
        user = user.first()  # *-* 获取到用户对象 -*-

        try:
            with transaction.atomic():
                models.OurWannaToDo.objects.create(user=user, content=content, weather=weather, status=status)
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


# 数据处理视图：
class DataHandleAPI(APIView):

    def __init__(self):
        super(DataHandleAPI).__init__()
        self.res = ResMsg()

    def get(self, request, *args, **kwargs):
        """
        获取单个用户的数据进行展示
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        username = request.GET.get('username')
        try:
            user = models.UserInfo.objects.get(username=username)
            dobj = models.DataDetail.objects.filter(user=user)
            ser = DataDetailserializers(instance=dobj, many=True)
            self.res.update(data=ser.data)
        except Exception as e:
            self.res.update(code=GeneralCode.FAIL)
        return Response(self.res.data)

    def post(self, request, *args, **kwargs):
        """
        用户进行修改数据
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        username = request.POST.get('username')
        itemName = request.POST.get('itemName')
        itemNum = request.POST.get('itemNum')
        itemExpNum = request.POST.get('itemExpNum')
        itemNewName = request.POST.get("itemNewName")
        if not itemName or not itemNum or not itemNewName:
            self.res.update(code=GeneralCode.INVALID_PARAMS)
            return Response(self.res.data)
        # TODO:暂时不支持超过100的数字，显示会有误
        if int(itemExpNum) > 100 or int(itemNum) > 100:
            self.res.update(code=GeneralCode.NOT_EXCEED_100)
            return Response(self.res.data)
        try:
            user = models.UserInfo.objects.get(username=username)
            # 先判断类别名是否有修改
            if itemNum == itemNewName:
                # 判断是否有正确的修改，有会返回1，没有则返回0
                if_modify = models.DataDetail.objects.filter(user=user, title=itemName).update(num=itemNum,
                                                                                               exp_num=itemExpNum)
            else:
                if_modify = models.DataDetail.objects.filter(user=user, title=itemName).update(num=itemNum,
                                                                                               exp_num=itemExpNum,
                                                                                               title=itemNewName)
            if if_modify:
                dobj = models.DataDetail.objects.filter(user=user)
                ser = DataDetailserializers(instance=dobj, many=True)
                self.res.update(data=ser.data)
            else:
                self.res.update(code=GeneralCode.INVALID_PARAMS)
        except Exception as e:
            print(e)
            self.res.update(code=GeneralCode.INVALID_PARAMS)
        return Response(self.res.data)


# 处理我们的文章
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
        size = 5  # 默认5条每页
        aobj = models.Article.objects.all().filter(status=1).order_by("-create_time")
        count = aobj.count()
        aobj = aobj[(page - 1) * size:page * size]
        ser = Articleserializers(instance=aobj, many=True)
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
                print(e)
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
            del_obj.update(status=0)
        return Response(self.res.data)


# 极简校验处理滑动验证
def get_geetest(request):
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    # request.session[gt.GT_STATUS_SESSION_KEY] = status
    # request.session["user_id"] = user_id
    # 由于前后端分离，使用数据库存储形式
    models.Session.objects.update_or_create(STATUS_SESSION_KEY=status, USERID=user_id)
    response_str = gt.get_response_str()
    return HttpResponse(response_str)


# 其他数据显示
class PoetRating(APIView):
    url = 'http://www.shicimingju.com/paiming'

    def __init__(self):
        super(PoetRating).__init__()
        self.res = ResMsg()

    def post(self, request, *args, **kwargs):
        """
        更新最新诗人信息详情（爬取最新数据）
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        # ret = {'code': 1000, 'data': ''}
        list_p = []
        models.PoetAndPoem.objects.all().delete()
        print("删除成功")
        if not self.get_poem(self.url, list_p):
            # ret = {'code': 1001, 'data': 'error'}
            self.res.update(code=GeneralCode.FAIL)
        return Response(self.res.data)

    def get(self, request, *args, **kwargs):
        """
         获取数据库所有诗人信息，进行排名
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        # 根据作者的名字分组，得到每一个作者上榜的诗歌个数，倒序排序
        current_page = request.GET.get("page", 1)  # 获取当前的页数
        p_obj = HandlePage(current_page)
        poem_list = []
        try:
            all_author = models.PoetAndPoem.objects.all().values('author').annotate(count=Count('author')). \
                values('author', 'count').order_by('-count')
            count = all_author.count()  # 计算数据总数
            button_list = p_obj.page_str(count)  # 获取到当前页面下生成的按钮
            for i in all_author[p_obj.start:p_obj.end]:
                poem_list.append(i)
            self.res.add_field("button", button_list)
            self.res.update(data=poem_list)
        except Exception as e:
            print(e)
            self.res.update(code=GeneralCode.FAIL)
        return Response(self.res.data)

    # 通过爬虫获取排名信息
    def get_poem(self, url, list_p):
        """
        爬虫函数
        :param url:
        :param list_p:
        :return:
        """
        etree = html.etree
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"}
        response = requests.get(url, headers=headers).text
        parser = etree.HTMLParser(encoding="utf-8")
        tree = etree.HTML(response, parser=parser)
        content_list = tree.xpath('/html/body//div[@class="card shici_card"]')
        for content in content_list:
            try:
                title = content.xpath('.//div[@class="shici_list_main"]//a/text()')[0]
                author = content.xpath('.//div[@class="list_num_info"]//a/text()')[0]
                list_p.append(models.PoetAndPoem(poetry=title, author=author))
                print(title, author, 'ok')
            except IndexError:
                pass
        try:
            next_page = tree.xpath('//div[@id="list_nav_part"]//a[contains(text(),"下一页")]/@href')[0]
            print(next_page)
            if next_page:
                next_path = 'http://www.shicimingju.com' + next_page
                self.get_poem(url=next_path, list_p=list_p)
        except IndexError:
            models.PoetAndPoem.objects.bulk_create(list_p)
        return True


# 处理评论相关
class CommentAPI(APIView):

    def __init__(self):
        super(CommentAPI).__init__()
        self.res = ResMsg()

    def get(self, request, *args, **kwargs):
        """
        展示评论树
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        article_id = request.GET.get("article_id")
        ret = list(models.Comment.objects. \
                   filter(article_id=article_id). \
                   values('pk', 'content', 'parent_comment_id', 'create_time', 'user'))
        comment_list = list()
        try:
            for item in ret:
                date = item.get("create_time")  # *-* datetime类型 -*-
                create_time = datetime.strftime(date, '%Y-%m-%d %H:%M:%S')  # *-* 格式化日期 -*-
                content = item.get("content")
                parent_comment_id = item.get("parent_comment_id")
                user_id = item.get("user")  # *-* userid -*-
                user = models.UserInfo.objects.get(uid=user_id)
                username = user.username  # *-* 获取评论人名 -*-

                p_comment = ""
                p_username = ""
                # *-* 判断是否有父评论 -*-
                if parent_comment_id:
                    parent_obj = models.Comment.objects.filter(cid=parent_comment_id).first()
                    p_comment = parent_obj.content
                    p_username = parent_obj.user.username
                comment_list.append({
                    "username": username,
                    "content": content,
                    "parent_comment_id": parent_comment_id,
                    "p_comment": p_comment,
                    "p_username": p_username,
                    "create_time": create_time
                })
            self.res.update(data=comment_list)
            return JsonResponse(self.res.data, safe=False)
        except Exception as e:
            print(e)

    def post(self, request, *args, **kwargs):
        """
        提交评论
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        # *-* 把提交评论的数据拿到后保存到数据库 -*-
        username = request.POST.get("username")
        usertoken = request.POST.get("usertoken")
        pid = request.POST.get('pid')  # *-* 父评论 -*-
        article_id = request.POST.get('article_id')  # *-* 文章id -*-
        content = request.POST.get('comment')  # *-* 文章内容 -*-
        content = content.strip()
        if not content:
            self.res.update(code=GeneralCode.COMMENT_NOT_NULL)
            return JsonResponse(self.res.data)
        try:
            user = models.UserInfo.objects.get(username=username, token=usertoken)
            with transaction.atomic():  # *-* 事务回滚 -*-
                # *-* 判断是否有父评论 -*-
                if pid:
                    models.Comment.objects.create(user=user, article_id=article_id, content=content,
                                                  parent_comment_id=pid)
                else:
                    models.Comment.objects.create(user=user, article_id=article_id, content=content)
        except Exception as e:
            print(e)
            self.res.update(code=GeneralCode.FAIL)
            return JsonResponse(self.res.data)
        return JsonResponse(self.res.data)


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


###############################################################
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel, Field
import json


# 测试fastapi中的请求体和校验字段

class Item(BaseModel):
    name: str = Field(default="null", min_length=1, max_length=5)
    age: int = Field(default=18, lg=120, gt=12)
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None


def test(request):
    data = request.body
    data = json.loads(data)
    ret = Item(**data)
    ret.dict(by_alias=True)
    print(ret)
    return HttpResponse("OK")
###############################################################
