from django.contrib import admin
from api import models
# Register your models here.

admin.site.register(models.CaseDetail)
admin.site.register(models.DataDetail)
admin.site.register(models.UserInfo)
admin.site.register(models.Article)
admin.site.register(models.ArticleDetail)