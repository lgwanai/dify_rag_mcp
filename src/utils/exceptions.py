"""异常定义模块"""

from typing import Any, Dict, Optional


class DifyMCPException(Exception):
    """基础异常类"""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class DifyAPIError(DifyMCPException):
    """Dify API 错误"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code="DIFY_API_ERROR")
        self.status_code = status_code
        self.response_data = response_data or {}


class MCPError(DifyMCPException):
    """MCP 服务器错误"""

    def __init__(self, message: str, tool_name: Optional[str] = None):
        super().__init__(message, code="MCP_ERROR")
        self.tool_name = tool_name


class ValidationError(DifyMCPException):
    """验证错误"""

    def __init__(
        self, message: str, field: Optional[str] = None, value: Optional[Any] = None
    ):
        super().__init__(message, code="VALIDATION_ERROR")
        self.field = field
        self.value = value


class ConfigurationError(DifyMCPException):
    """配置错误"""

    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(message, code="CONFIGURATION_ERROR")
        self.config_key = config_key


class AuthenticationError(DifyMCPException):
    """认证错误"""

    def __init__(self, message: str = "API Key 无效或已过期"):
        super().__init__(message, code="AUTHENTICATION_ERROR")


class ResourceNotFoundError(DifyMCPException):
    """资源未找到错误"""

    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
    ):
        super().__init__(message, code="RESOURCE_NOT_FOUND")
        self.resource_type = resource_type
        self.resource_id = resource_id


class RateLimitError(DifyMCPException):
    """速率限制错误"""

    def __init__(
        self, message: str = "API 请求频率超出限制", retry_after: Optional[int] = None
    ):
        super().__init__(message, code="RATE_LIMIT_ERROR")
        self.retry_after = retry_after


class NetworkError(DifyMCPException):
    """网络错误"""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message, code="NETWORK_ERROR")
        self.original_error = original_error


class TimeoutError(DifyMCPException):
    """超时错误"""

    def __init__(
        self, message: str = "请求超时", timeout_seconds: Optional[int] = None
    ):
        super().__init__(message, code="TIMEOUT_ERROR")
        self.timeout_seconds = timeout_seconds
