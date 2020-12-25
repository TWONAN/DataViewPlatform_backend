from django.conf.urls import url
from api import views

urlpatterns = [
    url(r'^login/$', views.LoginAPI.as_view()),
    url(r'^reg/$', views.reg),
    url(r'^case_detail/$', views.CaseDetail.as_view()),
    url(r'^data_detail/$', views.DataHandleAPI.as_view()),
    url(r'^pc-geetest/register', views.get_geetest),
    url(r'^article/$', views.ArticleAPI.as_view()),
    url(r'^poetrating/$', views.PoetRating.as_view()),
    url(r'^comments', views.CommentAPI.as_view()),
    url(r'^test/$', views.test),
    url(r'^our_poem/$', views.OurPoemAPI.as_view())
]
