"""
闲鱼平台发布适配器

处理闲鱼平台的内容发布逻辑
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
from core.content_adapter import XianyuAdapter


class XianyuPublisher(PlatformPublisher):
    """闲鱼发布器"""
    
    def __init__(self):
        super().__init__(PlatformType.XIANYU)
        self.adapter = XianyuAdapter()
    
    async def validate_content(self, content: PublishContent) -> tuple[bool, Optional[str]]:
        """
        验证内容是否符合闲鱼要求
        
        Args:
            content: 发布内容
            
        Returns:
            (是否有效, 错误信息)
        """
        # 验证标题
        if not content.title or len(content.title) > 30:
            return False, "标题不能为空且不能超过30字"
        
        # 验证价格
        if not content.price or content.price <= 0:
            return False, "价格必须大于0"
        
        # 验证分类
        if not content.category:
            return False, "必须指定商品分类"
        
        # 验证图片
        if len(content.images) > 9:
            return False, "图片不能超过9张"
        
        return True, None
    
    async def adapt_content(self, content: PublishContent) -> PublishContent:
        """
        将内容适配到闲鱼格式
        
        Args:
            content: 原始内容
            
        Returns:
            适配后的内容
        """
        return self.adapter.adapt(content)
    
    async def publish(
        self, 
        content: PublishContent, 
        use_browser: bool = True,
        cookies_file: str = "data/xianyu_cookies.json"
    ) -> PublishResult:
        """
        发布内容到闲鱼（支持真实浏览器发布）
        
        Args:
            content: 发布内容
            use_browser: 是否使用真实浏览器发布（True=真实，False=模拟）
            cookies_file: Cookie文件路径
            
        Returns:
            发布结果
        """
        start_time = datetime.now()
        
        try:
            # 转换为商品数据格式
            product = {
                "title": content.title,
                "price": content.price or 0,
                "description": content.body or content.title,
                "images": content.images or [],
                "category": content.category or "二手闲置"
            }
            
            if not use_browser:
                # 模拟发布
                print(f"  📤 闲鱼: 正在发布商品（模拟模式）...")
                print(f"     标题: {content.title}")
                print(f"     价格: ¥{content.price}")
                print(f"     分类: {content.category}")
                print(f"     图片: {len(content.images)}张")
                
                # 模拟网络延迟
                await asyncio.sleep(1.5)
                
                # 模拟发布成功
                duration = (datetime.now() - start_time).total_seconds()
                
                return PublishResult(
                    platform=self.platform,
                    status=PublishStatus.SUCCESS,
                    post_id=f"xianyu_mock_{int(datetime.now().timestamp())}",
                    post_url=f"https://2.taobao.com/item.htm?id={int(datetime.now().timestamp())}",
                    published_at=datetime.now(),
                    duration=duration,
                    extra_data={
                        "title": content.title,
                        "price": content.price,
                        "category": content.category,
                        "mode": "模拟"
                    }
                )
            
            # 真实发布
            print(f"  📤 闲鱼: 正在发布商品（真实模式）...")
            print(f"     标题: {product['title']}")
            print(f"     价格: ¥{product['price']}")
            
            # 导入XianyuPublisher
            from plugins.xianyu.publisher import XianyuPublisher
            
            # 创建发布器
            publisher = XianyuPublisher()
            
            # 调用真实发布
            result = await publisher.publish_product(
                product=product,
                use_browser=True,
                cookies_file=cookies_file
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            if result["success"]:
                return PublishResult(
                    platform=self.platform,
                    status=PublishStatus.SUCCESS,
                    post_id=result.get("post_id", "unknown"),
                    post_url=result.get("post_url", ""),
                    published_at=datetime.now(),
                    duration=duration,
                    extra_data={
                        "title": content.title,
                        "price": content.price,
                        "category": content.category,
                        "mode": "真实"
                    }
                )
            else:
                return PublishResult(
                    platform=self.platform,
                    status=PublishStatus.FAILED,
                    error=result.get("error", "未知错误"),
                    duration=duration
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
            "📝 标题要突出商品核心卖点",
            "💰 定价要合理，可参考同类商品",
            "📷 图片要清晰真实，第一张最重要",
            "🏷️ 选择准确的分类，提高曝光",
            "⏰ 建议在晚上19-22点发布，流量高"
        ]

