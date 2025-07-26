"""知识库MCP工具"""

from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from pydantic import BaseModel, Field

from src.api.dataset import DatasetAPI
from src.models.dataset import (DatasetCreate, DatasetListQuery,
                               DatasetTagBinding, DatasetTagCreate,
                               DatasetTagUpdate, DatasetUpdate)
from src.utils.exceptions import DifyMCPException
from src.utils.logger import get_logger


class CreateDatasetArgs(BaseModel):
    """创建知识库参数"""

    name: str = Field(description="知识库名称")
    description: Optional[str] = Field(default=None, description="知识库描述")
    indexing_technique: str = Field(default="high_quality", description="索引技术")
    permission: str = Field(default="only_me", description="权限设置")
    provider: str = Field(default="vendor", description="供应商")
    model: Optional[str] = Field(default=None, description="模型名称")
    external_knowledge_api_id: Optional[str] = Field(
        default=None, description="外部知识API ID"
    )
    external_knowledge_id: Optional[str] = Field(default=None, description="外部知识ID")


class UpdateDatasetArgs(BaseModel):
    """更新知识库参数"""

    dataset_id: str = Field(description="知识库ID")
    name: Optional[str] = Field(default=None, description="知识库名称")
    description: Optional[str] = Field(default=None, description="知识库描述")
    indexing_technique: Optional[str] = Field(default=None, description="索引技术")
    permission: Optional[str] = Field(default=None, description="权限设置")
    provider: Optional[str] = Field(default=None, description="供应商")
    model: Optional[str] = Field(default=None, description="模型名称")
    retrieval_model: Optional[Dict[str, Any]] = Field(
        default=None, description="检索模型配置"
    )


class ListDatasetsArgs(BaseModel):
    """获取知识库列表参数"""

    page: int = Field(default=1, description="页码")
    limit: int = Field(default=20, description="每页条数")
    keyword: Optional[str] = Field(default=None, description="搜索关键词")
    tag_ids: Optional[List[str]] = Field(default=None, description="标签ID列表")


class GetDatasetArgs(BaseModel):
    """获取知识库详情参数"""

    dataset_id: str = Field(description="知识库ID")


class DeleteDatasetArgs(BaseModel):
    """删除知识库参数"""

    dataset_id: str = Field(description="知识库ID")


class CreateDatasetTagArgs(BaseModel):
    """创建知识库标签参数"""

    name: str = Field(description="标签名称")
    color: Optional[str] = Field(default=None, description="标签颜色")


class UpdateDatasetTagArgs(BaseModel):
    """更新知识库标签参数"""

    tag_id: str = Field(description="标签ID")
    name: Optional[str] = Field(default=None, description="标签名称")
    color: Optional[str] = Field(default=None, description="标签颜色")


class DeleteDatasetTagArgs(BaseModel):
    """删除知识库标签参数"""

    tag_id: str = Field(description="标签ID")


class BindDatasetTagsArgs(BaseModel):
    """绑定知识库标签参数"""

    dataset_id: str = Field(description="知识库ID")
    tag_ids: List[str] = Field(description="标签ID列表")


class UnbindDatasetTagsArgs(BaseModel):
    """解绑知识库标签参数"""

    dataset_id: str = Field(description="知识库ID")
    tag_ids: List[str] = Field(description="标签ID列表")


class CopyDatasetArgs(BaseModel):
    """复制知识库参数"""

    dataset_id: str = Field(description="源知识库ID")
    name: str = Field(description="新知识库名称")


