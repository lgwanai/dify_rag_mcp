#!/usr/bin/env python3
"""测试MCP服务器"""

import asyncio
import json
from src.mcp.server import DifyMCPServer
from src.utils.logger import get_logger

logger = get_logger(__name__)

async def test_mcp_server():
    """测试MCP服务器启动和工具调用"""
    try:
        # 初始化MCP服务器
        logger.info("Initializing MCP server...")
        mcp_server = DifyMCPServer()
        await mcp_server.initialize()
        
        # 获取FastMCP实例
        mcp = mcp_server.mcp
        
        # 测试获取知识库列表工具
        logger.info("Testing list_datasets tool...")
        
        # 模拟工具调用参数
        args = {
            "page": 1,
            "limit": 10
        }
        
        # 调用工具
        result = await mcp._call_tool("list_datasets", args)
        
        logger.info(f"Tool call result: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # 测试创建知识库工具
        logger.info("Testing create_dataset tool...")
        
        import time
        timestamp = int(time.time())
        
        create_args = {
            "name": f"测试知识库_{timestamp}",
            "description": "这是一个通过MCP工具创建的测试知识库",
            "indexing_technique": "high_quality",
            "permission": "only_me"
        }
        
        create_result = await mcp._call_tool("create_dataset", create_args)
        logger.info(f"Create dataset result: {json.dumps(create_result, indent=2, ensure_ascii=False)}")
        
        logger.info("MCP server test completed successfully!")
        
    except Exception as e:
        logger.error(f"MCP server test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_mcp_server())