"""
知乎标题生成器
根据知乎平台特点，生成专业、数字化、痛点导向的标题
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import random

# 导入AI引擎
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from core.ai_engine import AIEngine, TaskComplexity


class ZhihuTitleGenerator:
    """知乎标题生成器"""
    
    # 标题风格模板
    TITLE_STYLES = {
        "问答型": [
            "如何{action}？{number}个方法教你{result}",
            "为什么{problem}？深度解析{reason}",
            "{topic}怎么做？{number}步完整指南",
            "什么是{concept}？{number}个要点全面解析",
            "{topic}值得吗？{number}个维度深度分析",
        ],
        "分析型": [
            "{topic}深度分析：{number}个关键点",
            "关于{topic}的{number}个真相",
            "{topic}完全指南：从{start}到{end}",
            "{topic}的{number}个误区，你中了几个？",
            "深度：{topic}背后的{number}个逻辑",
        ],
        "指南型": [
            "{topic}完全指南：{benefit}",
            "{topic}最全总结：{number}个要点",
            "{topic}实操手册：{number}步从零到一",
            "{topic}避坑指南：{number}个常见错误",
            "{topic}精进之路：{number}个核心技巧",
        ],
        "总结型": [
            "{year}年{topic}最全总结",
            "{topic}精华整理：{number}个核心要点",
            "{topic}知识图谱：{number}个必知概念",
            "{topic}最全合集：{benefit}",
            "{topic}全景解读：{number}个关键维度",
        ],
        "经验型": [
            "我用{time}{action}，总结{number}个经验",
            "{topic}实战{time}，分享{number}点心得",
            "从{start}到{end}：{number}个关键节点",
            "{number}年{topic}经验总结",
            "{topic}踩坑记：{number}个教训",
        ]
    }
    
    # 数字词库（知乎喜欢数字化）
    NUMBERS = ["3", "5", "7", "10", "12", "15", "20"]
    
    # 痛点关键词
    PAIN_POINTS = [
        "为什么", "怎么办", "如何", "能不能",
        "应该", "必须", "值得", "推荐"
    ]
    
    # 价值词
    VALUE_WORDS = [
        "完全指南", "深度解析", "全面解读", "系统总结",
        "实战经验", "避坑指南", "精进之路", "核心要点"
    ]
    
    def __init__(self, ai_engine: Optional[AIEngine] = None):
        """
        初始化知乎标题生成器
        
        Args:
            ai_engine: AI引擎实例，如果不提供则创建新实例
        """
        self.ai_engine = ai_engine or AIEngine()
    
    async def generate_title(
        self,
        topic: str,
        keywords: Optional[List[str]] = None,
        style: str = "问答型",
        use_ai: bool = True,
        count: int = 5
    ) -> List[str]:
        """
        生成知乎标题
        
        Args:
            topic: 文章主题
            keywords: 关键词列表
            style: 标题风格（问答型/分析型/指南型/总结型/经验型）
            use_ai: 是否使用AI生成
            count: 生成数量
            
        Returns:
            标题列表
        """
        titles = []
        
        # 方式1：使用模板生成（快速）
        template_titles = self._generate_from_template(topic, keywords, style, count)
        titles.extend(template_titles)
        
        # 方式2：使用AI生成（高质量）
        if use_ai:
            ai_titles = await self._generate_with_ai(topic, keywords, style, count)
            titles.extend(ai_titles)
        
        # 去重并限制数量
        titles = list(dict.fromkeys(titles))  # 保持顺序的去重
        
        return titles[:count]
    
    def _generate_from_template(
        self,
        topic: str,
        keywords: Optional[List[str]],
        style: str,
        count: int
    ) -> List[str]:
        """
        从模板生成标题
        
        Args:
            topic: 主题
            keywords: 关键词
            style: 风格
            count: 数量
            
        Returns:
            标题列表
        """
        titles = []
        templates = self.TITLE_STYLES.get(style, self.TITLE_STYLES["问答型"])
        
        # 准备填充词
        replacements = {
            "topic": topic,
            "number": random.choice(self.NUMBERS),
            "action": keywords[0] if keywords else "优化",
            "result": keywords[1] if keywords and len(keywords) > 1 else "成功",
            "problem": f"{topic}效果不好",
            "reason": f"{topic}的本质",
            "start": "零",
            "end": "精通",
            "benefit": "全面提升",
            "concept": topic,
            "year": datetime.now().year,
            "time": "3年",
        }
        
        # 生成标题
        for template in templates[:count]:
            try:
                title = template.format(**replacements)
                # 检查长度（知乎标题建议不超过50字）
                if len(title) <= 50:
                    titles.append(title)
            except KeyError:
                continue
        
        return titles
    
    async def _generate_with_ai(
        self,
        topic: str,
        keywords: Optional[List[str]],
        style: str,
        count: int
    ) -> List[str]:
        """
        使用AI生成标题
        
        Args:
            topic: 主题
            keywords: 关键词
            style: 风格
            count: 数量
            
        Returns:
            标题列表
        """
        # 构建提示词
        keywords_str = "、".join(keywords) if keywords else ""
        
        prompt = f"""
为知乎平台生成专业、吸引人的文章标题：

主题：{topic}
关键词：{keywords_str}
风格：{style}

知乎标题特点：
1. 数字化表达（如：5个方法、3个步骤）
2. 痛点导向（如：为什么、如何、怎么办）
3. 干货感强（如：深度解析、完全指南、全面总结）
4. 专业性强（使用专业术语）
5. 逻辑清晰（问题-解决方案）

