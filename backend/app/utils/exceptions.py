from fastapi import HTTPException


class DocumentParseError(Exception):
    """文档解析错误"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class LLMError(Exception):
    """LLM调用错误"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(HTTPException):
    """资源未找到"""
    def __init__(self, resource: str = "资源"):
        super().__init__(status_code=404, detail=f"{resource}不存在")


class BadRequestError(HTTPException):
    """请求参数错误"""
    def __init__(self, message: str):
        super().__init__(status_code=400, detail=message)
