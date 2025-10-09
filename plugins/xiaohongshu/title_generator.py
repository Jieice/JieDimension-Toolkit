"""
JieDimension Toolkit - 小红书爆款标题生成器
根据主题和关键词生成吸引人的小红书标题
Version: 1.0.0
"""

import sys
import os
from typing import List, Optional
from enum import Enum

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.ai_engine import AIEngine, TaskComplexity


class TitleStyle(Enum):
    """标题风格枚举"""
    ZHONGCAO = "种草"  # 推荐好物
    JIAOCHENG = "教程"  # 干货教程
    FENXIANG = "分享"  # 个人经历
    PINGCE = "测评"  # 产品测评
    YILIAO = "疑问"  # 提问式
    JINGYAN = "经验"  # 避坑指南


class XiaohongshuTitleGenerator:
    """小红书爆款标题生成器"""
    
    # 爆款标题模板库
    TITLE_TEMPLATES = {
        TitleStyle.ZHONGCAO: [
            "震惊！{keyword}竟然这么{adj}！",
            "姐妹们！这个{keyword}真的太{adj}了！",
            "实测{days}天，{keyword}让我{result}！",
            "发现宝藏{keyword}！{adj}到飞起！",
            "终于找到完美的{keyword}了！{emotion}",
        ],
        TitleStyle.JIAOCHENG: [
            "超详细！{keyword}教程来啦{emoji}",
            "手把手教你{action}！{keyword}秘籍",
            "新手必看！{keyword}完整攻略",
            "3分钟学会{keyword}的{point}个技巧！",
            "保姆级教程！{keyword}从入门到精通",
        ],
        TitleStyle.FENXIANG: [
            "我的{keyword}使用心得！建议收藏",
            "用了{time}的{keyword}，终于可以分享了",
            "关于{keyword}，我有话要说！",
            "{keyword}使用感受｜真实不踩雷",
            "分享我的{keyword}日常｜超治愈",
        ],
        TitleStyle.PINGCE: [
            "{keyword}深度测评！优缺点全说",
            "实测{keyword}｜到底值不值？",
            "{brand}vs{brand2}｜{keyword}对比测评",
            "花{price}买{keyword}｜是智商税吗？",
            "{keyword}测评｜踩雷还是真香？",
        ],
        TitleStyle.YILIAO: [
            "{keyword}真的有用吗？｜答案在这",
            "为什么大家都在用{keyword}？",
            "{keyword}怎么选？｜避坑指南",
            "你还不知道{keyword}吗？｜必看",
            "{keyword}是智商税吗？｜真相了",
        ],
        TitleStyle.JINGYAN: [
            "别再{wrong_way}了！试试{keyword}",
            "求求了！{keyword}千万别{mistake}",
            "{keyword}避坑指南｜新手必看",
            "用了{keyword}才知道，原来{truth}",
            "千万别买{keyword}！除非你{condition}",
        ]
    }
    
    # 常用形容词
    ADJECTIVES = {
        "好": ["绝了", "爱了", "上头", "香", "nice", "优秀", "宝藏"],
        "坏": ["踩雷", "翻车", "鸡肋", "一般", "不推荐"],
        "惊讶": ["震惊", "惊艳", "意外", "没想到", "绝绝子"],
    }
    
    # 常用emoji组合
    EMOJI_COMBOS = {
        TitleStyle.ZHONGCAO: ["✨", "💕", "🎀", "💖", "🌟"],
        TitleStyle.JIAOCHENG: ["📝", "✅", "💡", "🎯", "📌"],
        TitleStyle.FENXIANG: ["💭", "📷", "🌈", "☁️", "🎨"],
        TitleStyle.PINGCE: ["📊", "🔍", "⭐", "💯", "🆚"],
        TitleStyle.YILIAO: ["❓", "💬", "🤔", "❗", "‼️"],
        TitleStyle.JINGYAN: ["⚠️", "❌", "⛔", "🚫", "💢"],
    }
    
    def __init__(self, ai_engine: Optional[AIEngine] = None):
        """
        初始化标题生成器
        
        Args:
            ai_engine: AI引擎实例，如果不提供则创建新实例
        """
        self.ai_engine = ai_engine or AIEngine()
    
    async def generate_title(
        self,
        topic: str,
        keywords: List[str],
        style: TitleStyle = TitleStyle.ZHONGCAO,
        use_template: bool = False
    ) -> str:
        """
        生成小红书标题
        
        Args:
            topic: 笔记主题
            keywords: 关键词列表
            style: 标题风格
            use_template: 是否使用模板（模板+AI混合）
            
        Returns:
            生成的标题
        """
        if use_template:
            # 使用模板生成
            import random
            template = random.choice(self.TITLE_TEMPLATES[style])
            
            # 简单变量替换（示例）
            title = template.replace("{keyword}", keywords[0] if keywords else topic)
            title = title.replace("{adj}", random.choice(self.ADJECTIVES["好"]))
            title = title.replace("{emotion}", "🥰")
            
            return title
        else:
            # 使用AI生成
            return await self._generate_with_ai(topic, keywords, style)
    
    async def _generate_with_ai(
        self,
        topic: str,
        keywords: List[str],
        style: TitleStyle
    ) -> str:
        """
        使用AI生成标题
        
        Args:
            topic: 笔记主题
            keywords: 关键词列表
            style: 标题风格
            
        Returns:
            生成的标题
        """
        # 构建提示词
        prompt = f"""
为小红书生成一个爆款标题：

主题：{topic}
关键词：{', '.join(keywords)}
风格：{style.value}

要求：
1. 标题长度：15-20字
2. 必须包含1-2个合适的emoji
3. 口语化表达，有代入感
4. 制造好奇心或情感共鸣
5. 符合小红书平台调性
6. 突出核心卖点

风格特点：
- 种草：突出产品优势，使用"绝了"、"爱了"等口语
- 教程：强调实用性，"手把手"、"新手必看"
- 分享：真实感受，"使用心得"、"建议收藏"
- 测评：客观评价，"值不值"、"踩雷还是真香"
- 疑问：提问式，引发好奇
- 经验：避坑指南，"千万别"、"除非"

只输出标题，不要任何解释。

标题：
"""
        
        # 调用AI生成
        response = await self.ai_engine.generate(
            prompt=prompt,
            system_prompt="你是小红书爆款内容专家，擅长创作高点击率标题",
            complexity=TaskComplexity.MEDIUM
        )
        
        if response.success:
            title = response.content.strip().strip('"').strip("'")
            
            # 确保长度合适
            if len(title) > 25:
                title = title[:25]
            
            # 确保有emoji
            if not self._has_emoji(title):
                emojis = self.EMOJI_COMBOS[style]
                import random
                title = title + " " + random.choice(emojis)
            
            return title
        else:
            return f"❌ 生成失败: {response.error}"
    
    async def generate_multiple_titles(
        self,
        topic: str,
        keywords: List[str],
        count: int = 5,
        style: TitleStyle = TitleStyle.ZHONGCAO
    ) -> List[str]:
        """
        批量生成多个标题供选择
        
        Args:
            topic: 笔记主题
            keywords: 关键词列表
            count: 生成数量
            style: 标题风格
            
        Returns:
            标题列表
        """
        titles = []
        
        for i in range(count):
            # 混合使用模板和AI
            use_template = (i % 2 == 0)  # 交替使用
            
            title = await self.generate_title(
                topic=topic,
                keywords=keywords,
                style=style,
                use_template=use_template
            )
            
            titles.append(title)
        
        return titles
    
    def _has_emoji(self, text: str) -> bool:
        """
        检查文本是否包含emoji
        
        Args:
            text: 要检查的文本
            
        Returns:
            是否包含emoji
        """
        # 简单的emoji检测
        import re
        emoji_pattern = re.compile(
            "[\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE
        )
        
        return bool(emoji_pattern.search(text))
    
    def optimize_title(self, title: str) -> str:
        """
        优化现有标题
        
        Args:
            title: 原始标题
            
        Returns:
            优化后的标题
        """
        optimized = title.strip()
        
        # 去除多余空格
        optimized = " ".join(optimized.split())
        
        # 确保有emoji
        if not self._has_emoji(optimized):
            optimized += " ✨"
        
        # 控制长度
        if len(optimized) > 25:
            optimized = optimized[:25] + "..."
        
        return optimized


