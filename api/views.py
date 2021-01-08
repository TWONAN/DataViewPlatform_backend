from django.shortcuts import render, HttpResponse, redirect

# Create your views here.


###############################################################
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel, Field
import json


# 测试fastapi中的请求体和校验字段

class Item(BaseModel):
    name: str = Field(default="null", min_length=1, max_length=5)
    age: int = Field(default=18, lg=120, gt=12)
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None


def test(request):
    data = request.body
    data = json.loads(data)
    ret = Item(**data)
    ret.dict(by_alias=True)
    print(ret)
    return HttpResponse("OK")
###############################################################
