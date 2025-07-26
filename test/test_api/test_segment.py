"""分段API测试"""

from unittest.mock import AsyncMock

import pytest

from src.api.segment import SegmentAPI
from src.models.segment import (Segment, SegmentBatchOperation,
                                SegmentBatchOperationResponse, SegmentCreate,
                                SegmentList, SegmentListQuery,
                                SegmentStatistics, SegmentUpdate)
from src.utils.exceptions import DifyAPIError, ValidationError


class TestSegmentAPI:
    """分段API测试类"""

    @pytest.fixture
    def segment_api(self, mock_api_client: AsyncMock) -> SegmentAPI:
        """创建分段API实例"""
        return SegmentAPI(mock_api_client)

    @pytest.mark.asyncio
    async def test_list_segments_success(
        self,
        segment_api: SegmentAPI,
        mock_api_client: AsyncMock,
        sample_segment_data: dict,
    ):
        """测试获取分段列表成功"""
        # 准备响应数据
        response_data = {
            "data": [sample_segment_data],
            "has_more": False,
            "limit": 20,
            "total": 1,
            "page": 1,
        }
        mock_api_client.get.return_value = response_data

        # 执行测试
        query = SegmentListQuery(page=1, limit=20, keyword="测试")
        result = await segment_api.list_segments("dataset-123", "doc-123", query)

        # 验证结果
        assert isinstance(result, SegmentList)
        assert len(result.data) == 1
        assert result.data[0].id == sample_segment_data["id"]
        assert result.data[0].content == sample_segment_data["content"]
        assert result.total == 1

        # 验证API调用
        mock_api_client.get.assert_called_once_with(
            "datasets/dataset-123/documents/doc-123/segments",
            params={"page": 1, "limit": 20, "keyword": "测试"},
        )

    @pytest.mark.asyncio
    async def test_create_segment_success(
        self,
        segment_api: SegmentAPI,
        mock_api_client: AsyncMock,
        sample_segment_data: dict,
    ):
        """测试创建分段成功"""
        # 准备响应数据
        mock_api_client.post.return_value = sample_segment_data

        # 执行测试
        segment_data = SegmentCreate(
            content="这是一个测试分段", answer="这是答案", keywords=["测试", "分段"]
        )
        result = await segment_api.create_segment(
            "dataset-123", "doc-123", segment_data
        )

        # 验证结果
        assert isinstance(result, Segment)
        assert result.id == sample_segment_data["id"]
        assert result.content == sample_segment_data["content"]

        # 验证API调用
        mock_api_client.post.assert_called_once_with(
            "datasets/dataset-123/documents/doc-123/segments",
            json_data={
                "content": "这是一个测试分段",
                "answer": "这是答案",
                "keywords": ["测试", "分段"],
            },
        )

    @pytest.mark.asyncio
    async def test_get_segment_success(
        self,
        segment_api: SegmentAPI,
        mock_api_client: AsyncMock,
        sample_segment_data: dict,
    ):
        """测试获取分段详情成功"""
        # 准备响应数据
        mock_api_client.get.return_value = sample_segment_data

        # 执行测试
        result = await segment_api.get_segment("dataset-123", "doc-123", "seg-123")

        # 验证结果
        assert isinstance(result, Segment)
        assert result.id == sample_segment_data["id"]
        assert result.content == sample_segment_data["content"]

        # 验证API调用
        mock_api_client.get.assert_called_once_with(
            "datasets/dataset-123/documents/doc-123/segments/seg-123"
        )

    @pytest.mark.asyncio
    async def test_update_segment_success(
        self,
        segment_api: SegmentAPI,
        mock_api_client: AsyncMock,
        sample_segment_data: dict,
    ):
        """测试更新分段成功"""
        # 准备响应数据
        updated_data = sample_segment_data.copy()
        updated_data["content"] = "更新后的分段内容"
        mock_api_client.patch.return_value = updated_data

        # 执行测试
        segment_data = SegmentUpdate(content="更新后的分段内容")
        result = await segment_api.update_segment(
            "dataset-123", "doc-123", "seg-123", segment_data
        )

        # 验证结果
        assert isinstance(result, Segment)
        assert result.id == sample_segment_data["id"]
        assert result.content == "更新后的分段内容"

        # 验证API调用
        mock_api_client.patch.assert_called_once_with(
            "datasets/dataset-123/documents/doc-123/segments/seg-123",
            json_data={"content": "更新后的分段内容"},
        )

    @pytest.mark.asyncio
    async def test_delete_segment_success(
        self, segment_api: SegmentAPI, mock_api_client: AsyncMock
    ):
        """测试删除分段成功"""
        # 准备响应数据
        mock_api_client.delete.return_value = {"success": True}

        # 执行测试
        result = await segment_api.delete_segment("dataset-123", "doc-123", "seg-123")

        # 验证结果
        assert result is True

        # 验证API调用
        mock_api_client.delete.assert_called_once_with(
            "datasets/dataset-123/documents/doc-123/segments/seg-123"
        )

    @pytest.mark.asyncio
    async def test_enable_segment_success(
        self, segment_api: SegmentAPI, mock_api_client: AsyncMock
    ):
        """测试启用分段成功"""
        # 准备响应数据
        mock_api_client.patch.return_value = {"success": True}

        # 执行测试
        result = await segment_api.enable_segment("dataset-123", "doc-123", "seg-123")

        # 验证结果
        assert result is True

        # 验证API调用
        mock_api_client.patch.assert_called_once_with(
            "datasets/dataset-123/documents/doc-123/segments/seg-123/enable"
        )

    @pytest.mark.asyncio
    async def test_disable_segment_success(
        self, segment_api: SegmentAPI, mock_api_client: AsyncMock
    ):
        """测试禁用分段成功"""
        # 准备响应数据
        mock_api_client.patch.return_value = {"success": True}

        # 执行测试
        result = await segment_api.disable_segment("dataset-123", "doc-123", "seg-123")

        # 验证结果
        assert result is True

        # 验证API调用
        mock_api_client.patch.assert_called_once_with(
            "datasets/dataset-123/documents/doc-123/segments/seg-123/disable"
        )

    @pytest.mark.asyncio
    async def test_get_segment_statistics_success(
        self, segment_api: SegmentAPI, mock_api_client: AsyncMock
    ):
        """测试获取分段统计信息成功"""
        # 准备响应数据
        stats_data = {
            "total_segments": 100,
            "enabled_segments": 95,
            "disabled_segments": 5,
            "total_characters": 50000,
            "average_characters_per_segment": 500,
        }
        mock_api_client.get.return_value = stats_data

        # 执行测试
        result = await segment_api.get_segment_statistics("dataset-123", "doc-123")

        # 验证结果
        assert isinstance(result, SegmentStatistics)
        assert result.total_segments == 100
        assert result.enabled_segments == 95
        assert result.disabled_segments == 5

        # 验证API调用
        mock_api_client.get.assert_called_once_with(
            "datasets/dataset-123/documents/doc-123/segments/statistics"
        )

    @pytest.mark.asyncio
    async def test_batch_enable_segments_success(
        self, segment_api: SegmentAPI, mock_api_client: AsyncMock
    ):
        """测试批量启用分段成功"""
        # 准备响应数据
        response_data = {
            "success_count": 2,
            "failed_count": 0,
            "success_ids": ["seg-123", "seg-456"],
            "failed_ids": [],
        }
        mock_api_client.patch.return_value = response_data

        # 执行测试
        operation = SegmentBatchOperation(segment_ids=["seg-123", "seg-456"])
        result = await segment_api.batch_enable_segments(
            "dataset-123", "doc-123", operation
        )

        # 验证结果
        assert isinstance(result, SegmentBatchOperationResponse)
        assert result.success_count == 2
        assert result.failed_count == 0
        assert len(result.success_ids) == 2

        # 验证API调用
        mock_api_client.patch.assert_called_once_with(
            "datasets/dataset-123/documents/doc-123/segments/batch/enable",
            json_data={"segment_ids": ["seg-123", "seg-456"]},
        )

    @pytest.mark.asyncio
    async def test_batch_disable_segments_success(
        self, segment_api: SegmentAPI, mock_api_client: AsyncMock
    ):
        """测试批量禁用分段成功"""
        # 准备响应数据
        response_data = {
            "success_count": 2,
            "failed_count": 0,
            "success_ids": ["seg-123", "seg-456"],
            "failed_ids": [],
        }
        mock_api_client.patch.return_value = response_data

        # 执行测试
        operation = SegmentBatchOperation(segment_ids=["seg-123", "seg-456"])
        result = await segment_api.batch_disable_segments(
            "dataset-123", "doc-123", operation
        )

        # 验证结果
        assert isinstance(result, SegmentBatchOperationResponse)
        assert result.success_count == 2
        assert result.failed_count == 0

        # 验证API调用
        mock_api_client.patch.assert_called_once_with(
            "datasets/dataset-123/documents/doc-123/segments/batch/disable",
            json_data={"segment_ids": ["seg-123", "seg-456"]},
        )

    @pytest.mark.asyncio
    async def test_batch_delete_segments_success(
        self, segment_api: SegmentAPI, mock_api_client: AsyncMock
    ):
        """测试批量删除分段成功"""
        # 准备响应数据
        response_data = {
            "success_count": 2,
            "failed_count": 0,
            "success_ids": ["seg-123", "seg-456"],
            "failed_ids": [],
        }
        mock_api_client.delete.return_value = response_data

        # 执行测试
        operation = SegmentBatchOperation(segment_ids=["seg-123", "seg-456"])
        result = await segment_api.batch_delete_segments(
            "dataset-123", "doc-123", operation
        )

        # 验证结果
        assert isinstance(result, SegmentBatchOperationResponse)
        assert result.success_count == 2
        assert result.failed_count == 0

        # 验证API调用
        mock_api_client.delete.assert_called_once_with(
            "datasets/dataset-123/documents/doc-123/segments/batch",
            json_data={"segment_ids": ["seg-123", "seg-456"]},
        )

    @pytest.mark.asyncio
    async def test_reindex_segments_success(
        self, segment_api: SegmentAPI, mock_api_client: AsyncMock
    ):
        """测试重新索引分段成功"""
        # 准备响应数据
        mock_api_client.post.return_value = {"success": True, "task_id": "task-123"}

        # 执行测试
        result = await segment_api.reindex_segments("dataset-123", "doc-123")

        # 验证结果
        assert result["success"] is True
        assert result["task_id"] == "task-123"

        # 验证API调用
        mock_api_client.post.assert_called_once_with(
            "datasets/dataset-123/documents/doc-123/segments/reindex"
        )

    @pytest.mark.asyncio
    async def test_hit_test_segments_success(
        self, segment_api: SegmentAPI, mock_api_client: AsyncMock
    ):
        """测试分段命中测试成功"""
        # 准备响应数据
        hit_data = {
            "query": "测试查询",
            "hits": [
                {"segment_id": "seg-123", "score": 0.95, "content": "匹配的分段内容"}
            ],
        }
        mock_api_client.post.return_value = hit_data

        # 执行测试
        result = await segment_api.hit_test_segments(
            "dataset-123", "doc-123", "测试查询"
        )

        # 验证结果
        assert result["query"] == "测试查询"
        assert len(result["hits"]) == 1
        assert result["hits"][0]["segment_id"] == "seg-123"

        # 验证API调用
        mock_api_client.post.assert_called_once_with(
            "datasets/dataset-123/documents/doc-123/segments/hit_test",
            json_data={"query": "测试查询"},
        )

    @pytest.mark.asyncio
    async def test_invalid_dataset_id_raises_error(self, segment_api: SegmentAPI):
        """测试无效的知识库ID抛出错误"""
        with pytest.raises(ValidationError):
            await segment_api.list_segments("invalid-id", "doc-123")

    @pytest.mark.asyncio
    async def test_invalid_document_id_raises_error(self, segment_api: SegmentAPI):
        """测试无效的文档ID抛出错误"""
        with pytest.raises(ValidationError):
            await segment_api.list_segments("dataset-123", "invalid-id")

    @pytest.mark.asyncio
    async def test_invalid_segment_id_raises_error(self, segment_api: SegmentAPI):
        """测试无效的分段ID抛出错误"""
        with pytest.raises(ValidationError):
            await segment_api.get_segment("dataset-123", "doc-123", "invalid-id")

    @pytest.mark.asyncio
    async def test_api_error_propagation(
        self, segment_api: SegmentAPI, mock_api_client: AsyncMock
    ):
        """测试API错误传播"""
        # 模拟API错误
        mock_api_client.get.side_effect = DifyAPIError("API Error", status_code=500)

        # 执行测试并验证错误
        with pytest.raises(DifyAPIError):
            await segment_api.get_segment("dataset-123", "doc-123", "seg-123")

    @pytest.mark.asyncio
    async def test_list_segments_with_empty_query(
        self, segment_api: SegmentAPI, mock_api_client: AsyncMock
    ):
        """测试使用空查询参数获取分段列表"""
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
        result = await segment_api.list_segments("dataset-123", "doc-123")

        # 验证结果
        assert isinstance(result, SegmentList)
        assert len(result.data) == 0
        assert result.total == 0

        # 验证API调用（无参数）
        mock_api_client.get.assert_called_once_with(
            "datasets/dataset-123/documents/doc-123/segments", params={}
        )

    @pytest.mark.asyncio
    async def test_batch_operation_with_empty_ids(self, segment_api: SegmentAPI):
        """测试空分段ID列表的批量操作"""
        operation = SegmentBatchOperation(segment_ids=[])

        with pytest.raises(ValidationError):
            await segment_api.batch_enable_segments("dataset-123", "doc-123", operation)

    @pytest.mark.asyncio
    async def test_batch_operation_partial_failure(
        self, segment_api: SegmentAPI, mock_api_client: AsyncMock
    ):
        """测试批量操作部分失败"""
        # 准备响应数据
        response_data = {
            "success_count": 1,
            "failed_count": 1,
            "success_ids": ["seg-123"],
            "failed_ids": ["seg-456"],
        }
        mock_api_client.patch.return_value = response_data

        # 执行测试
        operation = SegmentBatchOperation(segment_ids=["seg-123", "seg-456"])
        result = await segment_api.batch_enable_segments(
            "dataset-123", "doc-123", operation
        )

        # 验证结果
        assert isinstance(result, SegmentBatchOperationResponse)
        assert result.success_count == 1
        assert result.failed_count == 1
        assert len(result.success_ids) == 1
        assert len(result.failed_ids) == 1
