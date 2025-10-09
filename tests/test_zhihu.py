"""
知乎插件测试套件
测试标题生成、SEO优化、内容生成等功能
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.zhihu.title_generator import ZhihuTitleGenerator
from plugins.zhihu.seo_optimizer import SEOOptimizer
from plugins.zhihu.content_generator import ZhihuContentGenerator


class TestZhihuPlugin:
    """知乎插件测试类"""
    
    def __init__(self):
        self.title_generator = None
        self.seo_optimizer = SEOOptimizer()
        self.content_generator = None
        self.test_results = []
    
    async def test_title_generation(self):
        """测试标题生成"""
        print("\n" + "="*60)
        print("🧪 测试1: 知乎标题生成")
        print("="*60)
        
        try:
            # 初始化
            if not self.title_generator:
                from core.ai_engine import AIEngine
                self.title_generator = ZhihuTitleGenerator(ai_engine=AIEngine())
            
            # 测试模板生成
            print("\n1.1 测试模板生成（快速）")
            titles_template = await self.title_generator.generate_title(
                topic="Python数据分析",
                keywords=["Pandas", "NumPy", "可视化"],
                style="问答型",
                use_ai=False,
                count=5
            )
            
            print(f"   生成了 {len(titles_template)} 个标题：")
            for i, title in enumerate(titles_template, 1):
                print(f"   {i}. {title}")
                # 质量分析
                analysis = self.title_generator.analyze_title_quality(title)
                print(f"      评分: {analysis['score']}/100 ({analysis['level']})")
            
            # 测试AI生成
            print("\n1.2 测试AI生成（高质量）")
            titles_ai = await self.title_generator.generate_title(
                topic="人工智能",
                keywords=["机器学习", "深度学习"],
                style="分析型",
                use_ai=True,
                count=3
            )
            
            print(f"   生成了 {len(titles_ai)} 个标题：")
            for i, title in enumerate(titles_ai, 1):
                print(f"   {i}. {title}")
            
            # 测试SEO优化
            print("\n1.3 测试标题SEO优化")
            original = "学习编程的方法"
            optimized = self.title_generator.optimize_title_seo(
                original,
                ["Python", "编程", "学习"]
            )
            print(f"   原标题: {original}")
            print(f"   优化后: {optimized}")
            
            self.test_results.append(("标题生成", True, ""))
            print("\n✅ 测试1通过")
            
        except Exception as e:
            self.test_results.append(("标题生成", False, str(e)))
            print(f"\n❌ 测试1失败: {e}")
    
    def test_seo_optimizer(self):
        """测试SEO优化器"""
        print("\n" + "="*60)
        print("🧪 测试2: SEO优化器")
        print("="*60)
        
        try:
            test_content = """
            Python是一门强大的编程语言。它在数据科学、人工智能、Web开发等领域广泛应用。
            学习Python需要掌握基础语法、数据结构、面向对象编程。
            本文介绍Python学习的完整路径。
            我们从环境搭建开始，深入到实战项目开发。
            """
            
            # 测试关键词提取
            print("\n2.1 测试关键词提取")
            keywords = self.seo_optimizer.extract_keywords(test_content, top_k=5)
            print("   提取的关键词：")
            for kw in keywords:
                print(f"   - {kw['word']}: 权重 {kw['weight']}, 出现 {kw['count']} 次")
            
            # 测试关键词布局优化
            print("\n2.2 测试关键词布局优化")
            title = "编程语言学习指南"
            optimized = self.seo_optimizer.optimize_keywords_layout(
                title,
                ["Python", "入门", "实战"]
            )
            print(f"   原标题: {title}")
            print(f"   优化后: {optimized}")
            
            # 测试长尾关键词生成
            print("\n2.3 测试长尾关键词生成")
            long_tail = self.seo_optimizer.generate_long_tail_keywords(
                "Python",
                ["学习", "教程"]
            )
            print("   生成的长尾关键词（前5个）：")
            for i, kw in enumerate(long_tail[:5], 1):
                print(f"   {i}. {kw}")
            
            # 测试元描述生成
            print("\n2.4 测试元描述生成")
            meta_desc = self.seo_optimizer.generate_meta_description(
                test_content,
                keywords=["Python", "学习"]
            )
            print(f"   元描述: {meta_desc}")
            
            # 测试关键词密度分析
            print("\n2.5 测试关键词密度分析")
            density = self.seo_optimizer.analyze_keyword_density(
                test_content,
                ["Python", "学习", "编程"]
            )
            for word, data in density.items():
                print(f"   - {word}: {data['density']}% ({data['status']})")
            
            # 测试可读性检查
            print("\n2.6 测试可读性检查")
            readability = self.seo_optimizer.check_readability(test_content)
            print(f"   评分: {readability['score']}/100 ({readability['level']})")
            print(f"   总字数: {readability['total_chars']}")
            print(f"   平均句长: {readability['avg_sentence_length']}字")
            
            self.test_results.append(("SEO优化", True, ""))
            print("\n✅ 测试2通过")
            
        except Exception as e:
            self.test_results.append(("SEO优化", False, str(e)))
            print(f"\n❌ 测试2失败: {e}")
    
    async def test_content_generation(self):
        """测试内容生成"""
        print("\n" + "="*60)
        print("🧪 测试3: 内容生成器")
        print("="*60)
        
        try:
            # 初始化
            if not self.content_generator:
                from core.ai_engine import AIEngine
                self.content_generator = ZhihuContentGenerator(ai_engine=AIEngine())
            
            # 测试大纲生成
            print("\n3.1 测试大纲生成")
            outline = await self.content_generator.generate_outline(
                topic="Python数据分析入门",
                article_type="指南型",
                keywords=["Pandas", "数据清洗"]
            )
            
            print(f"   主题: {outline['topic']}")
            print(f"   类型: {outline['type']}")
            print("   结构:")
            for section in outline['structure']['sections']:
                print(f"      - {section}")
            
            # 测试章节生成
            print("\n3.2 测试章节生成")
            section_content = await self.content_generator.generate_section(
                section_title="准备工作",
                context="这是关于Python数据分析的入门指南",
                word_count=150
            )
            print(f"   生成的章节内容（前100字）: {section_content[:100]}...")
            
            # 测试Markdown格式化
            print("\n3.3 测试Markdown格式化")
            test_md = "# 标题\n## 小标题\n- 列表项\n**加粗**\n普通文本"
            formatted = self.content_generator.format_for_zhihu(test_md)
            print("   格式化成功")
            
            self.test_results.append(("内容生成", True, ""))
            print("\n✅ 测试3通过")
            
        except Exception as e:
            self.test_results.append(("内容生成", False, str(e)))
            print(f"\n❌ 测试3失败: {e}")
    
    async def test_integration(self):
        """测试集成流程"""
        print("\n" + "="*60)
        print("🧪 测试4: 集成流程测试")
        print("="*60)
        
        try:
            print("\n4.1 完整工作流测试")
            
            # 1. 生成标题
            print("   步骤1: 生成标题...")
            if not self.title_generator:
                from core.ai_engine import AIEngine
                self.title_generator = ZhihuTitleGenerator(ai_engine=AIEngine())
            
            titles = await self.title_generator.generate_title(
                topic="如何提高工作效率",
                keywords=["时间管理", "工具"],
                style="问答型",
                use_ai=False,
                count=3
            )
            print(f"   ✓ 生成了 {len(titles)} 个标题")
            
            # 2. SEO优化标题
            print("   步骤2: SEO优化...")
            optimized_title = self.seo_optimizer.optimize_keywords_layout(
                titles[0] if titles else "提高效率的方法",
                ["效率", "工作"]
            )
            print(f"   ✓ 优化后标题: {optimized_title}")
            
            # 3. 生成大纲
            print("   步骤3: 生成大纲...")
            if not self.content_generator:
                from core.ai_engine import AIEngine
                self.content_generator = ZhihuContentGenerator(ai_engine=AIEngine())
            
            outline = await self.content_generator.generate_outline(
                topic="如何提高工作效率",
                article_type="问答型",
                keywords=["时间管理"]
            )
            print(f"   ✓ 生成了 {len(outline['structure']['sections'])} 个章节")
            
            self.test_results.append(("集成流程", True, ""))
            print("\n✅ 测试4通过")
            
        except Exception as e:
            self.test_results.append(("集成流程", False, str(e)))
            print(f"\n❌ 测试4失败: {e}")
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "="*60)
        print("📊 测试总结")
        print("="*60)
        
        total = len(self.test_results)
        passed = sum(1 for _, success, _ in self.test_results if success)
        failed = total - passed
        
        print(f"\n总计: {total} 个测试")
        print(f"通过: {passed} ✅")
        print(f"失败: {failed} ❌")
        print(f"成功率: {passed/total*100:.1f}%")
        
        if failed > 0:
            print("\n失败的测试:")
            for name, success, error in self.test_results:
                if not success:
                    print(f"  ❌ {name}: {error}")
        
        print("\n" + "="*60)
        if failed == 0:
            print("🎉 所有测试通过！知乎插件工作正常！")
        else:
            print("⚠️ 有测试失败，请检查上述错误")
        print("="*60)


async def run_all_tests():
    """运行所有测试"""
    print("="*60)
    print("🚀 JieDimension Toolkit - 知乎插件测试套件")
    print("="*60)
    print("测试环境: Python 3.11+")
    print("测试时间:", __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    tester = TestZhihuPlugin()
    
    # 运行测试
    await tester.test_title_generation()
    tester.test_seo_optimizer()
    await tester.test_content_generation()
    await tester.test_integration()
    
    # 打印总结
    tester.print_summary()


if __name__ == "__main__":
    asyncio.run(run_all_tests())


