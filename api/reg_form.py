from django import forms
from django.core.exceptions import ValidationError
from api import models


class Regform(forms.Form):
    """
    基于forms的注册
    """
    username = forms.CharField(
        max_length=32,
        label="用户名",
        error_messages={
            "required": "用户名不能为空",
            "max_length": "不能超过16个字符"
        },
        widget=forms.widgets.TextInput(
            attrs={"class": "form-control"}
        )
    )

    pwd = forms.CharField(
        min_length=6,
        label='密码:',
        error_messages={
            'required': '密码不能为空',
            'min_length': '至少6个字符'
        },
        widget=forms.widgets.PasswordInput(
            attrs={'class': 'form-control'},
            render_value=True
        )
    )

    re_pwd = forms.CharField(
        min_length=6,
        label='确认密码:',
        error_messages={
            'required': '密码不能为空',
            'min_length': '至少6个字符'
        },
        widget=forms.widgets.PasswordInput(
            attrs={'class': 'form-control'},
            render_value=True
        )
    )

    email = forms.EmailField(
        label='邮箱:',
        error_messages={
            'required': '邮箱不能为空',
            'invalid': '邮箱格式错误'
        },
        widget=forms.widgets.PasswordInput(
            attrs={'class': 'form-control'},
            render_value=True
        )
    )

    def clean_username(self):
        value = self.cleaned_data['username']
        if '傻逼' in value:
            raise ValidationError('包含不当字符')
        elif models.UserInfo.objects.filter(username=value):
            raise ValidationError('该用户已经被注册')
        return value

    def clean_email(self):
        email = self.cleaned_data['email']
        if models.UserInfo.objects.filter(email=email):
            raise ValidationError('该邮箱已被注册')
        return email

    def clean(self):
        pwd = self.cleaned_data.get('pwd')
        re_pwd = self.cleaned_data.get('re_pwd')
        if pwd != re_pwd:
            self.add_error('re_pwd', ValidationError('密码不一致'))
        return self.cleaned_data
