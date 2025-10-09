"""
批量发布插件

支持跨平台一键发布内容
"""

from plugins.batch_publisher.task_manager import BatchPublishManager
from core.publisher import PublishContent, PublishResult, PlatformType

__all__ = [
    'BatchPublishManager',
    'PublishContent',
    'PublishResult',
    'PlatformType',
]

