"""
B站内容生成插件

支持功能：
- 标题生成（悬念/教程/测评）
- 动态生成（短动态/视频简介）
- 标签推荐（智能推荐10个标签）
- 分区优化（游戏/科技/生活等）
"""

from .title_generator import BilibiliTitleGenerator
from .dynamic_generator import BilibiliDynamicGenerator
from .tag_recommender import BilibiliTagRecommender
from .zone_optimizer import BilibiliZoneOptimizer

__all__ = [
    "BilibiliTitleGenerator",
    "BilibiliDynamicGenerator",
    "BilibiliTagRecommender",
    "BilibiliZoneOptimizer",
]

__version__ = "1.0.0"

