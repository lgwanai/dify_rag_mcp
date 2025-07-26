#!/usr/bin/env python3
"""测试Dify API连接"""

import asyncio
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from config.settings import get_settings
from src.api.client import DifyAPIClient
from src.api.dataset import DatasetAPI


async def test_connection():
    """测试基本连接"""
    print("🧪 开始测试Dify API连接...")

    try:
        # 获取配置
        settings = get_settings()
        print(f"📋 配置信息:")
        print(f"  - Base URL: {settings.dify_base_url}")
        print(f"  - API Key: {settings.dify_api_key[:20]}...")

        # 创建客户端
        async with DifyAPIClient() as client:
            print("✅ 客户端创建成功")

            # 尝试一个简单的请求
            try:
                dataset_api = DatasetAPI(client)
                print("🔍 尝试获取知识库列表...")
                result = await dataset_api.list_datasets()
                print(f"✅ API调用成功: {result}")

            except Exception as api_error:
                print(f"❌ API调用失败: {api_error}")
                print("💡 这可能是因为:")
                print("  1. Dify服务器没有运行")
                print("  2. API Key无效")
                print("  3. 网络连接问题")
                print("  4. API端点不正确")

                # 尝试检查服务器是否可达
                import httpx

                try:
                    async with httpx.AsyncClient() as http_client:
                        response = await http_client.get(settings.dify_base_url)
                        print(f"🌐 服务器响应状态: {response.status_code}")
                except Exception as conn_error:
                    print(f"🌐 无法连接到服务器: {conn_error}")

                return False

            return True

    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("=" * 50)
    print("🚀 Dify API 连接测试")
    print("=" * 50)

    success = await test_connection()

    print("\n" + "=" * 50)
    if success:
        print("✅ 连接测试成功")
    else:
        print("❌ 连接测试失败")
        print("\n💡 建议检查:")
        print("  1. 确保Dify服务器正在运行")
        print("  2. 检查config/config.yaml中的配置")
        print("  3. 验证API Key是否正确")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
