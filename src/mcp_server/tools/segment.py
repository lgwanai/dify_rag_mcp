"""分段MCP工具"""

from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from pydantic import BaseModel, Field

from src.api.segment import SegmentAPI
from src.models.segment import SegmentCreate, SegmentListQuery, SegmentUpdate
from src.utils.exceptions import DifyMCPException
from src.utils.logger import get_logger


class CreateSegmentArgs(BaseModel):
    """创建分段参数"""

    dataset_id: str = Field(description="知识库ID")
    document_id: str = Field(description="文档ID")
    content: str = Field(description="分段内容")
    answer: Optional[str] = Field(default=None, description="分段答案")
    keywords: Optional[List[str]] = Field(default=None, description="关键词列表")


class UpdateSegmentArgs(BaseModel):
    """更新分段参数"""

    dataset_id: str = Field(description="知识库ID")
    document_id: str = Field(description="文档ID")
    segment_id: str = Field(description="分段ID")
    content: Optional[str] = Field(default=None, description="分段内容")
    answer: Optional[str] = Field(default=None, description="分段答案")
    keywords: Optional[List[str]] = Field(default=None, description="关键词列表")
    enabled: Optional[bool] = Field(default=None, description="是否启用")


class ListSegmentsArgs(BaseModel):
    """获取分段列表参数"""

    dataset_id: str = Field(description="知识库ID")
    document_id: str = Field(description="文档ID")
    page: int = Field(default=1, description="页码")
    limit: int = Field(default=20, description="每页条数")
    keyword: Optional[str] = Field(default=None, description="搜索关键词")
    status: Optional[str] = Field(default=None, description="分段状态")


class GetSegmentArgs(BaseModel):
    """获取分段详情参数"""

    dataset_id: str = Field(description="知识库ID")
    document_id: str = Field(description="文档ID")
    segment_id: str = Field(description="分段ID")


class DeleteSegmentArgs(BaseModel):
    """删除分段参数"""

    dataset_id: str = Field(description="知识库ID")
    document_id: str = Field(description="文档ID")
    segment_id: str = Field(description="分段ID")


class SegmentTools:
    """分段MCP工具类"""

    def __init__(self, segment_api: SegmentAPI):
        """初始化分段工具

        Args:
            segment_api: 分段API实例
        """
        self.segment_api = segment_api
        self.logger = get_logger(__name__)

    def register_tools(self, mcp: FastMCP):
        """注册分段相关的MCP工具

        Args:
            mcp: FastMCP服务器实例
        """
        self.logger.info("Registering segment tools...")

        # 使用装饰器模式注册工具
        @mcp.tool
        async def create_segment(args: CreateSegmentArgs) -> dict:
            """创建分段"""
            return await self.create_segment(args)

        @mcp.tool
        async def list_segments(args: ListSegmentsArgs) -> dict:
            """列出分段"""
            return await self.list_segments(args)

        self.logger.info("Segment tools registered successfully")

    async def create_segment(self, args: CreateSegmentArgs) -> Dict[str, Any]:
        """创建分段"""
        try:
            segment_data = SegmentCreate(
                content=args.content, answer=args.answer, keywords=args.keywords
            )

            segment = await self.segment_api.create_segment(
                args.dataset_id, args.document_id, segment_data
            )
            return {
                "success": True,
                "data": segment.model_dump(),
                "message": "分段创建成功",
            }
        except Exception as e:
            self.logger.error(f"Failed to create segment: {e}")
            raise DifyMCPException(f"创建分段失败: {e}")

    async def update_segment(self, args: UpdateSegmentArgs) -> Dict[str, Any]:
        """更新分段"""
        try:
            segment_data = SegmentUpdate(
                content=args.content,
                answer=args.answer,
                keywords=args.keywords,
                enabled=args.enabled,
            )

            segment = await self.segment_api.update_segment(
                args.dataset_id, args.document_id, args.segment_id, segment_data
            )
            return {
                "success": True,
                "data": segment.model_dump(),
                "message": "分段更新成功",
            }
        except Exception as e:
            self.logger.error(f"Failed to update segment: {e}")
            raise DifyMCPException(f"更新分段失败: {e}")

    async def list_segments(self, args: ListSegmentsArgs) -> Dict[str, Any]:
        """获取分段列表"""
        try:
            query = SegmentListQuery(
                page=args.page,
                limit=args.limit,
                keyword=args.keyword,
                status=args.status,
            )

            segment_list = await self.segment_api.list_segments(
                args.dataset_id, args.document_id, query
            )
            return {
                "success": True,
                "data": segment_list.model_dump(),
                "message": f"获取到 {len(segment_list.data)} 个分段",
            }
        except Exception as e:
            self.logger.error(f"Failed to list segments: {e}")
            raise DifyMCPException(f"获取分段列表失败: {e}")

    async def get_segment(self, args: GetSegmentArgs) -> Dict[str, Any]:
        """获取分段详情"""
        try:
            segment = await self.segment_api.get_segment(
                args.dataset_id, args.document_id, args.segment_id
            )
            return {
                "success": True,
                "data": segment.model_dump(),
                "message": "获取分段详情成功",
            }
        except Exception as e:
            self.logger.error(f"Failed to get segment: {e}")
            raise DifyMCPException(f"获取分段详情失败: {e}")

    async def delete_segment(self, args: DeleteSegmentArgs) -> Dict[str, Any]:
        """删除分段"""
        try:
            success = await self.segment_api.delete_segment(
                args.dataset_id, args.document_id, args.segment_id
            )
            return {
                "success": success,
                "message": "分段删除成功" if success else "分段删除失败",
            }
        except Exception as e:
            self.logger.error(f"Failed to delete segment: {e}")
            raise DifyMCPException(f"删除分段失败: {e}")

    async def enable_segment(self, args: GetSegmentArgs) -> Dict[str, Any]:
        """启用分段"""
        try:
            segment_data = SegmentUpdate(enabled=True)
            segment = await self.segment_api.update_segment(
                args.dataset_id, args.document_id, args.segment_id, segment_data
            )
            return {
                "success": True,
                "data": segment.model_dump(),
                "message": "分段启用成功",
            }
        except Exception as e:
            self.logger.error(f"Failed to enable segment: {e}")
            raise DifyMCPException(f"启用分段失败: {e}")

    async def disable_segment(self, args: GetSegmentArgs) -> Dict[str, Any]:
        """禁用分段"""
        try:
            segment_data = SegmentUpdate(enabled=False)
            segment = await self.segment_api.update_segment(
                args.dataset_id, args.document_id, args.segment_id, segment_data
            )
            return {
                "success": True,
                "data": segment.model_dump(),
                "message": "分段禁用成功",
            }
        except Exception as e:
            self.logger.error(f"Failed to disable segment: {e}")
            raise DifyMCPException(f"禁用分段失败: {e}")
