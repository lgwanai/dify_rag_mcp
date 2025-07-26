"""日志工具模块"""

import sys
from pathlib import Path
from typing import Optional

from loguru import logger


def setup_logger(settings) -> logger:
    """设置日志配置"""
    # 移除默认处理器
    logger.remove()
    
    # 设置日志格式
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    
    # 控制台输出
    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.log_level,
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # 文件输出
    if settings.log_file:
        log_file_path = Path(settings.log_file)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_file_path,
            format=log_format,
            level=settings.log_level,
            rotation="10 MB",
            retention="7 days",
            compression="zip",
            backtrace=True,
            diagnose=True
        )
    
    return logger


def get_logger(name: Optional[str] = None):
    """获取日志记录器"""
    if name:
        return logger.bind(name=name)
    return logger