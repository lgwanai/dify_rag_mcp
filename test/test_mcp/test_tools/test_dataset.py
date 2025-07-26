"""知识库工具测试"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.mcp.tools.dataset import DatasetTools
from src.models.dataset import (Dataset, DatasetCreate, DatasetList,
                                DatasetUpdate)
from src.utils.exceptions import DifyAPIError, ValidationError


class TestDatasetTools:
    """知识库工具测试类"""

    @pytest.fixture
    def mock_dataset_api(self) -> AsyncMock:
        """创建模拟知识库API"""
        return AsyncMock()

    @pytest.fixture
    def dataset_tools(self, mock_dataset_api: AsyncMock) -> DatasetTools:
        """创建知识库工具实例"""
        return DatasetTools(mock_dataset_api)

    @pytest.fixture
    def mock_app(self) -> MagicMock:
        """创建模拟FastMCP应用"""
        return MagicMock()

    def test_register_tools(self, dataset_tools: DatasetTools, mock_app: MagicMock):
        """测试注册工具"""
        dataset_tools.register_tools(mock_app)

        # 验证所有工具都已注册
        assert mock_app.tool.call_count >= 10  # 至少注册了10个工具

    @pytest.mark.asyncio
    async def test_create_dataset_success(
        self,
        dataset_tools: DatasetTools,
        mock_dataset_api: AsyncMock,
        sample_dataset_data: dict,
    ):
        """测试创建知识库成功"""
        # 准备模拟响应
        mock_dataset = Dataset(**sample_dataset_data)
        mock_dataset_api.create_dataset.return_value = mock_dataset

        # 执行测试
        result = await dataset_tools.create_dataset(
            name="测试知识库",
            description="这是一个测试知识库",
            indexing_technique="high_quality",
            permission="only_me",
        )

        # 验证结果
        assert "success" in result
        assert result["success"] is True
        assert "dataset" in result
        assert result["dataset"]["id"] == sample_dataset_data["id"]

        # 验证API调用
        mock_dataset_api.create_dataset.assert_called_once()
        call_args = mock_dataset_api.create_dataset.call_args[0][0]
        assert call_args.name == "测试知识库"
        assert call_args.description == "这是一个测试知识库"

    @pytest.mark.asyncio
    async def test_create_dataset_failure(
        self, dataset_tools: DatasetTools, mock_dataset_api: AsyncMock
    ):
        """测试创建知识库失败"""
        # 模拟API错误
        mock_dataset_api.create_dataset.side_effect = DifyAPIError(
            "创建失败", status_code=400
        )

        # 执行测试
        result = await dataset_tools.create_dataset(
            name="测试知识库", description="这是一个测试知识库"
        )

        # 验证结果
        assert "success" in result
        assert result["success"] is False
        assert "error" in result
        assert "创建失败" in result["error"]

    @pytest.mark.asyncio
    async def test_list_datasets_success(
        self,
        dataset_tools: DatasetTools,
        mock_dataset_api: AsyncMock,
        sample_dataset_data: dict,
    ):
        """测试获取知识库列表成功"""
        # 准备模拟响应
        mock_dataset_list = DatasetList(
            data=[Dataset(**sample_dataset_data)],
            has_more=False,
            limit=20,
            total=1,
            page=1,
        )
        mock_dataset_api.list_datasets.return_value = mock_dataset_list

        # 执行测试
        result = await dataset_tools.list_datasets(page=1, limit=20, keyword="测试")

        # 验证结果
        assert "success" in result
        assert result["success"] is True
        assert "datasets" in result
        assert len(result["datasets"]) == 1
        assert result["total"] == 1

        # 验证API调用
        mock_dataset_api.list_datasets.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_dataset_success(
        self,
        dataset_tools: DatasetTools,
        mock_dataset_api: AsyncMock,
        sample_dataset_data: dict,
    ):
        """测试获取知识库详情成功"""
        # 准备模拟响应
        mock_dataset = Dataset(**sample_dataset_data)
        mock_dataset_api.get_dataset.return_value = mock_dataset

        # 执行测试
        result = await dataset_tools.get_dataset(dataset_id="dataset-123")

        # 验证结果
        assert "success" in result
        assert result["success"] is True
        assert "dataset" in result
        assert result["dataset"]["id"] == sample_dataset_data["id"]

        # 验证API调用
        mock_dataset_api.get_dataset.assert_called_once_with("dataset-123")

    @pytest.mark.asyncio
    async def test_get_dataset_not_found(
        self, dataset_tools: DatasetTools, mock_dataset_api: AsyncMock
    ):
        """测试获取不存在的知识库"""
        # 模拟API错误
        mock_dataset_api.get_dataset.side_effect = DifyAPIError(
            "知识库不存在", status_code=404
        )

        # 执行测试
        result = await dataset_tools.get_dataset(dataset_id="nonexistent-id")

        # 验证结果
        assert "success" in result
        assert result["success"] is False
        assert "error" in result
        assert "知识库不存在" in result["error"]

    @pytest.mark.asyncio
    async def test_update_dataset_success(
        self,
        dataset_tools: DatasetTools,
        mock_dataset_api: AsyncMock,
        sample_dataset_data: dict,
    ):
        """测试更新知识库成功"""
        # 准备模拟响应
        updated_data = sample_dataset_data.copy()
        updated_data["name"] = "更新后的知识库"
        mock_dataset = Dataset(**updated_data)
        mock_dataset_api.update_dataset.return_value = mock_dataset

        # 执行测试
        result = await dataset_tools.update_dataset(
            dataset_id="dataset-123", name="更新后的知识库", description="更新后的描述"
        )

        # 验证结果
        assert "success" in result
        assert result["success"] is True
        assert "dataset" in result
        assert result["dataset"]["name"] == "更新后的知识库"

        # 验证API调用
        mock_dataset_api.update_dataset.assert_called_once()
        call_args = mock_dataset_api.update_dataset.call_args
        assert call_args[0][0] == "dataset-123"
        assert call_args[0][1].name == "更新后的知识库"

    @pytest.mark.asyncio
    async def test_delete_dataset_success(
        self, dataset_tools: DatasetTools, mock_dataset_api: AsyncMock
    ):
        """测试删除知识库成功"""
        # 准备模拟响应
        mock_dataset_api.delete_dataset.return_value = True

        # 执行测试
        result = await dataset_tools.delete_dataset(dataset_id="dataset-123")

        # 验证结果
        assert "success" in result
        assert result["success"] is True
        assert "message" in result

        # 验证API调用
        mock_dataset_api.delete_dataset.assert_called_once_with("dataset-123")

    @pytest.mark.asyncio
    async def test_copy_dataset_success(
        self,
        dataset_tools: DatasetTools,
        mock_dataset_api: AsyncMock,
        sample_dataset_data: dict,
    ):
        """测试复制知识库成功"""
        # 准备模拟响应
        copied_data = sample_dataset_data.copy()
        copied_data["id"] = "dataset-456"
        copied_data["name"] = "复制的知识库"
        mock_dataset = Dataset(**copied_data)
        mock_dataset_api.copy_dataset.return_value = mock_dataset

        # 执行测试
        result = await dataset_tools.copy_dataset(
            dataset_id="dataset-123", name="复制的知识库"
        )

        # 验证结果
        assert "success" in result
        assert result["success"] is True
        assert "dataset" in result
        assert result["dataset"]["id"] == "dataset-456"
        assert result["dataset"]["name"] == "复制的知识库"

        # 验证API调用
        mock_dataset_api.copy_dataset.assert_called_once_with(
            "dataset-123", "复制的知识库"
        )

    @pytest.mark.asyncio
    async def test_get_dataset_indexing_status_success(
        self, dataset_tools: DatasetTools, mock_dataset_api: AsyncMock
    ):
        """测试获取知识库索引状态成功"""
        # 准备模拟响应
        status_data = {
            "indexing_status": "completed",
            "total_documents": 10,
            "completed_documents": 10,
            "failed_documents": 0,
            "processing_documents": 0,
        }
        mock_dataset_api.get_dataset_indexing_status.return_value = status_data

        # 执行测试
        result = await dataset_tools.get_dataset_indexing_status(
            dataset_id="dataset-123"
        )

        # 验证结果
        assert "success" in result
        assert result["success"] is True
        assert "status" in result
        assert result["status"]["indexing_status"] == "completed"

        # 验证API调用
        mock_dataset_api.get_dataset_indexing_status.assert_called_once_with(
            "dataset-123"
        )

    @pytest.mark.asyncio
    async def test_get_dataset_queries_success(
        self, dataset_tools: DatasetTools, mock_dataset_api: AsyncMock
    ):
        """测试获取知识库查询记录成功"""
        # 准备模拟响应
        queries_data = [
            {
                "id": "query-123",
                "content": "测试查询",
                "source": "api",
                "created_at": 1640995200,
            }
        ]
        mock_dataset_api.get_dataset_queries.return_value = queries_data

        # 执行测试
        result = await dataset_tools.get_dataset_queries(dataset_id="dataset-123")

        # 验证结果
        assert "success" in result
        assert result["success"] is True
        assert "queries" in result
        assert len(result["queries"]) == 1

        # 验证API调用
        mock_dataset_api.get_dataset_queries.assert_called_once_with("dataset-123")

    @pytest.mark.asyncio
    async def test_get_dataset_error_docs_success(
        self, dataset_tools: DatasetTools, mock_dataset_api: AsyncMock
    ):
        """测试获取知识库错误文档成功"""
        # 准备模拟响应
        error_docs_data = [
            {
                "id": "doc-123",
                "name": "错误文档.txt",
                "error": "处理失败",
                "created_at": 1640995200,
            }
        ]
        mock_dataset_api.get_dataset_error_docs.return_value = error_docs_data

        # 执行测试
        result = await dataset_tools.get_dataset_error_docs(dataset_id="dataset-123")

        # 验证结果
        assert "success" in result
        assert result["success"] is True
        assert "error_docs" in result
        assert len(result["error_docs"]) == 1

        # 验证API调用
        mock_dataset_api.get_dataset_error_docs.assert_called_once_with("dataset-123")

    @pytest.mark.asyncio
    async def test_invalid_dataset_id_validation(self, dataset_tools: DatasetTools):
        """测试无效知识库ID验证"""
        result = await dataset_tools.get_dataset(dataset_id="")

        assert "success" in result
        assert result["success"] is False
        assert "error" in result
        assert "无效" in result["error"] or "Invalid" in result["error"]

    @pytest.mark.asyncio
    async def test_create_dataset_with_minimal_params(
        self,
        dataset_tools: DatasetTools,
        mock_dataset_api: AsyncMock,
        sample_dataset_data: dict,
    ):
        """测试使用最少参数创建知识库"""
        # 准备模拟响应
        mock_dataset = Dataset(**sample_dataset_data)
        mock_dataset_api.create_dataset.return_value = mock_dataset

        # 执行测试（只提供必需参数）
        result = await dataset_tools.create_dataset(name="最小知识库")

        # 验证结果
        assert "success" in result
        assert result["success"] is True

        # 验证API调用
        mock_dataset_api.create_dataset.assert_called_once()
        call_args = mock_dataset_api.create_dataset.call_args[0][0]
        assert call_args.name == "最小知识库"

    @pytest.mark.asyncio
    async def test_list_datasets_with_pagination(
        self, dataset_tools: DatasetTools, mock_dataset_api: AsyncMock
    ):
        """测试分页获取知识库列表"""
        # 准备模拟响应
        mock_dataset_list = DatasetList(
            data=[], has_more=True, limit=5, total=100, page=2
        )
        mock_dataset_api.list_datasets.return_value = mock_dataset_list

        # 执行测试
        result = await dataset_tools.list_datasets(page=2, limit=5)

        # 验证结果
        assert "success" in result
        assert result["success"] is True
        assert result["page"] == 2
        assert result["limit"] == 5
        assert result["total"] == 100
        assert result["has_more"] is True

    @pytest.mark.asyncio
    async def test_update_dataset_with_partial_data(
        self,
        dataset_tools: DatasetTools,
        mock_dataset_api: AsyncMock,
        sample_dataset_data: dict,
    ):
        """测试部分更新知识库"""
        # 准备模拟响应
        mock_dataset = Dataset(**sample_dataset_data)
        mock_dataset_api.update_dataset.return_value = mock_dataset

        # 执行测试（只更新名称）
        result = await dataset_tools.update_dataset(
            dataset_id="dataset-123", name="新名称"
        )

        # 验证结果
        assert "success" in result
        assert result["success"] is True

        # 验证API调用
        mock_dataset_api.update_dataset.assert_called_once()
        call_args = mock_dataset_api.update_dataset.call_args[0][1]
        assert call_args.name == "新名称"
        assert call_args.description is None  # 未提供的字段应为None

    @pytest.mark.asyncio
    async def test_error_handling_with_network_error(
        self, dataset_tools: DatasetTools, mock_dataset_api: AsyncMock
    ):
        """测试网络错误处理"""
        # 模拟网络错误
        mock_dataset_api.get_dataset.side_effect = Exception("网络连接失败")

        # 执行测试
        result = await dataset_tools.get_dataset(dataset_id="dataset-123")

        # 验证结果
        assert "success" in result
        assert result["success"] is False
        assert "error" in result
        assert "网络连接失败" in result["error"]
