"""
B站动态生成器

功能：
- 短动态生成（最多233字）
- 视频简介生成
- 章节时间轴
"""

import asyncio
from typing import List, Dict, Any, Optional
from core.ai_engine import AIEngine, TaskComplexity


class BilibiliDynamicGenerator:
    """B站动态生成器"""
    
    # 动态模板
    DYNAMIC_TEMPLATES = {
        "视频宣传": "{emoji} 新视频来啦！{title}\n\n{highlight}\n\n{hashtags}\n\n{cta}",
        "日常分享": "{emoji} {content}\n\n{hashtags}",
        "互动提问": "小伙伴们{question}？\n\n{options}\n\n评论区告诉我！{emoji}",
    }
    
    def __init__(self, ai_engine: Optional[AIEngine] = None):
        """
        初始化动态生成器
        
        Args:
            ai_engine: AI引擎实例
        """
        self.ai_engine = ai_engine or AIEngine()
    
    async def generate_short_dynamic(
        self,
        video_title: str,
        highlights: List[str],
        hashtags: Optional[List[str]] = None,
        max_length: int = 233
    ) -> str:
        """
        生成短动态（视频宣传）
        
        Args:
            video_title: 视频标题
            highlights: 亮点列表（2-3个）
            hashtags: 话题标签
            max_length: 最大长度（B站限制233字）
            
        Returns:
            动态文案
        """
        
        # 构建提示词
        highlights_str = "\n".join([f"- {h}" for h in highlights[:3]])
        hashtags_str = " ".join([f"#{tag}" for tag in (hashtags or [])])
        
        prompt = f"""
为以下B站视频生成一条宣传动态，最多233字。

视频标题：{video_title}

视频亮点：
{highlights_str}

话题标签：{hashtags_str if hashtags_str else "无"}

要求：
1. 开头用emoji吸引注意
2. 简短介绍视频内容
3. 突出2-3个核心亮点
4. 包含话题标签
5. 结尾加行动号召（如：快来看看吧）
6. 总长度不超过233字
7. 语气轻松、有趣、有感染力
8. 适当使用emoji点缀（不要过多）

请直接输出动态文案，不要解释：
"""
        
        try:
            response = await self.ai_engine.generate(
                prompt=prompt,
                system_prompt="你是B站UP主，擅长写吸引人的动态。",
                complexity=TaskComplexity.SIMPLE,
                max_length=300
            )
            
            if response.success:
                dynamic = response.content.strip()
                
                # 确保长度限制
                if len(dynamic) > max_length:
                    dynamic = dynamic[:max_length-3] + "..."
                
                return dynamic
        
        except Exception as e:
            print(f"⚠️ AI生成动态失败: {e}")
        
        # 降级：使用模板
        return self._generate_from_template(
            video_title, highlights, hashtags, max_length
        )
    
    def _generate_from_template(
        self,
        video_title: str,
        highlights: List[str],
        hashtags: Optional[List[str]],
        max_length: int
    ) -> str:
        """使用模板生成动态"""
        
        template = self.DYNAMIC_TEMPLATES["视频宣传"]
        
        # 填充变量
        emoji = "🎬"
        title = video_title
        highlight = "\n".join([f"✨ {h}" for h in highlights[:3]])
        hashtag_str = " ".join([f"#{tag}" for tag in (hashtags or [])])
        cta = "快来看看吧！👀"
        
        dynamic = template.format(
            emoji=emoji,
            title=title,
            highlight=highlight,
            hashtags=hashtag_str,
            cta=cta
        )
        
        # 确保长度
        if len(dynamic) > max_length:
            dynamic = dynamic[:max_length-3] + "..."
        
        return dynamic
    
    async def generate_video_description(
        self,
        video_info: Dict[str, Any],
        chapters: Optional[List[Dict[str, str]]] = None,
        links: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        生成视频简介
        
        Args:
            video_info: 视频信息
                - title: 标题
                - summary: 概要
                - highlights: 亮点列表
            chapters: 章节时间轴
                - time: 时间点（如：00:00）
                - title: 章节标题
            links: 相关链接
                - name: 链接名称
                - url: 链接地址
                
        Returns:
            视频简介（Markdown格式）
        """
        
        # 构建简介
        parts = []
        
        # 1. 视频概要
        if video_info.get("summary"):
            parts.append(f"📝 {video_info['summary']}\n")
        
        # 2. 核心亮点
        if video_info.get("highlights"):
            parts.append("✨ 本期亮点：")
            for highlight in video_info["highlights"]:
                parts.append(f"  • {highlight}")
            parts.append("")
        
        # 3. 章节时间轴
        if chapters:
            parts.append("⏰ 章节时间轴：")
            for chapter in chapters:
                parts.append(f"  {chapter['time']} - {chapter['title']}")
            parts.append("")
        
        # 4. 相关资源
        if links:
            parts.append("🔗 相关资源：")
            for link in links:
                parts.append(f"  • {link['name']}")
                if link.get("url"):
                    parts.append(f"    {link['url']}")
            parts.append("")
        
        # 5. 结尾
        parts.append("---")
        parts.append("💬 喜欢视频的话记得点赞投币收藏三连哦！")
        parts.append("📢 有问题欢迎评论区讨论~")
        
        return "\n".join(parts)
    
    async def generate_interaction_dynamic(
        self,
        question: str,
        options: Optional[List[str]] = None
    ) -> str:
        """
        生成互动动态（投票/提问）
        
        Args:
            question: 问题
            options: 选项列表
            
        Returns:
            互动动态
        """
        
        parts = []
        
        # 问题（确保有问号）
        question_text = question if question.endswith(('?', '？')) else f"{question}？"
        parts.append(f"💬 小伙伴们，想问一下：")
        parts.append(f"\n❓ {question_text}")
        parts.append("")
        
        # 选项
        if options:
            parts.append("请选择：")
            for i, option in enumerate(options, 1):
                parts.append(f"  {i}. {option}")
            parts.append("")
        
        # 结尾
        parts.append("👇 评论区告诉我你的答案！")
        
        return "\n".join(parts)


# ===== 测试代码 =====

async def test_bilibili_dynamic_generator():
    """测试B站动态生成器"""
    
    print("="*60)
    print("📝 测试B站动态生成器")
    print("="*60)
    
    generator = BilibiliDynamicGenerator()
    
    # 测试1：短动态（视频宣传）
    print("\n【测试1：视频宣传动态】")
    dynamic = await generator.generate_short_dynamic(
        video_title="Python从入门到精通完整教程",
        highlights=[
            "零基础友好，跟着做就能学会",
            "配套练习项目，边学边练",
            "100+知识点全覆盖"
        ],
        hashtags=["Python教程", "编程", "干货"]
    )
    print(dynamic)
    print(f"\n长度: {len(dynamic)}字")
    
    # 测试2：视频简介
    print("\n【测试2：视频简介】")
    description = await generator.generate_video_description(
        video_info={
            "title": "原神5.0版本攻略",
            "summary": "全新版本内容深度解析，带你了解所有新功能和玩法！",
            "highlights": [
                "5.0新角色强度分析",
                "新地图探索路线推荐",
                "活动奖励全收集攻略"
            ]
        },
        chapters=[
            {"time": "00:00", "title": "版本更新内容"},
            {"time": "03:25", "title": "新角色介绍"},
            {"time": "08:10", "title": "新地图探索"},
            {"time": "15:30", "title": "活动攻略"},
        ],
        links=[
            {"name": "攻略文档", "url": "https://example.com/guide"},
            {"name": "资源下载", "url": "https://example.com/download"},
        ]
    )
    print(description)
    
    # 测试3：互动动态
    print("\n【测试3：互动动态】")
    interaction = await generator.generate_interaction_dynamic(
        question="你们更喜欢哪种类型的教程视频",
        options=[
            "保姆级详细教程",
            "快速上手速通",
            "项目实战系列",
            "踩坑经验分享"
        ]
    )
    print(interaction)
    
    print("\n" + "="*60)
    print("✅ 测试完成！")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_bilibili_dynamic_generator())

