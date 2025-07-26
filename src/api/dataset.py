"""知识库API模块"""

from typing import Any, Dict, List, Optional

from ..models.common import DataResponse, PaginationResponse
from ..models.dataset import (Dataset, DatasetCreate, DatasetList,
                              DatasetListQuery, DatasetTag, DatasetTagBinding,
                              DatasetTagCreate, DatasetTagUpdate,
                              DatasetUpdate, EmbeddingModelList)
from ..utils.logger import get_logger
from ..utils.validators import validate_dataset_id, validate_uuid
from .client import DifyAPIClient


class DatasetAPI:
    """知识库API类"""

    def __init__(self, client: DifyAPIClient):
        """初始化知识库API

        Args:
            client: Dify API客户端
        """
        self.client = client
        self.logger = get_logger(__name__)

    async def list_datasets(
        self, query: Optional[DatasetListQuery] = None
    ) -> DatasetList:
        """获取知识库列表

        Args:
            query: 查询参数

        Returns:
            知识库列表
        """
        params = {}
        if query:
            if query.page:
                params["page"] = query.page
            if query.limit:
                params["limit"] = query.limit
            if query.keyword:
                params["keyword"] = query.keyword
            if query.tag_ids:
                params["tag_ids"] = ",".join(query.tag_ids)

        response = await self.client.get("datasets", params=params)
        return DatasetList(**response)

    async def create_dataset(self, dataset_data: DatasetCreate) -> Dataset:
        """创建知识库

        Args:
            dataset_data: 知识库创建数据

        Returns:
            创建的知识库
        """
        data = dataset_data.model_dump(exclude_none=True)
        response = await self.client.post("datasets", json_data=data)
        return Dataset(**response)

    async def get_dataset(self, dataset_id: str) -> Dataset:
        """获取知识库详情

        Args:
            dataset_id: 知识库ID

        Returns:
            知识库详情
        """
        validate_dataset_id(dataset_id)
        response = await self.client.get(f"datasets/{dataset_id}")
        return Dataset(**response)

    async def update_dataset(
        self, dataset_id: str, dataset_data: DatasetUpdate
    ) -> Dataset:
        """更新知识库

        Args:
            dataset_id: 知识库ID
            dataset_data: 更新数据

        Returns:
            更新后的知识库
        """
        validate_dataset_id(dataset_id)
        data = dataset_data.model_dump(exclude_none=True)
        response = await self.client.patch(f"datasets/{dataset_id}", json_data=data)
        return Dataset(**response)

    async def delete_dataset(self, dataset_id: str) -> bool:
        """删除知识库

        Args:
            dataset_id: 知识库ID

        Returns:
            是否删除成功
        """
        validate_dataset_id(dataset_id)
        await self.client.delete(f"datasets/{dataset_id}")
        return True

    async def get_dataset_queries(self, dataset_id: str) -> List[Dict[str, Any]]:
        """获取知识库查询记录

        Args:
            dataset_id: 知识库ID

        Returns:
            查询记录列表
        """
        validate_dataset_id(dataset_id)
        response = await self.client.get(f"datasets/{dataset_id}/queries")
        return response.get("data", [])

    async def get_dataset_indexing_status(self, dataset_id: str) -> Dict[str, Any]:
        """获取知识库索引状态

        Args:
            dataset_id: 知识库ID

        Returns:
            索引状态信息
        """
        validate_dataset_id(dataset_id)
        response = await self.client.get(f"datasets/{dataset_id}/indexing-status")
        return response

    async def get_dataset_error_docs(self, dataset_id: str) -> List[Dict[str, Any]]:
        """获取知识库错误文档

        Args:
            dataset_id: 知识库ID

        Returns:
            错误文档列表
        """
        validate_dataset_id(dataset_id)
        response = await self.client.get(f"datasets/{dataset_id}/error-docs")
        return response.get("data", [])

    # 标签管理
    async def list_dataset_tags(self) -> List[DatasetTag]:
        """获取知识库标签列表

        Returns:
            标签列表
        """
        response = await self.client.get("datasets/tags")
        return [DatasetTag(**tag) for tag in response.get("data", [])]

    async def create_dataset_tag(self, tag_data: DatasetTagCreate) -> DatasetTag:
        """创建知识库标签

        Args:
            tag_data: 标签创建数据

        Returns:
            创建的标签
        """
        data = tag_data.model_dump(exclude_none=True)
        response = await self.client.post("datasets/tags", json_data=data)
        return DatasetTag(**response)

    async def update_dataset_tag(
        self, tag_id: str, tag_data: DatasetTagUpdate
    ) -> DatasetTag:
        """更新知识库标签

        Args:
            tag_id: 标签ID
            tag_data: 更新数据

        Returns:
            更新后的标签
        """
        validate_uuid(tag_id)
        data = tag_data.model_dump(exclude_none=True)
        response = await self.client.patch(f"datasets/tags/{tag_id}", json_data=data)
        return DatasetTag(**response)

    async def delete_dataset_tag(self, tag_id: str) -> bool:
        """删除知识库标签

        Args:
            tag_id: 标签ID

        Returns:
            是否删除成功
        """
        validate_uuid(tag_id)
        await self.client.delete(f"datasets/tags/{tag_id}")
        return True

    async def bind_dataset_tags(
        self, dataset_id: str, tag_binding: DatasetTagBinding
    ) -> bool:
        """绑定知识库标签

        Args:
            dataset_id: 知识库ID
            tag_binding: 标签绑定数据

        Returns:
            是否绑定成功
        """
        validate_dataset_id(dataset_id)
        data = tag_binding.model_dump(exclude_none=True)
        await self.client.post(f"datasets/{dataset_id}/tags", json_data=data)
        return True

    async def unbind_dataset_tags(
        self, dataset_id: str, tag_binding: DatasetTagBinding
    ) -> bool:
        """解绑知识库标签

        Args:
            dataset_id: 知识库ID
            tag_binding: 标签绑定数据

        Returns:
            是否解绑成功
        """
        validate_dataset_id(dataset_id)
        data = tag_binding.model_dump(exclude_none=True)
        await self.client.delete(f"datasets/{dataset_id}/tags", json_data=data)
        return True

    # 嵌入模型管理
    async def list_embedding_models(self) -> EmbeddingModelList:
        """获取嵌入模型列表

        Returns:
            嵌入模型列表
        """
        response = await self.client.get("datasets/embedding-models")
        return EmbeddingModelList(**response)

    async def get_dataset_retrieval_settings(self, dataset_id: str) -> Dict[str, Any]:
        """获取知识库检索设置

        Args:
            dataset_id: 知识库ID

        Returns:
            检索设置
        """
        validate_dataset_id(dataset_id)
        response = await self.client.get(f"datasets/{dataset_id}/retrieval-settings")
        return response

    async def update_dataset_retrieval_settings(
        self, dataset_id: str, settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """更新知识库检索设置

        Args:
            dataset_id: 知识库ID
            settings: 检索设置

        Returns:
            更新后的检索设置
        """
        validate_dataset_id(dataset_id)
        response = await self.client.patch(
            f"datasets/{dataset_id}/retrieval-settings", json_data=settings
        )
        return response

    async def copy_dataset(self, dataset_id: str, name: str) -> Dataset:
        """复制知识库

        Args:
            dataset_id: 源知识库ID
            name: 新知识库名称

        Returns:
            复制的知识库
        """
        validate_dataset_id(dataset_id)
        data = {"name": name}
        response = await self.client.post(f"datasets/{dataset_id}/copy", json_data=data)
        return Dataset(**response)

    async def export_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """导出知识库

        Args:
            dataset_id: 知识库ID

        Returns:
            导出信息
        """
        validate_dataset_id(dataset_id)
        response = await self.client.post(f"datasets/{dataset_id}/export")
        return response

    async def import_dataset(self, import_data: Dict[str, Any]) -> Dataset:
        """导入知识库

        Args:
            import_data: 导入数据

        Returns:
            导入的知识库
        """
        response = await self.client.post("datasets/import", json_data=import_data)
        return Dataset(**response)
