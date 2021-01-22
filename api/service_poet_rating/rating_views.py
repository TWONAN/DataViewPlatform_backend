"""
处理诗歌排行
"""
import requests
import logging
from django.db.models import Count
from lxml import html
from rest_framework.response import Response
from rest_framework.views import APIView
from api import models
from utils.code import ResMsg, GeneralCode

logger = logging.getLogger("error")

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


# 诗歌排行显示
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
            logger.error(e)
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
