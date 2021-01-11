from django.conf.urls import url
from api import views
from api.service_auth.login import LoginAPI
from api.service_auth.login import get_geetest
from api.service_auth.reg import reg
from api.service_data_handle.data_handle_views import DataHandleAPI
from api.service_our_article.article_views import ArticleAPI
from api.service_our_article.comments_views import CommentAPI
from api.service_our_poem.our_poem_views import OurPoemAPI
from api.service_poet_rating.rating_views import PoetRating
from api.service_wanna_to_do.wanna_views import OurWannaTodo
from api.service_daily_notice.notice_views import NoticeDaily

urlpatterns = [
    url(r'^login/$', LoginAPI.as_view()),  # 登录视图
    url(r'^pc-geetest/register', get_geetest),  # 极简校验
    url(r'^reg/$', reg),  # 注册视图
    url(r'^our_poem/$', OurPoemAPI.as_view()),  # 我们的诗歌视图
    url(r'^article/$', ArticleAPI.as_view()),  # 我们的文章视图
    url(r'^wanna_to_do/$', OurWannaTodo.as_view()),  # 我们想做的事视图
    url(r'^data_detail/$', DataHandleAPI.as_view()),  # 数据处理视图
    url(r'^comments', CommentAPI.as_view()),  # 处理评论相关视图
    url(r'^poetrating/$', PoetRating.as_view()),  # 诗歌排行视图
    url(r'^daily_notice/$', NoticeDaily.as_view()),  # 每日提示视图

    url(r'^test/$', views.test),
]
