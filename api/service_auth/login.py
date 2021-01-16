"""
登录视图，含极简校验
"""
from uuid import uuid4

from django.http import HttpResponse
from geetest import GeetestLib
from rest_framework.response import Response

from rest_framework.views import APIView
from api import models
from utils.code import ResMsg, GeneralCode

pc_geetest_id = 'b46d1900d0a894591916ea94ea91bd2c'
pc_geetest_key = '36fc3fe98530eea08dfc6ce76e3d24c4'


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
                avatar = str(user.avatar)
                uid = str(uuid4())
                models.UserInfo.objects.update_or_create(username=username, pwd=pwd, defaults={'token': uid})
                self.res.add_field("token", uid)
                self.res.add_field("avatar", avatar)
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
