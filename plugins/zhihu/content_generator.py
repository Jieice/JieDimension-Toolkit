"""
知乎内容生成器
生成符合知乎风格的文章结构和内容
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

# 导入AI引擎
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from core.ai_engine import AIEngine, TaskComplexity


class ZhihuContentGenerator:
    """知乎内容生成器"""
    
    # 文章结构模板
    ARTICLE_STRUCTURES = {
        "问答型": {
            "sections": [
                "开门见山回答",
                "详细展开（3-5点）",
                "案例/数据支撑",
                "总结和建议"
            ],
            "tips": "直接给出答案，然后逐步展开论证"
        },
        "分析型": {
            "sections": [
                "背景介绍",
                "问题分析",
                "多角度论证",
                "结论和启示"
            ],
            "tips": "逻辑清晰，层层递进，数据支撑"
        },
        "指南型": {
            "sections": [
                "前言（为什么要学）",
                "准备工作",
                "详细步骤（分点叙述）",
                "常见问题FAQ"
            ],
            "tips": "循序渐进，步骤清晰，实操性强"
        },
        "总结型": {
            "sections": [
                "开篇概述",
                "核心要点（逐一展开）",
                "对比分析",
                "结语"
            ],
            "tips": "全面系统，要点突出，便于收藏"
        },
        "经验型": {
            "sections": [
                "个人背景",
                "踩坑经历",
                "解决方案",
                "经验总结"
            ],
            "tips": "真实可信，有共鸣感，可操作"
        }
    }
    
    def __init__(self, ai_engine: Optional[AIEngine] = None):
        """
        初始化内容生成器
        
        Args:
            ai_engine: AI引擎实例
        """
        self.ai_engine = ai_engine or AIEngine()
    
    async def generate_outline(
        self,
        topic: str,
        article_type: str = "问答型",
        keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        生成文章大纲
        
        Args:
            topic: 文章主题
            article_type: 文章类型
            keywords: 关键词
            
        Returns:
            大纲结构
        """
        # 获取结构模板
        structure = self.ARTICLE_STRUCTURES.get(
            article_type,
            self.ARTICLE_STRUCTURES["问答型"]
        )
        
        # 使用AI生成详细大纲
        keywords_str = "、".join(keywords) if keywords else ""
        
        prompt = f"""
为知乎平台生成文章详细大纲：

主题：{topic}
类型：{article_type}
关键词：{keywords_str}

文章结构：
{chr(10).join(f"{i+1}. {section}" for i, section in enumerate(structure['sections']))}

写作建议：{structure['tips']}

要求：
1. 每个章节生成2-3个要点
2. 要点要具体、可执行
3. 逻辑连贯，层层递进
4. 符合知乎专业、理性的风格

请为每个章节生成详细要点：
"""
        
        response = await self.ai_engine.generate(
            prompt=prompt,
            system_prompt="你是知乎资深创作者，擅长撰写逻辑清晰、干货满满的文章。",
            complexity=TaskComplexity.MEDIUM
        )
        
        if response.success:
            outline = {
                "topic": topic,
                "type": article_type,
                "structure": structure,
                "content": response.content,
                "created_at": datetime.now().isoformat()
            }
            return outline
        else:
            # 返回基础大纲
            return {
                "topic": topic,
                "type": article_type,
                "structure": structure,
                "content": "\n".join(structure['sections']),
                "error": response.error
            }
    
    async def generate_section(
        self,
        section_title: str,
        context: str,
        word_count: int = 300
    ) -> str:
        """
        生成章节内容
        
        Args:
            section_title: 章节标题
            context: 上下文信息
            word_count: 目标字数
            
        Returns:
            章节内容
        """
        prompt = f"""
为知乎文章生成章节内容：

章节标题：{section_title}
上下文：{context}
目标字数：{word_count}字左右

要求：
1. 专业、理性、逻辑清晰
2. 使用数据、案例支撑观点
3. 分点叙述，便于阅读
4. 符合知乎风格（不使用emoji）
5. 包含具体可执行的建议

章节内容：
"""
        
        response = await self.ai_engine.generate(
            prompt=prompt,
            system_prompt="你是知乎资深创作者，擅长撰写专业、有深度的文章内容。",
            complexity=TaskComplexity.COMPLEX
        )
        
        return response.content if response.success else f"[生成失败: {response.error}]"
    
    async def generate_full_article(
        self,
        topic: str,
        article_type: str = "问答型",
        keywords: Optional[List[str]] = None,
        word_count: int = 2000
    ) -> Dict[str, Any]:
        """
        生成完整文章
        
        Args:
            topic: 主题
            article_type: 类型
            keywords: 关键词
            word_count: 总字数
            
        Returns:
            完整文章
        """
        print(f"🔄 正在生成文章大纲...")
        
        # 1. 生成大纲
        outline = await self.generate_outline(topic, article_type, keywords)
        
        # 2. 生成各个章节
        structure = outline.get("structure", {})
        sections = structure.get("sections", [])
        
        section_word_count = word_count // len(sections) if sections else 300
        
        print(f"🔄 正在生成 {len(sections)} 个章节...")
        
        article_sections = []
        for i, section_title in enumerate(sections, 1):
            print(f"   生成章节 {i}/{len(sections)}: {section_title}")
            
            content = await self.generate_section(
                section_title=section_title,
                context=f"这是关于'{topic}'的文章，类型为{article_type}",
                word_count=section_word_count
            )
            
            article_sections.append({
                "title": section_title,
                "content": content
            })
        
        # 3. 组装文章
        full_content = self._format_article(
            topic=topic,
            sections=article_sections,
            keywords=keywords
        )
        
        return {
            "topic": topic,
            "type": article_type,
            "outline": outline,
            "sections": article_sections,
            "full_content": full_content,
            "word_count": len(full_content),
            "created_at": datetime.now().isoformat()
        }
    
    def _format_article(
        self,
        topic: str,
        sections: List[Dict[str, str]],
        keywords: Optional[List[str]] = None
    ) -> str:
        """
        格式化文章为Markdown
        
        Args:
            topic: 主题
            sections: 章节列表
            keywords: 关键词
            
        Returns:
            格式化后的文章
        """
        # 标题
        lines = [f"# {topic}\n"]
        
        # 前言（如果有关键词）
        if keywords:
            lines.append(f"**关键词**: {' | '.join(keywords)}\n")
        
        lines.append("---\n")
        
        # 各个章节
        for i, section in enumerate(sections, 1):
            lines.append(f"## {i}. {section['title']}\n")
            lines.append(f"{section['content']}\n")
            lines.append("")  # 空行
        
        # 结尾
        lines.append("---\n")
        lines.append(f"*创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
        
        return "\n".join(lines)
    
    def format_for_zhihu(self, content: str) -> str:
        """
        格式化为知乎Markdown格式
        
        Args:
            content: 原始内容
            
        Returns:
            知乎格式内容
        """
        # 知乎支持的Markdown特性
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            # 标题
            if line.startswith('#'):
                formatted_lines.append(line)
            
            # 列表
            elif line.strip().startswith(('-', '*', '+')):
                formatted_lines.append(line)
            
            # 数字列表
            elif line.strip() and line.strip()[0].isdigit() and '. ' in line:
                formatted_lines.append(line)
            
            # 引用
            elif line.startswith('>'):
                formatted_lines.append(line)
            
            # 代码块
            elif line.startswith('```'):
                formatted_lines.append(line)
            
            # 加粗
            elif '**' in line:
                formatted_lines.append(line)
            
            # 斜体
            elif '*' in line or '_' in line:
                formatted_lines.append(line)
            
            # 普通文本
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def add_call_to_action(self, content: str) -> str:
        """
        添加行动号召（CTA）
        
        Args:
            content: 原始内容
            
        Returns:
            添加CTA后的内容
        """
        cta_options = [
            "\n\n如果这篇文章对你有帮助，欢迎点赞、收藏、关注。",
            "\n\n有任何问题欢迎在评论区讨论，我会及时回复。",
            "\n\n更多干货内容，欢迎关注我的专栏。",
        ]
        
        # 随机选择一个CTA
        import random
        cta = random.choice(cta_options)
        
        return content + cta


# 测试代码
async def test_content_generator():
    """测试内容生成器"""
    print("="*60)
    print("🧪 测试知乎内容生成器")
    print("="*60)
    
    generator = ZhihuContentGenerator()
    
    # 测试1：生成大纲
    print("\n1️⃣ 测试生成大纲")
    outline = await generator.generate_outline(
        topic="Python数据分析入门",
        article_type="指南型",
        keywords=["Pandas", "数据清洗", "可视化"]
    )
    print(f"   主题: {outline['topic']}")
    print(f"   类型: {outline['type']}")
    print(f"   结构:")
    for section in outline['structure']['sections']:
        print(f"      - {section}")
    
    # 测试2：生成单个章节
    print("\n2️⃣ 测试生成章节")
    section_content = await generator.generate_section(
        section_title="准备工作",
        context="这是关于Python数据分析的入门指南",
        word_count=200
    )
    print(f"   章节内容预览: {section_content[:100]}...")
    
    # 测试3：格式化为Markdown
    print("\n3️⃣ 测试Markdown格式化")
    test_content = """
# 标题
## 小标题
- 列表项1
- 列表项2
**加粗文本**
普通文本
"""
    formatted = generator.format_for_zhihu(test_content)
    print("   格式化成功")
    
    # 测试4：添加CTA
    print("\n4️⃣ 测试添加CTA")
    with_cta = generator.add_call_to_action("文章内容")
    print(f"   CTA: {with_cta[5:]}")
    
    print("\n" + "="*60)
    print("✅ 测试完成！")
    print("="*60)
    print("\n💡 提示：要测试完整文章生成，需要较长时间，建议单独测试")


async def test_full_article_generation():
    """测试完整文章生成（耗时较长）"""
    print("="*60)
    print("🧪 测试完整文章生成")
    print("="*60)
    
    generator = ZhihuContentGenerator()
    
    article = await generator.generate_full_article(
        topic="如何高效学习编程？",
        article_type="经验型",
        keywords=["学习方法", "实战项目", "持续进步"],
        word_count=1500
    )
    
    print(f"\n✅ 文章生成完成")
    print(f"   主题: {article['topic']}")
    print(f"   类型: {article['type']}")
    print(f"   字数: {article['word_count']}")
    print(f"   章节数: {len(article['sections'])}")
    
    print(f"\n📄 文章预览（前500字）:")
    print(article['full_content'][:500])
    print("...\n")


if __name__ == "__main__":
    # 基础测试
    asyncio.run(test_content_generator())
    
    # 完整文章生成测试（可选，取消注释运行）
    # asyncio.run(test_full_article_generation())


