"""Dify API客户端"""

import json
from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin

import httpx

from config.settings import get_settings

from ..utils.exceptions import (AuthenticationError, DifyAPIError,
                                NetworkError, RateLimitError,
                                ResourceNotFoundError, TimeoutError)
from ..utils.logger import get_logger


class DifyAPIClient:
    """Dify API客户端基础类"""

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """初始化客户端

        Args:
            base_url: Dify服务器基础URL
            api_key: API密钥
        """
        self.settings = get_settings()
        self.logger = get_logger(__name__)

        self.base_url = base_url or self.settings.dify_base_url
        self.api_key = api_key or self.settings.dify_api_key

        if not self.base_url:
            raise ValueError("Dify base URL is required")
        if not self.api_key:
            raise ValueError("Dify API key is required")

        # 确保base_url以/结尾
        if not self.base_url.endswith("/"):
            self.base_url += "/"

        # 创建HTTP客户端
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout=self.settings.http_timeout),
            headers=self._get_default_headers(),
        )

    def _get_default_headers(self) -> Dict[str, str]:
        """获取默认请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"dify-rag-mcp/{self.settings.mcp_server_version}",
        }

    def _build_url(self, endpoint: str) -> str:
        """构建完整的API URL

        Args:
            endpoint: API端点

        Returns:
            完整的API URL
        """
        # 移除endpoint开头的/
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]

        return urljoin(self.base_url, endpoint)

    async def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """处理API响应

        Args:
            response: HTTP响应对象

        Returns:
            解析后的JSON数据

        Raises:
            DifyAPIError: API错误
            AuthenticationError: 认证错误
            ResourceNotFoundError: 资源未找到
            RateLimitError: 速率限制
        """
        try:
            # 记录响应信息
            self.logger.debug(f"API Response: {response.status_code} {response.url}")

            # 打印响应内容用于调试
            response_text = response.text
            self.logger.debug(f"Response content: {response_text[:500]}...")

            # 处理不同的HTTP状态码
            if response.status_code == 200:
                if not response_text.strip():
                    self.logger.warning("Empty response received")
                    return {}
                return response.json()
            elif response.status_code == 201:
                return response.json()
            elif response.status_code == 204:
                return {"success": True}
            elif response.status_code == 400:
                error_data = response.json() if response.content else {}
                raise DifyAPIError(
                    f"Bad request: {error_data.get('message', 'Invalid request')}",
                    status_code=400,
                    response_data=error_data,
                )
            elif response.status_code == 401:
                raise AuthenticationError("Invalid API key or authentication failed")
            elif response.status_code == 403:
                raise AuthenticationError("Access forbidden")
            elif response.status_code == 404:
                raise ResourceNotFoundError("Resource not found")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status_code >= 500:
                error_data = response.json() if response.content else {}
                raise DifyAPIError(
                    f"Server error: {error_data.get('message', 'Internal server error')}",
                    status_code=response.status_code,
                    response_data=error_data,
                )
            else:
                error_data = response.json() if response.content else {}
                raise DifyAPIError(
                    f"Unexpected status code {response.status_code}: {error_data.get('message', 'Unknown error')}",
                    status_code=response.status_code,
                    response_data=error_data,
                )

        except (json.JSONDecodeError, ValueError):
            raise DifyAPIError(
                f"Invalid JSON response from server (status: {response.status_code})",
                status_code=response.status_code,
            )

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """发送HTTP请求

        Args:
            method: HTTP方法
            endpoint: API端点
            params: URL参数
            json_data: JSON数据
            data: 表单数据
            files: 文件数据
            headers: 额外的请求头

        Returns:
            API响应数据
        """
        url = self._build_url(endpoint)

        # 合并请求头
        request_headers = self._get_default_headers()
        if headers:
            request_headers.update(headers)

        # 如果有文件上传，移除Content-Type让httpx自动设置
        if files:
            request_headers.pop("Content-Type", None)

        try:
            self.logger.debug(f"API Request: {method.upper()} {url}")
            if params:
                self.logger.debug(f"Params: {params}")
            if json_data:
                self.logger.debug(f"JSON: {json_data}")

            response = await self.client.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                data=data,
                files=files,
                headers=request_headers,
            )

            return await self._handle_response(response)

        except httpx.TimeoutException as e:
            self.logger.error(f"Request timeout: {e}")
            raise TimeoutError(f"Request timeout: {e}")
        except httpx.NetworkError as e:
            self.logger.error(f"Network error: {e}")
            raise NetworkError(f"Network error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise DifyAPIError(f"Unexpected error: {e}")

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """发送GET请求"""
        return await self._request("GET", endpoint, params=params, headers=headers)

    async def post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """发送POST请求"""
        return await self._request(
            "POST",
            endpoint,
            json_data=json_data,
            data=data,
            files=files,
            headers=headers,
        )

    async def put(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """发送PUT请求"""
        return await self._request(
            "PUT",
            endpoint,
            json_data=json_data,
            data=data,
            files=files,
            headers=headers,
        )

    async def patch(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """发送PATCH请求"""
        return await self._request(
            "PATCH", endpoint, json_data=json_data, headers=headers
        )

    async def delete(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """发送DELETE请求"""
        return await self._request("DELETE", endpoint, headers=headers)

    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()

    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
