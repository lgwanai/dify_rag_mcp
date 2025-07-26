#!/usr/bin/env python3
"""测试MCP客户端连接"""

import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp_client():
    """测试MCP客户端连接"""
    try:
        print("正在连接到MCP服务器...")
        
        # 创建服务器参数
        server_params = StdioServerParameters(
            command="python",
            args=["src/main.py", "--transport", "stdio"]
        )
        
        # 连接到服务器
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # 初始化连接
                await session.initialize()
                
                print("✓ 成功连接到MCP服务器")
                
                # 列出可用的工具
                tools = await session.list_tools()
                print(f"✓ 发现 {len(tools.tools)} 个工具:")
                for tool in tools.tools:
                    print(f"  - {tool.name}: {tool.description}")
                
                # 列出可用的资源
                resources = await session.list_resources()
                print(f"✓ 发现 {len(resources.resources)} 个资源:")
                for resource in resources.resources:
                    print(f"  - {resource.uri}: {resource.name}")
                
                print("\n✓ MCP服务器测试成功完成！")
                return True
                
    except Exception as e:
        print(f"✗ MCP客户端测试失败: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mcp_client())
    sys.exit(0 if success else 1)