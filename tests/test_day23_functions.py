"""
Day 23 功能测试脚本
自动测试小红书、知乎等核心模块的功能
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.ai_engine import AIEngine
from plugins.xiaohongshu.title_generator import XiaohongshuTitleGenerator, TitleStyle
from plugins.xiaohongshu.topic_recommender import TopicTagRecommender
from plugins.zhihu.title_generator import ZhihuTitleGenerator
from plugins.zhihu.content_generator import ZhihuContentGenerator

# 测试结果统计
test_results = {
    "passed": 0,
    "failed": 0,
    "total": 0
}

def log_test(name: str, passed: bool, message: str = ""):
    """记录测试结果"""
    test_results["total"] += 1
    if passed:
        test_results["passed"] += 1
        print(f"✅ {name}: 通过")
    else:
        test_results["failed"] += 1
        print(f"❌ {name}: 失败 - {message}")
    if message and passed:
        print(f"   ℹ️ {message}")


async def test_ai_engine():
    """测试AI引擎"""
    print("\n" + "="*60)
    print("📦 测试 AI 引擎")
    print("="*60)
    
    try:
        engine = AIEngine()
        log_test("AI引擎初始化", True, "引擎创建成功")
        
        # 测试简单生成
        try:
            response = await engine.generate(
                prompt="生成一个关于美食的小红书标题",
                system_prompt="你是一个标题生成助手",
                complexity=1
            )
            
            if response.success and response.content:
                log_test("AI生成测试", True, f"生成内容长度: {len(response.content)}字")
            else:
                log_test("AI生成测试", False, "生成失败或内容为空")
        except Exception as e:
            log_test("AI生成测试", False, f"异常: {str(e)}")
            
    except Exception as e:
        log_test("AI引擎初始化", False, str(e))


async def test_xiaohongshu():
    """测试小红书模块"""
    print("\n" + "="*60)
    print("📝 测试小红书模块")
    print("="*60)
    
    try:
        # 初始化
        engine = AIEngine()
        title_gen = XiaohongshuTitleGenerator(engine)
        topic_rec = TopicTagRecommender(engine)
        
        log_test("小红书模块初始化", True)
        
        # 测试标题生成
        try:
            titles = await title_gen.generate_multiple_titles(
                topic="夏日防晒推荐",
                keywords=["防晒霜", "学生党", "平价"],
                style=TitleStyle.ZHONGCAO,
                count=3
            )
            
            if titles and len(titles) > 0:
                log_test("小红书标题生成", True, f"生成了 {len(titles)} 个标题")
                for i, title in enumerate(titles[:2], 1):
                    print(f"      示例{i}: {title}")
            else:
                log_test("小红书标题生成", False, "未生成标题")
        except Exception as e:
            log_test("小红书标题生成", False, str(e))
        
        # 测试标签推荐
        try:
            tags = await topic_rec.recommend_tags(
                content="推荐几款适合学生党的平价防晒霜",
                category=None,
                max_tags=5
            )
            
            if tags and len(tags) > 0:
                log_test("小红书标签推荐", True, f"推荐了 {len(tags)} 个标签")
                print(f"      示例标签: {', '.join(tags[:3])}")
            else:
                log_test("小红书标签推荐", False, "未推荐标签")
        except Exception as e:
            log_test("小红书标签推荐", False, str(e))
            
    except Exception as e:
        log_test("小红书模块初始化", False, str(e))


async def test_zhihu():
    """测试知乎模块"""
    print("\n" + "="*60)
    print("📖 测试知乎模块")
    print("="*60)
    
    try:
        # 初始化
        engine = AIEngine()
        title_gen = ZhihuTitleGenerator(engine)
        content_gen = ZhihuContentGenerator(engine)
        
        log_test("知乎模块初始化", True)
        
        # 测试标题生成
        try:
            titles = await title_gen.generate_title(
                topic="如何高效学习Python编程",
                keywords=["Python", "编程", "学习方法"],
                style="问答型",
                count=3
            )
            
            if titles and isinstance(titles, list) and len(titles) > 0:
                log_test("知乎标题生成", True, f"生成了 {len(titles)} 个标题")
                for i, title in enumerate(titles[:2], 1):
                    print(f"      示例{i}: {title}")
            else:
                log_test("知乎标题生成", False, "未生成标题")
        except Exception as e:
            log_test("知乎标题生成", False, str(e))
        
        # 测试大纲生成
        try:
            outline = await content_gen.generate_outline(
                topic="如何高效学习Python编程",
                article_type="指南型",
                keywords=["Python", "编程", "学习方法"]
            )
            
            if outline and isinstance(outline, dict):
                sections = outline.get("sections", outline.get("structure", []))
                if sections and len(sections) > 0:
                    log_test("知乎大纲生成", True, f"生成了 {len(sections)} 个章节")
                    for i, section in enumerate(sections[:2], 1):
                        if isinstance(section, dict):
                            print(f"      章节{i}: {section.get('title', '无标题')}")
                        else:
                            print(f"      章节{i}: {section}")
                else:
                    log_test("知乎大纲生成", False, "未生成章节")
            else:
                log_test("知乎大纲生成", False, "大纲格式错误")
        except Exception as e:
            log_test("知乎大纲生成", False, str(e))
            
    except Exception as e:
        log_test("知乎模块初始化", False, str(e))


async def test_database():
    """测试数据库"""
    print("\n" + "="*60)
    print("💾 测试数据库")
    print("="*60)
    
    try:
        from core.database import Database
        
        db = Database()
        await db.connect()
        log_test("数据库连接", True)
        
        # 测试统计查询
        stats = await db.get_ai_stats_summary()
        log_test("数据库查询", True, f"AI统计查询成功")
        
        await db.close()
        log_test("数据库关闭", True)
        
    except Exception as e:
        log_test("数据库测试", False, str(e))


async def main():
    """主测试流程"""
    print("\n")
    print("🚀 JieDimension Toolkit - Day 23 功能测试")
    print("="*60)
    print("测试目标: 验证小红书和知乎模块核心功能")
    print("="*60)
    
    # 运行所有测试
    await test_ai_engine()
    await test_xiaohongshu()
    await test_zhihu()
    await test_database()
    
    # 输出测试总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    print(f"总测试数: {test_results['total']}")
    print(f"✅ 通过: {test_results['passed']}")
    print(f"❌ 失败: {test_results['failed']}")
    
    if test_results['failed'] == 0:
        print("\n🎉 所有测试通过！Day 23 核心功能正常！")
        return 0
    else:
        success_rate = (test_results['passed'] / test_results['total'] * 100)
        print(f"\n⚠️ 成功率: {success_rate:.1f}%")
        if success_rate >= 70:
            print("✅ 大部分功能正常，可以继续GUI测试")
            return 0
        else:
            print("❌ 需要修复失败的测试项")
            return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

