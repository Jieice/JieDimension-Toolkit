"""
JieDimension Toolkit - 视频生产插件
自动化短视频生产：内容抓取→AI分析→自动剪辑→发布
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "JieDimension Studio"

from .content_scraper import ContentScraper
from .viral_analyzer import ViralAnalyzer
from .ai_analyzer import AIContentAnalyzer
from .video_generator import VideoGenerator
from .publisher import VideoPublisher
from .capcut_integration import CapCutAPI, VideoEditorSelector

__all__ = [
    'ContentScraper',
    'ViralAnalyzer', 
    'AIContentAnalyzer',
    'VideoGenerator',
    'VideoPublisher',
    'CapCutAPI',
    'VideoEditorSelector'
]

