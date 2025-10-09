"""
内容适配器 - 跨平台内容转换

将通用内容格式转换为不同平台的特定格式
"""

from typing import Dict, List, Optional, Any
import re
from core.publisher import PublishContent, PlatformType


class ContentAdapter:
    """
    内容适配器基类
    """
    
    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
        """
        截断文本到指定长度
        
        Args:
            text: 原文本
            max_length: 最大长度
            suffix: 截断后缀
            
        Returns:
            截断后的文本
        """
        if len(text) <= max_length:
            return text
        
        # 留出后缀空间
        actual_length = max_length - len(suffix)
        return text[:actual_length] + suffix
    
    @staticmethod
    def remove_emoji(text: str) -> str:
        """
        移除文本中的emoji
        
        Args:
            text: 原文本
            
        Returns:
            移除emoji后的文本
        """
        # 简单的emoji过滤（可以改进）
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE
        )
        return emoji_pattern.sub('', text)
    
    @staticmethod
    def add_emoji(text: str, position: str = "start") -> str:
        """
        添加通用emoji（简化版）
        
        Args:
            text: 原文本
            position: 位置（start/end）
            
        Returns:
            添加emoji后的文本
        """
        common_emojis = ["✨", "🔥", "💡", "🎉", "⭐"]
        emoji = common_emojis[0]  # 简单选择第一个
        
        if position == "start":
            return f"{emoji} {text}"
        else:
            return f"{text} {emoji}"
    
    @staticmethod
    def extract_keywords(text: str, max_count: int = 5) -> List[str]:
        """
        从文本中提取关键词（简化版）
        
        Args:
            text: 文本
            max_count: 最大数量
            
        Returns:
            关键词列表
        """
        # 简单实现：分词后取高频词
        # 这里仅作示例，实际应该使用jieba等分词工具
        words = re.findall(r'[\u4e00-\u9fff]+', text)
        
        # 简单去重和计数
        word_freq = {}
        for word in words:
            if len(word) >= 2:  # 至少2个字
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # 按频率排序
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, _ in sorted_words[:max_count]]


class XianyuAdapter(ContentAdapter):
    """闲鱼内容适配器"""
    
    @staticmethod
    def adapt(content: PublishContent) -> PublishContent:
        """
        适配内容到闲鱼格式
        
        Args:
            content: 原始内容
            
        Returns:
            适配后的内容
        """
        adapted = PublishContent(
            title=ContentAdapter.truncate_text(content.title, 30),
            description=ContentAdapter.truncate_text(
                content.description or content.content, 
                500
            ),
            images=content.images[:9],  # 最多9张图
            tags=content.tags[:10],     # 最多10个标签
            category=content.category,
            price=content.price,
            platform_data=content.platform_data
        )
        
        return adapted


class XiaohongshuAdapter(ContentAdapter):
    """小红书内容适配器"""
    
    @staticmethod
    def adapt(content: PublishContent) -> PublishContent:
        """
        适配内容到小红书格式
        
        特点：
        - 标题必须有emoji
        - 标题15-20字
        - 内容最多1000字
        - 最多9张图
        """
        # 确保标题有emoji
        title = content.title
        if not re.search(r'[\U0001F000-\U0001F9FF]', title):
            title = ContentAdapter.add_emoji(title, "start")
        
        # 截断标题
        title = ContentAdapter.truncate_text(title, 20)
        
        # 处理内容
        adapted_content = content.content or content.description
        adapted_content = ContentAdapter.truncate_text(adapted_content, 1000)
        
        adapted = PublishContent(
            title=title,
            content=adapted_content,
            images=content.images[:9],
            tags=content.tags[:10],
            category=content.category,
            platform_data=content.platform_data
        )
        
        return adapted


class ZhihuAdapter(ContentAdapter):
    """知乎内容适配器"""
    
    @staticmethod
    def adapt(content: PublishContent) -> PublishContent:
        """
        适配内容到知乎格式
        
        特点：
        - 不使用emoji（移除）
        - 标题20-50字
        - 支持长文（最高100000字）
        - 支持Markdown
        """
        # 移除标题中的emoji
        title = ContentAdapter.remove_emoji(content.title)
        title = ContentAdapter.truncate_text(title, 50)
        
        # 移除内容中的emoji
        adapted_content = ContentAdapter.remove_emoji(
            content.content or content.description
        )
        adapted_content = ContentAdapter.truncate_text(adapted_content, 100000)
        
        adapted = PublishContent(
            title=title,
            content=adapted_content,
            images=content.images[:100],  # 最多100张图
            tags=content.tags[:5],         # 最多5个标签
            category=content.category,
            platform_data={
                **content.platform_data,
                "markdown": True  # 标记支持Markdown
            }
        )
        
        return adapted


