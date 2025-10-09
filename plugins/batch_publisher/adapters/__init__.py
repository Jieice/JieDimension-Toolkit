"""
平台适配器

各个平台的具体发布实现
"""

from plugins.batch_publisher.adapters.xianyu_adapter import XianyuPublisher
from plugins.batch_publisher.adapters.xiaohongshu_adapter import XiaohongshuPublisher
from plugins.batch_publisher.adapters.zhihu_adapter import ZhihuPublisher
from plugins.batch_publisher.adapters.bilibili_adapter import BilibiliPublisher

__all__ = [
    'XianyuPublisher',
    'XiaohongshuPublisher',
    'ZhihuPublisher',
    'BilibiliPublisher',
]

