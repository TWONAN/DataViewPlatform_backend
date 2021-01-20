"""
处理评论相关
"""
from datetime import datetime

from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, QueryDict
from rest_framework.response import Response
from rest_framework.views import APIView

from api import models
from utils.code import ResMsg, GeneralCode


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
                   filter(article_id=article_id, status=1). \
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


class MyCommentAPI(APIView):
    def __init__(self, *args, **kwargs):
        super(MyCommentAPI).__init__(*args, **kwargs)
        self.res = ResMsg()

    def get(self, request, *args, **kwargs):
        """
        查看自己评论
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        page = int(request.GET.get("page"))
        size = 5  # 默认5条每页
        usertoken = request.GET.get("usertoken")
        username = request.GET.get("username")
        user = models.UserInfo.objects.filter(username=username, token=usertoken)
        # *-* 验证用户 -*-
        if not user:
            self.res.update(code=GeneralCode.AUTHORITY_FAIL)
            return Response(self.res.data)

        query = models.Comment.objects.filter(user=user, status=1). \
            values("article__title", 'pk', 'content',
                   "article__articledetail__content",
                   "article__aid",
                   'parent_comment_id',
                   'create_time', 'user'). \
            order_by("-create_time")
        count = query.count()
        query = query[(page - 1) * size:page * size]
        for item in query:
            create_time = item.get("create_time")
            item["create_time"] = create_time.strftime("%Y-%m-%d %H:%M:%S")
        self.res.update(data=query)
        self.res.add_field("total_page", count)
        return Response(self.res.data)

    def delete(self, request, *args, **kwargs):
        """
        删除自己评论
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        data = QueryDict(request.body)
        cid = data.get("cid")
        del_obj = models.Comment.objects.filter(cid=cid)
        if del_obj:
            del_obj.update(status=0)
        return Response(self.res.data)


class ReplyAPI(APIView):
    def __init__(self, *args, **kwargs):
        super(ReplyAPI).__init__(*args, **kwargs)
        self.res = ResMsg()

    def get(self, request, *args, **kwargs):
        """
        查看别人的评论
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        page = int(request.GET.get("page"))
        size = 5  # 默认5条每页
        usertoken = request.GET.get("usertoken")
        username = request.GET.get("username")
        user = models.UserInfo.objects.filter(username=username, token=usertoken)

        # *-* 验证用户 -*-
        if not user:
            self.res.update(code=GeneralCode.AUTHORITY_FAIL)
            return Response(self.res.data)

        # 查询他人评论
        article_list = models.Article.objects.filter(user=user).values("aid")
        reply_query = models.Comment.objects.filter(article__in=article_list)
        print(reply_query)

