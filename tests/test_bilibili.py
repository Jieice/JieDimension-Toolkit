"""
B站插件测试套件

测试功能：
- 标题生成器
- 动态生成器
- 标签推荐器
- 分区优化器
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.bilibili.title_generator import BilibiliTitleGenerator
from plugins.bilibili.dynamic_generator import BilibiliDynamicGenerator
from plugins.bilibili.tag_recommender import BilibiliTagRecommender
from plugins.bilibili.zone_optimizer import BilibiliZoneOptimizer


class TestBilibiliPlugin:
    """B站插件测试类"""
    
    def __init__(self):
        self.title_gen = BilibiliTitleGenerator()
        self.dynamic_gen = BilibiliDynamicGenerator()
        self.tag_recommender = BilibiliTagRecommender()
        self.zone_optimizer = BilibiliZoneOptimizer()
        
        self.passed = 0
        self.failed = 0
    
    async def test_title_generator(self):
        """测试标题生成器"""
        
        print("\n" + "="*60)
        print("【测试1：标题生成器】")
        print("="*60)
        
        try:
            # 测试1.1: 悬念型标题
            print("\n1.1 悬念型标题生成")
            titles = await self.title_gen.generate_titles(
                topic="原神5.0新版本攻略",
                keywords=["原神", "攻略", "新版本"],
                style="悬念型",
                zone="游戏",
                count=3,
                use_ai=False  # 不使用AI，快速测试
            )
            
            assert len(titles) > 0, "应该生成至少1个标题"
            assert all('title' in t and 'score' in t for t in titles), "标题应包含title和score字段"
            
            print(f"✅ 生成了{len(titles)}个标题")
            for i, t in enumerate(titles[:2], 1):
                print(f"   {i}. {t['title']} (评分: {t['score']})")
            
            # 测试1.2: 教程型标题
            print("\n1.2 教程型标题生成")
            titles = await self.title_gen.generate_titles(
                topic="Python编程教程",
                keywords=["Python", "编程", "教程"],
                style="教程型",
                zone="知识",
                count=3,
                use_ai=False
            )
            
            assert len(titles) > 0, "应该生成至少1个标题"
            print(f"✅ 生成了{len(titles)}个教程型标题")
            
            # 测试1.3: 测评型标题
            print("\n1.3 测评型标题生成")
            titles = await self.title_gen.generate_titles(
                topic="iPhone 16 Pro评测",
                keywords=["iPhone", "评测", "手机"],
                style="测评型",
                zone="科技",
                count=3,
                use_ai=False
            )
            
            assert len(titles) > 0, "应该生成至少1个标题"
            print(f"✅ 生成了{len(titles)}个测评型标题")
            
            self.passed += 1
            print("\n✅ 标题生成器测试通过")
            
        except Exception as e:
            self.failed += 1
            print(f"\n❌ 标题生成器测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    async def test_dynamic_generator(self):
        """测试动态生成器"""
        
        print("\n" + "="*60)
        print("【测试2：动态生成器】")
        print("="*60)
        
        try:
            # 测试2.1: 短动态生成
            print("\n2.1 短动态生成")
            dynamic = await self.dynamic_gen.generate_short_dynamic(
                video_title="Python入门教程完整版",
                highlights=[
                    "零基础也能学会",
                    "配套练习项目",
                    "100+知识点覆盖"
                ],
                hashtags=["Python", "编程教程", "干货"]
            )
            
            assert dynamic, "应该生成动态文案"
            assert len(dynamic) <= 233, f"动态长度应不超过233字，当前{len(dynamic)}字"
            
            print(f"✅ 生成动态: {len(dynamic)}字")
            print(f"   预览: {dynamic[:50]}...")
            
            # 测试2.2: 视频简介生成
            print("\n2.2 视频简介生成")
            description = await self.dynamic_gen.generate_video_description(
                video_info={
                    "title": "原神攻略",
                    "summary": "新版本全面解析",
                    "highlights": ["新角色分析", "新地图探索"]
                },
                chapters=[
                    {"time": "00:00", "title": "开场"},
                    {"time": "05:00", "title": "新角色"}
                ]
            )
            
            assert description, "应该生成视频简介"
            assert "章节时间轴" in description, "简介应包含章节信息"
            
            print(f"✅ 生成视频简介: {len(description)}字")
            
            # 测试2.3: 互动动态
            print("\n2.3 互动动态生成")
            interaction = await self.dynamic_gen.generate_interaction_dynamic(
                question="你喜欢哪种视频风格",
                options=["教程型", "实战型", "理论型"]
            )
            
            assert interaction, "应该生成互动动态"
            assert "?" in interaction or "？" in interaction, "互动动态应包含问号"
            
            print(f"✅ 生成互动动态")
            
            self.passed += 1
            print("\n✅ 动态生成器测试通过")
            
        except Exception as e:
            self.failed += 1
            print(f"\n❌ 动态生成器测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    async def test_tag_recommender(self):
        """测试标签推荐器"""
        
        print("\n" + "="*60)
        print("【测试3：标签推荐器】")
        print("="*60)
        
        try:
            # 测试3.1: 标签推荐
            print("\n3.1 标签推荐")
            tags = await self.tag_recommender.recommend_tags(
                title="原神5.0新版本攻略",
                content="详细介绍新角色、新地图、新活动",
                zone="游戏",
                count=10,
                use_ai=False
            )
            
            assert len(tags) > 0, "应该推荐至少1个标签"
            assert all('tag' in t for t in tags), "每个标签应有tag字段"
            
            print(f"✅ 推荐了{len(tags)}个标签")
            for i, t in enumerate(tags[:5], 1):
                print(f"   {i}. {t['tag']} (热度:{t.get('hot_score', 0)})")
            
            # 测试3.2: 关键词建议
            print("\n3.2 关键词标签建议")
            suggestions = self.tag_recommender.get_tag_suggestions_by_keyword(
                keyword="编程",
                zone="知识"
            )
            
            assert isinstance(suggestions, list), "应该返回列表"
            print(f"✅ 找到{len(suggestions)}个相关标签")
            if suggestions:
                print(f"   示例: {', '.join(suggestions[:3])}")
            
            self.passed += 1
            print("\n✅ 标签推荐器测试通过")
            
        except Exception as e:
            self.failed += 1
            print(f"\n❌ 标签推荐器测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    def test_zone_optimizer(self):
        """测试分区优化器"""
        
        print("\n" + "="*60)
        print("【测试4：分区优化器】")
        print("="*60)
        
        try:
            # 测试4.1: 获取分区信息
            print("\n4.1 获取分区信息")
            zone_info = self.zone_optimizer.get_zone_info("游戏")
            
            assert zone_info, "应该返回分区信息"
            assert "description" in zone_info, "应包含description字段"
            assert "keywords" in zone_info, "应包含keywords字段"
            
            print(f"✅ 获取游戏区信息")
            print(f"   描述: {zone_info['description']}")
            
            # 测试4.2: 推荐分区
            print("\n4.2 推荐分区")
            suggestions = self.zone_optimizer.suggest_zone(
                title="Python编程教程",
                content="详细讲解Python基础知识和实战项目"
            )
            
            assert len(suggestions) > 0, "应该推荐至少1个分区"
            assert all('zone' in s and 'score' in s for s in suggestions), "推荐应包含zone和score"
            
            print(f"✅ 推荐了{len(suggestions)}个分区")
            for i, s in enumerate(suggestions[:3], 1):
                print(f"   {i}. {s['zone']}: {s['score']}分")
            
            # 测试4.3: 分区优化建议
            print("\n4.3 分区优化建议")
            result = self.zone_optimizer.optimize_for_zone(
                content={
                    "title": "游戏测试",
                    "description": "简单测试",
                    "tags": []
                },
                zone="游戏"
            )
            
            assert "score" in result, "应包含score字段"
            assert "suggestions" in result, "应包含suggestions字段"
            
            print(f"✅ 匹配度评分: {result['score']}分")
            if result['suggestions']:
                print(f"   优化建议: {len(result['suggestions'])}条")
            
            # 测试4.4: 风格建议
            print("\n4.4 风格建议")
            style = self.zone_optimizer.get_style_suggestions("科技")
            
            assert "title_style" in style, "应包含标题风格"
            assert "content_features" in style, "应包含内容特点"
            
            print(f"✅ 科技区风格: {style['title_style']}")
            
            self.passed += 1
            print("\n✅ 分区优化器测试通过")
            
        except Exception as e:
            self.failed += 1
            print(f"\n❌ 分区优化器测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    async def run_all_tests(self):
        """运行所有测试"""
        
        print("\n" + "="*60)
        print("🧪 B站插件完整测试套件")
        print("="*60)
        
        # 运行所有测试
        await self.test_title_generator()
        await self.test_dynamic_generator()
        await self.test_tag_recommender()
        self.test_zone_optimizer()  # 同步测试
        
        # 测试总结
        print("\n" + "="*60)
        print("📊 测试总结")
        print("="*60)
        print(f"✅ 通过: {self.passed}")
        print(f"❌ 失败: {self.failed}")
        print(f"总计: {self.passed + self.failed}")
        
        if self.failed == 0:
            print("\n🎉 所有测试通过！B站插件工作正常！")
            return True
        else:
            print(f"\n⚠️ 有 {self.failed} 个测试失败，请检查！")
            return False


async def main():
    """主测试函数"""
    tester = TestBilibiliPlugin()
    success = await tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

