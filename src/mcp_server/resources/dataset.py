"""知识库MCP资源"""

from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from pydantic import BaseModel, Field

from src.api.dataset import DatasetAPI
from src.utils.exceptions import DifyMCPException
from src.utils.logger import get_logger


class DatasetResource:
    """知识库MCP资源类"""

    def __init__(self, dataset_api: DatasetAPI):
        """初始化知识库资源

        Args:
            dataset_api: 知识库API实例
        """
        self.dataset_api = dataset_api
        self.logger = get_logger(__name__)

    def register_resources(self, mcp: FastMCP):
        """注册知识库相关的MCP资源

        Args:
            mcp: FastMCP服务器实例
        """
        self.logger.info("Registering dataset resources...")

        # 使用装饰器模式注册资源
        @mcp.resource("dataset://{dataset_id}")
        async def get_dataset_resource(dataset_id: str) -> Dict[str, Any]:
            """获取知识库资源"""
            return await self.get_dataset_resource(dataset_id)

        @mcp.resource("datasets://")
        async def get_datasets_resource() -> Dict[str, Any]:
            """获取知识库列表资源"""
            return await self.get_datasets_resource()

        self.logger.info("Dataset resources registered successfully")

    async def get_dataset_resource(self, dataset_id: str) -> Dict[str, Any]:
        """获取知识库资源

        Args:
            dataset_id: 知识库ID

        Returns:
            知识库资源数据
        """
        try:
            dataset = await self.dataset_api.get_dataset(dataset_id)
            return {
                "uri": f"dataset://{dataset_id}",
                "name": dataset.name,
                "description": dataset.description,
                "mimeType": "application/json",
                "text": dataset.model_dump_json(indent=2),
            }
        except Exception as e:
            self.logger.error(f"Failed to get dataset resource: {e}")
            raise DifyMCPException(f"获取知识库资源失败: {e}")

    async def get_datasets_resource(self) -> Dict[str, Any]:
        """获取知识库列表资源

        Returns:
            知识库列表资源数据
        """
        try:
            from src.models.dataset import DatasetListQuery

            query = DatasetListQuery(page=1, limit=100)
            dataset_list = await self.dataset_api.list_datasets(query)

            return {
                "uri": "datasets://",
                "name": "知识库列表",
                "description": f"包含 {len(dataset_list.data)} 个知识库",
                "mimeType": "application/json",
                "text": dataset_list.model_dump_json(indent=2),
            }
        except Exception as e:
            self.logger.error(f"Failed to get datasets resource: {e}")
            raise DifyMCPException(f"获取知识库列表资源失败: {e}")
