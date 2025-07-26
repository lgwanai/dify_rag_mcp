#!/usr/bin/env python3
"""简单的服务器功能测试"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.mcp_server.server import DifyMCPServer
from src.utils.logger import get_logger

logger = get_logger(__name__)

async def test_server_functionality():
    """测试服务器基本功能"""
    try:
        logger.info("创建Dify MCP服务器...")
        server = DifyMCPServer()
        
        logger.info("初始化服务器...")
        await server.initialize()
        
        logger.info("获取服务器信息...")
        server_info = await server.get_server_info()
        
        print("\n=== 服务器信息 ===")
        print(f"名称: {server_info['name']}")
        print(f"版本: {server_info['version']}")
        print(f"描述: {server_info['description']}")
        print(f"初始化状态: {server_info['initialized']}")
        
        print("\n=== 功能特性 ===")
        for feature in server_info['features']:
            print(f"  ✓ {feature}")
        
        # 获取MCP服务器实例
        mcp = server.get_mcp_server()
        
        print("\n=== MCP服务器状态 ===")
        print(f"MCP服务器类型: {type(mcp).__name__}")
        print(f"MCP服务器名称: {mcp.name}")
        # 版本信息从server_info中获取
        print(f"MCP服务器版本: {server_info['version']}")
        
        # 尝试获取工具和资源信息
        try:
            # 检查是否有工具注册方法
            if hasattr(mcp, 'tools'):
                tools = mcp.tools
                print(f"\n=== MCP工具 ===")
                print(f"注册的工具数量: {len(tools) if tools else 0}")
            else:
                print("\n=== MCP工具 ===")
                print("工具信息不可直接访问（这是正常的）")
                
            if hasattr(mcp, 'resources'):
                resources = mcp.resources
                print(f"\n=== MCP资源 ===")
                print(f"注册的资源数量: {len(resources) if resources else 0}")
            else:
                print("\n=== MCP资源 ===")
                print("资源信息不可直接访问（这是正常的）")
        except Exception as e:
            print(f"\n注意: 无法直接访问工具/资源列表: {e}")
            print("这是正常的，因为FastMCP可能不暴露内部结构")
        
        logger.info("清理服务器资源...")
        await server.cleanup()
        
        print("\n✓ 服务器功能测试成功完成！")
        return True
        
    except Exception as e:
        logger.error(f"服务器功能测试失败: {e}")
        print(f"\n✗ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_server_functionality())
    sys.exit(0 if success else 1)