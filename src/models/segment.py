"""分段数据模型"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Segment(BaseModel):
    """分段模型"""

    id: str = Field(description="分段 ID")
    position: int = Field(description="位置")
    document_id: str = Field(description="文档 ID")
    content: str = Field(description="分段内容")
    word_count: int = Field(description="词汇数量")
    tokens: int = Field(description="token 数量")
    keywords: List[str] = Field(default_factory=list, description="关键词")
    index_node_id: Optional[str] = Field(default=None, description="索引节点 ID")
    index_node_hash: Optional[str] = Field(default=None, description="索引节点哈希")
    hit_count: int = Field(default=0, description="命中次数")
    enabled: bool = Field(default=True, description="是否启用")
    disabled_at: Optional[int] = Field(default=None, description="禁用时间戳")
    disabled_by: Optional[str] = Field(default=None, description="禁用者")
    status: str = Field(description="状态")
    created_by: str = Field(description="创建者")
    created_at: int = Field(description="创建时间戳")
    indexing_at: Optional[int] = Field(default=None, description="索引时间戳")
    completed_at: Optional[int] = Field(default=None, description="完成时间戳")
    error: Optional[str] = Field(default=None, description="错误信息")
    stopped_at: Optional[int] = Field(default=None, description="停止时间戳")

    @property
    def created_datetime(self) -> datetime:
        """创建时间"""
        return datetime.fromtimestamp(self.created_at)

    @property
    def disabled_datetime(self) -> Optional[datetime]:
        """禁用时间"""
        return datetime.fromtimestamp(self.disabled_at) if self.disabled_at else None

    @property
    def indexing_datetime(self) -> Optional[datetime]:
        """索引时间"""
        return datetime.fromtimestamp(self.indexing_at) if self.indexing_at else None

    @property
    def completed_datetime(self) -> Optional[datetime]:
        """完成时间"""
        return datetime.fromtimestamp(self.completed_at) if self.completed_at else None


class SegmentCreate(BaseModel):
    """创建分段请求模型"""

    content: str = Field(description="分段内容")
    answer: Optional[str] = Field(default=None, description="答案（Q&A 模式）")
    keywords: Optional[List[str]] = Field(default=None, description="关键词")


class SegmentUpdate(BaseModel):
    """更新分段请求模型"""

    content: Optional[str] = Field(default=None, description="分段内容")
    answer: Optional[str] = Field(default=None, description="答案（Q&A 模式）")
    keywords: Optional[List[str]] = Field(default=None, description="关键词")
    enabled: Optional[bool] = Field(default=None, description="是否启用")


class SegmentListQuery(BaseModel):
    """分段列表查询参数"""

    keyword: Optional[str] = Field(default=None, description="搜索关键词")
    status: Optional[str] = Field(default=None, description="状态筛选")
    hit_count_gte: Optional[int] = Field(default=None, description="命中次数大于等于")
    hit_count_lte: Optional[int] = Field(default=None, description="命中次数小于等于")
    word_count_gte: Optional[int] = Field(default=None, description="词汇数量大于等于")
    word_count_lte: Optional[int] = Field(default=None, description="词汇数量小于等于")
    enabled: Optional[bool] = Field(default=None, description="是否启用")
    page: int = Field(default=1, description="页码")
    limit: int = Field(default=20, description="每页条数")


class SegmentList(BaseModel):
    """分段列表响应模型"""

    data: List[Segment] = Field(description="分段列表")
    has_more: bool = Field(description="是否有更多数据")
    limit: int = Field(description="每页条数")
    total: int = Field(description="总条数")
    page: int = Field(description="当前页码")


class SubSegment(BaseModel):
    """子分段模型"""

    id: str = Field(description="子分段 ID")
    parent_segment_id: str = Field(description="父分段 ID")
    position: int = Field(description="位置")
    content: str = Field(description="子分段内容")
    word_count: int = Field(description="词汇数量")
    tokens: int = Field(description="token 数量")
    keywords: List[str] = Field(default_factory=list, description="关键词")
    index_node_id: Optional[str] = Field(default=None, description="索引节点 ID")
    index_node_hash: Optional[str] = Field(default=None, description="索引节点哈希")
    hit_count: int = Field(default=0, description="命中次数")
    enabled: bool = Field(default=True, description="是否启用")
    disabled_at: Optional[int] = Field(default=None, description="禁用时间戳")
    disabled_by: Optional[str] = Field(default=None, description="禁用者")
    status: str = Field(description="状态")
    created_by: str = Field(description="创建者")
    created_at: int = Field(description="创建时间戳")
    indexing_at: Optional[int] = Field(default=None, description="索引时间戳")
    completed_at: Optional[int] = Field(default=None, description="完成时间戳")
    error: Optional[str] = Field(default=None, description="错误信息")
    stopped_at: Optional[int] = Field(default=None, description="停止时间戳")

    @property
    def created_datetime(self) -> datetime:
        """创建时间"""
        return datetime.fromtimestamp(self.created_at)

    @property
    def disabled_datetime(self) -> Optional[datetime]:
        """禁用时间"""
        return datetime.fromtimestamp(self.disabled_at) if self.disabled_at else None


class SubSegmentCreate(BaseModel):
    """创建子分段请求模型"""

    content: str = Field(description="子分段内容")
    keywords: Optional[List[str]] = Field(default=None, description="关键词")


class SubSegmentUpdate(BaseModel):
    """更新子分段请求模型"""

    content: Optional[str] = Field(default=None, description="子分段内容")
    keywords: Optional[List[str]] = Field(default=None, description="关键词")
    enabled: Optional[bool] = Field(default=None, description="是否启用")


class SubSegmentListQuery(BaseModel):
    """子分段列表查询参数"""

    keyword: Optional[str] = Field(default=None, description="搜索关键词")
    status: Optional[str] = Field(default=None, description="状态筛选")
    enabled: Optional[bool] = Field(default=None, description="是否启用")
    page: int = Field(default=1, description="页码")
    limit: int = Field(default=20, description="每页条数")


class SubSegmentList(BaseModel):
    """子分段列表响应模型"""

    data: List[SubSegment] = Field(description="子分段列表")
    has_more: bool = Field(description="是否有更多数据")
    limit: int = Field(description="每页条数")
    total: int = Field(description="总条数")
    page: int = Field(description="当前页码")


class SegmentStatistics(BaseModel):
    """分段统计信息"""

    total_segments: int = Field(description="总分段数")
    enabled_segments: int = Field(description="启用的分段数")
    disabled_segments: int = Field(description="禁用的分段数")
    total_word_count: int = Field(description="总词汇数")
    total_tokens: int = Field(description="总 token 数")
    average_word_count: float = Field(description="平均词汇数")
    average_tokens: float = Field(description="平均 token 数")
    total_hit_count: int = Field(description="总命中次数")


class SegmentBatchOperation(BaseModel):
    """分段批量操作请求模型"""

    segment_ids: List[str] = Field(description="分段 ID 列表")
    operation: str = Field(description="操作类型")


class SegmentBatchOperationResponse(BaseModel):
    """分段批量操作响应模型"""

    success_count: int = Field(description="成功数量")
    failed_count: int = Field(description="失败数量")
    failed_segments: List[Dict[str, Any]] = Field(
        default_factory=list, description="失败的分段信息"
    )