class DatasetTools:
    """知识库MCP工具类"""

    def __init__(self, dataset_api: DatasetAPI):
        """初始化知识库工具

        Args:
            dataset_api: 知识库API实例
        """
        self.dataset_api = dataset_api
        self.logger = get_logger(__name__)

    def register_tools(self, mcp: FastMCP):
        """注册知识库相关的MCP工具

        Args:
            mcp: FastMCP服务器实例
        """
        self.logger.info("Registering dataset tools...")

        # 使用装饰器模式注册工具
        @mcp.tool
        async def create_dataset(args: CreateDatasetArgs) -> dict:
            """创建知识库"""
            return await self.create_dataset(args)

        @mcp.tool
        async def update_dataset(args: UpdateDatasetArgs) -> dict:
            """更新知识库"""
            return await self.update_dataset(args)

        @mcp.tool
        async def list_datasets(args: ListDatasetsArgs) -> dict:
            """列出知识库"""
            return await self.list_datasets(args)

        @mcp.tool
        async def get_dataset(dataset_id: str) -> dict:
            """获取知识库详情"""
            return await self.get_dataset(dataset_id)

        @mcp.tool
        async def delete_dataset(dataset_id: str) -> dict:
            """删除知识库"""
            return await self.delete_dataset(dataset_id)

        self.logger.info("Dataset tools registered successfully")

    async def create_dataset(self, args: CreateDatasetArgs) -> Dict[str, Any]:
        """创建知识库"""
        try:
            dataset_data = DatasetCreate(
                name=args.name,
                description=args.description,
                indexing_technique=args.indexing_technique,
                permission=args.permission,
                provider=args.provider,
                model=args.model,
                external_knowledge_api_id=args.external_knowledge_api_id,
                external_knowledge_id=args.external_knowledge_id,
            )

            dataset = await self.dataset_api.create_dataset(dataset_data)
            return {
                "success": True,
                "data": dataset.model_dump(),
                "message": f"知识库 '{dataset.name}' 创建成功",
            }
        except Exception as e:
            self.logger.error(f"Failed to create dataset: {e}")
            raise DifyMCPException(f"创建知识库失败: {e}")

    async def update_dataset(self, args: UpdateDatasetArgs) -> Dict[str, Any]:
        """更新知识库"""
        try:
            dataset_data = DatasetUpdate(
                name=args.name,
                description=args.description,
                indexing_technique=args.indexing_technique,
                permission=args.permission,
                provider=args.provider,
                model=args.model,
                retrieval_model=args.retrieval_model,
            )

            dataset = await self.dataset_api.update_dataset(
                args.dataset_id, dataset_data
            )
            return {
                "success": True,
                "data": dataset.model_dump(),
                "message": f"知识库 '{dataset.name}' 更新成功",
            }
        except Exception as e:
            self.logger.error(f"Failed to update dataset: {e}")
            raise DifyMCPException(f"更新知识库失败: {e}")

    async def list_datasets(self, args: ListDatasetsArgs) -> Dict[str, Any]:
        """获取知识库列表"""
        try:
            query = DatasetListQuery(
                page=args.page,
                limit=args.limit,
                keyword=args.keyword,
                tag_ids=args.tag_ids,
            )

            dataset_list = await self.dataset_api.list_datasets(query)
            return {
                "success": True,
                "data": dataset_list.model_dump(),
                "message": f"获取到 {len(dataset_list.data)} 个知识库",
            }
        except Exception as e:
            self.logger.error(f"Failed to list datasets: {e}")
            raise DifyMCPException(f"获取知识库列表失败: {e}")

    async def get_dataset(self, args: GetDatasetArgs) -> Dict[str, Any]:
        """获取知识库详情"""
        try:
            dataset = await self.dataset_api.get_dataset(args.dataset_id)
            return {
                "success": True,
                "data": dataset.model_dump(),
                "message": f"获取知识库 '{dataset.name}' 详情成功",
            }
        except Exception as e:
            self.logger.error(f"Failed to get dataset: {e}")
            raise DifyMCPException(f"获取知识库详情失败: {e}")

    async def delete_dataset(self, args: DeleteDatasetArgs) -> Dict[str, Any]:
        """删除知识库"""
        try:
            success = await self.dataset_api.delete_dataset(args.dataset_id)
            return {
                "success": success,
                "message": "知识库删除成功" if success else "知识库删除失败",
            }
        except Exception as e:
            self.logger.error(f"Failed to delete dataset: {e}")
            raise DifyMCPException(f"删除知识库失败: {e}")

    async def copy_dataset(self, args: CopyDatasetArgs) -> Dict[str, Any]:
        """复制知识库"""
        try:
            dataset = await self.dataset_api.copy_dataset(args.dataset_id, args.name)
            return {
                "success": True,
                "data": dataset.model_dump(),
                "message": f"知识库复制成功，新知识库名称: '{dataset.name}'",
            }
        except Exception as e:
            self.logger.error(f"Failed to copy dataset: {e}")
            raise DifyMCPException(f"复制知识库失败: {e}")

    async def get_dataset_indexing_status(self, args: GetDatasetArgs) -> Dict[str, Any]:
        """获取知识库索引状态"""
        try:
            status = await self.dataset_api.get_dataset_indexing_status(args.dataset_id)
            return {
                "success": True,
                "data": status,
                "message": "获取知识库索引状态成功",
            }
        except Exception as e:
            self.logger.error(f"Failed to get dataset indexing status: {e}")
            raise DifyMCPException(f"获取知识库索引状态失败: {e}")

    async def get_dataset_queries(self, args: GetDatasetArgs) -> Dict[str, Any]:
        """获取知识库查询记录"""
        try:
            queries = await self.dataset_api.get_dataset_queries(args.dataset_id)
            return {
                "success": True,
                "data": queries,
                "message": f"获取到 {len(queries)} 条查询记录",
            }
        except Exception as e:
            self.logger.error(f"Failed to get dataset queries: {e}")
            raise DifyMCPException(f"获取知识库查询记录失败: {e}")

    async def get_dataset_error_docs(self, args: GetDatasetArgs) -> Dict[str, Any]:
        """获取知识库错误文档"""
        try:
            error_docs = await self.dataset_api.get_dataset_error_docs(args.dataset_id)
            return {
                "success": True,
                "data": error_docs,
                "message": f"获取到 {len(error_docs)} 个错误文档",
            }
        except Exception as e:
            self.logger.error(f"Failed to get dataset error docs: {e}")
            raise DifyMCPException(f"获取知识库错误文档失败: {e}")

    # 标签管理工具
    async def list_dataset_tags(self) -> Dict[str, Any]:
        """获取知识库标签列表"""
        try:
            tags = await self.dataset_api.list_dataset_tags()
            return {
                "success": True,
                "data": [tag.model_dump() for tag in tags],
                "message": f"获取到 {len(tags)} 个标签",
            }
        except Exception as e:
            self.logger.error(f"Failed to list dataset tags: {e}")
            raise DifyMCPException(f"获取知识库标签列表失败: {e}")

    async def create_dataset_tag(self, args: CreateDatasetTagArgs) -> Dict[str, Any]:
        """创建知识库标签"""
        try:
            tag_data = DatasetTagCreate(name=args.name, color=args.color)

            tag = await self.dataset_api.create_dataset_tag(tag_data)
            return {
                "success": True,
                "data": tag.model_dump(),
                "message": f"标签 '{tag.name}' 创建成功",
            }
        except Exception as e:
            self.logger.error(f"Failed to create dataset tag: {e}")
            raise DifyMCPException(f"创建知识库标签失败: {e}")

    async def update_dataset_tag(self, args: UpdateDatasetTagArgs) -> Dict[str, Any]:
        """更新知识库标签"""
        try:
            tag_data = DatasetTagUpdate(name=args.name, color=args.color)

            tag = await self.dataset_api.update_dataset_tag(args.tag_id, tag_data)
            return {
                "success": True,
                "data": tag.model_dump(),
                "message": f"标签 '{tag.name}' 更新成功",
            }
        except Exception as e:
            self.logger.error(f"Failed to update dataset tag: {e}")
            raise DifyMCPException(f"更新知识库标签失败: {e}")

    async def delete_dataset_tag(self, args: DeleteDatasetTagArgs) -> Dict[str, Any]:
        """删除知识库标签"""
        try:
            success = await self.dataset_api.delete_dataset_tag(args.tag_id)
            return {
                "success": success,
                "message": "标签删除成功" if success else "标签删除失败",
            }
        except Exception as e:
            self.logger.error(f"Failed to delete dataset tag: {e}")
            raise DifyMCPException(f"删除知识库标签失败: {e}")

    async def bind_dataset_tags(self, args: BindDatasetTagsArgs) -> Dict[str, Any]:
        """绑定知识库标签"""
        try:
            tag_binding = DatasetTagBinding(tag_ids=args.tag_ids)
            success = await self.dataset_api.bind_dataset_tags(
                args.dataset_id, tag_binding
            )
            return {
                "success": success,
                "message": (
                    f"成功绑定 {len(args.tag_ids)} 个标签"
                    if success
                    else "标签绑定失败"
                ),
            }
        except Exception as e:
            self.logger.error(f"Failed to bind dataset tags: {e}")
            raise DifyMCPException(f"绑定知识库标签失败: {e}")

    async def unbind_dataset_tags(self, args: UnbindDatasetTagsArgs) -> Dict[str, Any]:
        """解绑知识库标签"""
        try:
            tag_binding = DatasetTagBinding(tag_ids=args.tag_ids)
            success = await self.dataset_api.unbind_dataset_tags(
                args.dataset_id, tag_binding
            )
            return {
                "success": success,
                "message": (
                    f"成功解绑 {len(args.tag_ids)} 个标签"
                    if success
                    else "标签解绑失败"
                ),
            }
        except Exception as e:
            self.logger.error(f"Failed to unbind dataset tags: {e}")
            raise DifyMCPException(f"解绑知识库标签失败: {e}")

    # 嵌入模型工具
    async def list_embedding_models(self) -> Dict[str, Any]:
        """获取嵌入模型列表"""
        try:
            models = await self.dataset_api.list_embedding_models()
            return {
                "success": True,
                "data": models.model_dump(),
                "message": f"获取到 {len(models.data)} 个嵌入模型",
            }
        except Exception as e:
            self.logger.error(f"Failed to list embedding models: {e}")
            raise DifyMCPException(f"获取嵌入模型列表失败: {e}")

    # 检索设置工具
    async def get_dataset_retrieval_settings(
        self, args: GetDatasetArgs
    ) -> Dict[str, Any]:
        """获取知识库检索设置"""
        try:
            settings = await self.dataset_api.get_dataset_retrieval_settings(
                args.dataset_id
            )
            return {
                "success": True,
                "data": settings,
                "message": "获取知识库检索设置成功",
            }
        except Exception as e:
            self.logger.error(f"Failed to get dataset retrieval settings: {e}")
            raise DifyMCPException(f"获取知识库检索设置失败: {e}")

    async def update_dataset_retrieval_settings(
        self, args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """更新知识库检索设置"""
        try:
            dataset_id = args.get("dataset_id")
            if not dataset_id:
                raise ValueError("dataset_id is required")

            settings = {k: v for k, v in args.items() if k != "dataset_id"}
            updated_settings = await self.dataset_api.update_dataset_retrieval_settings(
                dataset_id, settings
            )
            return {
                "success": True,
                "data": updated_settings,
                "message": "知识库检索设置更新成功",
            }
        except Exception as e:
            self.logger.error(f"Failed to update dataset retrieval settings: {e}")
            raise DifyMCPException(f"更新知识库检索设置失败: {e}")
