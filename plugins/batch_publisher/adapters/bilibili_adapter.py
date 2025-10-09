"""
B站平台发布适配器

处理B站平台的内容发布逻辑
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
from core.content_adapter import BilibiliAdapter


class BilibiliPublisher(PlatformPublisher):
    """B站发布器"""
    
    def __init__(self):
        super().__init__(PlatformType.BILIBILI)
        self.adapter = BilibiliAdapter()
    
    async def validate_content(self, content: PublishContent) -> tuple[bool, Optional[str]]:
        """
        验证内容是否符合B站要求
        
        Args:
            content: 发布内容
            
        Returns:
            (是否有效, 错误信息)
        """
        # 验证标题
        if not content.title:
            return False, "标题不能为空"
        
        if len(content.title) > 80:
            return False, "标题不能超过80字"
        
        # 验证简介
        if content.description and len(content.description) > 2000:
            return False, "简介不能超过2000字"
        
        # B站视频发布需要视频文件
        # 这里暂时不做强制要求，可以用于发布动态
        
        # 验证标签
        if len(content.tags) > 10:
            return False, "标签不能超过10个"
        
        # 验证动态
        if content.platform_data.get("dynamic"):
            dynamic = content.platform_data["dynamic"]
            if len(dynamic) > 233:
                return False, "动态内容不能超过233字"
        
        return True, None
    
    async def adapt_content(self, content: PublishContent) -> PublishContent:
        """
        将内容适配到B站格式
        
        Args:
            content: 原始内容
            
        Returns:
            适配后的内容
        """
        return self.adapter.adapt(content)
    
    async def publish(self, content: PublishContent) -> PublishResult:
        """
        发布内容到B站
        
        注意：B站有官方API，但需要申请创作者权限
        这里仅为模拟实现
        
        Args:
            content: 发布内容
            
        Returns:
            发布结果
        """
        start_time = datetime.now()
        
        try:
            # 判断发布类型
            publish_type = "视频" if content.video else "动态"
            
            # 模拟发布过程
            print(f"  📤 B站: 正在发布{publish_type}...")
            print(f"     标题: {content.title}")
            print(f"     简介: {len(content.description or '')}字")
            
            if content.video:
                print(f"     视频: {content.video}")
            
            if content.platform_data.get("dynamic"):
                print(f"     动态: {content.platform_data['dynamic'][:50]}...")
            
            print(f"     标签: {', '.join(content.tags) if content.tags else '无'}")
            
            # 模拟网络延迟（视频上传时间更长）
            delay = 3.0 if content.video else 1.5
            await asyncio.sleep(delay)
            
            # 模拟发布成功
            duration = (datetime.now() - start_time).total_seconds()
            
            # 生成BV号（模拟）
            bv_id = f"BV1{int(datetime.now().timestamp()) % 1000000000}"
            
            return PublishResult(
                platform=self.platform,
                status=PublishStatus.SUCCESS,
                post_id=bv_id,
                post_url=f"https://www.bilibili.com/video/{bv_id}",
                published_at=datetime.now(),
                duration=duration,
                extra_data={
                    "title": content.title,
                    "type": publish_type,
                    "description_length": len(content.description or ''),
                    "tags": content.tags,
                    "has_video": content.video is not None,
                    "has_dynamic": "dynamic" in content.platform_data
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
            "🎬 标题要有悬念感，吸引点击",
            "🔑 关键词要前置，提高搜索排名",
            "🏷️ 标签要精准，提高推荐率",
            "📝 封面和标题要相关，避免标题党",
            "⏰ 建议在晚上18-22点发布，流量最高"
        ]

