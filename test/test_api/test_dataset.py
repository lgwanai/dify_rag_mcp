"""知识库API测试"""

from unittest.mock import AsyncMock

import pytest

from src.api.dataset import DatasetAPI
from src.models.dataset import (Dataset, DatasetCreate, DatasetList,
                                DatasetListQuery, DatasetTag, DatasetTagCreate,
                                DatasetUpdate)
from src.utils.exceptions import DifyAPIError, ValidationError


class TestDatasetAPI:
    """知识库API测试类"""

    @pytest.fixture
    def dataset_api(self, mock_api_client: AsyncMock) -> DatasetAPI:
        """创建知识库API实例"""
        return DatasetAPI(mock_api_client)

    @pytest.mark.asyncio
    async def test_list_datasets_success(
        self,
        dataset_api: DatasetAPI,
        mock_api_client: AsyncMock,
        sample_dataset_data: dict,
    ):
        """测试获取知识库列表成功"""
        # 准备响应数据
        response_data = {
            "data": [sample_dataset_data],
            "has_more": False,
            "limit": 20,
            "total": 1,
            "page": 1,
        }
        mock_api_client.get.return_value = response_data

        # 执行测试
        query = DatasetListQuery(page=1, limit=20, keyword="测试")
        result = await dataset_api.list_datasets(query)

        # 验证结果
        assert isinstance(result, DatasetList)
        assert len(result.data) == 1
        assert result.data[0].id == sample_dataset_data["id"]
        assert result.data[0].name == sample_dataset_data["name"]
        assert result.total == 1
        assert result.page == 1

        # 验证API调用
        mock_api_client.get.assert_called_once_with(
            "datasets", params={"page": 1, "limit": 20, "keyword": "测试"}
        )

    @pytest.mark.asyncio
    async def test_create_dataset_success(
        self,
        dataset_api: DatasetAPI,
        mock_api_client: AsyncMock,
        sample_dataset_data: dict,
    ):
        """测试创建知识库成功"""
        # 准备响应数据
        mock_api_client.post.return_value = sample_dataset_data

        # 执行测试
        dataset_data = DatasetCreate(
            name="测试知识库",
            description="这是一个测试知识库",
            indexing_technique="high_quality",
            permission="only_me",
        )
        result = await dataset_api.create_dataset(dataset_data)

        # 验证结果
        assert isinstance(result, Dataset)
        assert result.id == sample_dataset_data["id"]
        assert result.name == sample_dataset_data["name"]

        # 验证API调用
        mock_api_client.post.assert_called_once_with(
            "datasets",
            json_data={
                "name": "测试知识库",
                "description": "这是一个测试知识库",
                "indexing_technique": "high_quality",
                "permission": "only_me",
            },
        )

    @pytest.mark.asyncio
    async def test_get_dataset_success(
        self,
        dataset_api: DatasetAPI,
        mock_api_client: AsyncMock,
        sample_dataset_data: dict,
    ):
        """测试获取知识库详情成功"""
        # 准备响应数据
        mock_api_client.get.return_value = sample_dataset_data

        # 执行测试
        result = await dataset_api.get_dataset("dataset-123")

        # 验证结果
        assert isinstance(result, Dataset)
        assert result.id == sample_dataset_data["id"]
        assert result.name == sample_dataset_data["name"]

        # 验证API调用
        mock_api_client.get.assert_called_once_with("datasets/dataset-123")

    @pytest.mark.asyncio
    async def test_update_dataset_success(
        self,
        dataset_api: DatasetAPI,
        mock_api_client: AsyncMock,
        sample_dataset_data: dict,
    ):
        """测试更新知识库成功"""
        # 准备响应数据
        updated_data = sample_dataset_data.copy()
        updated_data["name"] = "更新后的知识库"
        mock_api_client.patch.return_value = updated_data

        # 执行测试
        dataset_data = DatasetUpdate(name="更新后的知识库")
        result = await dataset_api.update_dataset("dataset-123", dataset_data)

        # 验证结果
        assert isinstance(result, Dataset)
        assert result.id == sample_dataset_data["id"]
        assert result.name == "更新后的知识库"

        # 验证API调用
        mock_api_client.patch.assert_called_once_with(
            "datasets/dataset-123", json_data={"name": "更新后的知识库"}
        )

    @pytest.mark.asyncio
    async def test_delete_dataset_success(
        self, dataset_api: DatasetAPI, mock_api_client: AsyncMock
    ):
        """测试删除知识库成功"""
        # 准备响应数据
        mock_api_client.delete.return_value = {"success": True}

        # 执行测试
        result = await dataset_api.delete_dataset("dataset-123")

        # 验证结果
        assert result is True

        # 验证API调用
        mock_api_client.delete.assert_called_once_with("datasets/dataset-123")

    @pytest.mark.asyncio
    async def test_get_dataset_indexing_status(
        self, dataset_api: DatasetAPI, mock_api_client: AsyncMock
    ):
        """测试获取知识库索引状态"""
        # 准备响应数据
        status_data = {
            "indexing_status": "completed",
            "total_documents": 10,
            "completed_documents": 10,
            "failed_documents": 0,
            "processing_documents": 0,
        }
        mock_api_client.get.return_value = status_data

        # 执行测试
        result = await dataset_api.get_dataset_indexing_status("dataset-123")

        # 验证结果
        assert result == status_data

        # 验证API调用
        mock_api_client.get.assert_called_once_with(
            "datasets/dataset-123/indexing-status"
        )

    @pytest.mark.asyncio
    async def test_list_dataset_tags_success(
        self, dataset_api: DatasetAPI, mock_api_client: AsyncMock
    ):
        """测试获取知识库标签列表成功"""
        # 准备响应数据
        tag_data = {
            "id": "tag-123",
            "name": "测试标签",
            "color": "#FF0000",
            "created_by": "user-123",
            "created_at": 1640995200,
        }
        response_data = {"data": [tag_data]}
        mock_api_client.get.return_value = response_data

        # 执行测试
        result = await dataset_api.list_dataset_tags()

        # 验证结果
        assert len(result) == 1
        assert isinstance(result[0], DatasetTag)
        assert result[0].id == tag_data["id"]
        assert result[0].name == tag_data["name"]

        # 验证API调用
        mock_api_client.get.assert_called_once_with("datasets/tags")

    @pytest.mark.asyncio
    async def test_create_dataset_tag_success(
        self, dataset_api: DatasetAPI, mock_api_client: AsyncMock
    ):
        """测试创建知识库标签成功"""
        # 准备响应数据
        tag_data = {
            "id": "tag-123",
            "name": "新标签",
            "color": "#00FF00",
            "created_by": "user-123",
            "created_at": 1640995200,
        }
        mock_api_client.post.return_value = tag_data

        # 执行测试
        tag_create_data = DatasetTagCreate(name="新标签", color="#00FF00")
        result = await dataset_api.create_dataset_tag(tag_create_data)

        # 验证结果
        assert isinstance(result, DatasetTag)
        assert result.id == tag_data["id"]
        assert result.name == tag_data["name"]
        assert result.color == tag_data["color"]

        # 验证API调用
        mock_api_client.post.assert_called_once_with(
            "datasets/tags", json_data={"name": "新标签", "color": "#00FF00"}
        )

    @pytest.mark.asyncio
    async def test_copy_dataset_success(
        self,
        dataset_api: DatasetAPI,
        mock_api_client: AsyncMock,
        sample_dataset_data: dict,
    ):
        """测试复制知识库成功"""
        # 准备响应数据
        copied_data = sample_dataset_data.copy()
        copied_data["id"] = "dataset-456"
        copied_data["name"] = "复制的知识库"
        mock_api_client.post.return_value = copied_data

        # 执行测试
        result = await dataset_api.copy_dataset("dataset-123", "复制的知识库")

        # 验证结果
        assert isinstance(result, Dataset)
        assert result.id == "dataset-456"
        assert result.name == "复制的知识库"

        # 验证API调用
        mock_api_client.post.assert_called_once_with(
            "datasets/dataset-123/copy", json_data={"name": "复制的知识库"}
        )

    @pytest.mark.asyncio
    async def test_invalid_dataset_id_raises_error(self, dataset_api: DatasetAPI):
        """测试无效的知识库ID抛出错误"""
        with pytest.raises(ValidationError):
            await dataset_api.get_dataset("invalid-id")

    @pytest.mark.asyncio
    async def test_api_error_propagation(
        self, dataset_api: DatasetAPI, mock_api_client: AsyncMock
    ):
        """测试API错误传播"""
        # 模拟API错误
        mock_api_client.get.side_effect = DifyAPIError("API Error", status_code=500)

        # 执行测试并验证错误
        with pytest.raises(DifyAPIError):
            await dataset_api.get_dataset("dataset-123")

    @pytest.mark.asyncio
    async def test_list_datasets_with_empty_query(
        self, dataset_api: DatasetAPI, mock_api_client: AsyncMock
    ):
        """测试使用空查询参数获取知识库列表"""
        # 准备响应数据
        response_data = {
            "data": [],
            "has_more": False,
            "limit": 20,
            "total": 0,
            "page": 1,
        }
        mock_api_client.get.return_value = response_data

        # 执行测试
        result = await dataset_api.list_datasets()

        # 验证结果
        assert isinstance(result, DatasetList)
        assert len(result.data) == 0
        assert result.total == 0

        # 验证API调用（无参数）
        mock_api_client.get.assert_called_once_with("datasets", params={})

    @pytest.mark.asyncio
    async def test_get_dataset_queries(
        self, dataset_api: DatasetAPI, mock_api_client: AsyncMock
    ):
        """测试获取知识库查询记录"""
        # 准备响应数据
        queries_data = {
            "data": [
                {
                    "id": "query-123",
                    "content": "测试查询",
                    "source": "api",
                    "created_at": 1640995200,
                }
            ]
        }
        mock_api_client.get.return_value = queries_data

        # 执行测试
        result = await dataset_api.get_dataset_queries("dataset-123")

        # 验证结果
        assert result == queries_data["data"]

        # 验证API调用
        mock_api_client.get.assert_called_once_with("datasets/dataset-123/queries")

    @pytest.mark.asyncio
    async def test_get_dataset_error_docs(
        self, dataset_api: DatasetAPI, mock_api_client: AsyncMock
    ):
        """测试获取知识库错误文档"""
        # 准备响应数据
        error_docs_data = {
            "data": [
                {
                    "id": "doc-123",
                    "name": "错误文档.txt",
                    "error": "处理失败",
                    "created_at": 1640995200,
                }
            ]
        }
        mock_api_client.get.return_value = error_docs_data

        # 执行测试
        result = await dataset_api.get_dataset_error_docs("dataset-123")

        # 验证结果
        assert result == error_docs_data["data"]

        # 验证API调用
        mock_api_client.get.assert_called_once_with("datasets/dataset-123/error-docs")
