"""搜索API测试"""

from unittest.mock import AsyncMock

import pytest

from src.api.search import SearchAPI
from src.models.common import SearchRequest, SearchResponse, SearchResult
from src.utils.exceptions import DifyAPIError, ValidationError


class TestSearchAPI:
    """搜索API测试类"""

    @pytest.fixture
    def search_api(self, mock_api_client: AsyncMock) -> SearchAPI:
        """创建搜索API实例"""
        return SearchAPI(mock_api_client)

    @pytest.mark.asyncio
    async def test_semantic_search_success(
        self,
        search_api: SearchAPI,
        mock_api_client: AsyncMock,
        sample_search_response: dict,
    ):
        """测试语义搜索成功"""
        # 准备响应数据
        mock_api_client.post.return_value = sample_search_response

        # 执行测试
        request = SearchRequest(query="测试查询", top_k=5, score_threshold=0.7)
        result = await search_api.semantic_search("dataset-123", request)

        # 验证结果
        assert isinstance(result, SearchResponse)
        assert result.query == sample_search_response["query"]
        assert len(result.results) == len(sample_search_response["results"])
        assert isinstance(result.results[0], SearchResult)

        # 验证API调用
        mock_api_client.post.assert_called_once_with(
            "datasets/dataset-123/search/semantic",
            json_data={"query": "测试查询", "top_k": 5, "score_threshold": 0.7},
        )

    @pytest.mark.asyncio
    async def test_keyword_search_success(
        self,
        search_api: SearchAPI,
        mock_api_client: AsyncMock,
        sample_search_response: dict,
    ):
        """测试关键词搜索成功"""
        # 准备响应数据
        mock_api_client.post.return_value = sample_search_response

        # 执行测试
        request = SearchRequest(query="测试 关键词", top_k=10)
        result = await search_api.keyword_search("dataset-123", request)

        # 验证结果
        assert isinstance(result, SearchResponse)
        assert result.query == sample_search_response["query"]

        # 验证API调用
        mock_api_client.post.assert_called_once_with(
            "datasets/dataset-123/search/keyword",
            json_data={"query": "测试 关键词", "top_k": 10},
        )

    @pytest.mark.asyncio
    async def test_hybrid_search_success(
        self,
        search_api: SearchAPI,
        mock_api_client: AsyncMock,
        sample_search_response: dict,
    ):
        """测试混合搜索成功"""
        # 准备响应数据
        mock_api_client.post.return_value = sample_search_response

        # 执行测试
        request = SearchRequest(query="混合搜索测试", top_k=8, score_threshold=0.6)
        result = await search_api.hybrid_search("dataset-123", request)

        # 验证结果
        assert isinstance(result, SearchResponse)
        assert result.query == sample_search_response["query"]

        # 验证API调用
        mock_api_client.post.assert_called_once_with(
            "datasets/dataset-123/search/hybrid",
            json_data={"query": "混合搜索测试", "top_k": 8, "score_threshold": 0.6},
        )

    @pytest.mark.asyncio
    async def test_fulltext_search_success(
        self,
        search_api: SearchAPI,
        mock_api_client: AsyncMock,
        sample_search_response: dict,
    ):
        """测试全文搜索成功"""
        # 准备响应数据
        mock_api_client.post.return_value = sample_search_response

        # 执行测试
        request = SearchRequest(query="全文搜索内容", top_k=15)
        result = await search_api.fulltext_search("dataset-123", request)

        # 验证结果
        assert isinstance(result, SearchResponse)
        assert result.query == sample_search_response["query"]

        # 验证API调用
        mock_api_client.post.assert_called_once_with(
            "datasets/dataset-123/search/fulltext",
            json_data={"query": "全文搜索内容", "top_k": 15},
        )

    @pytest.mark.asyncio
    async def test_multi_dataset_search_success(
        self,
        search_api: SearchAPI,
        mock_api_client: AsyncMock,
        sample_search_response: dict,
    ):
        """测试多知识库搜索成功"""
        # 准备响应数据
        mock_api_client.post.return_value = sample_search_response

        # 执行测试
        request = SearchRequest(query="多知识库搜索", top_k=20)
        dataset_ids = ["dataset-123", "dataset-456", "dataset-789"]
        result = await search_api.multi_dataset_search(dataset_ids, request)

        # 验证结果
        assert isinstance(result, SearchResponse)
        assert result.query == sample_search_response["query"]

        # 验证API调用
        mock_api_client.post.assert_called_once_with(
            "datasets/search",
            json_data={
                "dataset_ids": ["dataset-123", "dataset-456", "dataset-789"],
                "query": "多知识库搜索",
                "top_k": 20,
            },
        )

    @pytest.mark.asyncio
    async def test_search_hit_test_success(
        self, search_api: SearchAPI, mock_api_client: AsyncMock
    ):
        """测试搜索命中测试成功"""
        # 准备响应数据
        hit_test_data = {
            "query": "命中测试",
            "hit_count": 5,
            "hits": [
                {"segment_id": "seg-123", "score": 0.95, "content": "匹配内容1"},
                {"segment_id": "seg-456", "score": 0.88, "content": "匹配内容2"},
            ],
        }
        mock_api_client.post.return_value = hit_test_data

        # 执行测试
        result = await search_api.search_hit_test("dataset-123", "命中测试")

        # 验证结果
        assert result["query"] == "命中测试"
        assert result["hit_count"] == 5
        assert len(result["hits"]) == 2

        # 验证API调用
        mock_api_client.post.assert_called_once_with(
            "datasets/dataset-123/search/hit_test", json_data={"query": "命中测试"}
        )

    @pytest.mark.asyncio
    async def test_get_search_suggestions_success(
        self, search_api: SearchAPI, mock_api_client: AsyncMock
    ):
        """测试获取搜索建议成功"""
        # 准备响应数据
        suggestions_data = {"suggestions": ["搜索建议1", "搜索建议2", "搜索建议3"]}
        mock_api_client.get.return_value = suggestions_data

        # 执行测试
        result = await search_api.get_search_suggestions("dataset-123", "搜索")

        # 验证结果
        assert result == suggestions_data["suggestions"]

        # 验证API调用
        mock_api_client.get.assert_called_once_with(
            "datasets/dataset-123/search/suggestions", params={"query": "搜索"}
        )

    @pytest.mark.asyncio
    async def test_get_search_history_success(
        self, search_api: SearchAPI, mock_api_client: AsyncMock
    ):
        """测试获取搜索历史成功"""
        # 准备响应数据
        history_data = {
            "data": [
                {"id": "history-123", "query": "历史查询1", "created_at": 1640995200},
                {"id": "history-456", "query": "历史查询2", "created_at": 1640995100},
            ],
            "total": 2,
        }
        mock_api_client.get.return_value = history_data

        # 执行测试
        result = await search_api.get_search_history("dataset-123", limit=10)

        # 验证结果
        assert result == history_data["data"]

        # 验证API调用
        mock_api_client.get.assert_called_once_with(
            "datasets/dataset-123/search/history", params={"limit": 10}
        )

    @pytest.mark.asyncio
    async def test_clear_search_history_success(
        self, search_api: SearchAPI, mock_api_client: AsyncMock
    ):
        """测试清空搜索历史成功"""
        # 准备响应数据
        mock_api_client.delete.return_value = {"success": True}

        # 执行测试
        result = await search_api.clear_search_history("dataset-123")

        # 验证结果
        assert result is True

        # 验证API调用
        mock_api_client.delete.assert_called_once_with(
            "datasets/dataset-123/search/history"
        )

    @pytest.mark.asyncio
    async def test_export_search_results_success(
        self, search_api: SearchAPI, mock_api_client: AsyncMock
    ):
        """测试导出搜索结果成功"""
        # 准备响应数据
        export_data = {
            "export_id": "export-123",
            "download_url": "https://example.com/download/export-123.csv",
            "status": "completed",
        }
        mock_api_client.post.return_value = export_data

        # 执行测试
        request = SearchRequest(query="导出测试", top_k=100)
        result = await search_api.export_search_results("dataset-123", request, "csv")

        # 验证结果
        assert result["export_id"] == "export-123"
        assert result["download_url"] == "https://example.com/download/export-123.csv"

        # 验证API调用
        mock_api_client.post.assert_called_once_with(
            "datasets/dataset-123/search/export",
            json_data={
                "search_request": {"query": "导出测试", "top_k": 100},
                "format": "csv",
            },
        )

    @pytest.mark.asyncio
    async def test_invalid_dataset_id_raises_error(self, search_api: SearchAPI):
        """测试无效的知识库ID抛出错误"""
        request = SearchRequest(query="测试")

        with pytest.raises(ValidationError):
            await search_api.semantic_search("invalid-id", request)

    @pytest.mark.asyncio
    async def test_empty_query_raises_error(self, search_api: SearchAPI):
        """测试空查询抛出错误"""
        request = SearchRequest(query="", top_k=5)

        with pytest.raises(ValidationError):
            await search_api.semantic_search("dataset-123", request)

    @pytest.mark.asyncio
    async def test_invalid_top_k_raises_error(self, search_api: SearchAPI):
        """测试无效的top_k值抛出错误"""
        request = SearchRequest(query="测试", top_k=0)

        with pytest.raises(ValidationError):
            await search_api.semantic_search("dataset-123", request)

    @pytest.mark.asyncio
    async def test_invalid_score_threshold_raises_error(self, search_api: SearchAPI):
        """测试无效的分数阈值抛出错误"""
        request = SearchRequest(query="测试", score_threshold=1.5)

        with pytest.raises(ValidationError):
            await search_api.semantic_search("dataset-123", request)

    @pytest.mark.asyncio
    async def test_empty_dataset_ids_raises_error(self, search_api: SearchAPI):
        """测试空知识库ID列表抛出错误"""
        request = SearchRequest(query="测试")

        with pytest.raises(ValidationError):
            await search_api.multi_dataset_search([], request)

    @pytest.mark.asyncio
    async def test_api_error_propagation(
        self, search_api: SearchAPI, mock_api_client: AsyncMock
    ):
        """测试API错误传播"""
        # 模拟API错误
        mock_api_client.post.side_effect = DifyAPIError("API Error", status_code=500)

        # 执行测试并验证错误
        request = SearchRequest(query="测试")
        with pytest.raises(DifyAPIError):
            await search_api.semantic_search("dataset-123", request)

    @pytest.mark.asyncio
    async def test_search_with_filters(
        self,
        search_api: SearchAPI,
        mock_api_client: AsyncMock,
        sample_search_response: dict,
    ):
        """测试带过滤条件的搜索"""
        # 准备响应数据
        mock_api_client.post.return_value = sample_search_response

        # 执行测试
        request = SearchRequest(
            query="过滤搜索",
            top_k=5,
            score_threshold=0.8,
            filters={"document_type": "pdf", "language": "zh"},
        )
        result = await search_api.semantic_search("dataset-123", request)

        # 验证结果
        assert isinstance(result, SearchResponse)

        # 验证API调用包含过滤条件
        mock_api_client.post.assert_called_once_with(
            "datasets/dataset-123/search/semantic",
            json_data={
                "query": "过滤搜索",
                "top_k": 5,
                "score_threshold": 0.8,
                "filters": {"document_type": "pdf", "language": "zh"},
            },
        )

    @pytest.mark.asyncio
    async def test_search_with_reranking(
        self,
        search_api: SearchAPI,
        mock_api_client: AsyncMock,
        sample_search_response: dict,
    ):
        """测试带重排序的搜索"""
        # 准备响应数据
        mock_api_client.post.return_value = sample_search_response

        # 执行测试
        request = SearchRequest(
            query="重排序搜索", top_k=10, rerank=True, rerank_model="bge-reranker-large"
        )
        result = await search_api.semantic_search("dataset-123", request)

        # 验证结果
        assert isinstance(result, SearchResponse)

        # 验证API调用包含重排序参数
        mock_api_client.post.assert_called_once_with(
            "datasets/dataset-123/search/semantic",
            json_data={
                "query": "重排序搜索",
                "top_k": 10,
                "rerank": True,
                "rerank_model": "bge-reranker-large",
            },
        )

    @pytest.mark.asyncio
    async def test_get_search_history_with_pagination(
        self, search_api: SearchAPI, mock_api_client: AsyncMock
    ):
        """测试分页获取搜索历史"""
        # 准备响应数据
        history_data = {"data": [], "total": 0, "page": 2, "limit": 5}
        mock_api_client.get.return_value = history_data

        # 执行测试
        result = await search_api.get_search_history("dataset-123", page=2, limit=5)

        # 验证结果
        assert result == history_data["data"]

        # 验证API调用
        mock_api_client.get.assert_called_once_with(
            "datasets/dataset-123/search/history", params={"page": 2, "limit": 5}
        )
