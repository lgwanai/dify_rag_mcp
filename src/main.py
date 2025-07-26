#!/usr/bin/env python3
"""
Dify RAG MCP Server 主入口模块

这个文件提供了启动MCP服务器的命令行接口，支持多种传输方式。
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.config.settings import Settings
from src.mcp_server.server import DifyMCPServer
from src.utils.logger import setup_logger


def setup_logging(settings) -> None:
    """设置日志配置"""
    setup_logger(settings)


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="Dify RAG MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --transport stdio
  %(prog)s --transport sse --host localhost --port 8000
  %(prog)s --transport websocket --host 0.0.0.0 --port 9000
  %(prog)s --config config/production.yaml
        """,
    )

    # 传输方式
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "websocket"],
        default="stdio",
        help="传输方式 (默认: stdio)",
    )

    # 网络配置
    parser.add_argument(
        "--host", default="localhost", help="服务器主机地址 (默认: localhost)"
    )

    parser.add_argument(
        "--port", type=int, default=8000, help="服务器端口 (默认: 8000)"
    )

    # 配置文件
    parser.add_argument("--config", type=Path, help="配置文件路径")

    # Dify配置
    parser.add_argument("--dify-api-key", help="Dify API密钥")

    parser.add_argument("--dify-base-url", help="Dify API基础URL")

    # 日志配置
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="日志级别 (默认: INFO)",
    )

    parser.add_argument("--log-file", help="日志文件路径")

    # 开发选项
    parser.add_argument("--dev", action="store_true", help="开发模式")

    parser.add_argument("--debug", action="store_true", help="调试模式")

    # 健康检查
    parser.add_argument(
        "--health-check", action="store_true", help="运行健康检查并退出"
    )

    # 版本信息
    parser.add_argument(
        "--version", action="version", version="Dify RAG MCP Server 1.0.0"
    )

    return parser.parse_args()


def load_settings(args: argparse.Namespace) -> Settings:
    """加载配置"""
    # 设置环境变量以覆盖默认值
    if args.dify_api_key:
        os.environ["DIFY_API_KEY"] = args.dify_api_key

    if args.dify_base_url:
        os.environ["DIFY_BASE_URL"] = args.dify_base_url

    if args.log_level:
        os.environ["DIFY_LOG_LEVEL"] = args.log_level

    if args.debug:
        os.environ["DIFY_DEBUG"] = "true"
        os.environ["DIFY_LOG_LEVEL"] = "DEBUG"

    if args.dev:
        os.environ["DIFY_LOG_LEVEL"] = "DEBUG"

    # 创建设置实例（会自动从环境变量和.env文件加载）
    settings = Settings()
    
    return settings


async def health_check() -> bool:
    """健康检查"""
    try:
        server = DifyMCPServer()
        await server.initialize()
        result = await server.health_check()
        if result.get("status") == "healthy":
            print("✓ 健康检查通过")
            return True
        else:
            print(f"✗ 健康检查失败: {result.get('message', '未知错误')}")
            return False
    except Exception as e:
        print(f"✗ 健康检查错误: {e}")
        return False


async def main() -> None:
    """主函数"""
    logger = None
    args = None
    
    try:
        # 解析参数
        args = parse_args()

        # 加载配置
        settings = load_settings(args)

        # 设置日志
        setup_logging(settings)

        from src.utils.logger import get_logger
        logger = get_logger("dify-mcp-server")

        # 健康检查模式
        if args.health_check:
            success = await health_check()
            sys.exit(0 if success else 1)

        # 显示启动信息
        logger.info("启动 Dify RAG MCP Server")
        logger.info(f"传输方式: {args.transport}")
        logger.info(f"日志级别: {settings.dify_log_level}")

        if args.transport != "stdio":
            logger.info(f"服务器地址: {args.host}:{args.port}")

        # 验证配置
        if not settings.dify_api_key:
            logger.error("未设置 Dify API 密钥")
            logger.error("请设置环境变量 DIFY_API_KEY 或使用 --dify-api-key 参数")
            sys.exit(1)

        # 启动服务器
        server = DifyMCPServer()
        await server.start(
            transport=args.transport,
            host=args.host if args.transport != "stdio" else "localhost",
            port=args.port if args.transport != "stdio" else 8000,
        )

    except KeyboardInterrupt:
        if logger:
            logger.info("收到中断信号，正在关闭服务器...")
        else:
            print("收到中断信号，正在关闭服务器...")
    except Exception as e:
        if logger:
            logger.error(f"服务器启动失败: {e}")
            if args and args.debug:
                logger.exception("详细错误信息:")
        else:
            print(f"服务器启动失败: {e}")
        sys.exit(1)


def cli() -> None:
    """命令行入口点"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
