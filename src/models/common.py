"""通用数据模型"""

from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class BaseResponse(BaseModel):
    """基础响应模型"""

    success: bool = Field(default=True, description="请求是否成功")
    message: Optional[str] = Field(default=None, description="响应消息")


class ErrorResponse(BaseResponse):
    """错误响应模型"""

    success: bool = Field(default=False, description="请求失败")
    error_code: Optional[str] = Field(default=None, description="错误代码")
    error_details: Optional[Dict[str, Any]] = Field(
        default=None, description="错误详情"
    )


class DataResponse(BaseResponse, Generic[T]):
    """数据响应模型"""

    data: T = Field(description="响应数据")


class PaginationInfo(BaseModel):
    """分页信息"""

    page: int = Field(description="当前页码")
    limit: int = Field(description="每页条数")
    total: int = Field(description="总条数")
    has_more: bool = Field(description="是否有更多数据")


class PaginationResponse(BaseResponse, Generic[T]):
    """分页响应模型"""

    data: List[T] = Field(description="数据列表")
    pagination: PaginationInfo = Field(description="分页信息")


class UploadFileInfo(BaseModel):
    """上传文件信息"""

    upload_file_id: str = Field(description="上传文件 ID")


class DataSourceInfo(BaseModel):
    """数据源信息"""

    upload_file_id: Optional[str] = Field(default=None, description="上传文件 ID")


class PreProcessingRule(BaseModel):
    """预处理规则"""

    id: str = Field(description="规则 ID")
    enabled: bool = Field(description="是否启用")


class SegmentationRule(BaseModel):
    """分段规则"""

    separator: str = Field(default="\n", description="分段标识符")
    max_tokens: int = Field(default=1000, description="最大长度（token）")
    chunk_overlap: Optional[int] = Field(default=None, description="分段重叠")


class ProcessingRules(BaseModel):
    """处理规则"""

    pre_processing_rules: List[PreProcessingRule] = Field(
        default_factory=list, description="预处理规则"
    )
    segmentation: SegmentationRule = Field(description="分段规则")
    parent_mode: Optional[str] = Field(default=None, description="父分段召回模式")
    subchunk_segmentation: Optional[SegmentationRule] = Field(
        default=None, description="子分段规则"
    )


class ProcessRule(BaseModel):
    """处理规则配置"""

    mode: str = Field(description="处理模式")
    rules: Optional[ProcessingRules] = Field(default=None, description="自定义规则")


class RerankingModel(BaseModel):
    """重排序模型"""

    reranking_provider_name: str = Field(description="重排序模型提供商")
    reranking_model_name: str = Field(description="重排序模型名称")


class RetrievalModel(BaseModel):
    """检索模型"""

    search_method: Optional[str] = Field(default=None, description="搜索方法")
    reranking_enable: bool = Field(default=False, description="是否启用重排序")
    reranking_mode: Optional[str] = Field(default=None, description="重排序模式")
    reranking_model: Optional[RerankingModel] = Field(
        default=None, description="重排序模型"
    )
    weights: Optional[Any] = Field(default=None, description="权重（可能是数字或字典）")
    top_k: int = Field(default=2, description="召回条数")
    score_threshold_enabled: Optional[bool] = Field(
        default=False, description="是否启用分数阈值"
    )
    score_threshold: Optional[float] = Field(default=None, description="分数阈值")


class ExternalKnowledgeInfo(BaseModel):
    """外部知识库信息"""

    external_knowledge_id: Optional[str] = Field(
        default=None, description="外部知识库 ID"
    )
    external_knowledge_api_id: Optional[str] = Field(
        default=None, description="外部知识库 API ID"
    )
    external_knowledge_api_name: Optional[str] = Field(
        default=None, description="外部知识库 API 名称"
    )
    external_knowledge_api_endpoint: Optional[str] = Field(
        default=None, description="外部知识库 API 端点"
    )


class Tag(BaseModel):
    """标签"""

    id: str = Field(description="标签 ID")
    name: str = Field(description="标签名称")
    color: Optional[str] = Field(default=None, description="标签颜色")


class EmbeddingModel(BaseModel):
    """嵌入模型"""

    provider: str = Field(description="模型提供商")
    model: str = Field(description="模型名称")
    max_tokens: Optional[int] = Field(default=None, description="最大 token 数")
    dimensions: Optional[int] = Field(default=None, description="向量维度")


class SearchResult(BaseModel):
    """搜索结果"""

    id: str = Field(description="结果 ID")
    content: str = Field(description="内容")
    score: float = Field(description="相关性分数")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    document_id: str = Field(description="文档 ID")
    document_name: str = Field(description="文档名称")
    segment_id: Optional[str] = Field(default=None, description="分段 ID")


class SearchRequest(BaseModel):
    """搜索请求"""

    query: str = Field(description="搜索查询")
    top_k: Optional[int] = Field(default=None, description="返回结果数量")
    score_threshold: Optional[float] = Field(default=None, description="分数阈值")
    search_method: Optional[str] = Field(default=None, description="搜索方法")
    reranking_enable: Optional[bool] = Field(default=None, description="是否启用重排序")


class SearchResponse(BaseModel):
    """搜索响应"""

    data: List[SearchResult] = Field(description="搜索结果")
    total: int = Field(description="总结果数")
    query: str = Field(description="搜索查询")
    search_method: str = Field(description="使用的搜索方法")


class SemanticSearchRequest(BaseModel):
    """语义搜索请求"""

    query: str = Field(description="搜索查询")
    top_k: int = Field(default=10, description="返回结果数量")
    score_threshold: Optional[float] = Field(default=None, description="相似度阈值")
    retrieval_model: Optional[Dict[str, Any]] = Field(
        default=None, description="检索模型配置"
    )


class KeywordSearchRequest(BaseModel):
    """关键词搜索请求"""

    query: str = Field(description="搜索查询")
    top_k: int = Field(default=10, description="返回结果数量")
    optional_words: Optional[List[str]] = Field(default=None, description="可选关键词")


class HybridSearchRequest(BaseModel):
    """混合搜索请求"""

    query: str = Field(description="搜索查询")
    top_k: int = Field(default=10, description="返回结果数量")
    score_threshold: Optional[float] = Field(default=None, description="相似度阈值")
    rerank_model: Optional[Dict[str, Any]] = Field(
        default=None, description="重排序模型配置"
    )
    weights: Optional[Dict[str, float]] = Field(default=None, description="权重配置")


class FulltextSearchRequest(BaseModel):
    """全文搜索请求"""

    query: str = Field(description="搜索查询")
    top_k: int = Field(default=10, description="返回结果数量")
    search_method: str = Field(default="semantic_search", description="搜索方法")


class MultiDatasetSearchRequest(BaseModel):
    """多知识库搜索请求"""

    dataset_ids: List[str] = Field(description="知识库ID列表")
    query: str = Field(description="搜索查询")
    top_k: int = Field(default=10, description="返回结果数量")
    score_threshold: Optional[float] = Field(default=None, description="相似度阈值")
    rerank_model: Optional[Dict[str, Any]] = Field(
        default=None, description="重排序模型配置"
    )
