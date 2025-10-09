"""
小红书平台发布适配器

处理小红书平台的内容发布逻辑
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
from core.content_adapter import XiaohongshuAdapter


class XiaohongshuPublisher(PlatformPublisher):
    """小红书发布器"""
    
    def __init__(self):
        super().__init__(PlatformType.XIAOHONGSHU)
        self.adapter = XiaohongshuAdapter()
    
    async def validate_content(self, content: PublishContent) -> tuple[bool, Optional[str]]:
        """
        验证内容是否符合小红书要求
        
        Args:
            content: 发布内容
            
        Returns:
            (是否有效, 错误信息)
        """
        # 验证标题
        if not content.title or len(content.title) > 20:
            return False, "标题不能为空且不能超过20字"
        
        # 验证内容
        if content.content and len(content.content) > 1000:
            return False, "内容不能超过1000字"
        
        # 验证图片
        if len(content.images) == 0:
            return False, "至少需要1张图片"
        
        if len(content.images) > 9:
            return False, "图片不能超过9张"
        
        # 验证标签
        if len(content.tags) > 10:
            return False, "标签不能超过10个"
        
        return True, None
    
    async def adapt_content(self, content: PublishContent) -> PublishContent:
        """
        将内容适配到小红书格式
        
        Args:
            content: 原始内容
            
        Returns:
            适配后的内容
        """
        return self.adapter.adapt(content)
    
    async def publish(self, content: PublishContent) -> PublishResult:
        """
        发布内容到小红书
        
        注意：小红书也没有公开API，这里仅为模拟实现
        实际使用需要：
        1. 使用Selenium/Playwright自动化
        2. 或使用官方创作者平台（如果有权限）
        
        Args:
            content: 发布内容
            
        Returns:
            发布结果
        """
        start_time = datetime.now()
        
        try:
            # 模拟发布过程
            print(f"  📤 小红书: 正在发布笔记...")
            print(f"     标题: {content.title}")
            print(f"     内容: {len(content.content or '')}字")
            print(f"     图片: {len(content.images)}张")
            print(f"     标签: {', '.join(content.tags)}")
            
            # 模拟网络延迟
            await asyncio.sleep(2.0)
            
            # 模拟发布成功
            duration = (datetime.now() - start_time).total_seconds()
            
            return PublishResult(
                platform=self.platform,
                status=PublishStatus.SUCCESS,
                post_id=f"xhs_{int(datetime.now().timestamp())}",
                post_url=f"https://www.xiaohongshu.com/explore/{int(datetime.now().timestamp())}",
                published_at=datetime.now(),
                duration=duration,
                extra_data={
                    "title": content.title,
                    "content_length": len(content.content or ''),
                    "images_count": len(content.images),
                    "tags": content.tags
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
            "✨ 标题必须有emoji，增加吸引力",
            "📷 首图要吸引眼球，决定点击率",
            "🏷️ 话题标签要精准，提高曝光",
            "💬 内容要真诚分享，避免硬广",
            "⏰ 建议在早上7-9点或晚上20-22点发布"
        ]

