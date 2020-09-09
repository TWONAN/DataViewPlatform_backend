import json
import copy

# 只要是json格式的，不论是字符串还是bytes类型都可以序列化和反序列化
a = b'{"name":"li","age":18}'
b = json.loads(a)
# print(b, type(b))


a = " sad "
b = a.strip()
print(b)