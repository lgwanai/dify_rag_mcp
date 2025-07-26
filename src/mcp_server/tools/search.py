"""搜索MCP工具"""

from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from pydantic import BaseModel, Field

from src.api.search import SearchAPI
from src.models.common import (FulltextSearchRequest, HybridSearchRequest,
                              KeywordSearchRequest, MultiDatasetSearchRequest,
                              SearchRequest, SemanticSearchRequest)
from src.utils.exceptions import DifyMCPException
from src.utils.logger import get_logger


class SemanticSearchArgs(BaseModel):
    """语义搜索参数"""

    dataset_id: str = Field(description="知识库ID")
    query: str = Field(description="搜索查询")
    top_k: int = Field(default=10, description="返回结果数量")
    score_threshold: Optional[float] = Field(default=None, description="相似度阈值")
    retrieval_model: Optional[Dict[str, Any]] = Field(
        default=None, description="检索模型配置"
    )


class KeywordSearchArgs(BaseModel):
    """关键词搜索参数"""

    dataset_id: str = Field(description="知识库ID")
    query: str = Field(description="搜索查询")
    top_k: int = Field(default=10, description="返回结果数量")
    optional_words: Optional[List[str]] = Field(default=None, description="可选关键词")


class HybridSearchArgs(BaseModel):
    """混合搜索参数"""

    dataset_id: str = Field(description="知识库ID")
    query: str = Field(description="搜索查询")
    top_k: int = Field(default=10, description="返回结果数量")
    score_threshold: Optional[float] = Field(default=None, description="相似度阈值")
    rerank_model: Optional[Dict[str, Any]] = Field(
        default=None, description="重排序模型配置"
    )
    weights: Optional[Dict[str, float]] = Field(default=None, description="权重配置")


class FulltextSearchArgs(BaseModel):
    """全文搜索参数"""

    dataset_id: str = Field(description="知识库ID")
    query: str = Field(description="搜索查询")
    top_k: int = Field(default=10, description="返回结果数量")
    search_method: str = Field(default="semantic_search", description="搜索方法")


class MultiDatasetSearchArgs(BaseModel):
    """多知识库搜索参数"""

    dataset_ids: List[str] = Field(description="知识库ID列表")
    query: str = Field(description="搜索查询")
    top_k: int = Field(default=10, description="返回结果数量")
    score_threshold: Optional[float] = Field(default=None, description="相似度阈值")
    rerank_model: Optional[Dict[str, Any]] = Field(
        default=None, description="重排序模型配置"
    )


class SearchTools:
    """搜索MCP工具类"""

    def __init__(self, search_api: SearchAPI):
        """初始化搜索工具

        Args:
            search_api: 搜索API实例
        """
        self.search_api = search_api
        self.logger = get_logger(__name__)

    def register_tools(self, mcp: FastMCP):
        """注册搜索相关的MCP工具

        Args:
            mcp: FastMCP服务器实例
        """
        self.logger.info("Registering search tools...")

        # 使用装饰器模式注册工具
        @mcp.tool
        async def semantic_search(args: SemanticSearchArgs) -> dict:
            """语义搜索"""
            return await self.semantic_search(args)

        @mcp.tool
        async def keyword_search(args: KeywordSearchArgs) -> dict:
            """关键词搜索"""
            return await self.keyword_search(args)

        self.logger.info("Search tools registered successfully")

    async def semantic_search(self, args: SemanticSearchArgs) -> Dict[str, Any]:
        """语义搜索"""
        try:
            search_request = SemanticSearchRequest(
                query=args.query,
                top_k=args.top_k,
                score_threshold=args.score_threshold,
                retrieval_model=args.retrieval_model,
            )

            results = await self.search_api.semantic_search(
                args.dataset_id, search_request
            )
            return {
                "success": True,
                "data": results.model_dump(),
                "message": f"语义搜索完成，找到 {len(results.data)} 个结果",
            }
        except Exception as e:
            self.logger.error(f"Failed to perform semantic search: {e}")
            raise DifyMCPException(f"语义搜索失败: {e}")

    async def keyword_search(self, args: KeywordSearchArgs) -> Dict[str, Any]:
        """关键词搜索"""
        try:
            search_request = KeywordSearchRequest(
                query=args.query, top_k=args.top_k, optional_words=args.optional_words
            )

            results = await self.search_api.keyword_search(
                args.dataset_id, search_request
            )
            return {
                "success": True,
                "data": results.model_dump(),
                "message": f"关键词搜索完成，找到 {len(results.data)} 个结果",
            }
        except Exception as e:
            self.logger.error(f"Failed to perform keyword search: {e}")
            raise DifyMCPException(f"关键词搜索失败: {e}")

    async def hybrid_search(self, args: HybridSearchArgs) -> Dict[str, Any]:
        """混合搜索"""
        try:
            search_request = HybridSearchRequest(
                query=args.query,
                top_k=args.top_k,
                score_threshold=args.score_threshold,
                rerank_model=args.rerank_model,
                weights=args.weights,
            )

            results = await self.search_api.hybrid_search(
                args.dataset_id, search_request
            )
            return {
                "success": True,
                "data": results.model_dump(),
                "message": f"混合搜索完成，找到 {len(results.data)} 个结果",
            }
        except Exception as e:
            self.logger.error(f"Failed to perform hybrid search: {e}")
            raise DifyMCPException(f"混合搜索失败: {e}")

    async def fulltext_search(self, args: FulltextSearchArgs) -> Dict[str, Any]:
        """全文搜索"""
        try:
            search_request = FulltextSearchRequest(
                query=args.query, top_k=args.top_k, search_method=args.search_method
            )

            results = await self.search_api.fulltext_search(
                args.dataset_id, search_request
            )
            return {
                "success": True,
                "data": results.model_dump(),
                "message": f"全文搜索完成，找到 {len(results.data)} 个结果",
            }
        except Exception as e:
            self.logger.error(f"Failed to perform fulltext search: {e}")
            raise DifyMCPException(f"全文搜索失败: {e}")

    async def multi_dataset_search(
        self, args: MultiDatasetSearchArgs
    ) -> Dict[str, Any]:
        """多知识库搜索"""
        try:
            search_request = MultiDatasetSearchRequest(
                dataset_ids=args.dataset_ids,
                query=args.query,
                top_k=args.top_k,
                score_threshold=args.score_threshold,
                rerank_model=args.rerank_model,
            )

            results = await self.search_api.multi_dataset_search(search_request)
            return {
                "success": True,
                "data": results.model_dump(),
                "message": f"多知识库搜索完成，找到 {len(results.data)} 个结果",
            }
        except Exception as e:
            self.logger.error(f"Failed to perform multi-dataset search: {e}")
            raise DifyMCPException(f"多知识库搜索失败: {e}")
