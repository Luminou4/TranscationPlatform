class RequestResponse:
    def __init__(self):
        self.code: int = 0
        self.msg: str = ""
        self.data = {}

    def toJson(self):
        return {
            "code": self.code,
            "msg": self.msg,
            "data": self.data,
        }

    @staticmethod
    def error_response(code, msg):
        return {
            "code": code,
            "msg": msg,
            "data": {},

        }

    @staticmethod
    def success_response(data):
        return {
            "code": 0,
            "msg": "成功",
            "data": data,
        }
