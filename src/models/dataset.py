"""知识库数据模型"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .common import ExternalKnowledgeInfo, RetrievalModel, Tag


class Dataset(BaseModel):
    """知识库模型"""

    id: str = Field(description="知识库 ID")
    name: str = Field(description="知识库名称")
    description: Optional[str] = Field(default=None, description="知识库描述")
    provider: str = Field(description="提供商")
    permission: str = Field(description="权限")
    data_source_type: Optional[str] = Field(default=None, description="数据源类型")
    indexing_technique: Optional[str] = Field(default=None, description="索引技术")
    app_count: int = Field(default=0, description="应用数量")
    document_count: int = Field(default=0, description="文档数量")
    word_count: int = Field(default=0, description="词汇数量")
    created_by: str = Field(description="创建者")
    created_at: int = Field(description="创建时间戳")
    updated_by: Optional[str] = Field(default=None, description="更新者")
    updated_at: int = Field(description="更新时间戳")
    embedding_model: Optional[str] = Field(default=None, description="嵌入模型")
    embedding_model_provider: Optional[str] = Field(
        default=None, description="嵌入模型提供商"
    )
    embedding_available: Optional[bool] = Field(
        default=None, description="嵌入是否可用"
    )
    retrieval_model_dict: Optional[RetrievalModel] = Field(
        default=None, description="检索模型配置"
    )
    tags: List[Tag] = Field(default_factory=list, description="标签列表")
    doc_form: Optional[str] = Field(default=None, description="文档形式")
    external_knowledge_info: Optional[ExternalKnowledgeInfo] = Field(
        default=None, description="外部知识库信息"
    )
    external_retrieval_model: Optional[RetrievalModel] = Field(
        default=None, description="外部检索模型"
    )
    partial_member_list: List[str] = Field(
        default_factory=list, description="部分成员列表"
    )

    @property
    def created_datetime(self) -> datetime:
        """创建时间"""
        return datetime.fromtimestamp(self.created_at)

    @property
    def updated_datetime(self) -> datetime:
        """更新时间"""
        return datetime.fromtimestamp(self.updated_at)


class DatasetCreate(BaseModel):
    """创建知识库请求模型"""

    name: str = Field(description="知识库名称")
    description: Optional[str] = Field(default=None, description="知识库描述")
    indexing_technique: Optional[str] = Field(
        default="high_quality", description="索引技术"
    )
    permission: Optional[str] = Field(default="only_me", description="权限")
    provider: Optional[str] = Field(default="vendor", description="提供商")
    external_knowledge_api_id: Optional[str] = Field(
        default=None, description="外部知识库 API ID"
    )
    external_knowledge_id: Optional[str] = Field(
        default=None, description="外部知识库 ID"
    )
    embedding_model: Optional[str] = Field(default=None, description="嵌入模型")
    embedding_model_provider: Optional[str] = Field(
        default=None, description="嵌入模型提供商"
    )
    retrieval_model: Optional[RetrievalModel] = Field(
        default=None, description="检索模型"
    )


class DatasetUpdate(BaseModel):
    """更新知识库请求模型"""

    name: Optional[str] = Field(default=None, description="知识库名称")
    description: Optional[str] = Field(default=None, description="知识库描述")
    indexing_technique: Optional[str] = Field(default=None, description="索引技术")
    permission: Optional[str] = Field(default=None, description="权限")
    embedding_model_provider: Optional[str] = Field(
        default=None, description="嵌入模型提供商"
    )
    embedding_model: Optional[str] = Field(default=None, description="嵌入模型")
    retrieval_model: Optional[RetrievalModel] = Field(
        default=None, description="检索模型"
    )
    partial_member_list: Optional[List[str]] = Field(
        default=None, description="部分成员列表"
    )


class DatasetListQuery(BaseModel):
    """知识库列表查询参数"""

    keyword: Optional[str] = Field(default=None, description="搜索关键词")
    tag_ids: Optional[List[str]] = Field(default=None, description="标签 ID 列表")
    page: int = Field(default=1, description="页码")
    limit: int = Field(default=20, description="每页条数")
    include_all: bool = Field(default=False, description="是否包含所有数据集")


class DatasetList(BaseModel):
    """知识库列表响应模型"""

    data: List[Dataset] = Field(description="知识库列表")
    has_more: bool = Field(description="是否有更多数据")
    limit: int = Field(description="每页条数")
    total: int = Field(description="总条数")
    page: int = Field(description="当前页码")


class DatasetTag(BaseModel):
    """知识库标签模型"""

    id: str = Field(description="标签 ID")
    name: str = Field(description="标签名称")
    color: Optional[str] = Field(default=None, description="标签颜色")
    description: Optional[str] = Field(default=None, description="标签描述")
    created_by: str = Field(description="创建者")
    created_at: int = Field(description="创建时间戳")
    updated_at: int = Field(description="更新时间戳")
    dataset_count: int = Field(default=0, description="关联的知识库数量")


class DatasetTagCreate(BaseModel):
    """创建知识库标签请求模型"""

    name: str = Field(description="标签名称")
    color: Optional[str] = Field(default=None, description="标签颜色")
    description: Optional[str] = Field(default=None, description="标签描述")


class DatasetTagUpdate(BaseModel):
    """更新知识库标签请求模型"""

    name: Optional[str] = Field(default=None, description="标签名称")
    color: Optional[str] = Field(default=None, description="标签颜色")
    description: Optional[str] = Field(default=None, description="标签描述")


class DatasetTagBinding(BaseModel):
    """知识库标签绑定模型"""

    dataset_id: str = Field(description="知识库 ID")
    tag_ids: List[str] = Field(description="标签 ID 列表")


class EmbeddingModelInfo(BaseModel):
    """嵌入模型信息"""

    provider: str = Field(description="模型提供商")
    model: str = Field(description="模型名称")
    model_type: str = Field(description="模型类型")
    max_tokens: Optional[int] = Field(default=None, description="最大 token 数")
    dimensions: Optional[int] = Field(default=None, description="向量维度")
    price: Optional[Dict[str, Any]] = Field(default=None, description="价格信息")
    available: bool = Field(default=True, description="是否可用")


class EmbeddingModelList(BaseModel):
    """嵌入模型列表响应"""

    data: List[EmbeddingModelInfo] = Field(description="嵌入模型列表")
    total: int = Field(description="总数量")