class BilibiliAdapter(ContentAdapter):
    """B站内容适配器"""
    
    @staticmethod
    def adapt(content: PublishContent) -> PublishContent:
        """
        适配内容到B站格式
        
        特点：
        - 标题最多80字
        - 简介最多2000字
        - 最多10个标签
        - 动态最多233字
        """
        title = ContentAdapter.truncate_text(content.title, 80)
        
        # B站简介
        description = content.description or content.content
        description = ContentAdapter.truncate_text(description, 2000)
        
        # 动态内容（如果需要）
        dynamic_text = ""
        if content.platform_data.get("dynamic"):
            dynamic_text = ContentAdapter.truncate_text(
                content.platform_data["dynamic"],
                233
            )
        
        adapted = PublishContent(
            title=title,
            description=description,
            images=content.images[:3],  # 最多3张封面
            tags=content.tags[:10],
            video=content.video,
            category=content.category,
            platform_data={
                **content.platform_data,
                "dynamic": dynamic_text
            }
        )
        
        return adapted


class UniversalContentAdapter:
    """
    通用内容适配器
    
    根据目标平台自动选择合适的适配器
    """
    
    # 适配器映射
    ADAPTERS = {
        PlatformType.XIANYU: XianyuAdapter,
        PlatformType.XIAOHONGSHU: XiaohongshuAdapter,
        PlatformType.ZHIHU: ZhihuAdapter,
        PlatformType.BILIBILI: BilibiliAdapter,
    }
    
    @classmethod
    def adapt(
        cls,
        content: PublishContent,
        target_platform: PlatformType
    ) -> PublishContent:
        """
        适配内容到目标平台
        
        Args:
            content: 原始内容
            target_platform: 目标平台
            
        Returns:
            适配后的内容
        """
        adapter_class = cls.ADAPTERS.get(target_platform)
        
        if not adapter_class:
            print(f"⚠️ 平台 {target_platform.value} 暂无专用适配器，使用原内容")
            return content
        
        return adapter_class.adapt(content)
    
    @classmethod
    def adapt_to_multiple_platforms(
        cls,
        content: PublishContent,
        platforms: List[PlatformType]
    ) -> Dict[PlatformType, PublishContent]:
        """
        将内容适配到多个平台
        
        Args:
            content: 原始内容
            platforms: 目标平台列表
            
        Returns:
            平台 -> 适配内容的字典
        """
        adapted_contents = {}
        
        for platform in platforms:
            adapted_contents[platform] = cls.adapt(content, platform)
        
        return adapted_contents
    
    @classmethod
    def compare_adaptations(
        cls,
        content: PublishContent,
        platforms: List[PlatformType]
    ) -> Dict[str, Any]:
        """
        比较不同平台的适配结果
        
        Args:
            content: 原始内容
            platforms: 平台列表
            
        Returns:
            对比数据
        """
        comparison = {
            "original": {
                "title": content.title,
                "title_length": len(content.title),
                "content_length": len(content.content or ""),
                "images_count": len(content.images),
                "tags_count": len(content.tags)
            },
            "adapted": {}
        }
        
        for platform in platforms:
            adapted = cls.adapt(content, platform)
            comparison["adapted"][platform.value] = {
                "title": adapted.title,
                "title_length": len(adapted.title),
                "content_length": len(adapted.content or ""),
                "images_count": len(adapted.images),
                "tags_count": len(adapted.tags)
            }
        
        return comparison


# 便捷函数

def adapt_content(
    content: PublishContent,
    platform: str
) -> PublishContent:
    """
    适配内容到指定平台（便捷函数）
    
    Args:
        content: 原始内容
        platform: 平台名称（如 "xiaohongshu"）
        
    Returns:
        适配后的内容
    """
    try:
        platform_enum = PlatformType(platform)
        return UniversalContentAdapter.adapt(content, platform_enum)
    except ValueError:
        print(f"❌ 未知平台: {platform}")
        return content

