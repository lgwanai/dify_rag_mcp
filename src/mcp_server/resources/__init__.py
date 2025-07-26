"""MCP资源模块"""

from .dataset import DatasetResource
from .document import DocumentResource
from .segment import SegmentResource

__all__ = [
    "DatasetResource",
    "DocumentResource",
    "SegmentResource",
]
