"""文档MCP工具"""

from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from pydantic import BaseModel, Field

from src.api.document import DocumentAPI
from src.models.document import (DocumentCreate, DocumentListQuery,
                                DocumentUpdate)
from src.utils.exceptions import DifyMCPException
from src.utils.logger import get_logger


class CreateDocumentArgs(BaseModel):
    """创建文档参数"""

    dataset_id: str = Field(description="知识库ID")
    name: str = Field(description="文档名称")
    text: Optional[str] = Field(default=None, description="文档文本内容")
    indexing_technique: str = Field(default="high_quality", description="索引技术")
    process_rule: Optional[Dict[str, Any]] = Field(default=None, description="处理规则")


class UpdateDocumentArgs(BaseModel):
    """更新文档参数"""

    dataset_id: str = Field(description="知识库ID")
    document_id: str = Field(description="文档ID")
    name: Optional[str] = Field(default=None, description="文档名称")
    text: Optional[str] = Field(default=None, description="文档文本内容")
    process_rule: Optional[Dict[str, Any]] = Field(default=None, description="处理规则")


class ListDocumentsArgs(BaseModel):
    """获取文档列表参数"""

    dataset_id: str = Field(description="知识库ID")
    page: int = Field(default=1, description="页码")
    limit: int = Field(default=20, description="每页条数")
    keyword: Optional[str] = Field(default=None, description="搜索关键词")
    status: Optional[str] = Field(default=None, description="文档状态")


class GetDocumentArgs(BaseModel):
    """获取文档详情参数"""

    dataset_id: str = Field(description="知识库ID")
    document_id: str = Field(description="文档ID")


class DeleteDocumentArgs(BaseModel):
    """删除文档参数"""

    dataset_id: str = Field(description="知识库ID")
    document_id: str = Field(description="文档ID")


class DocumentTools:
    """文档MCP工具类"""

    def __init__(self, document_api: DocumentAPI):
        """初始化文档工具

        Args:
            document_api: 文档API实例
        """
        self.document_api = document_api
        self.logger = get_logger(__name__)

    def register_tools(self, mcp: FastMCP):
        """注册文档相关的MCP工具

        Args:
            mcp: FastMCP服务器实例
        """
        self.logger.info("Registering document tools...")

        # 使用装饰器模式注册工具
        @mcp.tool
        async def create_document(args: CreateDocumentArgs) -> dict:
            """创建文档"""
            return await self.create_document(args)

        @mcp.tool
        async def list_documents(args: ListDocumentsArgs) -> dict:
            """列出文档"""
            return await self.list_documents(args)

        self.logger.info("Document tools registered successfully")

    async def create_document(self, args: CreateDocumentArgs) -> Dict[str, Any]:
        """创建文档"""
        try:
            document_data = DocumentCreate(
                name=args.name,
                text=args.text,
                indexing_technique=args.indexing_technique,
                process_rule=args.process_rule,
            )

            document = await self.document_api.create_document(
                args.dataset_id, document_data
            )
            return {
                "success": True,
                "data": document.model_dump(),
                "message": f"文档 '{document.name}' 创建成功",
            }
        except Exception as e:
            self.logger.error(f"Failed to create document: {e}")
            raise DifyMCPException(f"创建文档失败: {e}")

    async def update_document(self, args: UpdateDocumentArgs) -> Dict[str, Any]:
        """更新文档"""
        try:
            document_data = DocumentUpdate(
                name=args.name, text=args.text, process_rule=args.process_rule
            )

            document = await self.document_api.update_document(
                args.dataset_id, args.document_id, document_data
            )
            return {
                "success": True,
                "data": document.model_dump(),
                "message": f"文档 '{document.name}' 更新成功",
            }
        except Exception as e:
            self.logger.error(f"Failed to update document: {e}")
            raise DifyMCPException(f"更新文档失败: {e}")

    async def list_documents(self, args: ListDocumentsArgs) -> Dict[str, Any]:
        """获取文档列表"""
        try:
            query = DocumentListQuery(
                page=args.page,
                limit=args.limit,
                keyword=args.keyword,
                status=args.status,
            )

            document_list = await self.document_api.list_documents(
                args.dataset_id, query
            )
            return {
                "success": True,
                "data": document_list.model_dump(),
                "message": f"获取到 {len(document_list.data)} 个文档",
            }
        except Exception as e:
            self.logger.error(f"Failed to list documents: {e}")
            raise DifyMCPException(f"获取文档列表失败: {e}")

    async def get_document(self, args: GetDocumentArgs) -> Dict[str, Any]:
        """获取文档详情"""
        try:
            document = await self.document_api.get_document(
                args.dataset_id, args.document_id
            )
            return {
                "success": True,
                "data": document.model_dump(),
                "message": f"获取文档 '{document.name}' 详情成功",
            }
        except Exception as e:
            self.logger.error(f"Failed to get document: {e}")
            raise DifyMCPException(f"获取文档详情失败: {e}")

    async def delete_document(self, args: DeleteDocumentArgs) -> Dict[str, Any]:
        """删除文档"""
        try:
            success = await self.document_api.delete_document(
                args.dataset_id, args.document_id
            )
            return {
                "success": success,
                "message": "文档删除成功" if success else "文档删除失败",
            }
        except Exception as e:
            self.logger.error(f"Failed to delete document: {e}")
            raise DifyMCPException(f"删除文档失败: {e}")

    async def get_document_indexing_status(
        self, args: GetDocumentArgs
    ) -> Dict[str, Any]:
        """获取文档索引状态"""
        try:
            status = await self.document_api.get_document_indexing_status(
                args.dataset_id, args.document_id
            )
            return {"success": True, "data": status, "message": "获取文档索引状态成功"}
        except Exception as e:
            self.logger.error(f"Failed to get document indexing status: {e}")
            raise DifyMCPException(f"获取文档索引状态失败: {e}")

    async def pause_document_indexing(self, args: GetDocumentArgs) -> Dict[str, Any]:
        """暂停文档索引"""
        try:
            success = await self.document_api.pause_document_indexing(
                args.dataset_id, args.document_id
            )
            return {
                "success": success,
                "message": "文档索引暂停成功" if success else "文档索引暂停失败",
            }
        except Exception as e:
            self.logger.error(f"Failed to pause document indexing: {e}")
            raise DifyMCPException(f"暂停文档索引失败: {e}")

    async def resume_document_indexing(self, args: GetDocumentArgs) -> Dict[str, Any]:
        """恢复文档索引"""
        try:
            success = await self.document_api.resume_document_indexing(
                args.dataset_id, args.document_id
            )
            return {
                "success": success,
                "message": "文档索引恢复成功" if success else "文档索引恢复失败",
            }
        except Exception as e:
            self.logger.error(f"Failed to resume document indexing: {e}")
            raise DifyMCPException(f"恢复文档索引失败: {e}")
