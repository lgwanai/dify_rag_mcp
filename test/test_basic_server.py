#!/usr/bin/env python3
"""
基础MCP服务器测试脚本
只测试服务器的创建和初始化功能
"""

import asyncio
import sys
import os
from loguru import logger

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.mcp_server.server import DifyMCPServer
from config.settings import Settings

async def test_basic_server():
    """测试基础服务器功能"""
    try:
        logger.info("Starting basic MCP server test...")
        
        # 创建MCP服务器
        mcp_server = DifyMCPServer()
        logger.info("MCP server created successfully")
        
        # 初始化服务器
        await mcp_server.initialize()
        logger.info("MCP server initialized successfully")
        
        # 获取服务器信息
        info = await mcp_server.get_server_info()
        logger.info(f"Server info: {info}")
        
        # 获取健康检查
        health = await mcp_server.health_check()
        logger.info(f"Health check: {health}")
        
        logger.info("Basic MCP server test completed successfully")
        
    except Exception as e:
        logger.error(f"Basic MCP server test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_basic_server())