# 测试函数
async def test_title_generator():
    """测试标题生成器"""
    print("="*60)
    print("🧪 测试小红书标题生成器")
    print("="*60)
    
    generator = XiaohongshuTitleGenerator()
    
    # 测试1：种草风格
    print("\n📝 测试1：种草风格标题生成")
    print("-"*60)
    
    topic = "夏日防晒"
    keywords = ["防晒霜", "不油腻", "学生党"]
    
    print(f"主题：{topic}")
    print(f"关键词：{keywords}")
    print(f"风格：种草")
    print()
    
    # 生成多个标题
    titles = await generator.generate_multiple_titles(
        topic=topic,
        keywords=keywords,
        count=3,
        style=TitleStyle.ZHONGCAO
    )
    
    for i, title in enumerate(titles, 1):
        print(f"{i}. {title}")
    
    # 测试2：教程风格
    print("\n📝 测试2：教程风格标题生成")
    print("-"*60)
    
    topic = "化妆技巧"
    keywords = ["新手", "底妆", "持久"]
    
    title = await generator.generate_title(
        topic=topic,
        keywords=keywords,
        style=TitleStyle.JIAOCHENG
    )
    
    print(f"生成标题：{title}")
    
    # 测试3：测评风格
    print("\n📝 测试3：测评风格标题生成")
    print("-"*60)
    
    topic = "耳机对比"
    keywords = ["AirPods", "小米", "音质"]
    
    title = await generator.generate_title(
        topic=topic,
        keywords=keywords,
        style=TitleStyle.PINGCE
    )
    
    print(f"生成标题：{title}")
    
    print("\n" + "="*60)
    print("✅ 测试完成")
    print("="*60)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_title_generator())

