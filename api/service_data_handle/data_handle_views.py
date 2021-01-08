"""
数据处理详情序列化
"""
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from api import models
from utils.code import ResMsg, GeneralCode


class DataDetailserializers(serializers.ModelSerializer):
    class Meta:
        model = models.DataDetail
        fields = '__all__'

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