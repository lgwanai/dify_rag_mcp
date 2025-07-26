"""Dify MCP服务器"""

import asyncio
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from pydantic import BaseModel

from src.api import DatasetAPI, DifyAPIClient, DocumentAPI, SearchAPI, SegmentAPI
from src.config import get_settings
from src.utils.exceptions import DifyMCPException
from src.utils.logger import get_logger, setup_logger
from .resources import DatasetResource, DocumentResource, SegmentResource
from .tools import DatasetTools, DocumentTools, SearchTools, SegmentTools


class DifyMCPServer:
    """Dify MCP服务器主类"""

    def __init__(self):
        """初始化MCP服务器"""
        self.settings = get_settings()
        self.logger = get_logger(__name__)

        # 初始化FastMCP服务器
        self.mcp = FastMCP(
            name=self.settings.mcp_server_name, version=self.settings.mcp_server_version
        )

        # API客户端
        self.api_client: Optional[DifyAPIClient] = None
        self.dataset_api: Optional[DatasetAPI] = None
        self.document_api: Optional[DocumentAPI] = None
        self.segment_api: Optional[SegmentAPI] = None
        self.search_api: Optional[SearchAPI] = None

        # 工具和资源
        self.dataset_tools: Optional[DatasetTools] = None
        self.document_tools: Optional[DocumentTools] = None
        self.segment_tools: Optional[SegmentTools] = None
        self.search_tools: Optional[SearchTools] = None

        self.dataset_resource: Optional[DatasetResource] = None
        self.document_resource: Optional[DocumentResource] = None
        self.segment_resource: Optional[SegmentResource] = None

        self._initialized = False

    async def initialize(self):
        """初始化服务器组件"""
        if self._initialized:
            return

        try:
            self.logger.info("Initializing Dify MCP Server...")

            # 初始化API客户端
            self.api_client = DifyAPIClient(
                base_url=self.settings.dify_base_url, api_key=self.settings.dify_api_key
            )

            # 初始化API模块
            self.dataset_api = DatasetAPI(self.api_client)
            self.document_api = DocumentAPI(self.api_client)
            self.segment_api = SegmentAPI(self.api_client)
            self.search_api = SearchAPI(self.api_client)

            # 初始化工具
            self.dataset_tools = DatasetTools(self.dataset_api)
            self.document_tools = DocumentTools(self.document_api)
            self.segment_tools = SegmentTools(self.segment_api)
            self.search_tools = SearchTools(self.search_api)

            # 初始化资源
            self.dataset_resource = DatasetResource(self.dataset_api)
            self.document_resource = DocumentResource(self.document_api)
            self.segment_resource = SegmentResource(self.segment_api)

            # 注册工具和资源
            self._register_tools()
            self._register_resources()

            self._initialized = True
            self.logger.info("Dify MCP Server initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize Dify MCP Server: {e}")
            raise DifyMCPException(f"Server initialization failed: {e}")

    def _register_tools(self):
        """注册MCP工具"""
        self.logger.info("Registering MCP tools...")

        # 注册知识库工具
        if self.dataset_tools:
            self.dataset_tools.register_tools(self.mcp)

        # 注册文档工具
        if self.document_tools:
            self.document_tools.register_tools(self.mcp)

        # 注册分段工具
        if self.segment_tools:
            self.segment_tools.register_tools(self.mcp)

        # 注册搜索工具
        if self.search_tools:
            self.search_tools.register_tools(self.mcp)

        self.logger.info("MCP tools registered successfully")

    def _register_resources(self):
        """注册MCP资源"""
        self.logger.info("Registering MCP resources...")

        # 注册知识库资源
        if self.dataset_resource:
            self.dataset_resource.register_resources(self.mcp)

        # 注册文档资源
        if self.document_resource:
            self.document_resource.register_resources(self.mcp)

        # 注册分段资源
        if self.segment_resource:
            self.segment_resource.register_resources(self.mcp)

        self.logger.info("MCP resources registered successfully")

    async def start(
        self, transport: str = "stdio", host: str = "localhost", port: int = 8000
    ):
        """启动MCP服务器

        Args:
            transport: 传输方式 (stdio, sse, websocket)
            host: 主机地址 (仅用于sse和websocket)
            port: 端口号 (仅用于sse和websocket)
        """
        if not self._initialized:
            await self.initialize()

        try:
            self.logger.info(f"Starting Dify MCP Server with transport: {transport}")

            if transport == "stdio":
                # 使用stdio传输
                await self.mcp.run_stdio_async()
            elif transport == "sse":
                # 使用SSE传输
                await self.mcp.run_sse_async(host=host, port=port)
            elif transport == "websocket":
                # 使用WebSocket传输
                await self.mcp.run_streamable_http_async(host=host, port=port)
            else:
                raise ValueError(f"Unsupported transport: {transport}")

        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal, shutting down...")
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            raise DifyMCPException(f"Server runtime error: {e}")
        finally:
            await self.cleanup()

    async def cleanup(self):
        """清理资源"""
        self.logger.info("Cleaning up server resources...")

        try:
            if self.api_client:
                await self.api_client.close()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

        self.logger.info("Server cleanup completed")

    async def health_check(self) -> Dict[str, Any]:
        """健康检查

        Returns:
            健康状态信息
        """
        try:
            # 检查API连接
            if not self.api_client:
                return {"status": "unhealthy", "message": "API client not initialized"}

            # 尝试获取知识库列表来测试连接
            if self.dataset_api:
                await self.dataset_api.list_datasets()

            return {
                "status": "healthy",
                "message": "Server is running normally",
                "version": self.settings.mcp_server_version,
                "dify_base_url": self.settings.dify_base_url,
                "initialized": self._initialized,
            }

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "message": f"Health check failed: {e}"}

    async def get_server_info(self) -> Dict[str, Any]:
        """获取服务器信息

        Returns:
            服务器信息
        """
        return {
            "name": "dify-rag-mcp",
            "version": self.settings.mcp_server_version,
            "description": "Dify知识库API MCP服务器",
            "author": "Dify RAG MCP Team",
            "dify_config": {
                "base_url": self.settings.dify_base_url,
                "api_key_configured": bool(self.settings.dify_api_key),
            },
            "mcp_config": {
                "server_name": self.settings.mcp_server_name,
                "version": self.settings.mcp_server_version,
                "description": "Dify知识库API MCP服务器，提供知识库管理、文档管理、分段管理和检索功能",
            },
            "features": [
                "知识库管理",
                "文档管理",
                "分段管理",
                "语义搜索",
                "关键词搜索",
                "混合搜索",
                "标签管理",
                "批量操作",
            ],
            "initialized": self._initialized,
        }

    def get_mcp_server(self) -> FastMCP:
        """获取FastMCP服务器实例

        Returns:
            FastMCP服务器实例
        """
        return self.mcp

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.cleanup()


# 便捷函数
async def create_server() -> DifyMCPServer:
    """创建并初始化Dify MCP服务器

    Returns:
        初始化后的服务器实例
    """
    server = DifyMCPServer()
    await server.initialize()
    return server


async def run_server(
    transport: str = "stdio",
    host: str = "localhost",
    port: int = 8000,
    setup_logging: bool = True,
):
    """运行Dify MCP服务器

    Args:
        transport: 传输方式
        host: 主机地址
        port: 端口号
        setup_logging: 是否设置日志
    """
    if setup_logging:
        setup_logger()

    server = DifyMCPServer()
    await server.start(transport=transport, host=host, port=port)


if __name__ == "__main__":
    # 直接运行服务器
    asyncio.run(run_server())
