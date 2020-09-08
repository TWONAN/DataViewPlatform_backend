"""编码对应表"""
from utils.msg import GeneralMsg


class GeneralCode(object):
    INVALID_PARAMS = 10001  # *-* 无效参数 -*-
    AUTHORITY_FAIL = 10002  # *-* 授权失败 -*-
    NOT_EXCEED_100 = 10003  # *-* 暂不支持超过100 -*-
    COMMENT_NOT_NULL = 10004  # *-* 评论不能为空 -*-
    FAIL = 1001  # *-* 失败 -*-
    SUCCESS = 1000  # *-* 成功 -*-
    USERNAME_OR_PASSWORD_ERROR = 1002  # *-* 用户名或密码错误 -*-
    VERIFICATION_ERROR = 1003  # *-* 验证码错误 -*-


class ResMsg(object):
    def __init__(self, data=None, code=GeneralCode.SUCCESS):
        self._data = data
        self._code = code
        self._msg = GeneralMsg.rm_map.get(code)

    def update(self, code=None, data=None, msg=None):
        if code is not None:
            self._code = code
            self._msg = GeneralMsg.rm_map.get(code)
        if data is not None:
            self._data = data
        if msg is not None:
            self._msg = msg

    def add_field(self, name=None, value=None):
        if name is not None and value is not None:
            self.__dict__[name] = value

    @property
    def data(self):
        body = self.__dict__
        body["data"] = body.pop("_data")
        body["code"] = body.pop("_code")
        body["msg"] = body.pop("_msg")
        return body
