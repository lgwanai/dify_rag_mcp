"""搜索API模块"""

from typing import Any, Dict, List, Optional

from ..models.common import SearchRequest, SearchResponse, SearchResult
from ..utils.logger import get_logger
from ..utils.validators import (validate_dataset_id, validate_non_empty_string,
                                validate_positive_integer,
                                validate_score_threshold,
                                validate_search_method)
from .client import DifyAPIClient


class SearchAPI:
    """搜索API类"""

    def __init__(self, client: DifyAPIClient):
        """初始化搜索API

        Args:
            client: Dify API客户端
        """
        self.client = client
        self.logger = get_logger(__name__)

    async def search_dataset(
        self,
        dataset_id: str,
        query: str,
        search_method: str = "semantic_search",
        top_k: int = 10,
        score_threshold: Optional[float] = None,
        reranking_enable: bool = False,
        reranking_model: Optional[Dict[str, Any]] = None,
        weights: Optional[Dict[str, float]] = None,
        filter: Optional[Dict[str, Any]] = None,
    ) -> SearchResponse:
        """在知识库中搜索

        Args:
            dataset_id: 知识库ID
            query: 搜索查询
            search_method: 搜索方法
            top_k: 返回结果数量
            score_threshold: 分数阈值
            reranking_enable: 是否启用重排序
            reranking_model: 重排序模型配置
            weights: 权重配置
            filter: 过滤条件

        Returns:
            搜索响应
        """
        validate_dataset_id(dataset_id)
        validate_non_empty_string(query, "query")
        validate_search_method(search_method)
        validate_positive_integer(top_k, "top_k")

        if score_threshold is not None:
            validate_score_threshold(score_threshold)

        search_request = SearchRequest(
            query=query,
            search_method=search_method,
            top_k=top_k,
            score_threshold=score_threshold,
            reranking_enable=reranking_enable,
            reranking_model=reranking_model,
            weights=weights,
            filter=filter,
        )

        data = search_request.model_dump(exclude_none=True)
        response = await self.client.post(
            f"datasets/{dataset_id}/retrieve", json_data=data
        )
        return SearchResponse(**response)

    async def search_multiple_datasets(
        self,
        dataset_ids: List[str],
        query: str,
        search_method: str = "semantic_search",
        top_k: int = 10,
        score_threshold: Optional[float] = None,
        reranking_enable: bool = False,
        reranking_model: Optional[Dict[str, Any]] = None,
        weights: Optional[Dict[str, float]] = None,
        filter: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, SearchResponse]:
        """在多个知识库中搜索

        Args:
            dataset_ids: 知识库ID列表
            query: 搜索查询
            search_method: 搜索方法
            top_k: 返回结果数量
            score_threshold: 分数阈值
            reranking_enable: 是否启用重排序
            reranking_model: 重排序模型配置
            weights: 权重配置
            filter: 过滤条件

        Returns:
            每个知识库的搜索响应
        """
        if not dataset_ids:
            raise ValueError("dataset_ids cannot be empty")

        for dataset_id in dataset_ids:
            validate_dataset_id(dataset_id)

        validate_non_empty_string(query, "query")
        validate_search_method(search_method)
        validate_positive_integer(top_k, "top_k")

        if score_threshold is not None:
            validate_score_threshold(score_threshold)

        search_request = SearchRequest(
            query=query,
            search_method=search_method,
            top_k=top_k,
            score_threshold=score_threshold,
            reranking_enable=reranking_enable,
            reranking_model=reranking_model,
            weights=weights,
            filter=filter,
        )

        data = search_request.model_dump(exclude_none=True)
        data["dataset_ids"] = dataset_ids

        response = await self.client.post("datasets/retrieve", json_data=data)

        # 解析多个知识库的响应
        results = {}
        for dataset_id in dataset_ids:
            if dataset_id in response:
                results[dataset_id] = SearchResponse(**response[dataset_id])

        return results

    async def hybrid_search(
        self,
        dataset_id: str,
        query: str,
        top_k: int = 10,
        score_threshold: Optional[float] = None,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3,
        reranking_enable: bool = True,
        reranking_model: Optional[Dict[str, Any]] = None,
        filter: Optional[Dict[str, Any]] = None,
    ) -> SearchResponse:
        """混合搜索（语义搜索 + 关键词搜索）

        Args:
            dataset_id: 知识库ID
            query: 搜索查询
            top_k: 返回结果数量
            score_threshold: 分数阈值
            semantic_weight: 语义搜索权重
            keyword_weight: 关键词搜索权重
            reranking_enable: 是否启用重排序
            reranking_model: 重排序模型配置
            filter: 过滤条件

        Returns:
            搜索响应
        """
        weights = {"semantic_search": semantic_weight, "keyword_search": keyword_weight}

        return await self.search_dataset(
            dataset_id=dataset_id,
            query=query,
            search_method="hybrid_search",
            top_k=top_k,
            score_threshold=score_threshold,
            reranking_enable=reranking_enable,
            reranking_model=reranking_model,
            weights=weights,
            filter=filter,
        )

    async def semantic_search(
        self,
        dataset_id: str,
        query: str,
        top_k: int = 10,
        score_threshold: Optional[float] = None,
        reranking_enable: bool = False,
        reranking_model: Optional[Dict[str, Any]] = None,
        filter: Optional[Dict[str, Any]] = None,
    ) -> SearchResponse:
        """语义搜索

        Args:
            dataset_id: 知识库ID
            query: 搜索查询
            top_k: 返回结果数量
            score_threshold: 分数阈值
            reranking_enable: 是否启用重排序
            reranking_model: 重排序模型配置
            filter: 过滤条件

        Returns:
            搜索响应
        """
        return await self.search_dataset(
            dataset_id=dataset_id,
            query=query,
            search_method="semantic_search",
            top_k=top_k,
            score_threshold=score_threshold,
            reranking_enable=reranking_enable,
            reranking_model=reranking_model,
            filter=filter,
        )

    async def keyword_search(
        self,
        dataset_id: str,
        query: str,
        top_k: int = 10,
        score_threshold: Optional[float] = None,
        filter: Optional[Dict[str, Any]] = None,
    ) -> SearchResponse:
        """关键词搜索

        Args:
            dataset_id: 知识库ID
            query: 搜索查询
            top_k: 返回结果数量
            score_threshold: 分数阈值
            filter: 过滤条件

        Returns:
            搜索响应
        """
        return await self.search_dataset(
            dataset_id=dataset_id,
            query=query,
            search_method="keyword_search",
            top_k=top_k,
            score_threshold=score_threshold,
            reranking_enable=False,  # 关键词搜索通常不需要重排序
            filter=filter,
        )

    async def full_text_search(
        self,
        dataset_id: str,
        query: str,
        top_k: int = 10,
        score_threshold: Optional[float] = None,
        filter: Optional[Dict[str, Any]] = None,
    ) -> SearchResponse:
        """全文搜索

        Args:
            dataset_id: 知识库ID
            query: 搜索查询
            top_k: 返回结果数量
            score_threshold: 分数阈值
            filter: 过滤条件

        Returns:
            搜索响应
        """
        return await self.search_dataset(
            dataset_id=dataset_id,
            query=query,
            search_method="full_text_search",
            top_k=top_k,
            score_threshold=score_threshold,
            reranking_enable=False,
            filter=filter,
        )

    async def search_with_hit_testing(
        self,
        dataset_id: str,
        query: str,
        search_method: str = "semantic_search",
        top_k: int = 10,
        score_threshold: Optional[float] = None,
    ) -> Dict[str, Any]:
        """搜索并进行命中测试

        Args:
            dataset_id: 知识库ID
            query: 搜索查询
            search_method: 搜索方法
            top_k: 返回结果数量
            score_threshold: 分数阈值

        Returns:
            命中测试结果
        """
        validate_dataset_id(dataset_id)
        validate_non_empty_string(query, "query")
        validate_search_method(search_method)
        validate_positive_integer(top_k, "top_k")

        if score_threshold is not None:
            validate_score_threshold(score_threshold)

        params = {"query": query, "search_method": search_method, "top_k": top_k}

        if score_threshold is not None:
            params["score_threshold"] = score_threshold

        response = await self.client.get(
            f"datasets/{dataset_id}/hit-testing", params=params
        )
        return response

    async def get_search_suggestions(
        self, dataset_id: str, query: str, limit: int = 5
    ) -> List[str]:
        """获取搜索建议

        Args:
            dataset_id: 知识库ID
            query: 查询前缀
            limit: 建议数量限制

        Returns:
            搜索建议列表
        """
        validate_dataset_id(dataset_id)
        validate_non_empty_string(query, "query")
        validate_positive_integer(limit, "limit")

        params = {"query": query, "limit": limit}

        response = await self.client.get(
            f"datasets/{dataset_id}/search-suggestions", params=params
        )
        return response.get("suggestions", [])

    async def get_search_history(
        self, dataset_id: str, page: int = 1, limit: int = 20
    ) -> Dict[str, Any]:
        """获取搜索历史

        Args:
            dataset_id: 知识库ID
            page: 页码
            limit: 每页数量

        Returns:
            搜索历史
        """
        validate_dataset_id(dataset_id)
        validate_positive_integer(page, "page")
        validate_positive_integer(limit, "limit")

        params = {"page": page, "limit": limit}

        response = await self.client.get(
            f"datasets/{dataset_id}/search-history", params=params
        )
        return response

    async def clear_search_history(self, dataset_id: str) -> bool:
        """清空搜索历史

        Args:
            dataset_id: 知识库ID

        Returns:
            是否清空成功
        """
        validate_dataset_id(dataset_id)

        await self.client.delete(f"datasets/{dataset_id}/search-history")
        return True

    async def export_search_results(
        self,
        dataset_id: str,
        query: str,
        search_method: str = "semantic_search",
        top_k: int = 100,
        format: str = "json",
    ) -> Dict[str, Any]:
        """导出搜索结果

        Args:
            dataset_id: 知识库ID
            query: 搜索查询
            search_method: 搜索方法
            top_k: 返回结果数量
            format: 导出格式

        Returns:
            导出信息
        """
        validate_dataset_id(dataset_id)
        validate_non_empty_string(query, "query")
        validate_search_method(search_method)
        validate_positive_integer(top_k, "top_k")

        data = {
            "query": query,
            "search_method": search_method,
            "top_k": top_k,
            "format": format,
        }

        response = await self.client.post(
            f"datasets/{dataset_id}/search-results/export", json_data=data
        )
        return response
