"""分段MCP资源"""

from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from pydantic import BaseModel, Field

from src.api.segment import SegmentAPI
from src.utils.exceptions import DifyMCPException
from src.utils.logger import get_logger


class SegmentResource:
    """分段MCP资源类"""

    def __init__(self, segment_api: SegmentAPI):
        """初始化分段资源

        Args:
            segment_api: 分段API实例
        """
        self.segment_api = segment_api
        self.logger = get_logger(__name__)

    def register_resources(self, mcp: FastMCP):
        """注册分段相关的MCP资源

        Args:
            mcp: FastMCP服务器实例
        """
        self.logger.info("Registering segment resources...")

        # 使用装饰器模式注册资源
        @mcp.resource("segment://{dataset_id}/{document_id}/{segment_id}")
        async def get_segment_resource(
            dataset_id: str, document_id: str, segment_id: str
        ) -> Dict[str, Any]:
            """获取分段资源"""
            return await self.get_segment_resource(dataset_id, document_id, segment_id)

        @mcp.resource("segments://{dataset_id}/{document_id}")
        async def get_segments_resource(
            dataset_id: str, document_id: str
        ) -> Dict[str, Any]:
            """获取分段列表资源"""
            return await self.get_segments_resource(dataset_id, document_id)

        self.logger.info("Segment resources registered successfully")

    async def get_segment_resource(
        self, dataset_id: str, document_id: str, segment_id: str
    ) -> Dict[str, Any]:
        """获取分段资源

        Args:
            dataset_id: 知识库ID
            document_id: 文档ID
            segment_id: 分段ID

        Returns:
            分段资源数据
        """
        try:
            segment = await self.segment_api.get_segment(
                dataset_id, document_id, segment_id
            )
            return {
                "uri": f"segment://{dataset_id}/{document_id}/{segment_id}",
                "name": f"分段 {segment_id}",
                "description": f"文档 {document_id} 的分段",
                "mimeType": "application/json",
                "text": segment.model_dump_json(indent=2),
            }
        except Exception as e:
            self.logger.error(f"Failed to get segment resource: {e}")
            raise DifyMCPException(f"获取分段资源失败: {e}")

    async def get_segments_resource(
        self, dataset_id: str, document_id: str
    ) -> Dict[str, Any]:
        """获取分段列表资源

        Args:
            dataset_id: 知识库ID
            document_id: 文档ID

        Returns:
            分段列表资源数据
        """
        try:
            from src.models.segment import SegmentListQuery

            query = SegmentListQuery(page=1, limit=100)
            segment_list = await self.segment_api.list_segments(
                dataset_id, document_id, query
            )

            return {
                "uri": f"segments://{dataset_id}/{document_id}",
                "name": f"文档 {document_id} 的分段列表",
                "description": f"包含 {len(segment_list.data)} 个分段",
                "mimeType": "application/json",
                "text": segment_list.model_dump_json(indent=2),
            }
        except Exception as e:
            self.logger.error(f"Failed to get segments resource: {e}")
            raise DifyMCPException(f"获取分段列表资源失败: {e}")
