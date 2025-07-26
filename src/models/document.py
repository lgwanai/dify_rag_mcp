"""文档数据模型"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .common import DataSourceInfo, ProcessRule, RetrievalModel


class Document(BaseModel):
    """文档模型"""

    id: str = Field(description="文档 ID")
    position: int = Field(description="位置")
    data_source_type: str = Field(description="数据源类型")
    data_source_info: DataSourceInfo = Field(description="数据源信息")
    dataset_process_rule_id: Optional[str] = Field(
        default=None, description="数据集处理规则 ID"
    )
    name: str = Field(description="文档名称")
    created_from: str = Field(description="创建来源")
    created_by: str = Field(description="创建者")
    created_at: int = Field(description="创建时间戳")
    tokens: int = Field(default=0, description="token 数量")
    indexing_status: str = Field(description="索引状态")
    error: Optional[str] = Field(default=None, description="错误信息")
    enabled: bool = Field(default=True, description="是否启用")
    disabled_at: Optional[int] = Field(default=None, description="禁用时间戳")
    disabled_by: Optional[str] = Field(default=None, description="禁用者")
    archived: bool = Field(default=False, description="是否归档")
    display_status: str = Field(description="显示状态")
    word_count: int = Field(default=0, description="词汇数量")
    hit_count: int = Field(default=0, description="命中次数")
    doc_form: str = Field(description="文档形式")

    @property
    def created_datetime(self) -> datetime:
        """创建时间"""
        return datetime.fromtimestamp(self.created_at)

    @property
    def disabled_datetime(self) -> Optional[datetime]:
        """禁用时间"""
        return datetime.fromtimestamp(self.disabled_at) if self.disabled_at else None


class DocumentCreate(BaseModel):
    """创建文档请求模型"""

    name: str = Field(description="文档名称")
    text: Optional[str] = Field(default=None, description="文档内容")
    indexing_technique: str = Field(default="high_quality", description="索引技术")
    process_rule: Optional[Dict[str, Any]] = Field(default=None, description="处理规则")


class DocumentUpdate(BaseModel):
    """更新文档请求模型"""

    name: Optional[str] = Field(default=None, description="文档名称")
    text: Optional[str] = Field(default=None, description="文档内容")
    process_rule: Optional[Dict[str, Any]] = Field(default=None, description="处理规则")


class DocumentCreateByText(BaseModel):
    """通过文本创建文档请求模型"""

    name: str = Field(description="文档名称")
    text: str = Field(description="文档内容")
    indexing_technique: str = Field(description="索引技术")
    doc_form: Optional[str] = Field(default="text_model", description="文档形式")
    doc_language: Optional[str] = Field(default=None, description="文档语言")
    process_rule: ProcessRule = Field(description="处理规则")
    retrieval_model: Optional[RetrievalModel] = Field(
        default=None, description="检索模型"
    )
    embedding_model: Optional[str] = Field(default=None, description="嵌入模型")
    embedding_model_provider: Optional[str] = Field(
        default=None, description="嵌入模型提供商"
    )


class DocumentCreateByFile(BaseModel):
    """通过文件创建文档请求模型"""

    original_document_id: Optional[str] = Field(default=None, description="源文档 ID")
    indexing_technique: str = Field(description="索引技术")
    doc_form: Optional[str] = Field(default="text_model", description="文档形式")
    doc_language: Optional[str] = Field(default=None, description="文档语言")
    process_rule: ProcessRule = Field(description="处理规则")
    retrieval_model: Optional[RetrievalModel] = Field(
        default=None, description="检索模型"
    )
    embedding_model: Optional[str] = Field(default=None, description="嵌入模型")
    embedding_model_provider: Optional[str] = Field(
        default=None, description="嵌入模型提供商"
    )


class DocumentUpdateByText(BaseModel):
    """通过文本更新文档请求模型"""

    name: Optional[str] = Field(default=None, description="文档名称")
    text: Optional[str] = Field(default=None, description="文档内容")
    process_rule: Optional[ProcessRule] = Field(default=None, description="处理规则")


class DocumentUpdateByFile(BaseModel):
    """通过文件更新文档请求模型"""

    process_rule: Optional[ProcessRule] = Field(default=None, description="处理规则")


class DocumentListQuery(BaseModel):
    """文档列表查询参数"""

    keyword: Optional[str] = Field(default=None, description="搜索关键词")
    status: Optional[str] = Field(default=None, description="状态筛选")
    page: int = Field(default=1, description="页码")
    limit: int = Field(default=20, description="每页条数")


class DocumentList(BaseModel):
    """文档列表响应模型"""

    data: List[Document] = Field(description="文档列表")
    has_more: bool = Field(description="是否有更多数据")
    limit: int = Field(description="每页条数")
    total: int = Field(description="总条数")
    page: int = Field(description="当前页码")


class DocumentStatus(BaseModel):
    """文档状态模型"""

    id: str = Field(description="文档 ID")
    indexing_status: str = Field(description="索引状态")
    processing_started_at: Optional[int] = Field(
        default=None, description="处理开始时间戳"
    )
    parsing_completed_at: Optional[int] = Field(
        default=None, description="解析完成时间戳"
    )
    cleaning_completed_at: Optional[int] = Field(
        default=None, description="清洗完成时间戳"
    )
    splitting_completed_at: Optional[int] = Field(
        default=None, description="分割完成时间戳"
    )
    completed_at: Optional[int] = Field(default=None, description="完成时间戳")
    paused_at: Optional[int] = Field(default=None, description="暂停时间戳")
    error: Optional[str] = Field(default=None, description="错误信息")
    stopped_at: Optional[int] = Field(default=None, description="停止时间戳")
    completed_segments: int = Field(default=0, description="已完成分段数")
    total_segments: int = Field(default=0, description="总分段数")

    @property
    def progress_percentage(self) -> float:
        """进度百分比"""
        if self.total_segments == 0:
            return 0.0
        return (self.completed_segments / self.total_segments) * 100


class DocumentUpdateStatus(BaseModel):
    """更新文档状态请求模型"""

    enabled: bool = Field(description="是否启用")


class DocumentCreateResponse(BaseModel):
    """创建文档响应模型"""

    document: Document = Field(description="文档信息")
    batch: str = Field(description="批次 ID")


class DocumentMetadata(BaseModel):
    """文档元数据模型"""

    id: str = Field(description="元数据 ID")
    key: str = Field(description="元数据键")
    value: str = Field(description="元数据值")
    type: str = Field(description="元数据类型")
    description: Optional[str] = Field(default=None, description="元数据描述")


class DocumentMetadataCreate(BaseModel):
    """创建文档元数据请求模型"""

    key: str = Field(description="元数据键")
    value: str = Field(description="元数据值")
    type: str = Field(description="元数据类型")
    description: Optional[str] = Field(default=None, description="元数据描述")


class DocumentMetadataUpdate(BaseModel):
    """更新文档元数据请求模型"""

    value: Optional[str] = Field(default=None, description="元数据值")
    description: Optional[str] = Field(default=None, description="元数据描述")


class DocumentMetadataList(BaseModel):
    """文档元数据列表响应模型"""

    data: List[DocumentMetadata] = Field(description="元数据列表")
    total: int = Field(description="总数量")


class UploadFile(BaseModel):
    """上传文件模型"""

    id: str = Field(description="文件 ID")
    name: str = Field(description="文件名")
    size: int = Field(description="文件大小")
    extension: str = Field(description="文件扩展名")
    mime_type: str = Field(description="MIME 类型")
    created_by: str = Field(description="上传者")
    created_at: int = Field(description="上传时间戳")

    @property
    def created_datetime(self) -> datetime:
        """上传时间"""
        return datetime.fromtimestamp(self.created_at)

    @property
    def size_mb(self) -> float:
        """文件大小（MB）"""
        return self.size / (1024 * 1024)
