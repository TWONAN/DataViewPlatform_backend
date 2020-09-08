from django.db import models


# Create your models here.

class UserInfo(models.Model):
    """
    用户信息表
    """
    uid = models.AutoField(primary_key=True)
    username = models.CharField(max_length=64)
    pwd = models.CharField(max_length=32)
    token = models.CharField(max_length=64)
    # 使用ImageField必须要pip Pillow
    avatar = models.ImageField(upload_to="static/avatars/", default="static/avatars/hmbb.png", verbose_name="头像")
    create_time = models.DateTimeField(auto_now_add=True, )
    email = models.CharField(max_length=128, null=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = '用户数据'


class CaseDetail(models.Model):
    """
    案例详情表
    """
    title = models.CharField(max_length=64)
    content = models.TextField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '案例详情'


class DataDetail(models.Model):
    """
    数据详情表
    """
    title = models.CharField(max_length=64, null=True)
    num = models.IntegerField(null=True)  # 实际消费
    user = models.ForeignKey(to='UserInfo', null=True)
    exp_num = models.IntegerField()  # 期望消费

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '数据详情'


class Session(models.Model):
    """
    session缓存表
    """
    STATUS_SESSION_KEY = models.CharField(max_length=64)
    USERID = models.CharField(max_length=64)


class Article(models.Model):
    """
    用户文章表
    """
    aid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64)  # 文章标题
    desc = models.CharField(max_length=255)  # 文章概述
    user = models.ForeignKey(to='UserInfo')  # 所属用户
    create_time = models.DateTimeField(auto_now_add=True)  # 创建的时间

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '文章'


class ArticleDetail(models.Model):
    """
       文章详情表
    """
    article = models.OneToOneField(to='Article', related_name='articledetail')
    content = models.TextField()

    class Meta:
        verbose_name = '文章详情'

    def __str__(self):
        return self.article.title


class PoetAndPoem(models.Model):
    """诗人及所作诗表"""
    author = models.CharField(max_length=64)
    poetry = models.CharField(max_length=128)

    class Meta:
        verbose_name = '诗人及所作诗'

    def __str__(self):
        return self.poetry


class Comment(models.Model):
    """
    评论表
    """
    cid = models.AutoField(primary_key=True)
    article = models.ForeignKey(to="Article", to_field="aid")
    user = models.ForeignKey(to="UserInfo", to_field="uid")
    content = models.CharField(max_length=255, null=False)  # 评论内容
    create_time = models.DateTimeField(auto_now_add=True)

    parent_comment = models.ForeignKey("self", null=True)

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = "评论"
        verbose_name_plural = verbose_name
