"""测试配置文件"""

import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.api import (DatasetAPI, DifyAPIClient, DocumentAPI, SearchAPI,
                     SegmentAPI)
from src.config import Settings, get_settings
from src.mcp.server import DifyMCPServer


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """创建事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings() -> Settings:
    """测试配置"""
    return Settings(
        dify={"base_url": "http://localhost:8000", "api_key": "test-api-key"},
        logging={
            "level": "DEBUG",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file_enabled": False,
        },
        mcp_server={
            "name": "dify-rag-mcp-test",
            "version": "0.1.0",
            "description": "Test MCP Server",
        },
        development={"debug": True, "reload": False, "testing": True},
    )


@pytest.fixture
def mock_api_client() -> AsyncMock:
    """模拟API客户端"""
    client = AsyncMock(spec=DifyAPIClient)
    client.get = AsyncMock()
    client.post = AsyncMock()
    client.put = AsyncMock()
    client.patch = AsyncMock()
    client.delete = AsyncMock()
    client.close = AsyncMock()
    return client


@pytest.fixture
def mock_dataset_api(mock_api_client: AsyncMock) -> AsyncMock:
    """模拟知识库API"""
    api = AsyncMock(spec=DatasetAPI)
    api.client = mock_api_client
    return api


@pytest.fixture
def mock_document_api(mock_api_client: AsyncMock) -> AsyncMock:
    """模拟文档API"""
    api = AsyncMock(spec=DocumentAPI)
    api.client = mock_api_client
    return api


@pytest.fixture
def mock_segment_api(mock_api_client: AsyncMock) -> AsyncMock:
    """模拟分段API"""
    api = AsyncMock(spec=SegmentAPI)
    api.client = mock_api_client
    return api


@pytest.fixture
def mock_search_api(mock_api_client: AsyncMock) -> AsyncMock:
    """模拟搜索API"""
    api = AsyncMock(spec=SearchAPI)
    api.client = mock_api_client
    return api


@pytest.fixture
async def mock_mcp_server(
    test_settings: Settings,
    mock_api_client: AsyncMock,
    mock_dataset_api: AsyncMock,
    mock_document_api: AsyncMock,
    mock_segment_api: AsyncMock,
    mock_search_api: AsyncMock,
) -> AsyncGenerator[DifyMCPServer, None]:
    """模拟MCP服务器"""
    server = DifyMCPServer()

    # 注入模拟对象
    server.settings = test_settings
    server.api_client = mock_api_client
    server.dataset_api = mock_dataset_api
    server.document_api = mock_document_api
    server.segment_api = mock_segment_api
    server.search_api = mock_search_api

    yield server

    # 清理
    if server.api_client:
        await server.api_client.close()


# 测试数据
@pytest.fixture
def sample_dataset_data() -> dict:
    """示例知识库数据"""
    return {
        "id": "dataset-123",
        "name": "测试知识库",
        "description": "这是一个测试知识库",
        "permission": "only_me",
        "data_source_type": "upload_file",
        "indexing_technique": "high_quality",
        "app_count": 0,
        "document_count": 5,
        "word_count": 1000,
        "created_by": "user-123",
        "created_at": 1640995200,
        "updated_by": "user-123",
        "updated_at": 1640995200,
        "embedding_model": "text-embedding-ada-002",
        "embedding_model_provider": "openai",
        "embedding_available": True,
    }


@pytest.fixture
def sample_document_data() -> dict:
    """示例文档数据"""
    return {
        "id": "document-123",
        "position": 1,
        "data_source_type": "upload_file",
        "data_source_info": {"upload_file_id": "file-123"},
        "dataset_process_rule_id": "rule-123",
        "name": "测试文档.txt",
        "created_from": "api",
        "created_by": "user-123",
        "created_at": 1640995200,
        "tokens": 500,
        "indexing_status": "completed",
        "error": None,
        "enabled": True,
        "disabled_at": None,
        "disabled_by": None,
        "archived": False,
        "display_status": "available",
        "word_count": 200,
        "hit_count": 10,
        "doc_form": "text_model",
    }


@pytest.fixture
def sample_segment_data() -> dict:
    """示例分段数据"""
    return {
        "id": "segment-123",
        "position": 1,
        "document_id": "document-123",
        "content": "这是一个测试分段的内容。",
        "word_count": 10,
        "tokens": 15,
        "keywords": ["测试", "分段"],
        "index_node_id": "node-123",
        "index_node_hash": "hash-123",
        "hit_count": 5,
        "enabled": True,
        "disabled_at": None,
        "disabled_by": None,
        "status": "completed",
        "created_by": "user-123",
        "created_at": 1640995200,
        "indexing_at": 1640995200,
        "completed_at": 1640995200,
        "error": None,
        "stopped_at": None,
    }


@pytest.fixture
def sample_search_response() -> dict:
    """示例搜索响应数据"""
    return {
        "query": {
            "content": "测试查询",
            "search_method": "semantic_search",
            "top_k": 10,
            "score_threshold": 0.5,
        },
        "records": [
            {
                "segment": {
                    "id": "segment-123",
                    "position": 1,
                    "document_id": "document-123",
                    "content": "这是一个测试分段的内容。",
                    "word_count": 10,
                    "tokens": 15,
                    "keywords": ["测试", "分段"],
                    "hit_count": 5,
                },
                "score": 0.85,
                "tsne_position": {"x": 0.1, "y": 0.2},
            }
        ],
    }


# 测试工具函数
def assert_api_called_with(mock_api: AsyncMock, method: str, endpoint: str, **kwargs):
    """断言API被正确调用"""
    getattr(mock_api, method).assert_called_once()
    call_args = getattr(mock_api, method).call_args

    if call_args:
        args, call_kwargs = call_args
        if args:
            assert args[0] == endpoint
        for key, value in kwargs.items():
            assert call_kwargs.get(key) == value


def create_mock_response(data: dict, status_code: int = 200):
    """创建模拟响应"""
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.json.return_value = data
    mock_response.content = True
    return mock_response
