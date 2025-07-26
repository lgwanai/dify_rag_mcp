"""MCP服务器测试"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.config.settings import Settings
from src.mcp.server import DifyMCPServer, create_server, run_server
from src.utils.exceptions import DifyAPIError


class TestDifyMCPServer:
    """Dify MCP服务器测试类"""

    @pytest.fixture
    def mock_settings(self) -> Settings:
        """创建模拟配置"""
        return Settings(
            dify_api_key="test-api-key",
            dify_base_url="https://api.dify.ai/v1",
            log_level="INFO",
        )

    @pytest.fixture
    def mcp_server(self, mock_settings: Settings) -> DifyMCPServer:
        """创建MCP服务器实例"""
        return DifyMCPServer(mock_settings)

    def test_server_initialization(
        self, mcp_server: DifyMCPServer, mock_settings: Settings
    ):
        """测试服务器初始化"""
        assert mcp_server.settings == mock_settings
        assert mcp_server.app is not None
        assert mcp_server.client is None  # 初始化时为None
        assert mcp_server.dataset_api is None
        assert mcp_server.document_api is None
        assert mcp_server.segment_api is None
        assert mcp_server.search_api is None

    @pytest.mark.asyncio
    async def test_initialize_success(self, mcp_server: DifyMCPServer):
        """测试初始化成功"""
        with patch("src.mcp.server.DifyAPIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            await mcp_server.initialize()

            # 验证客户端和API实例已创建
            assert mcp_server.client is not None
            assert mcp_server.dataset_api is not None
            assert mcp_server.document_api is not None
            assert mcp_server.segment_api is not None
            assert mcp_server.search_api is not None
            assert mcp_server.dataset_tools is not None
            assert mcp_server.document_tools is not None
            assert mcp_server.segment_tools is not None
            assert mcp_server.search_tools is not None

    @pytest.mark.asyncio
    async def test_initialize_with_invalid_api_key(self, mock_settings: Settings):
        """测试使用无效API密钥初始化"""
        mock_settings.dify_api_key = ""
        mcp_server = DifyMCPServer(mock_settings)

        with pytest.raises(ValueError, match="Dify API key is required"):
            await mcp_server.initialize()

    @pytest.mark.asyncio
    async def test_register_tools_success(self, mcp_server: DifyMCPServer):
        """测试注册工具成功"""
        # 先初始化
        with patch("src.mcp.server.DifyAPIClient"):
            await mcp_server.initialize()

        # 模拟工具注册
        with patch.object(
            mcp_server.dataset_tools, "register_tools"
        ) as mock_dataset_register, patch.object(
            mcp_server.document_tools, "register_tools"
        ) as mock_document_register, patch.object(
            mcp_server.segment_tools, "register_tools"
        ) as mock_segment_register, patch.object(
            mcp_server.search_tools, "register_tools"
        ) as mock_search_register:

            await mcp_server.register_tools()

            # 验证所有工具都已注册
            mock_dataset_register.assert_called_once_with(mcp_server.app)
            mock_document_register.assert_called_once_with(mcp_server.app)
            mock_segment_register.assert_called_once_with(mcp_server.app)
            mock_search_register.assert_called_once_with(mcp_server.app)

    @pytest.mark.asyncio
    async def test_register_resources_success(self, mcp_server: DifyMCPServer):
        """测试注册资源成功"""
        # 先初始化
        with patch("src.mcp.server.DifyAPIClient"):
            await mcp_server.initialize()

        # 模拟资源注册
        with patch.object(
            mcp_server.dataset_resource, "register_resources"
        ) as mock_dataset_register, patch.object(
            mcp_server.document_resource, "register_resources"
        ) as mock_document_register, patch.object(
            mcp_server.segment_resource, "register_resources"
        ) as mock_segment_register:

            await mcp_server.register_resources()

            # 验证所有资源都已注册
            mock_dataset_register.assert_called_once_with(mcp_server.app)
            mock_document_register.assert_called_once_with(mcp_server.app)
            mock_segment_register.assert_called_once_with(mcp_server.app)

    @pytest.mark.asyncio
    async def test_start_stdio_success(self, mcp_server: DifyMCPServer):
        """测试启动stdio传输成功"""
        with patch("src.mcp.server.DifyAPIClient"), patch.object(
            mcp_server.app, "run_stdio"
        ) as mock_run_stdio:

            await mcp_server.initialize()
            await mcp_server.register_tools()
            await mcp_server.register_resources()

            await mcp_server.start(transport="stdio")

            mock_run_stdio.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_sse_success(self, mcp_server: DifyMCPServer):
        """测试启动SSE传输成功"""
        with patch("src.mcp.server.DifyAPIClient"), patch.object(
            mcp_server.app, "run_sse"
        ) as mock_run_sse:

            await mcp_server.initialize()
            await mcp_server.register_tools()
            await mcp_server.register_resources()

            await mcp_server.start(transport="sse", host="localhost", port=8000)

            mock_run_sse.assert_called_once_with("localhost", 8000)

    @pytest.mark.asyncio
    async def test_start_websocket_success(self, mcp_server: DifyMCPServer):
        """测试启动WebSocket传输成功"""
        with patch("src.mcp.server.DifyAPIClient"), patch.object(
            mcp_server.app, "run_websocket"
        ) as mock_run_websocket:

            await mcp_server.initialize()
            await mcp_server.register_tools()
            await mcp_server.register_resources()

            await mcp_server.start(transport="websocket", host="0.0.0.0", port=9000)

            mock_run_websocket.assert_called_once_with("0.0.0.0", 9000)

    @pytest.mark.asyncio
    async def test_start_invalid_transport_raises_error(
        self, mcp_server: DifyMCPServer
    ):
        """测试无效传输类型抛出错误"""
        with patch("src.mcp.server.DifyAPIClient"):
            await mcp_server.initialize()

            with pytest.raises(ValueError, match="Unsupported transport type"):
                await mcp_server.start(transport="invalid")

    @pytest.mark.asyncio
    async def test_start_without_initialization_raises_error(
        self, mcp_server: DifyMCPServer
    ):
        """测试未初始化就启动抛出错误"""
        with pytest.raises(RuntimeError, match="Server not initialized"):
            await mcp_server.start()

    @pytest.mark.asyncio
    async def test_cleanup_success(self, mcp_server: DifyMCPServer):
        """测试清理资源成功"""
        # 先初始化
        with patch("src.mcp.server.DifyAPIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            await mcp_server.initialize()

            # 执行清理
            await mcp_server.cleanup()

            # 验证客户端已关闭
            mock_client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_without_client(self, mcp_server: DifyMCPServer):
        """测试没有客户端时的清理"""
        # 直接清理（没有初始化）
        await mcp_server.cleanup()  # 应该不抛出错误

    @pytest.mark.asyncio
    async def test_health_check_success(self, mcp_server: DifyMCPServer):
        """测试健康检查成功"""
        with patch("src.mcp.server.DifyAPIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.health_check.return_value = True
            mock_client_class.return_value = mock_client

            await mcp_server.initialize()

            result = await mcp_server.health_check()

            assert result is True
            mock_client.health_check.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_failure(self, mcp_server: DifyMCPServer):
        """测试健康检查失败"""
        with patch("src.mcp.server.DifyAPIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.health_check.side_effect = DifyAPIError("Health check failed")
            mock_client_class.return_value = mock_client

            await mcp_server.initialize()

            result = await mcp_server.health_check()

            assert result is False

    @pytest.mark.asyncio
    async def test_health_check_without_client(self, mcp_server: DifyMCPServer):
        """测试没有客户端时的健康检查"""
        result = await mcp_server.health_check()
        assert result is False

    def test_get_server_info(self, mcp_server: DifyMCPServer):
        """测试获取服务器信息"""
        info = mcp_server.get_server_info()

        assert "name" in info
        assert "version" in info
        assert "description" in info
        assert "capabilities" in info
        assert info["name"] == "Dify RAG MCP Server"

    @pytest.mark.asyncio
    async def test_context_manager_usage(self, mock_settings: Settings):
        """测试上下文管理器使用"""
        with patch("src.mcp.server.DifyAPIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            async with DifyMCPServer(mock_settings) as server:
                # 验证服务器已初始化
                assert server.client is not None

            # 验证清理已调用
            mock_client.close.assert_called_once()


class TestServerHelperFunctions:
    """服务器辅助函数测试类"""

    @pytest.mark.asyncio
    async def test_create_server_success(self):
        """测试创建服务器成功"""
        with patch("src.mcp.server.Settings") as mock_settings_class, patch(
            "src.mcp.server.DifyMCPServer"
        ) as mock_server_class:

            mock_settings = MagicMock()
            mock_settings_class.return_value = mock_settings

            mock_server = AsyncMock()
            mock_server_class.return_value = mock_server

            server = await create_server()

            # 验证设置和服务器已创建
            mock_settings_class.assert_called_once()
            mock_server_class.assert_called_once_with(mock_settings)
            mock_server.initialize.assert_called_once()
            mock_server.register_tools.assert_called_once()
            mock_server.register_resources.assert_called_once()

            assert server == mock_server

    @pytest.mark.asyncio
    async def test_create_server_with_custom_settings(self):
        """测试使用自定义设置创建服务器"""
        custom_settings = Settings(
            dify_api_key="custom-key", dify_base_url="https://custom.api.com"
        )

        with patch("src.mcp.server.DifyMCPServer") as mock_server_class:
            mock_server = AsyncMock()
            mock_server_class.return_value = mock_server

            server = await create_server(custom_settings)

            # 验证使用了自定义设置
            mock_server_class.assert_called_once_with(custom_settings)
            mock_server.initialize.assert_called_once()

            assert server == mock_server

    @pytest.mark.asyncio
    async def test_run_server_stdio(self):
        """测试运行stdio服务器"""
        with patch("src.mcp.server.create_server") as mock_create_server:
            mock_server = AsyncMock()
            mock_create_server.return_value = mock_server

            await run_server(transport="stdio")

            # 验证服务器已创建和启动
            mock_create_server.assert_called_once_with(None)
            mock_server.start.assert_called_once_with(
                transport="stdio", host=None, port=None
            )

    @pytest.mark.asyncio
    async def test_run_server_sse(self):
        """测试运行SSE服务器"""
        with patch("src.mcp.server.create_server") as mock_create_server:
            mock_server = AsyncMock()
            mock_create_server.return_value = mock_server

            await run_server(transport="sse", host="localhost", port=8080)

            # 验证服务器已创建和启动
            mock_create_server.assert_called_once_with(None)
            mock_server.start.assert_called_once_with(
                transport="sse", host="localhost", port=8080
            )

    @pytest.mark.asyncio
    async def test_run_server_with_custom_settings(self):
        """测试使用自定义设置运行服务器"""
        custom_settings = Settings(dify_api_key="test-key")

        with patch("src.mcp.server.create_server") as mock_create_server:
            mock_server = AsyncMock()
            mock_create_server.return_value = mock_server

            await run_server(
                settings=custom_settings,
                transport="websocket",
                host="0.0.0.0",
                port=9000,
            )

            # 验证使用了自定义设置
            mock_create_server.assert_called_once_with(custom_settings)
            mock_server.start.assert_called_once_with(
                transport="websocket", host="0.0.0.0", port=9000
            )

    @pytest.mark.asyncio
    async def test_run_server_with_cleanup_on_error(self):
        """测试服务器运行出错时的清理"""
        with patch("src.mcp.server.create_server") as mock_create_server:
            mock_server = AsyncMock()
            mock_server.start.side_effect = Exception("Server error")
            mock_create_server.return_value = mock_server

            with pytest.raises(Exception, match="Server error"):
                await run_server()

            # 验证清理已调用
            mock_server.cleanup.assert_called_once()
