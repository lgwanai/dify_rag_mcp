"""文档API测试"""

from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from src.api.document import DocumentAPI
from src.models.document import (Document, DocumentCreateByFile,
                                 DocumentCreateByText, DocumentCreateResponse,
                                 DocumentList, DocumentListQuery,
                                 DocumentStatus, DocumentUpdateByText)
from src.utils.exceptions import DifyAPIError, ValidationError


class TestDocumentAPI:
    """文档API测试类"""

    @pytest.fixture
    def document_api(self, mock_api_client: AsyncMock) -> DocumentAPI:
        """创建文档API实例"""
        return DocumentAPI(mock_api_client)

    @pytest.mark.asyncio
    async def test_list_documents_success(
        self,
        document_api: DocumentAPI,
        mock_api_client: AsyncMock,
        sample_document_data: dict,
    ):
        """测试获取文档列表成功"""
        # 准备响应数据
        response_data = {
            "data": [sample_document_data],
            "has_more": False,
            "limit": 20,
            "total": 1,
            "page": 1,
        }
        mock_api_client.get.return_value = response_data

        # 执行测试
        query = DocumentListQuery(page=1, limit=20, keyword="测试")
        result = await document_api.list_documents("dataset-123", query)

        # 验证结果
        assert isinstance(result, DocumentList)
        assert len(result.data) == 1
        assert result.data[0].id == sample_document_data["id"]
        assert result.data[0].name == sample_document_data["name"]
        assert result.total == 1

        # 验证API调用
        mock_api_client.get.assert_called_once_with(
            "datasets/dataset-123/documents",
            params={"page": 1, "limit": 20, "keyword": "测试"},
        )

    @pytest.mark.asyncio
    async def test_create_document_by_text_success(
        self, document_api: DocumentAPI, mock_api_client: AsyncMock
    ):
        """测试通过文本创建文档成功"""
        # 准备响应数据
        response_data = {
            "document": {"id": "doc-123", "batch": "batch-123"},
            "batch": "batch-123",
        }
        mock_api_client.post.return_value = response_data

        # 执行测试
        document_data = DocumentCreateByText(
            name="测试文档", text="这是测试文档内容", indexing_technique="high_quality"
        )
        result = await document_api.create_document_by_text(
            "dataset-123", document_data
        )

        # 验证结果
        assert isinstance(result, DocumentCreateResponse)
        assert result.document["id"] == "doc-123"
        assert result.batch == "batch-123"

        # 验证API调用
        mock_api_client.post.assert_called_once_with(
            "datasets/dataset-123/document/create_by_text",
            json_data={
                "name": "测试文档",
                "text": "这是测试文档内容",
                "indexing_technique": "high_quality",
            },
        )

    @pytest.mark.asyncio
    async def test_create_document_by_file_success(
        self, document_api: DocumentAPI, mock_api_client: AsyncMock, tmp_path: Path
    ):
        """测试通过文件创建文档成功"""
        # 创建临时文件
        test_file = tmp_path / "test.txt"
        test_file.write_text("测试文件内容")

        # 准备响应数据
        response_data = {
            "document": {"id": "doc-123", "batch": "batch-123"},
            "batch": "batch-123",
        }
        mock_api_client.post.return_value = response_data

        # 执行测试
        document_data = DocumentCreateByFile(
            name="测试文档", file=str(test_file), indexing_technique="high_quality"
        )
        result = await document_api.create_document_by_file(
            "dataset-123", document_data
        )

        # 验证结果
        assert isinstance(result, DocumentCreateResponse)
        assert result.document["id"] == "doc-123"
        assert result.batch == "batch-123"

        # 验证API调用
        mock_api_client.post.assert_called_once()
        call_args = mock_api_client.post.call_args
        assert call_args[0][0] == "datasets/dataset-123/document/create_by_file"
        assert "files" in call_args[1]
        assert "data" in call_args[1]

    @pytest.mark.asyncio
    async def test_get_document_success(
        self,
        document_api: DocumentAPI,
        mock_api_client: AsyncMock,
        sample_document_data: dict,
    ):
        """测试获取文档详情成功"""
        # 准备响应数据
        mock_api_client.get.return_value = sample_document_data

        # 执行测试
        result = await document_api.get_document("dataset-123", "doc-123")

        # 验证结果
        assert isinstance(result, Document)
        assert result.id == sample_document_data["id"]
        assert result.name == sample_document_data["name"]

        # 验证API调用
        mock_api_client.get.assert_called_once_with(
            "datasets/dataset-123/documents/doc-123"
        )

    @pytest.mark.asyncio
    async def test_update_document_by_text_success(
        self,
        document_api: DocumentAPI,
        mock_api_client: AsyncMock,
        sample_document_data: dict,
    ):
        """测试通过文本更新文档成功"""
        # 准备响应数据
        updated_data = sample_document_data.copy()
        updated_data["name"] = "更新后的文档"
        mock_api_client.post.return_value = {
            "document": updated_data,
            "batch": "batch-456",
        }

        # 执行测试
        document_data = DocumentUpdateByText(name="更新后的文档", text="更新后的内容")
        result = await document_api.update_document_by_text(
            "dataset-123", "doc-123", document_data
        )

        # 验证结果
        assert isinstance(result, DocumentCreateResponse)
        assert result.document["name"] == "更新后的文档"
        assert result.batch == "batch-456"

        # 验证API调用
        mock_api_client.post.assert_called_once_with(
            "datasets/dataset-123/documents/doc-123/update_by_text",
            json_data={"name": "更新后的文档", "text": "更新后的内容"},
        )

    @pytest.mark.asyncio
    async def test_delete_document_success(
        self, document_api: DocumentAPI, mock_api_client: AsyncMock
    ):
        """测试删除文档成功"""
        # 准备响应数据
        mock_api_client.delete.return_value = {"success": True}

        # 执行测试
        result = await document_api.delete_document("dataset-123", "doc-123")

        # 验证结果
        assert result is True

        # 验证API调用
        mock_api_client.delete.assert_called_once_with(
            "datasets/dataset-123/documents/doc-123"
        )

    @pytest.mark.asyncio
    async def test_get_document_status_success(
        self, document_api: DocumentAPI, mock_api_client: AsyncMock
    ):
        """测试获取文档状态成功"""
        # 准备响应数据
        status_data = {
            "id": "doc-123",
            "status": "completed",
            "processing_started_at": 1640995200,
            "parsing_completed_at": 1640995260,
            "cleaning_completed_at": 1640995280,
            "splitting_completed_at": 1640995300,
            "completed_at": 1640995320,
            "paused_at": None,
            "error": None,
            "stopped_at": None,
        }
        mock_api_client.get.return_value = status_data

        # 执行测试
        result = await document_api.get_document_status("dataset-123", "doc-123")

        # 验证结果
        assert isinstance(result, DocumentStatus)
        assert result.id == "doc-123"
        assert result.status == "completed"

        # 验证API调用
        mock_api_client.get.assert_called_once_with(
            "datasets/dataset-123/documents/doc-123/status"
        )

    @pytest.mark.asyncio
    async def test_retry_document_processing(
        self, document_api: DocumentAPI, mock_api_client: AsyncMock
    ):
        """测试重试文档处理"""
        # 准备响应数据
        mock_api_client.patch.return_value = {"success": True}

        # 执行测试
        result = await document_api.retry_document_processing("dataset-123", "doc-123")

        # 验证结果
        assert result is True

        # 验证API调用
        mock_api_client.patch.assert_called_once_with(
            "datasets/dataset-123/documents/doc-123/processing/retry"
        )

    @pytest.mark.asyncio
    async def test_pause_document_processing(
        self, document_api: DocumentAPI, mock_api_client: AsyncMock
    ):
        """测试暂停文档处理"""
        # 准备响应数据
        mock_api_client.patch.return_value = {"success": True}

        # 执行测试
        result = await document_api.pause_document_processing("dataset-123", "doc-123")

        # 验证结果
        assert result is True

        # 验证API调用
        mock_api_client.patch.assert_called_once_with(
            "datasets/dataset-123/documents/doc-123/processing/pause"
        )

    @pytest.mark.asyncio
    async def test_resume_document_processing(
        self, document_api: DocumentAPI, mock_api_client: AsyncMock
    ):
        """测试恢复文档处理"""
        # 准备响应数据
        mock_api_client.patch.return_value = {"success": True}

        # 执行测试
        result = await document_api.resume_document_processing("dataset-123", "doc-123")

        # 验证结果
        assert result is True

        # 验证API调用
        mock_api_client.patch.assert_called_once_with(
            "datasets/dataset-123/documents/doc-123/processing/resume"
        )

    @pytest.mark.asyncio
    async def test_get_content_type_for_file(self, document_api: DocumentAPI):
        """测试获取文件Content-Type"""
        # 测试不同文件扩展名
        assert document_api._get_content_type("test.txt") == "text/plain"
        assert document_api._get_content_type("test.pdf") == "application/pdf"
        assert (
            document_api._get_content_type("test.docx")
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        assert (
            document_api._get_content_type("test.unknown") == "application/octet-stream"
        )

    @pytest.mark.asyncio
    async def test_invalid_dataset_id_raises_error(self, document_api: DocumentAPI):
        """测试无效的知识库ID抛出错误"""
        with pytest.raises(ValidationError):
            await document_api.list_documents("invalid-id")

    @pytest.mark.asyncio
    async def test_invalid_document_id_raises_error(self, document_api: DocumentAPI):
        """测试无效的文档ID抛出错误"""
        with pytest.raises(ValidationError):
            await document_api.get_document("dataset-123", "invalid-id")

    @pytest.mark.asyncio
    async def test_api_error_propagation(
        self, document_api: DocumentAPI, mock_api_client: AsyncMock
    ):
        """测试API错误传播"""
        # 模拟API错误
        mock_api_client.get.side_effect = DifyAPIError("API Error", status_code=500)

        # 执行测试并验证错误
        with pytest.raises(DifyAPIError):
            await document_api.get_document("dataset-123", "doc-123")

    @pytest.mark.asyncio
    async def test_list_documents_with_empty_query(
        self, document_api: DocumentAPI, mock_api_client: AsyncMock
    ):
        """测试使用空查询参数获取文档列表"""
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
        result = await document_api.list_documents("dataset-123")

        # 验证结果
        assert isinstance(result, DocumentList)
        assert len(result.data) == 0
        assert result.total == 0

        # 验证API调用（无参数）
        mock_api_client.get.assert_called_once_with(
            "datasets/dataset-123/documents", params={}
        )

    @pytest.mark.asyncio
    async def test_create_document_with_file_not_found(self, document_api: DocumentAPI):
        """测试文件不存在时创建文档"""
        document_data = DocumentCreateByFile(
            name="测试文档",
            file="/path/to/nonexistent/file.txt",
            indexing_technique="high_quality",
        )

        with pytest.raises(FileNotFoundError):
            await document_api.create_document_by_file("dataset-123", document_data)

    @pytest.mark.asyncio
    async def test_list_document_metadata(
        self, document_api: DocumentAPI, mock_api_client: AsyncMock
    ):
        """测试获取文档元数据列表"""
        # 准备响应数据
        metadata_data = {
            "data": [
                {
                    "id": "meta-123",
                    "key": "author",
                    "value": "张三",
                    "document_id": "doc-123",
                }
            ]
        }
        mock_api_client.get.return_value = metadata_data

        # 执行测试
        result = await document_api.list_document_metadata("dataset-123", "doc-123")

        # 验证结果
        assert result == metadata_data["data"]

        # 验证API调用
        mock_api_client.get.assert_called_once_with(
            "datasets/dataset-123/documents/doc-123/metadata"
        )
