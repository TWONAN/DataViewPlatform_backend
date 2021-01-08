"""
注册视图函数
"""
from django.http import JsonResponse
from django.shortcuts import render

from api import reg_form, models
from utils.code import ResMsg, GeneralCode


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
