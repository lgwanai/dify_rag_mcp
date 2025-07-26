"""文档API模块"""

from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional

from ..models.document import (Document, DocumentCreateByFile,
                               DocumentCreateByText, DocumentCreateResponse,
                               DocumentList, DocumentListQuery,
                               DocumentMetadata, DocumentMetadataCreate,
                               DocumentMetadataList, DocumentMetadataUpdate,
                               DocumentStatus, DocumentUpdateByFile,
                               DocumentUpdateByText, DocumentUpdateStatus,
                               UploadFile)
from ..utils.logger import get_logger
from ..utils.validators import validate_dataset_id, validate_document_id
from .client import DifyAPIClient


class DocumentAPI:
    """文档API类"""

    def __init__(self, client: DifyAPIClient):
        """初始化文档API

        Args:
            client: Dify API客户端
        """
        self.client = client
        self.logger = get_logger(__name__)

    async def list_documents(
        self, dataset_id: str, query: Optional[DocumentListQuery] = None
    ) -> DocumentList:
        """获取文档列表

        Args:
            dataset_id: 知识库ID
            query: 查询参数

        Returns:
            文档列表
        """
        validate_dataset_id(dataset_id)

        params = {}
        if query:
            if query.keyword:
                params["keyword"] = query.keyword
            if query.status:
                params["status"] = query.status
            if query.page:
                params["page"] = query.page
            if query.limit:
                params["limit"] = query.limit
            if query.search_id:
                params["search_id"] = query.search_id

        response = await self.client.get(
            f"datasets/{dataset_id}/documents", params=params
        )
        return DocumentList(**response)

    async def create_document_by_text(
        self, dataset_id: str, document_data: DocumentCreateByText
    ) -> DocumentCreateResponse:
        """通过文本创建文档

        Args:
            dataset_id: 知识库ID
            document_data: 文档创建数据

        Returns:
            创建响应
        """
        validate_dataset_id(dataset_id)
        data = document_data.model_dump(exclude_none=True)
        response = await self.client.post(
            f"datasets/{dataset_id}/document/create_by_text", json_data=data
        )
        return DocumentCreateResponse(**response)

    async def create_document_by_file(
        self,
        dataset_id: str,
        document_data: DocumentCreateByFile,
        file_path: Optional[str] = None,
        file_content: Optional[bytes] = None,
        file_name: Optional[str] = None,
    ) -> DocumentCreateResponse:
        """通过文件创建文档

        Args:
            dataset_id: 知识库ID
            document_data: 文档创建数据
            file_path: 文件路径
            file_content: 文件内容
            file_name: 文件名

        Returns:
            创建响应
        """
        validate_dataset_id(dataset_id)

        # 准备文件数据
        files = {}
        if file_path:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            with open(file_path_obj, "rb") as f:
                files["file"] = (
                    file_path_obj.name,
                    f.read(),
                    self._get_content_type(file_path_obj),
                )
        elif file_content and file_name:
            files["file"] = (
                file_name,
                file_content,
                self._get_content_type_by_name(file_name),
            )
        else:
            raise ValueError(
                "Either file_path or (file_content and file_name) must be provided"
            )

        # 准备表单数据
        data = document_data.model_dump(exclude_none=True, exclude={"file"})

        response = await self.client.post(
            f"datasets/{dataset_id}/document/create_by_file", data=data, files=files
        )
        return DocumentCreateResponse(**response)

    async def get_document(self, dataset_id: str, document_id: str) -> Document:
        """获取文档详情

        Args:
            dataset_id: 知识库ID
            document_id: 文档ID

        Returns:
            文档详情
        """
        validate_dataset_id(dataset_id)
        validate_document_id(document_id)

        response = await self.client.get(
            f"datasets/{dataset_id}/documents/{document_id}"
        )
        return Document(**response)

    async def update_document_by_text(
        self, dataset_id: str, document_id: str, document_data: DocumentUpdateByText
    ) -> Document:
        """通过文本更新文档

        Args:
            dataset_id: 知识库ID
            document_id: 文档ID
            document_data: 更新数据

        Returns:
            更新后的文档
        """
        validate_dataset_id(dataset_id)
        validate_document_id(document_id)

        data = document_data.model_dump(exclude_none=True)
        response = await self.client.post(
            f"datasets/{dataset_id}/documents/{document_id}/update_by_text",
            json_data=data,
        )
        return Document(**response)

    async def update_document_by_file(
        self,
        dataset_id: str,
        document_id: str,
        document_data: DocumentUpdateByFile,
        file_path: Optional[str] = None,
        file_content: Optional[bytes] = None,
        file_name: Optional[str] = None,
    ) -> Document:
        """通过文件更新文档

        Args:
            dataset_id: 知识库ID
            document_id: 文档ID
            document_data: 更新数据
            file_path: 文件路径
            file_content: 文件内容
            file_name: 文件名

        Returns:
            更新后的文档
        """
        validate_dataset_id(dataset_id)
        validate_document_id(document_id)

        # 准备文件数据
        files = {}
        if file_path:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            with open(file_path_obj, "rb") as f:
                files["file"] = (
                    file_path_obj.name,
                    f.read(),
                    self._get_content_type(file_path_obj),
                )
        elif file_content and file_name:
            files["file"] = (
                file_name,
                file_content,
                self._get_content_type_by_name(file_name),
            )

        # 准备表单数据
        data = document_data.model_dump(exclude_none=True, exclude={"file"})

        response = await self.client.post(
            f"datasets/{dataset_id}/documents/{document_id}/update_by_file",
            data=data,
            files=files if files else None,
        )
        return Document(**response)

    async def delete_document(self, dataset_id: str, document_id: str) -> bool:
        """删除文档

        Args:
            dataset_id: 知识库ID
            document_id: 文档ID

        Returns:
            是否删除成功
        """
        validate_dataset_id(dataset_id)
        validate_document_id(document_id)

        await self.client.delete(f"datasets/{dataset_id}/documents/{document_id}")
        return True

    async def get_document_status(
        self, dataset_id: str, document_id: str
    ) -> DocumentStatus:
        """获取文档状态

        Args:
            dataset_id: 知识库ID
            document_id: 文档ID

        Returns:
            文档状态
        """
        validate_dataset_id(dataset_id)
        validate_document_id(document_id)

        response = await self.client.get(
            f"datasets/{dataset_id}/documents/{document_id}/status"
        )
        return DocumentStatus(**response)

    async def update_document_status(
        self, dataset_id: str, document_id: str, status_data: DocumentUpdateStatus
    ) -> bool:
        """更新文档状态

        Args:
            dataset_id: 知识库ID
            document_id: 文档ID
            status_data: 状态更新数据

        Returns:
            是否更新成功
        """
        validate_dataset_id(dataset_id)
        validate_document_id(document_id)

        data = status_data.model_dump(exclude_none=True)
        await self.client.patch(
            f"datasets/{dataset_id}/documents/{document_id}/status", json_data=data
        )
        return True

    async def retry_document_processing(
        self, dataset_id: str, document_id: str
    ) -> bool:
        """重试文档处理

        Args:
            dataset_id: 知识库ID
            document_id: 文档ID

        Returns:
            是否重试成功
        """
        validate_dataset_id(dataset_id)
        validate_document_id(document_id)

        await self.client.post(
            f"datasets/{dataset_id}/documents/{document_id}/processing/retry"
        )
        return True

    async def pause_document_processing(
        self, dataset_id: str, document_id: str
    ) -> bool:
        """暂停文档处理

        Args:
            dataset_id: 知识库ID
            document_id: 文档ID

        Returns:
            是否暂停成功
        """
        validate_dataset_id(dataset_id)
        validate_document_id(document_id)

        await self.client.post(
            f"datasets/{dataset_id}/documents/{document_id}/processing/pause"
        )
        return True

    async def resume_document_processing(
        self, dataset_id: str, document_id: str
    ) -> bool:
        """恢复文档处理

        Args:
            dataset_id: 知识库ID
            document_id: 文档ID

        Returns:
            是否恢复成功
        """
        validate_dataset_id(dataset_id)
        validate_document_id(document_id)

        await self.client.post(
            f"datasets/{dataset_id}/documents/{document_id}/processing/resume"
        )
        return True

    # 文档元数据管理
    async def list_document_metadata(
        self, dataset_id: str, document_id: str
    ) -> DocumentMetadataList:
        """获取文档元数据列表

        Args:
            dataset_id: 知识库ID
            document_id: 文档ID

        Returns:
            元数据列表
        """
        validate_dataset_id(dataset_id)
        validate_document_id(document_id)

        response = await self.client.get(
            f"datasets/{dataset_id}/documents/{document_id}/metadata"
        )
        return DocumentMetadataList(**response)

    async def create_document_metadata(
        self, dataset_id: str, document_id: str, metadata_data: DocumentMetadataCreate
    ) -> DocumentMetadata:
        """创建文档元数据

        Args:
            dataset_id: 知识库ID
            document_id: 文档ID
            metadata_data: 元数据创建数据

        Returns:
            创建的元数据
        """
        validate_dataset_id(dataset_id)
        validate_document_id(document_id)

        data = metadata_data.model_dump(exclude_none=True)
        response = await self.client.post(
            f"datasets/{dataset_id}/documents/{document_id}/metadata", json_data=data
        )
        return DocumentMetadata(**response)

    async def update_document_metadata(
        self,
        dataset_id: str,
        document_id: str,
        metadata_id: str,
        metadata_data: DocumentMetadataUpdate,
    ) -> DocumentMetadata:
        """更新文档元数据

        Args:
            dataset_id: 知识库ID
            document_id: 文档ID
            metadata_id: 元数据ID
            metadata_data: 更新数据

        Returns:
            更新后的元数据
        """
        validate_dataset_id(dataset_id)
        validate_document_id(document_id)

        data = metadata_data.model_dump(exclude_none=True)
        response = await self.client.patch(
            f"datasets/{dataset_id}/documents/{document_id}/metadata/{metadata_id}",
            json_data=data,
        )
        return DocumentMetadata(**response)

    async def delete_document_metadata(
        self, dataset_id: str, document_id: str, metadata_id: str
    ) -> bool:
        """删除文档元数据

        Args:
            dataset_id: 知识库ID
            document_id: 文档ID
            metadata_id: 元数据ID

        Returns:
            是否删除成功
        """
        validate_dataset_id(dataset_id)
        validate_document_id(document_id)

        await self.client.delete(
            f"datasets/{dataset_id}/documents/{document_id}/metadata/{metadata_id}"
        )
        return True

    def _get_content_type(self, file_path: Path) -> str:
        """根据文件扩展名获取Content-Type"""
        suffix = file_path.suffix.lower()
        content_types = {
            ".txt": "text/plain",
            ".md": "text/markdown",
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".xls": "application/vnd.ms-excel",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".ppt": "application/vnd.ms-powerpoint",
            ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            ".csv": "text/csv",
            ".json": "application/json",
            ".xml": "application/xml",
            ".html": "text/html",
            ".htm": "text/html",
        }
        return content_types.get(suffix, "application/octet-stream")

    def _get_content_type_by_name(self, file_name: str) -> str:
        """根据文件名获取Content-Type"""
        return self._get_content_type(Path(file_name))
