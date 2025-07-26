"""配置管理模块"""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings
import yaml
from dotenv import load_dotenv


class Settings(BaseSettings):
    """应用配置类"""
    
    # Dify 服务器配置
    dify_base_url: str = Field(
        default="http://localhost:8088/",
        description="Dify 服务器地址"
    )
    dify_api_key: str = Field(
        default="dataset-",
        description="Dify API Key"
    )
    
    # 日志配置
    log_level: str = Field(
        default="INFO",
        description="日志级别"
    )
    log_file: Optional[str] = Field(
        default=None,
        description="日志文件路径"
    )
    
    # MCP 服务器配置
    mcp_server_name: str = Field(
        default="dify-rag-mcp",
        description="MCP 服务器名称"
    )
    mcp_server_version: str = Field(
        default="0.1.0",
        description="MCP 服务器版本"
    )
    
    # 开发环境配置
    debug: bool = Field(
        default=False,
        description="调试模式"
    )
    test_mode: bool = Field(
        default=False,
        description="测试模式"
    )
    
    # HTTP 客户端配置
    http_timeout: int = Field(
        default=30,
        description="HTTP 请求超时时间（秒）"
    )
    http_retries: int = Field(
        default=3,
        description="HTTP 请求重试次数"
    )
    
    @validator('dify_base_url')
    def validate_base_url(cls, v):
        if not v.endswith('/'):
            v += '/'
        if not v.startswith('http'):
            raise ValueError('Base URL must start with http:// or https://')
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # 忽略额外字段
        
    @classmethod
    def load_from_yaml(cls, config_path: str) -> "Settings":
        """从 YAML 文件加载配置"""
        config_file = Path(config_path)
        if not config_file.exists():
            return cls()
            
        with open(config_file, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)
            
        return cls(**config_data)
    
    def validate_config(self) -> bool:
        """验证配置是否有效"""
        if not self.dify_api_key:
            raise ValueError("DIFY_API_KEY 不能为空")
            
        if not self.dify_base_url:
            raise ValueError("DIFY_BASE_URL 不能为空")
            
        return True
    
    def get_dify_headers(self) -> dict:
        """获取 Dify API 请求头"""
        return {
            "Authorization": f"Bearer {self.dify_api_key}",
            "Content-Type": "application/json"
        }


# 全局配置实例
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """获取全局配置实例"""
    global _settings
    
    if _settings is None:
        # 加载环境变量
        load_dotenv()
        
        # 尝试从 YAML 文件加载配置
        config_path = os.getenv("CONFIG_PATH", "config/config.yaml")
        if os.path.exists(config_path):
            _settings = Settings.load_from_yaml(config_path)
        else:
            _settings = Settings()
            
        # 验证配置
        _settings.validate_config()
        
    return _settings


def reload_settings() -> Settings:
    """重新加载配置"""
    global _settings
    _settings = None
    return get_settings()