
class AppError(Exception):
    def __init__(self, message, error_code):
        # 调用父类的构造函数
        super().__init__(message)
        self.error_code = error_code
        self.message = message

    def __str__(self):
        return f"[AppError Code {self.error_code}] {super().__str__()}"
