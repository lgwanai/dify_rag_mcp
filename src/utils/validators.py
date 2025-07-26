"""验证工具模块"""

import re
from typing import Any, Optional
from uuid import UUID

from .exceptions import ValidationError


def validate_uuid(value: str, field_name: str = "ID") -> str:
    """验证 UUID 格式"""
    try:
        UUID(value)
        return value
    except ValueError:
        raise ValidationError(
            f"{field_name} 格式无效，必须是有效的 UUID", field=field_name, value=value
        )


def validate_dataset_id(dataset_id: str) -> str:
    """验证知识库 ID"""
    if not dataset_id or not isinstance(dataset_id, str):
        raise ValidationError(
            "知识库 ID 不能为空", field="dataset_id", value=dataset_id
        )

    return validate_uuid(dataset_id, "知识库 ID")


def validate_document_id(document_id: str) -> str:
    """验证文档 ID"""
    if not document_id or not isinstance(document_id, str):
        raise ValidationError(
            "文档 ID 不能为空", field="document_id", value=document_id
        )

    return validate_uuid(document_id, "文档 ID")


def validate_segment_id(segment_id: str) -> str:
    """验证分段 ID"""
    if not segment_id or not isinstance(segment_id, str):
        raise ValidationError("分段 ID 不能为空", field="segment_id", value=segment_id)

    return validate_uuid(segment_id, "分段 ID")


def validate_api_key(api_key: str) -> str:
    """验证 API Key 格式"""
    if not api_key or not isinstance(api_key, str):
        raise ValidationError("API Key 不能为空", field="api_key", value=api_key)

    # Dify API Key 通常以 dataset- 开头
    if not api_key.startswith("dataset-"):
        raise ValidationError(
            "API Key 格式无效，应以 'dataset-' 开头", field="api_key", value=api_key
        )

    return api_key


def validate_url(url: str, field_name: str = "URL") -> str:
    """验证 URL 格式"""
    if not url or not isinstance(url, str):
        raise ValidationError(f"{field_name} 不能为空", field=field_name, value=url)

    url_pattern = re.compile(
        r"^https?://"  # http:// 或 https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+"  # 域名
        r"(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # 顶级域名
        r"localhost|"  # localhost
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # IP 地址
        r"(?::\d+)?"  # 可选端口
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    if not url_pattern.match(url):
        raise ValidationError(f"{field_name} 格式无效", field=field_name, value=url)

    return url


def validate_indexing_technique(technique: str) -> str:
    """验证索引技术"""
    valid_techniques = ["high_quality", "economy"]
    if technique not in valid_techniques:
        raise ValidationError(
            f"索引技术无效，必须是 {valid_techniques} 之一",
            field="indexing_technique",
            value=technique,
        )
    return technique


def validate_permission(permission: str) -> str:
    """验证权限设置"""
    valid_permissions = ["only_me", "all_team_members", "partial_members"]
    if permission not in valid_permissions:
        raise ValidationError(
            f"权限设置无效，必须是 {valid_permissions} 之一",
            field="permission",
            value=permission,
        )
    return permission


def validate_search_method(method: str) -> str:
    """验证搜索方法"""
    valid_methods = [
        "semantic_search",
        "keyword_search",
        "hybrid_search",
        "full_text_search",
    ]
    if method not in valid_methods:
        raise ValidationError(
            f"搜索方法无效，必须是 {valid_methods} 之一",
            field="search_method",
            value=method,
        )
    return method


def validate_doc_form(doc_form: str) -> str:
    """验证文档形式"""
    valid_forms = ["text_model", "hierarchical_model", "qa_model"]
    if doc_form not in valid_forms:
        raise ValidationError(
            f"文档形式无效，必须是 {valid_forms} 之一", field="doc_form", value=doc_form
        )
    return doc_form


def validate_process_mode(mode: str) -> str:
    """验证处理模式"""
    valid_modes = ["automatic", "custom", "hierarchical"]
    if mode not in valid_modes:
        raise ValidationError(
            f"处理模式无效，必须是 {valid_modes} 之一", field="mode", value=mode
        )
    return mode


def validate_positive_integer(value: Any, field_name: str, min_value: int = 1) -> int:
    """验证正整数"""
    try:
        int_value = int(value)
        if int_value < min_value:
            raise ValidationError(
                f"{field_name} 必须大于等于 {min_value}", field=field_name, value=value
            )
        return int_value
    except (ValueError, TypeError):
        raise ValidationError(
            f"{field_name} 必须是有效的整数", field=field_name, value=value
        )


def validate_score_threshold(score: Any) -> float:
    """验证分数阈值"""
    try:
        float_score = float(score)
        if not 0.0 <= float_score <= 1.0:
            raise ValidationError(
                "分数阈值必须在 0.0 到 1.0 之间", field="score_threshold", value=score
            )
        return float_score
    except (ValueError, TypeError):
        raise ValidationError(
            "分数阈值必须是有效的数字", field="score_threshold", value=score
        )


def validate_non_empty_string(
    value: Any, field_name: str, max_length: Optional[int] = None
) -> str:
    """验证非空字符串"""
    if not value or not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field_name} 不能为空", field=field_name, value=value)

    if max_length and len(value) > max_length:
        raise ValidationError(
            f"{field_name} 长度不能超过 {max_length} 个字符",
            field=field_name,
            value=value,
        )

    return value.strip()
