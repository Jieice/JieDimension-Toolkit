"""
JieDimension Toolkit - 平台插件基类
所有平台插件必须继承此基类
Version: 2.0.0
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass


class PlatformType(Enum):
    """支持的平台类型"""
    XIANYU = "xianyu"              # 闲鱼
    XIAOHONGSHU = "xiaohongshu"    # 小红书
    ZHIHU = "zhihu"                # 知乎
    BILIBILI = "bilibili"          # B站
    DOUYIN = "douyin"              # 抖音
    KUAISHOU = "kuaishou"          # 快手
    WEIBO = "weibo"                # 微博
    WECHAT = "wechat"              # 微信公众号
    TAOBAO = "taobao"              # 淘宝
    PINDUODUO = "pinduoduo"        # 拼多多


class ContentType(Enum):
    """内容类型"""
    PRODUCT = "product"            # 商品（闲鱼、淘宝、拼多多）
    NOTE = "note"                  # 笔记（小红书）
    ARTICLE = "article"            # 文章（知乎、微信公众号）
    ANSWER = "answer"              # 回答（知乎）
    DYNAMIC = "dynamic"            # 动态（B站、微博）
    VIDEO = "video"                # 视频（B站、抖音、快手）
    SHORT_VIDEO = "short_video"    # 短视频（抖音、快手）


@dataclass
class PlatformLimits:
    """平台限制配置"""
    title_max_length: int                # 标题最大长度
    content_max_length: int              # 内容最大长度
    images_max_count: int                # 最大图片数
    tags_max_count: int = 10             # 最大标签数
    video_max_size_mb: int = 1024        # 视频最大大小(MB)
    video_max_duration: int = 3600       # 视频最大时长(秒)
    
    # 平台特性
    supports_markdown: bool = False      # 是否支持Markdown
    supports_emoji: bool = True          # 是否支持emoji
    supports_links: bool = True          # 是否支持链接
    supports_mentions: bool = True       # 是否支持@提及
    
    # 发布限制
    publish_interval: int = 2            # 发布间隔(秒)
    daily_publish_limit: int = 50        # 每日发布限制


@dataclass
class PublishResult:
    """发布结果"""
    success: bool                        # 是否成功
    content_id: Optional[str] = None     # 平台内容ID
    content_url: Optional[str] = None    # 内容链接
    error: Optional[str] = None          # 错误信息
    platform: str = ""                   # 平台名称
    publish_time: Optional[str] = None   # 发布时间


class BasePlatformPlugin(ABC):
    """
    平台插件基类
    
    所有平台插件必须继承此类并实现所有抽象方法
    """
    
    def __init__(self):
        """初始化插件"""
        self.platform_name: str = ""                    # 平台名称
        self.platform_type: Optional[PlatformType] = None  # 平台类型
        self.supported_content_types: List[ContentType] = []  # 支持的内容类型
        self.platform_limits: Optional[PlatformLimits] = None  # 平台限制
        self.enabled: bool = True                       # 是否启用
        self.version: str = "1.0.0"                    # 插件版本
    
    # ===== 必须实现的方法 =====
    
    @abstractmethod
    async def validate_content(self, content: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        验证内容是否符合平台规范
        
        Args:
            content: 内容数据
            
        Returns:
            (是否有效, 错误信息)
        """
        pass
    
    @abstractmethod
    async def optimize_title(
        self,
        title: str,
        content_type: ContentType = ContentType.PRODUCT,
        **kwargs
    ) -> str:
        """
        优化标题（使用AI）
        
        Args:
            title: 原始标题
            content_type: 内容类型
            **kwargs: 额外参数
            
        Returns:
            优化后的标题
        """
        pass
    
    @abstractmethod
    async def optimize_content(
        self,
        content: str,
        content_type: ContentType = ContentType.PRODUCT,
        **kwargs
    ) -> str:
        """
        优化内容/描述（使用AI）
        
        Args:
            content: 原始内容
            content_type: 内容类型
            **kwargs: 额外参数
            
        Returns:
            优化后的内容
        """
        pass
    
    @abstractmethod
    async def generate_tags(
        self,
        content: str,
        title: Optional[str] = None,
        max_tags: int = 10,
        **kwargs
    ) -> List[str]:
        """
        生成标签（使用AI）
        
        Args:
            content: 内容
            title: 标题
            max_tags: 最大标签数
            **kwargs: 额外参数
            
        Returns:
            标签列表
        """
        pass
    
    @abstractmethod
    async def publish(
        self,
        content: Dict[str, Any],
        content_type: ContentType = ContentType.PRODUCT,
        **kwargs
    ) -> PublishResult:
        """
        发布内容到平台
        
        Args:
            content: 内容数据（包含title, description, images等）
            content_type: 内容类型
            **kwargs: 额外参数
            
        Returns:
            发布结果
        """
        pass
    
    # ===== 可选实现的方法 =====
    
    def get_platform_limits(self) -> PlatformLimits:
        """
        获取平台限制
        
        Returns:
            平台限制配置
        """
        return self.platform_limits or PlatformLimits(
            title_max_length=100,
            content_max_length=1000,
            images_max_count=9
        )
    
    def get_platform_info(self) -> Dict[str, Any]:
        """
        获取平台信息
        
        Returns:
            平台信息字典
        """
        return {
            "name": self.platform_name,
            "type": self.platform_type.value if self.platform_type else "unknown",
            "supported_types": [ct.value for ct in self.supported_content_types],
            "enabled": self.enabled,
            "version": self.version,
            "limits": {
                "title_max": self.platform_limits.title_max_length if self.platform_limits else 0,
                "content_max": self.platform_limits.content_max_length if self.platform_limits else 0,
                "images_max": self.platform_limits.images_max_count if self.platform_limits else 0,
            }
        }
    
    async def pre_publish_check(self, content: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        发布前检查
        
        Args:
            content: 内容数据
            
        Returns:
            (是否通过, 错误信息)
        """
        # 验证内容
        valid, error = await self.validate_content(content)
        if not valid:
            return False, error
        
        # 检查字段长度
        limits = self.get_platform_limits()
        
        if "title" in content:
            if len(content["title"]) > limits.title_max_length:
                return False, f"标题超过最大长度 {limits.title_max_length} 字"
        
        if "content" in content or "description" in content:
            content_text = content.get("content") or content.get("description", "")
            if len(content_text) > limits.content_max_length:
                return False, f"内容超过最大长度 {limits.content_max_length} 字"
        
        if "images" in content:
            if len(content["images"]) > limits.images_max_count:
                return False, f"图片数量超过最大限制 {limits.images_max_count} 张"
        
        return True, None
    
    def get_ai_system_prompt(self, task_type: str, content_type: ContentType) -> str:
        """
        获取AI系统提示词
        
        Args:
            task_type: 任务类型 (title/content/tags)
            content_type: 内容类型
            
        Returns:
            系统提示词
        """
        # 子类可以重写此方法以自定义提示词
        base_prompts = {
            "title": f"你是{self.platform_name}平台的标题优化专家。",
            "content": f"你是{self.platform_name}平台的内容优化专家。",
            "tags": f"你是{self.platform_name}平台的标签生成专家。"
        }
        
        return base_prompts.get(task_type, f"你是{self.platform_name}平台的专家。")
    
    async def batch_publish(
        self,
        contents: List[Dict[str, Any]],
        content_type: ContentType = ContentType.PRODUCT,
        **kwargs
    ) -> List[PublishResult]:
        """
        批量发布
        
        Args:
            contents: 内容列表
            content_type: 内容类型
            **kwargs: 额外参数
            
        Returns:
            发布结果列表
        """
        results = []
        
        for content in contents:
            result = await self.publish(content, content_type, **kwargs)
            results.append(result)
            
            # 遵守发布间隔
            import asyncio
            limits = self.get_platform_limits()
            await asyncio.sleep(limits.publish_interval)
        
        return results
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"<{self.__class__.__name__}: {self.platform_name} ({self.version})>"
    
    def __repr__(self) -> str:
        """调试表示"""
        return self.__str__()


# ===== 辅助函数 =====

def get_all_platforms() -> List[str]:
    """获取所有支持的平台"""
    return [pt.value for pt in PlatformType]


def get_all_content_types() -> List[str]:
    """获取所有内容类型"""
    return [ct.value for ct in ContentType]

