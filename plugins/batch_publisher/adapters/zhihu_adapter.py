"""
知乎平台发布适配器

处理知乎平台的内容发布逻辑
"""

import asyncio
from datetime import datetime
from typing import Optional
from core.publisher import (
    PlatformPublisher,
    PublishContent,
    PublishResult,
    PlatformType,
    PublishStatus
)
from core.content_adapter import ZhihuAdapter


class ZhihuPublisher(PlatformPublisher):
    """知乎发布器"""
    
    def __init__(self):
        super().__init__(PlatformType.ZHIHU)
        self.adapter = ZhihuAdapter()
    
    async def validate_content(self, content: PublishContent) -> tuple[bool, Optional[str]]:
        """
        验证内容是否符合知乎要求
        
        Args:
            content: 发布内容
            
        Returns:
            (是否有效, 错误信息)
        """
        # 验证标题
        if not content.title:
            return False, "标题不能为空"
        
        if len(content.title) > 50:
            return False, "标题不能超过50字"
        
        if len(content.title) < 5:
            return False, "标题不能少于5字"
        
        # 验证内容
        if not content.content:
            return False, "内容不能为空"
        
        if len(content.content) < 100:
            return False, "内容不能少于100字"
        
        # 验证标签
        if len(content.tags) > 5:
            return False, "话题不能超过5个"
        
        return True, None
    
    async def adapt_content(self, content: PublishContent) -> PublishContent:
        """
        将内容适配到知乎格式
        
        Args:
            content: 原始内容
            
        Returns:
            适配后的内容
        """
        return self.adapter.adapt(content)
    
    async def publish(self, content: PublishContent) -> PublishResult:
        """
        发布内容到知乎
        
        注意：知乎有官方API，但需要申请权限
        这里仅为模拟实现
        
        Args:
            content: 发布内容
            
        Returns:
            发布结果
        """
        start_time = datetime.now()
        
        try:
            # 模拟发布过程
            print(f"  📤 知乎: 正在发布文章...")
            print(f"     标题: {content.title}")
            print(f"     内容: {len(content.content)}字")
            print(f"     图片: {len(content.images)}张")
            print(f"     话题: {', '.join(content.tags) if content.tags else '无'}")
            
            # 模拟网络延迟
            await asyncio.sleep(1.8)
            
            # 模拟发布成功
            duration = (datetime.now() - start_time).total_seconds()
            
            return PublishResult(
                platform=self.platform,
                status=PublishStatus.SUCCESS,
                post_id=f"zhihu_{int(datetime.now().timestamp())}",
                post_url=f"https://zhuanlan.zhihu.com/p/{int(datetime.now().timestamp())}",
                published_at=datetime.now(),
                duration=duration,
                extra_data={
                    "title": content.title,
                    "content_length": len(content.content),
                    "images_count": len(content.images),
                    "topics": content.tags,
                    "markdown": content.platform_data.get("markdown", False)
                }
            )
        
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return PublishResult(
                platform=self.platform,
                status=PublishStatus.FAILED,
                error=str(e),
                duration=duration
            )
    
    def get_publish_tips(self) -> list[str]:
        """获取发布建议"""
        return [
            "📖 内容要专业、有深度，符合知乎调性",
            "🔍 标题要包含关键词，有利于SEO",
            "📊 数据和案例能增加可信度",
            "🏷️ 选择准确的话题，提高推荐率",
            "⏰ 建议在工作日早上9-11点或晚上20-22点发布"
        ]