要求：
1. 生成{count}个不同的标题
2. 每个标题20-50字
3. 标题要专业、理性、逻辑清晰
4. 包含数字（如：3个、5步、10个技巧）
5. 每行一个标题，不要序号
6. 不要使用emoji

标题：
"""
        
        try:
            # 使用AI生成（中等复杂度）
            response = await self.ai_engine.generate(
                prompt=prompt,
                system_prompt="你是一位知乎资深创作者，擅长撰写专业、吸引人的文章标题。",
                complexity=TaskComplexity.MEDIUM,
                temperature=0.8
            )
            
            if response.success:
                # 解析标题
                titles = [
                    line.strip().strip('"').strip("'").strip('、').strip('，')
                    for line in response.content.strip().split('\n')
                    if line.strip() and len(line.strip()) > 10
                ]
                return titles
            else:
                print(f"⚠️ AI生成失败: {response.error}")
                return []
        
        except Exception as e:
            print(f"❌ AI生成错误: {e}")
            return []
    
    def optimize_title_seo(self, title: str, keywords: List[str]) -> str:
        """
        优化标题SEO
        
        Args:
            title: 原标题
            keywords: 关键词列表
            
        Returns:
            优化后的标题
        """
        # 1. 关键词前置
        if keywords and keywords[0] not in title[:10]:
            # 如果主关键词不在前10个字，尝试前置
            if keywords[0] in title:
                title = title.replace(keywords[0], "", 1)
                title = f"{keywords[0]}{title}"
        
        # 2. 确保长度合适（20-50字）
        if len(title) > 50:
            title = title[:47] + "..."
        
        # 3. 添加数字（如果没有）
        if not any(char.isdigit() for char in title):
            # 尝试添加数字
            for num in self.NUMBERS:
                if "方法" in title:
                    title = title.replace("方法", f"{num}个方法", 1)
                    break
                elif "技巧" in title:
                    title = title.replace("技巧", f"{num}个技巧", 1)
                    break
        
        return title
    
    def analyze_title_quality(self, title: str) -> Dict[str, Any]:
        """
        分析标题质量
        
        Args:
            title: 标题
            
        Returns:
            质量评分和建议
        """
        score = 0
        suggestions = []
        
        # 1. 长度检查（20-50字最佳）
        length = len(title)
        if 20 <= length <= 50:
            score += 25
        else:
            if length < 20:
                suggestions.append("标题过短，建议20字以上")
            else:
                suggestions.append("标题过长，建议50字以内")
        
        # 2. 数字检查
        has_number = any(char.isdigit() for char in title)
        if has_number:
            score += 20
        else:
            suggestions.append("建议加入数字（如：5个方法、3步）")
        
        # 3. 痛点词检查
        has_pain_point = any(word in title for word in self.PAIN_POINTS)
        if has_pain_point:
            score += 20
        else:
            suggestions.append("建议加入痛点词（如：如何、为什么）")
        
        # 4. 价值词检查
        has_value_word = any(word in title for word in self.VALUE_WORDS)
        if has_value_word:
            score += 20
        else:
            suggestions.append("建议加入价值词（如：完全指南、深度解析）")
        
        # 5. 避免clickbait
        clickbait_words = ["震惊", "不看后悔", "必须", "绝对"]
        has_clickbait = any(word in title for word in clickbait_words)
        if not has_clickbait:
            score += 15
        else:
            suggestions.append("避免使用过度clickbait词汇")
        
        return {
            "score": score,
            "level": "优秀" if score >= 80 else "良好" if score >= 60 else "需优化",
            "suggestions": suggestions
        }


# 测试代码
async def test_zhihu_title_generator():
    """测试知乎标题生成器"""
    print("="*60)
    print("🧪 测试知乎标题生成器")
    print("="*60)
    
    generator = ZhihuTitleGenerator()
    
    # 测试1：生成标题（仅模板）
    print("\n1️⃣ 测试模板生成（快速）")
    titles = await generator.generate_title(
        topic="Python编程",
        keywords=["学习", "入门", "实战"],
        style="问答型",
        use_ai=False,
        count=5
    )
    for i, title in enumerate(titles, 1):
        print(f"   {i}. {title}")
    
    # 测试2：分析标题质量
    print("\n2️⃣ 测试标题质量分析")
    test_title = "如何高效学习Python？5个方法让你快速入门"
    analysis = generator.analyze_title_quality(test_title)
    print(f"   标题: {test_title}")
    print(f"   评分: {analysis['score']}/100 ({analysis['level']})")
    if analysis['suggestions']:
        print(f"   建议: {', '.join(analysis['suggestions'])}")
    
    # 测试3：SEO优化
    print("\n3️⃣ 测试SEO优化")
    original = "学习方法分享"
    optimized = generator.optimize_title_seo(original, ["Python", "学习"])
    print(f"   原标题: {original}")
    print(f"   优化后: {optimized}")
    
    # 测试4：生成标题（使用AI）
    print("\n4️⃣ 测试AI生成（高质量）")
    print("   正在使用AI生成...")
    titles_ai = await generator.generate_title(
        topic="人工智能",
        keywords=["机器学习", "深度学习", "应用"],
        style="分析型",
        use_ai=True,
        count=3
    )
    for i, title in enumerate(titles_ai, 1):
        print(f"   {i}. {title}")
    
    print("\n" + "="*60)
    print("✅ 测试完成！")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_zhihu_title_generator())


