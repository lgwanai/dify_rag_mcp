"""文档MCP资源"""

from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from pydantic import BaseModel, Field

from src.api.document import DocumentAPI
from src.utils.exceptions import DifyMCPException
from src.utils.logger import get_logger


class DocumentResource:
    """文档MCP资源类"""

    def __init__(self, document_api: DocumentAPI):
        """初始化文档资源

        Args:
            document_api: 文档API实例
        """
        self.document_api = document_api
        self.logger = get_logger(__name__)

    def register_resources(self, mcp: FastMCP):
        """注册文档相关的MCP资源

        Args:
            mcp: FastMCP服务器实例
        """
        self.logger.info("Registering document resources...")

        # 使用装饰器模式注册资源
        @mcp.resource("document://{dataset_id}/{document_id}")
        async def get_document_resource(
            dataset_id: str, document_id: str
        ) -> Dict[str, Any]:
            """获取文档资源"""
            return await self.get_document_resource(dataset_id, document_id)

        @mcp.resource("documents://{dataset_id}")
        async def get_documents_resource(dataset_id: str) -> Dict[str, Any]:
            """获取文档列表资源"""
            return await self.get_documents_resource(dataset_id)

        self.logger.info("Document resources registered successfully")

    async def get_document_resource(
        self, dataset_id: str, document_id: str
    ) -> Dict[str, Any]:
        """获取文档资源

        Args:
            dataset_id: 知识库ID
            document_id: 文档ID

        Returns:
            文档资源数据
        """
        try:
            document = await self.document_api.get_document(dataset_id, document_id)
            return {
                "uri": f"document://{dataset_id}/{document_id}",
                "name": document.name,
                "description": f"文档ID: {document_id}",
                "mimeType": "application/json",
                "text": document.model_dump_json(indent=2),
            }
        except Exception as e:
            self.logger.error(f"Failed to get document resource: {e}")
            raise DifyMCPException(f"获取文档资源失败: {e}")

    async def get_documents_resource(self, dataset_id: str) -> Dict[str, Any]:
        """获取文档列表资源

        Args:
            dataset_id: 知识库ID

        Returns:
            文档列表资源数据
        """
        try:
            from src.models.document import DocumentListQuery

            query = DocumentListQuery(page=1, limit=100)
            document_list = await self.document_api.list_documents(dataset_id, query)

            return {
                "uri": f"documents://{dataset_id}",
                "name": f"知识库 {dataset_id} 的文档列表",
                "description": f"包含 {len(document_list.data)} 个文档",
                "mimeType": "application/json",
                "text": document_list.model_dump_json(indent=2),
            }
        except Exception as e:
            self.logger.error(f"Failed to get documents resource: {e}")
            raise DifyMCPException(f"获取文档列表资源失败: {e}")
