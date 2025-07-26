"""端到端集成测试"""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from src.config.settings import Settings
from src.mcp.server import DifyMCPServer, create_server
from src.models.common import SearchRequest
from src.models.dataset import DatasetCreate
from src.models.document import DocumentCreateByText
from src.models.segment import SegmentCreate


@pytest.mark.integration
class TestE2EIntegration:
    """端到端集成测试类"""

    @pytest.fixture
    def test_settings(self) -> Settings:
        """创建测试配置"""
        return Settings(
            dify_api_key="test-api-key-12345",
            dify_base_url="https://api.dify.ai/v1",
            log_level="DEBUG",
        )

    @pytest.fixture
    async def mcp_server(self, test_settings: Settings) -> DifyMCPServer:
        """创建并初始化MCP服务器"""
        with patch("src.api.client.httpx.AsyncClient") as mock_client:
            # 模拟HTTP客户端
            mock_client.return_value.__aenter__.return_value = AsyncMock()

            server = DifyMCPServer(test_settings)
            await server.initialize()
            await server.register_tools()
            await server.register_resources()

            yield server

            await server.cleanup()

    @pytest.mark.asyncio
    async def test_complete_workflow(self, mcp_server: DifyMCPServer):
        """测试完整的工作流程：创建知识库 -> 添加文档 -> 创建分段 -> 搜索"""
        # 模拟API响应数据
        dataset_data = {
            "id": "dataset-test-123",
            "name": "测试知识库",
            "description": "端到端测试知识库",
            "provider": "vendor",
            "permission": "only_me",
            "data_source_type": "upload_file",
            "indexing_technique": "high_quality",
            "app_count": 0,
            "document_count": 0,
            "word_count": 0,
            "created_by": "user-123",
            "created_at": 1640995200,
            "updated_by": "user-123",
            "updated_at": 1640995200,
        }

        document_data = {
            "id": "doc-test-123",
            "name": "测试文档",
            "character_count": 100,
            "word_count": 50,
            "tokens": 25,
            "status": "completed",
            "error": None,
            "enabled": True,
            "disabled_at": None,
            "disabled_by": None,
            "archived": False,
            "display_status": "available",
            "created_from": "api",
            "created_by": "user-123",
            "created_at": 1640995200,
            "updated_at": 1640995200,
            "indexing_status": "completed",
            "completed_at": 1640995300,
            "processing_started_at": 1640995200,
            "parsing_completed_at": 1640995220,
            "cleaning_completed_at": 1640995240,
            "splitting_completed_at": 1640995260,
        }

        segment_data = {
            "id": "seg-test-123",
            "position": 1,
            "document_id": "doc-test-123",
            "content": "这是一个测试分段内容",
            "answer": "这是测试答案",
            "word_count": 10,
            "tokens": 5,
            "keywords": ["测试", "分段"],
            "index_node_id": "node-123",
            "index_node_hash": "hash-123",
            "hit_count": 0,
            "enabled": True,
            "disabled_at": None,
            "disabled_by": None,
            "status": "completed",
            "created_by": "user-123",
            "created_at": 1640995200,
            "updated_at": 1640995200,
            "indexing_at": 1640995300,
        }

        search_response = {
            "query": "测试查询",
            "results": [
                {
                    "id": "seg-test-123",
                    "content": "这是一个测试分段内容",
                    "score": 0.95,
                    "metadata": {
                        "document_id": "doc-test-123",
                        "document_name": "测试文档",
                    },
                }
            ],
            "total": 1,
        }

        # 模拟API调用
        with patch.object(
            mcp_server.dataset_api, "create_dataset"
        ) as mock_create_dataset, patch.object(
            mcp_server.document_api, "create_document_by_text"
        ) as mock_create_document, patch.object(
            mcp_server.segment_api, "create_segment"
        ) as mock_create_segment, patch.object(
            mcp_server.search_api, "semantic_search"
        ) as mock_search:

            # 设置模拟返回值
            from src.models.common import SearchResponse, SearchResult
            from src.models.dataset import Dataset
            from src.models.document import DocumentCreateResponse
            from src.models.segment import Segment

            mock_create_dataset.return_value = Dataset(**dataset_data)
            mock_create_document.return_value = DocumentCreateResponse(
                document=document_data, batch="batch-123"
            )
            mock_create_segment.return_value = Segment(**segment_data)
            mock_search.return_value = SearchResponse(
                query=search_response["query"],
                results=[
                    SearchResult(**result) for result in search_response["results"]
                ],
                total=search_response["total"],
            )

            # 1. 创建知识库
            dataset_result = await mcp_server.dataset_tools.create_dataset(
                name="测试知识库",
                description="端到端测试知识库",
                indexing_technique="high_quality",
            )

            assert dataset_result["success"] is True
            dataset_id = dataset_result["dataset"]["id"]

            # 2. 创建文档
            document_result = await mcp_server.document_tools.create_document_by_text(
                dataset_id=dataset_id,
                name="测试文档",
                text="这是一个测试文档的内容，用于端到端测试。",
                indexing_technique="high_quality",
            )

            assert document_result["success"] is True
            document_id = document_result["document"]["id"]

            # 3. 创建分段
            segment_result = await mcp_server.segment_tools.create_segment(
                dataset_id=dataset_id,
                document_id=document_id,
                content="这是一个测试分段内容",
                answer="这是测试答案",
                keywords=["测试", "分段"],
            )

            assert segment_result["success"] is True
            segment_id = segment_result["segment"]["id"]

            # 4. 执行搜索
            search_result = await mcp_server.search_tools.semantic_search(
                dataset_id=dataset_id, query="测试查询", top_k=5, score_threshold=0.7
            )

            assert search_result["success"] is True
            assert len(search_result["results"]) > 0
            assert search_result["results"][0]["id"] == segment_id

            # 验证所有API都被正确调用
            mock_create_dataset.assert_called_once()
            mock_create_document.assert_called_once()
            mock_create_segment.assert_called_once()
            mock_search.assert_called_once()

    @pytest.mark.asyncio
    async def test_error_handling_workflow(self, mcp_server: DifyMCPServer):
        """测试错误处理工作流程"""
        from src.utils.exceptions import DifyAPIError

        # 模拟API错误
        with patch.object(
            mcp_server.dataset_api, "create_dataset"
        ) as mock_create_dataset:
            mock_create_dataset.side_effect = DifyAPIError(
                "API配额已用完", status_code=429
            )

            # 尝试创建知识库
            result = await mcp_server.dataset_tools.create_dataset(name="测试知识库")

            # 验证错误处理
            assert result["success"] is False
            assert "error" in result
            assert "API配额已用完" in result["error"]

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, mcp_server: DifyMCPServer):
        """测试并发操作"""
        # 模拟并发创建多个知识库
        dataset_data_template = {
            "id": "dataset-{}",
            "name": "知识库{}",
            "description": "测试知识库{}",
            "provider": "vendor",
            "permission": "only_me",
            "data_source_type": "upload_file",
            "indexing_technique": "high_quality",
            "app_count": 0,
            "document_count": 0,
            "word_count": 0,
            "created_by": "user-123",
            "created_at": 1640995200,
            "updated_by": "user-123",
            "updated_at": 1640995200,
        }

        async def create_dataset(index: int):
            """创建单个知识库"""
            from src.models.dataset import Dataset

            dataset_data = {
                k: v.format(index) if isinstance(v, str) else v
                for k, v in dataset_data_template.items()
            }

            with patch.object(mcp_server.dataset_api, "create_dataset") as mock_create:
                mock_create.return_value = Dataset(**dataset_data)

                result = await mcp_server.dataset_tools.create_dataset(
                    name=f"知识库{index}", description=f"测试知识库{index}"
                )

                return result

        # 并发创建5个知识库
        tasks = [create_dataset(i) for i in range(1, 6)]
        results = await asyncio.gather(*tasks)

        # 验证所有操作都成功
        for i, result in enumerate(results, 1):
            assert result["success"] is True
            assert result["dataset"]["name"] == f"知识库{i}"

    @pytest.mark.asyncio
    async def test_server_lifecycle(self, test_settings: Settings):
        """测试服务器生命周期"""
        with patch("src.api.client.httpx.AsyncClient"):
            # 测试服务器创建
            server = await create_server(test_settings)
            assert server is not None
            assert server.client is not None

            # 测试健康检查
            with patch.object(server.client, "health_check", return_value=True):
                health_status = await server.health_check()
                assert health_status is True

            # 测试服务器信息
            info = server.get_server_info()
            assert "name" in info
            assert "version" in info
            assert "capabilities" in info

            # 测试清理
            await server.cleanup()

    @pytest.mark.asyncio
    async def test_resource_management(self, mcp_server: DifyMCPServer):
        """测试资源管理"""
        # 测试资源注册
        assert mcp_server.dataset_resource is not None
        assert mcp_server.document_resource is not None
        assert mcp_server.segment_resource is not None

        # 模拟资源访问
        with patch.object(mcp_server.dataset_api, "list_datasets") as mock_list:
            from src.models.dataset import DatasetList

            mock_list.return_value = DatasetList(
                data=[], has_more=False, limit=20, total=0, page=1
            )

            # 通过资源获取知识库列表
            result = await mcp_server.dataset_tools.list_datasets()
            assert result["success"] is True
            assert "datasets" in result

    @pytest.mark.asyncio
    async def test_configuration_validation(self):
        """测试配置验证"""
        # 测试无效配置
        invalid_settings = Settings(
            dify_api_key="", dify_base_url="invalid-url"  # 空API密钥
        )

        server = DifyMCPServer(invalid_settings)

        with pytest.raises(ValueError):
            await server.initialize()

    @pytest.mark.asyncio
    async def test_performance_monitoring(self, mcp_server: DifyMCPServer):
        """测试性能监控"""
        import time

        # 模拟API响应延迟
        async def slow_api_call(*args, **kwargs):
            await asyncio.sleep(0.1)  # 模拟100ms延迟
            from src.models.dataset import Dataset

            return Dataset(
                id="dataset-123",
                name="测试知识库",
                description="性能测试",
                provider="vendor",
                permission="only_me",
                data_source_type="upload_file",
                indexing_technique="high_quality",
                app_count=0,
                document_count=0,
                word_count=0,
                created_by="user-123",
                created_at=1640995200,
                updated_by="user-123",
                updated_at=1640995200,
            )

        with patch.object(
            mcp_server.dataset_api, "create_dataset", side_effect=slow_api_call
        ):
            start_time = time.time()

            result = await mcp_server.dataset_tools.create_dataset(
                name="性能测试知识库"
            )

            end_time = time.time()
            duration = end_time - start_time

            # 验证操作成功且在合理时间内完成
            assert result["success"] is True
            assert duration >= 0.1  # 至少100ms（模拟延迟）
            assert duration < 1.0  # 不超过1秒

    @pytest.mark.asyncio
    async def test_data_consistency(self, mcp_server: DifyMCPServer):
        """测试数据一致性"""
        # 模拟创建知识库后立即获取
        dataset_data = {
            "id": "dataset-consistency-123",
            "name": "一致性测试知识库",
            "description": "测试数据一致性",
            "provider": "vendor",
            "permission": "only_me",
            "data_source_type": "upload_file",
            "indexing_technique": "high_quality",
            "app_count": 0,
            "document_count": 0,
            "word_count": 0,
            "created_by": "user-123",
            "created_at": 1640995200,
            "updated_by": "user-123",
            "updated_at": 1640995200,
        }

        from src.models.dataset import Dataset

        with patch.object(
            mcp_server.dataset_api, "create_dataset"
        ) as mock_create, patch.object(
            mcp_server.dataset_api, "get_dataset"
        ) as mock_get:

            mock_create.return_value = Dataset(**dataset_data)
            mock_get.return_value = Dataset(**dataset_data)

            # 创建知识库
            create_result = await mcp_server.dataset_tools.create_dataset(
                name="一致性测试知识库", description="测试数据一致性"
            )

            assert create_result["success"] is True
            created_id = create_result["dataset"]["id"]

            # 立即获取知识库
            get_result = await mcp_server.dataset_tools.get_dataset(
                dataset_id=created_id
            )

            assert get_result["success"] is True

            # 验证数据一致性
            created_dataset = create_result["dataset"]
            retrieved_dataset = get_result["dataset"]

            assert created_dataset["id"] == retrieved_dataset["id"]
            assert created_dataset["name"] == retrieved_dataset["name"]
            assert created_dataset["description"] == retrieved_dataset["description"]
