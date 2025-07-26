#!/usr/bin/env python3
"""测试第一个API接口：创建空知识库"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.api.client import DifyAPIClient
from src.api.dataset import DatasetAPI
from src.models.dataset import DatasetCreate
from config.settings import get_settings


async def test_list_datasets():
    """测试获取知识库列表"""
    print("🧪 开始测试获取知识库列表...")
    
    try:
        # 获取配置
        settings = get_settings()
        print(f"📋 配置信息: {settings.dify_base_url}")
        
        # 创建客户端
        async with DifyAPIClient() as client:
            dataset_api = DatasetAPI(client)
            
            # 获取知识库列表
            result = await dataset_api.list_datasets()
            print(f"✅ 获取知识库列表成功: {result}")
            
            return result
            
    except Exception as e:
        print(f"❌ 获取知识库列表失败: {e}")
        raise


async def test_create_dataset():
    """测试创建知识库"""
    print("🧪 开始测试创建知识库...")
    
    try:
        # 获取配置
        settings = get_settings()
        print(f"📋 配置信息: {settings.dify_base_url}")
        
        # 创建客户端
        async with DifyAPIClient() as client:
            dataset_api = DatasetAPI(client)
            
            # 准备测试数据（使用时间戳确保名称唯一）
            import time
            timestamp = int(time.time())
            dataset_data = DatasetCreate(
                name=f"测试知识库_{timestamp}",
                description="这是一个测试知识库",
                indexing_technique="high_quality"
            )
            
            # 创建知识库
            result = await dataset_api.create_dataset(dataset_data)
            print(f"✅ 创建知识库成功: {result}")
            
            return result
            
    except Exception as e:
        print(f"❌ 创建知识库失败: {e}")
        raise





async def main():
    """主测试函数"""
    print("=" * 50)
    print("🚀 开始测试 Dify 知识库 API")
    print("=" * 50)
    
    # 先测试获取知识库列表（更简单的API）
    await test_list_datasets()
    
    # 然后测试创建知识库
    await test_create_dataset()
    
    print("\n" + "=" * 50)
    print("✅ 所有测试完成")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())