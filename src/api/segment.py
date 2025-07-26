"""分段API模块"""

from typing import List, Optional, Dict, Any

from ..models.segment import (
    Segment,
    SegmentCreate,
    SegmentUpdate,
    SegmentList,
    SegmentListQuery,
    SubSegment,
    SubSegmentCreate,
    SubSegmentUpdate,
    SubSegmentList,
    SubSegmentListQuery,
    SegmentStatistics,
    SegmentBatchOperation,
    SegmentBatchOperationResponse,
)
from ..utils.logger import get_logger
from ..utils.validators import validate_dataset_id, validate_document_id, validate_segment_id
from .client import DifyAPIClient


class SegmentAPI:
    """分段API类"""
    
    def __init__(self, client: DifyAPIClient):
        """初始化分段API
        
        Args:
            client: Dify API客户端
        """
        self.client = client
        self.logger = get_logger(__name__)
    
    async def list_segments(
        self,
        dataset_id: str,
        document_id: str,
        query: Optional[SegmentListQuery] = None
    ) -> SegmentList:
        """获取分段列表
        
        Args:
            dataset_id: 知识库ID
            document_id: 文档ID
            query: 查询参数
            
        Returns:
            分段列表
        """
        validate_dataset_id(dataset_id)
        validate_document_id(document_id)
        
        params = {}
        if query:
            if query.keyword:
                params["keyword"] = query.keyword
            if query.status:
                params["status"] = query.status
            if query.hit_count_gte is not None:
                params["hit_count_gte"] = query.hit_count_gte
            if query.hit_count_lte is not None:
                params["hit_count_lte"] = query.hit_count_lte
            if query.word_count_gte is not None:
                params["word_count_gte"] = query.word_count_gte
            if query.word_count_lte is not None:
                params["word_count_lte"] = query.word_count_lte
            if query.enabled is not None:
                params["enabled"] = query.enabled
            if query.page:
                params["page"] = query.page
            if query.limit:
                params["limit"] = query.limit
        
        response = await self.client.get(
            f"datasets/{dataset_id}/documents/{document_id}/segments",
            params=params
        )
        return SegmentList(**response)
    
    async def create_segment(
        self,
        dataset_id: str,
        document_id: str,
        segment_data: SegmentCreate
    ) -> Segment:
        """创建分段
        
        Args:
            dataset_id: 知识库ID
            document_id: 文档ID
            segment_data: 分段创建数据
            
        Returns:
            创建的分段
        """
        validate_dataset_id(dataset_id)
        validate_document_id(document_id)
        
        data = segment_data.model_dump(exclude_none=True)
        response = await self.client.post(
            f"datasets/{dataset_id}/documents/{document_id}/segments",
            json_data=data
        )
        return Segment(**response)
    
    async def get_segment(
        self,
        dataset_id: str,
        document_id: str,
        segment_id: str
    ) -> Segment:
        """获取分段详情
        
        Args:
            dataset_id: 知识库ID
            document_id: 文档ID
            segment_id: 分段ID
            
        Returns:
            分段详情
        """
        validate_dataset_id(dataset_id)
        validate_document_id(document_id)
        validate_segment_id(segment_id)
        
        response = await self.client.get(
            f"datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}"
        )
        return Segment(**response)
    
    async def update_segment(
        self,
        dataset_id: str,
        document_id: str,
        segment_id: str,
        segment_data: SegmentUpdate
    ) -> Segment:
        """更新分段
        
        Args:
            dataset_id: 知识库ID
            document_id: 文档ID
            segment_id: 分段ID
            segment_data: 更新数据
            
        Returns:
            更新后的分段
        """
        validate_dataset_id(dataset_id)
        validate_document_id(document_id)
        validate_segment_id(segment_id)
        
        data = segment_data.model_dump(exclude_none=True)
        response = await self.client.patch(
            f"datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}",
            json_data=data
        )
        return Segment(**response)
    
    async def delete_segment(
        self,
        dataset_id: str,
        document_id: str,
        segment_id: str
    ) -> bool:
        """删除分段
        
        Args:
            dataset_id: 知识库ID
            document_id: 文档ID
            segment_id: 分段ID
            
        Returns:
            是否删除成功
        """
        validate_dataset_id(dataset_id)
        validate_document_id(document_id)
        validate_segment_id(segment_id)
        
        await self.client.delete(
            f"datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}"
        )
        return True
    
    async def enable_segment(
        self,
        dataset_id: str,
        document_id: str,
        segment_id: str
    ) -> bool:
        """启用分段
        
        Args:
            dataset_id: 知识库ID
            document_id: 文档ID
            segment_id: 分段ID
            
        Returns:
            是否启用成功
        """
        validate_dataset_id(dataset_id)
        validate_document_id(document_id)
        validate_segment_id(segment_id)
        
        await self.client.patch(
            f"datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}/enable"
        )
        return True
    
    async def disable_segment(
        self,
        dataset_id: str,
        document_id: str,
        segment_id: str
    ) -> bool:
        """禁用分段
        
        Args:
            dataset_id: 知识库ID
            document_id: 文档ID
            segment_id: 分段ID
            
        Returns:
            是否禁用成功
        """
        validate_dataset_id(dataset_id)
        validate_document_id(document_id)
        validate_segment_id(segment_id)
        
        await self.client.patch(
            f"datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}/disable"
        )
        return True
    
    # 子分段管理
    async def list_sub_segments(
        self,
        dataset_id: str,
        document_id: str,
        segment_id: str,
        query: Optional[SubSegmentListQuery] = None
    ) -> SubSegmentList:
        """获取子分段列表
        
        Args:
            dataset_id: 知识库ID
            document_id: 文档ID
            segment_id: 分段ID
            query: 查询参数
            
        Returns:
            子分段列表
        """
        validate_dataset_id(dataset_id)
        validate_document_id(document_id)
        validate_segment_id(segment_id)
        
        params = {}
        if query:
            if query.keyword:
                params["keyword"] = query.keyword
            if query.status:
                params["status"] = query.status
            if query.enabled is not None:
                params["enabled"] = query.enabled
            if query.page:
                params["page"] = query.page
            if query.limit:
                params["limit"] = query.limit
        
        response = await self.client.get(
            f"datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}/sub-segments",
            params=params
        )
        return SubSegmentList(**response)
    
    async def create_sub_segment(
        self,
        dataset_id: str,
        document_id: str,
        segment_id: str,
        sub_segment_data: SubSegmentCreate
    ) -> SubSegment:
        """创建子分段
        
        Args:
            dataset_id: 知识库ID
            document_id: 文档ID
            segment_id: 分段ID
            sub_segment_data: 子分段创建数据
            
        Returns:
            创建的子分段
        """
        validate_dataset_id(dataset_id)
        validate_document_id(document_id)
        validate_segment_id(segment_id)
        
        data = sub_segment_data.model_dump(exclude_none=True)
        response = await self.client.post(
            f"datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}/sub-segments",
            json_data=data
        )
        return SubSegment(**response)
    
    async def get_sub_segment(
        self,
        dataset_id: str,
        document_id: str,
        segment_id: str,
        sub_segment_id: str
    ) -> SubSegment:
        """获取子分段详情
        
        Args:
            dataset_id: 知识库ID
            document_id: 文档ID
            segment_id: 分段ID
            sub_segment_id: 子分段ID
            
        Returns:
            子分段详情
        """
        validate_dataset_id(dataset_id)
        validate_document_id(document_id)
        validate_segment_id(segment_id)
        validate_segment_id(sub_segment_id)  # 子分段ID格式与分段ID相同
        
        response = await self.client.get(
            f"datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}/sub-segments/{sub_segment_id}"
        )
        return SubSegment(**response)
    
    async def update_sub_segment(
        self,
        dataset_id: str,
        document_id: str,
        segment_id: str,
        sub_segment_id: str,
        sub_segment_data: SubSegmentUpdate
    ) -> SubSegment:
        """更新子分段
        
        Args:
            dataset_id: 知识库ID
            document_id: 文档ID
            segment_id: 分段ID
            sub_segment_id: 子分段ID
            sub_segment_data: 更新数据
            
        Returns:
            更新后的子分段
        """
        validate_dataset_id(dataset_id)
        validate_document_id(document_id)
        validate_segment_id(segment_id)
        validate_segment_id(sub_segment_id)
        
        data = sub_segment_data.model_dump(exclude_none=True)
        response = await self.client.patch(
            f"datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}/sub-segments/{sub_segment_id}",
            json_data=data
        )
        return SubSegment(**response)
    
    async def delete_sub_segment(
        self,
        dataset_id: str,
        document_id: str,
        segment_id: str,
        sub_segment_id: str
    ) -> bool:
        """删除子分段
        
        Args:
            dataset_id: 知识库ID
            document_id: 文档ID
            segment_id: 分段ID
            sub_segment_id: 子分段ID
            
        Returns:
            是否删除成功
        """
        validate_dataset_id(dataset_id)
        validate_document_id(document_id)
        validate_segment_id(segment_id)
        validate_segment_id(sub_segment_id)
        
        await self.client.delete(
            f"datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}/sub-segments/{sub_segment_id}"
        )
        return True
    
    # 分段统计和批量操作
    async def get_segment_statistics(
        self,
        dataset_id: str,
        document_id: str
    ) -> SegmentStatistics:
        """获取分段统计信息
        
        Args:
            dataset_id: 知识库ID
            document_id: 文档ID
            
        Returns:
            分段统计信息
        """
        validate_dataset_id(dataset_id)
        validate_document_id(document_id)
        
        response = await self.client.get(
            f"datasets/{dataset_id}/documents/{document_id}/segments/statistics"
        )
        return SegmentStatistics(**response)
    
    async def batch_enable_segments(
        self,
        dataset_id: str,
        document_id: str,
        segment_ids: List[str]
    ) -> SegmentBatchOperationResponse:
        """批量启用分段
        
        Args:
            dataset_id: 知识库ID
            document_id: 文档ID
            segment_ids: 分段ID列表
            
        Returns:
            批量操作响应
        """
        validate_dataset_id(dataset_id)
        validate_document_id(document_id)
        
        for segment_id in segment_ids:
            validate_segment_id(segment_id)
        
        operation = SegmentBatchOperation(
            segment_ids=segment_ids,
            operation="enable"
        )
        data = operation.model_dump()
        
        response = await self.client.post(
            f"datasets/{dataset_id}/documents/{document_id}/segments/batch",
            json_data=data
        )
        return SegmentBatchOperationResponse(**response)
    
    async def batch_disable_segments(
        self,
        dataset_id: str,
        document_id: str,
        segment_ids: List[str]
    ) -> SegmentBatchOperationResponse:
        """批量禁用分段
        
        Args:
            dataset_id: 知识库ID
            document_id: 文档ID
            segment_ids: 分段ID列表
            
        Returns:
            批量操作响应
        """
        validate_dataset_id(dataset_id)
        validate_document_id(document_id)
        
        for segment_id in segment_ids:
            validate_segment_id(segment_id)
        
        operation = SegmentBatchOperation(
            segment_ids=segment_ids,
            operation="disable"
        )
        data = operation.model_dump()
        
        response = await self.client.post(
            f"datasets/{dataset_id}/documents/{document_id}/segments/batch",
            json_data=data
        )
        return SegmentBatchOperationResponse(**response)
    
    async def batch_delete_segments(
        self,
        dataset_id: str,
        document_id: str,
        segment_ids: List[str]
    ) -> SegmentBatchOperationResponse:
        """批量删除分段
        
        Args:
            dataset_id: 知识库ID
            document_id: 文档ID
            segment_ids: 分段ID列表
            
        Returns:
            批量操作响应
        """
        validate_dataset_id(dataset_id)
        validate_document_id(document_id)
        
        for segment_id in segment_ids:
            validate_segment_id(segment_id)
        
        operation = SegmentBatchOperation(
            segment_ids=segment_ids,
            operation="delete"
        )
        data = operation.model_dump()
        
        response = await self.client.post(
            f"datasets/{dataset_id}/documents/{document_id}/segments/batch",
            json_data=data
        )
        return SegmentBatchOperationResponse(**response)
    
    async def reindex_segment(
        self,
        dataset_id: str,
        document_id: str,
        segment_id: str
    ) -> bool:
        """重新索引分段
        
        Args:
            dataset_id: 知识库ID
            document_id: 文档ID
            segment_id: 分段ID
            
        Returns:
            是否重新索引成功
        """
        validate_dataset_id(dataset_id)
        validate_document_id(document_id)
        validate_segment_id(segment_id)
        
        await self.client.post(
            f"datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}/reindex"
        )
        return True
    
    async def get_segment_hit_testing(
        self,
        dataset_id: str,
        document_id: str,
        segment_id: str,
        query: str
    ) -> Dict[str, Any]:
        """分段命中测试
        
        Args:
            dataset_id: 知识库ID
            document_id: 文档ID
            segment_id: 分段ID
            query: 查询文本
            
        Returns:
            命中测试结果
        """
        validate_dataset_id(dataset_id)
        validate_document_id(document_id)
        validate_segment_id(segment_id)
        
        params = {"query": query}
        response = await self.client.get(
            f"datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}/hit-testing",
            params=params
        )
        return response