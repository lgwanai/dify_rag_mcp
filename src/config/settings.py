"""配置设置模块"""
import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用程序配置设置"""
    
    # Dify API 配置
    dify_api_key: Optional[str] = Field(default=None, env="DIFY_API_KEY")
    dify_base_url: str = Field(default="https://api.dify.ai/v1", env="DIFY_BASE_URL")
    
    # 日志配置
    dify_log_level: str = Field(default="INFO", env="DIFY_LOG_LEVEL")
    dify_debug: bool = Field(default=False, env="DIFY_DEBUG")
    log_file: Optional[str] = Field(default=None, env="DIFY_LOG_FILE")
    
    # HTTP 配置
    dify_timeout: int = Field(default=30, env="DIFY_TIMEOUT")
    dify_max_retries: int = Field(default=3, env="DIFY_MAX_RETRIES")
    
    # 配置文件路径
    config_path: str = Field(default="config/config.yaml", env="CONFIG_PATH")
    
    # 服务器配置
    host: str = Field(default="localhost", env="DIFY_HOST")
    port: int = Field(default=8000, env="DIFY_PORT")
    
    # 数据库配置（如果需要）
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")
    
    # 缓存配置
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")  # 1小时
    
    # MCP服务器配置
    mcp_server_name: str = Field(default="dify-rag-mcp", env="MCP_SERVER_NAME")
    mcp_server_version: str = Field(default="1.0.0", env="MCP_SERVER_VERSION")
    
    @property
    def log_level(self) -> str:
        """获取日志级别（兼容性属性）"""
        return self.dify_log_level

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"  # 允许额外的字段


# 全局设置实例
settings = Settings()

def get_settings() -> Settings:
    """获取设置实例"""
    return settings