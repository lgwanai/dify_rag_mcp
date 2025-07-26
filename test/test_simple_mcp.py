#!/usr/bin/env python3
"""简化的MCP服务器测试脚本"""

import asyncio
from fastmcp import FastMCP
from src.utils.logger import get_logger

logger = get_logger(__name__)

async def test_simple_mcp():
    """测试简单的MCP服务器"""
    try:
        logger.info("Creating simple MCP server...")
        
        # 创建简单的MCP服务器
        mcp = FastMCP(name="test-server", version="0.1.0")
        
        # 添加一个简单的工具
        @mcp.tool
        def hello(name: str = "World") -> str:
            """Say hello to someone"""
            return f"Hello, {name}!"
        
        logger.info("Simple MCP server created successfully")
        logger.info("Simple MCP test completed successfully")
        
    except Exception as e:
        logger.error(f"Simple MCP test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_simple_mcp())