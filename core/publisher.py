"""
批量发布系统 - 统一发布接口

提供跨平台发布的统一接口和数据模型
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class PublishStatus(Enum):
    """发布状态"""
    PENDING = "pending"           # 待发布
    PROCESSING = "processing"     # 发布中
    SUCCESS = "success"           # 成功
    FAILED = "failed"            # 失败
    CANCELLED = "cancelled"       # 已取消


class PlatformType(Enum):
    """支持的平台类型"""
    XIANYU = "xianyu"             # 闲鱼
    XIAOHONGSHU = "xiaohongshu"   # 小红书
    ZHIHU = "zhihu"               # 知乎
    BILIBILI = "bilibili"         # B站
    DOUYIN = "douyin"             # 抖音（预留）
    KUAISHOU = "kuaishou"         # 快手（预留）


@dataclass
class PublishContent:
    """发布内容数据模型"""
    # 基础信息
    title: str                          # 标题
    content: str = ""                   # 正文内容
    description: str = ""               # 描述/简介
    
    # 媒体资源
    images: List[str] = field(default_factory=list)    # 图片路径列表
    video: Optional[str] = None                        # 视频路径
    
    # 元数据
    tags: List[str] = field(default_factory=list)      # 标签
    category: str = ""                                 # 分类
    price: Optional[float] = None                      # 价格（闲鱼）
    
    # 平台特定数据
    platform_data: Dict[str, Any] = field(default_factory=dict)
    
    # 元信息
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """数据验证"""
        if not self.title:
            raise ValueError("标题不能为空")
        
        # 确保列表类型正确
        if isinstance(self.images, str):
            self.images = [self.images] if self.images else []
        if isinstance(self.tags, str):
            self.tags = [tag.strip() for tag in self.tags.split(',') if tag.strip()]


@dataclass
class PublishResult:
    """发布结果"""
    platform: PlatformType              # 发布平台
    status: PublishStatus               # 发布状态
    
    # 成功信息
    post_id: Optional[str] = None       # 平台返回的ID
    post_url: Optional[str] = None      # 发布链接
    
    # 错误信息
    error: Optional[str] = None         # 错误描述
    error_code: Optional[str] = None    # 错误代码
    
    # 统计信息
    published_at: Optional[datetime] = None     # 发布时间
    duration: float = 0.0               # 耗时（秒）
    
    # 额外数据
    extra_data: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def success(self) -> bool:
        """是否发布成功"""
        return self.status == PublishStatus.SUCCESS
    
    def __str__(self) -> str:
        if self.success:
            return f"✅ {self.platform.value}: 发布成功 (ID: {self.post_id})"
        else:
            return f"❌ {self.platform.value}: 发布失败 - {self.error}"


class PlatformPublisher(ABC):
    """
    平台发布器基类
    
    所有平台适配器都必须继承此类
    """
    
    def __init__(self, platform: PlatformType):
        self.platform = platform
        self.enabled = True
    
    @abstractmethod
    async def validate_content(self, content: PublishContent) -> tuple[bool, Optional[str]]:
        """
        验证内容是否符合平台要求
        
        Args:
            content: 发布内容
            
        Returns:
            (是否有效, 错误信息)
        """
        pass
    
    @abstractmethod
    async def adapt_content(self, content: PublishContent) -> PublishContent:
        """
        将内容适配到平台格式
        
        Args:
            content: 原始内容
            
        Returns:
            适配后的内容
        """
        pass
    
    @abstractmethod
    async def publish(self, content: PublishContent) -> PublishResult:
        """
        发布内容到平台
        
        Args:
            content: 发布内容
            
        Returns:
            发布结果
        """
        pass
    
    async def pre_publish(self, content: PublishContent) -> PublishContent:
        """
        发布前预处理
        
        Args:
            content: 发布内容
            
        Returns:
            处理后的内容
        """
        # 默认实现：验证 + 适配
        is_valid, error = await self.validate_content(content)
        if not is_valid:
            raise ValueError(f"内容验证失败: {error}")
        
        return await self.adapt_content(content)
    
    async def post_publish(self, result: PublishResult) -> PublishResult:
        """
        发布后处理
        
        Args:
            result: 发布结果
            
        Returns:
            处理后的结果
        """
        # 默认实现：直接返回
        return result
    
    def get_platform_name(self) -> str:
        """获取平台名称"""
        platform_names = {
            PlatformType.XIANYU: "闲鱼",
            PlatformType.XIAOHONGSHU: "小红书",
            PlatformType.ZHIHU: "知乎",
            PlatformType.BILIBILI: "B站",
            PlatformType.DOUYIN: "抖音",
            PlatformType.KUAISHOU: "快手",
        }
        return platform_names.get(self.platform, self.platform.value)
    
    def get_platform_limits(self) -> Dict[str, Any]:
        """
        获取平台限制
        
        Returns:
            平台限制配置
        """
        limits = {
            PlatformType.XIANYU: {
                "title_max_length": 30,
                "description_max_length": 500,
                "max_images": 9,
                "supports_video": False,
                "supports_emoji": True,
                "max_tags": 10,
            },
            PlatformType.XIAOHONGSHU: {
                "title_max_length": 20,
                "content_max_length": 1000,
                "max_images": 9,
                "supports_video": True,
                "emoji_required": True,
                "max_tags": 10,
            },
            PlatformType.ZHIHU: {
                "title_max_length": 50,
                "content_max_length": 100000,
                "max_images": 100,
                "supports_video": True,
                "supports_markdown": True,
                "max_tags": 5,
            },
            PlatformType.BILIBILI: {
                "title_max_length": 80,
                "description_max_length": 2000,
                "max_images": 3,
                "supports_video": True,
                "max_tags": 10,
                "dynamic_max_length": 233,
            },
        }
        return limits.get(self.platform, {})


class PublishManager:
    """
    发布管理器
    
    管理多平台发布、队列、重试等功能
    """
    
    def __init__(self):
        self.publishers: Dict[PlatformType, PlatformPublisher] = {}
        self.publish_queue: List[tuple[PublishContent, List[PlatformType]]] = []
    
    def register_publisher(self, publisher: PlatformPublisher):
        """
        注册平台发布器
        
        Args:
            publisher: 平台发布器实例
        """
        self.publishers[publisher.platform] = publisher
        print(f"✅ 注册发布器: {publisher.get_platform_name()}")
    
    def get_publisher(self, platform: PlatformType) -> Optional[PlatformPublisher]:
        """
        获取平台发布器
        
        Args:
            platform: 平台类型
            
        Returns:
            发布器实例或None
        """
        return self.publishers.get(platform)
    
    def get_available_platforms(self) -> List[PlatformType]:
        """
        获取所有可用平台
        
        Returns:
            平台类型列表
        """
        return [p for p, pub in self.publishers.items() if pub.enabled]
    
    async def publish_to_single_platform(
        self,
        content: PublishContent,
        platform: PlatformType,
        max_retries: int = 3
    ) -> PublishResult:
        """
        发布到单个平台
        
        Args:
            content: 发布内容
            platform: 目标平台
            max_retries: 最大重试次数
            
        Returns:
            发布结果
        """
        publisher = self.get_publisher(platform)
        if not publisher:
            return PublishResult(
                platform=platform,
                status=PublishStatus.FAILED,
                error=f"平台发布器未注册: {platform.value}"
            )
        
        # 多次重试
        for attempt in range(max_retries):
            try:
                # 发布前处理
                adapted_content = await publisher.pre_publish(content)
                
                # 执行发布
                result = await publisher.publish(adapted_content)
                
                # 发布后处理
                result = await publisher.post_publish(result)
                
                # 成功则返回
                if result.success:
                    return result
                
                # 失败但不重试
                if attempt == max_retries - 1:
                    return result
                
                print(f"⚠️ {publisher.get_platform_name()} 发布失败，重试 {attempt + 1}/{max_retries}")
                
            except Exception as e:
                error_msg = f"发布异常: {str(e)}"
                print(f"❌ {publisher.get_platform_name()}: {error_msg}")
                
                if attempt == max_retries - 1:
                    return PublishResult(
                        platform=platform,
                        status=PublishStatus.FAILED,
                        error=error_msg
                    )
        
        # 不应该到达这里
        return PublishResult(
            platform=platform,
            status=PublishStatus.FAILED,
            error="未知错误"
        )
    
    async def publish_to_multiple_platforms(
        self,
        content: PublishContent,
        platforms: List[PlatformType],
        parallel: bool = False
    ) -> List[PublishResult]:
        """
        发布到多个平台
        
        Args:
            content: 发布内容
            platforms: 目标平台列表
            parallel: 是否并行发布（暂不支持）
            
        Returns:
            发布结果列表
        """
        results = []
        
        for platform in platforms:
            print(f"\n🚀 开始发布到 {platform.value}...")
            result = await self.publish_to_single_platform(content, platform)
            results.append(result)
            print(result)
        
        return results
    
    def get_publish_summary(self, results: List[PublishResult]) -> Dict[str, Any]:
        """
        获取发布结果摘要
        
        Args:
            results: 发布结果列表
            
        Returns:
            摘要数据
        """
        total = len(results)
        success_count = sum(1 for r in results if r.success)
        failed_count = total - success_count
        
        return {
            "total": total,
            "success": success_count,
            "failed": failed_count,
            "success_rate": success_count / total if total > 0 else 0,
            "platforms": {
                "success": [r.platform.value for r in results if r.success],
                "failed": [r.platform.value for r in results if not r.success]
            }
        }


# 便捷函数

def create_content(
    title: str,
    content: str = "",
    **kwargs
) -> PublishContent:
    """
    创建发布内容（便捷函数）
    
    Args:
        title: 标题
        content: 正文
        **kwargs: 其他参数
        
    Returns:
        PublishContent实例
    """
    return PublishContent(title=title, content=content, **kwargs)


async def quick_publish(
    content: PublishContent,
    platforms: List[str],
    manager: PublishManager
) -> List[PublishResult]:
    """
    快速发布（便捷函数）
    
    Args:
        content: 发布内容
        platforms: 平台名称列表（如 ["xianyu", "xiaohongshu"]）
        manager: 发布管理器
        
    Returns:
        发布结果列表
    """
    # 转换平台名称为枚举
    platform_enums = []
    for p in platforms:
        try:
            platform_enums.append(PlatformType(p))
        except ValueError:
            print(f"⚠️ 未知平台: {p}")
    
    return await manager.publish_to_multiple_platforms(content, platform_enums)

