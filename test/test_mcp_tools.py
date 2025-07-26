#!/usr/bin/env python3
"""
MCP 工具功能测试脚本
测试各种 MCP 工具的基本功能
"""

import asyncio
import sys
import os
import time
from loguru import logger

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.mcp_server.server import DifyMCPServer
from src.models.dataset import DatasetCreate


async def test_mcp_tools():
    """测试 MCP 工具功能"""
    logger.info("=" * 50)
    logger.info("🚀 开始 MCP 工具功能测试")
    logger.info("=" * 50)
    
    try:
        # 创建并初始化 MCP 服务器
        logger.info("📡 初始化 MCP 服务器...")
        server = DifyMCPServer()
        await server.initialize()
        logger.info("✅ MCP 服务器初始化成功")
        
        # 测试知识库工具
        await test_dataset_tools(server)
        
        # 清理资源
        await server.cleanup()
        
        logger.info("=" * 50)
        logger.info("🎉 所有 MCP 工具测试完成")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"❌ MCP 工具测试失败: {e}")
        raise


async def test_dataset_tools(server: DifyMCPServer):
    """测试知识库工具"""
    logger.info("\n📚 测试知识库工具...")
    
    try:
        # 获取知识库工具
        dataset_tools = server.dataset_tools
        if not dataset_tools:
            raise Exception("知识库工具未初始化")
        
        # 测试列出知识库
        logger.info("📋 测试获取知识库列表...")
        from src.mcp_server.tools.dataset import ListDatasetsArgs
        list_args = ListDatasetsArgs(page=1, limit=10)
        datasets_result = await dataset_tools.list_datasets(list_args)
        logger.info(f"✅ 获取到 {len(datasets_result.get('data', {}).get('data', []))} 个知识库")
        
        # 测试创建知识库
        logger.info("🆕 测试创建知识库...")
        timestamp = int(time.time())
        from src.mcp_server.tools.dataset import CreateDatasetArgs
        create_args = CreateDatasetArgs(
            name=f"MCP测试知识库_{timestamp}",
            description="通过MCP工具创建的测试知识库",
            indexing_technique="high_quality"
        )
        
        create_result = await dataset_tools.create_dataset(create_args)
        dataset_id = create_result.get('data', {}).get('id')
        logger.info(f"✅ 知识库创建成功，ID: {dataset_id}")
        
        # 测试获取知识库详情
        if dataset_id:
            logger.info("🔍 测试获取知识库详情...")
            from src.mcp_server.tools.dataset import GetDatasetArgs
            detail_args = GetDatasetArgs(dataset_id=dataset_id)
            detail_result = await dataset_tools.get_dataset(detail_args)
            logger.info(f"✅ 获取知识库详情成功: {detail_result.get('data', {}).get('name')}")
        
        logger.info("✅ 知识库工具测试完成")
        
    except Exception as e:
        logger.error(f"❌ 知识库工具测试失败: {e}")
        raise


async def test_search_tools(server: DifyMCPServer):
    """测试搜索工具"""
    logger.info("\n🔍 测试搜索工具...")
    
    try:
        # 获取搜索工具
        search_tools = server.search_tools
        if not search_tools:
            raise Exception("搜索工具未初始化")
        
        # 这里可以添加搜索测试
        # 由于需要有文档内容才能搜索，暂时跳过
        logger.info("⏭️  搜索工具测试跳过（需要文档内容）")
        
    except Exception as e:
        logger.error(f"❌ 搜索工具测试失败: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(test_mcp_tools())