"""
Day 24 - GUI 功能自动化测试脚本

测试所有 Tab 界面和核心功能流程
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 测试结果存储
test_results = {
    "基础环境": [],
    "小红书Tab": [],
    "知乎Tab": [],
    "闲鱼Tab": [],
    "B站Tab": [],
    "批量发布Tab": [],
    "设置界面": []
}

def log_test(category: str, test_name: str, passed: bool, details: str = ""):
    """记录测试结果"""
    status = "✅ 通过" if passed else "❌ 失败"
    result = {
        "name": test_name,
        "passed": passed,
        "details": details
    }
    test_results[category].append(result)
    print(f"{status} - {test_name}")
    if details:
        print(f"    详情: {details}")


async def test_environment():
    """测试基础环境"""
    print("\n" + "="*60)
    print("测试环节 1: 基础环境")
    print("="*60)
    
    # 测试1: 检查核心模块导入
    try:
        from core.ai_engine import AIEngine
        from core.database import Database
        log_test("基础环境", "核心模块导入", True, "AIEngine 和 Database 导入成功")
    except Exception as e:
        log_test("基础环境", "核心模块导入", False, str(e))
    
    # 测试2: 检查数据库
    try:
        db = Database()
        await db.connect()
        stats = await db.get_ai_stats_summary()
        ollama_stats = stats.get('ollama', {})
        log_test("基础环境", "数据库连接", True, f"数据库正常，Ollama调用次数: {ollama_stats.get('total_calls', 0)}")
        await db.close()
    except Exception as e:
        log_test("基础环境", "数据库连接", False, str(e))
    
    # 测试3: 检查插件模块
    try:
        from plugins.xiaohongshu.title_generator import XiaohongshuTitleGenerator
        from plugins.zhihu.title_generator import ZhihuTitleGenerator
        from plugins.bilibili.title_generator import BilibiliTitleGenerator
        log_test("基础环境", "插件模块导入", True, "所有插件模块导入成功")
    except Exception as e:
        log_test("基础环境", "插件模块导入", False, str(e))


async def test_xiaohongshu_module():
    """测试小红书模块"""
    print("\n" + "="*60)
    print("测试环节 2: 小红书模块")
    print("="*60)
    
    try:
        from plugins.xiaohongshu.title_generator import XiaohongshuTitleGenerator
        from plugins.xiaohongshu.emoji_optimizer import EmojiOptimizer
        from plugins.xiaohongshu.topic_recommender import TopicTagRecommender
        from core.ai_engine import AIEngine
        
        ai_engine = AIEngine()
        
        # 测试1: 标题生成器初始化
        try:
            title_gen = XiaohongshuTitleGenerator(ai_engine)
            log_test("小红书Tab", "标题生成器初始化", True)
        except Exception as e:
            log_test("小红书Tab", "标题生成器初始化", False, str(e))
            return
        
        # 测试2: 标题生成功能
        try:
            from plugins.xiaohongshu.title_generator import TitleStyle
            titles = await title_gen.generate_multiple_titles(
                topic="秋季穿搭推荐",
                keywords=["穿搭", "秋季", "时尚"],
                count=3,
                style=TitleStyle.ZHONGCAO
            )
            if titles and len(titles) > 0:
                log_test("小红书Tab", "标题生成功能", True, f"生成了 {len(titles)} 个标题")
            else:
                log_test("小红书Tab", "标题生成功能", False, "未生成任何标题")
        except Exception as e:
            log_test("小红书Tab", "标题生成功能", False, str(e))
        
        # 测试3: Emoji优化器
        try:
            emoji_opt = EmojiOptimizer()
            optimized = emoji_opt.optimize_emoji(
                text="这是一个测试标题",
                category="beauty",
                intensity="medium"
            )
            if optimized and optimized != "这是一个测试标题":
                log_test("小红书Tab", "Emoji优化器", True, f"优化后: {optimized}")
            else:
                log_test("小红书Tab", "Emoji优化器", False, "Emoji未添加")
        except Exception as e:
            log_test("小红书Tab", "Emoji优化器", False, str(e))
        
        # 测试4: 话题推荐器
        try:
            topic_rec = TopicTagRecommender(ai_engine)
            tags = await topic_rec.recommend_tags(
                content="分享秋季穿搭心得",
                max_tags=5
            )
            if tags and len(tags) > 0:
                log_test("小红书Tab", "话题推荐器", True, f"推荐了 {len(tags)} 个标签")
            else:
                log_test("小红书Tab", "话题推荐器", False, "未推荐任何标签")
        except Exception as e:
            log_test("小红书Tab", "话题推荐器", False, str(e))
            
    except Exception as e:
        log_test("小红书Tab", "模块加载", False, str(e))


async def test_zhihu_module():
    """测试知乎模块"""
    print("\n" + "="*60)
    print("测试环节 3: 知乎模块")
    print("="*60)
    
    try:
        from plugins.zhihu.title_generator import ZhihuTitleGenerator
        from plugins.zhihu.content_generator import ZhihuContentGenerator
        from plugins.zhihu.seo_optimizer import SEOOptimizer
        from core.ai_engine import AIEngine
        
        ai_engine = AIEngine()
        
        # 测试1: 标题生成器
        try:
            title_gen = ZhihuTitleGenerator(ai_engine)
            result = await title_gen.generate_title(
                topic="Python编程入门指南",
                keywords=["Python", "编程", "入门"],
                style="指南型"
            )
            # 检查返回值类型 - 可能返回dict、str或list
            if isinstance(result, dict) and "title" in result:
                log_test("知乎Tab", "标题生成功能", True, f"标题: {result['title']}")
            elif isinstance(result, str) and result:
                log_test("知乎Tab", "标题生成功能", True, f"标题: {result}")
            elif isinstance(result, list) and len(result) > 0:
                first_title = result[0] if isinstance(result[0], str) else result[0].get('title', '')
                log_test("知乎Tab", "标题生成功能", True, f"生成了{len(result)}个标题，第一个: {first_title}")
            else:
                log_test("知乎Tab", "标题生成功能", False, f"意外的返回值: {result}")
        except Exception as e:
            log_test("知乎Tab", "标题生成功能", False, str(e))
        
        # 测试2: 内容生成器 - 大纲生成
        try:
            content_gen = ZhihuContentGenerator(ai_engine)
            outline = await content_gen.generate_outline(
                topic="Python编程入门指南",
                article_type="指南型",
                keywords=["Python", "编程", "入门"]
            )
            if outline and len(outline) > 0:
                log_test("知乎Tab", "大纲生成功能", True, f"生成了 {len(outline)} 个章节")
            else:
                log_test("知乎Tab", "大纲生成功能", False, "大纲生成失败")
        except Exception as e:
            log_test("知乎Tab", "大纲生成功能", False, str(e))
        
        # 测试3: SEO优化器
        try:
            seo_opt = SEOOptimizer()
            keywords = seo_opt.extract_keywords("Python是一门流行的编程语言，适合初学者学习")
            if keywords and len(keywords) > 0:
                log_test("知乎Tab", "SEO关键词提取", True, f"提取了 {len(keywords)} 个关键词")
            else:
                log_test("知乎Tab", "SEO关键词提取", False, "未提取到关键词")
        except Exception as e:
            log_test("知乎Tab", "SEO关键词提取", False, str(e))
            
    except Exception as e:
        log_test("知乎Tab", "模块加载", False, str(e))


async def test_bilibili_module():
    """测试B站模块"""
    print("\n" + "="*60)
    print("测试环节 4: B站模块")
    print("="*60)
    
    try:
        from plugins.bilibili.title_generator import BilibiliTitleGenerator
        from plugins.bilibili.tag_recommender import BilibiliTagRecommender
        from core.ai_engine import AIEngine
        
        ai_engine = AIEngine()
        
        # 测试1: 标题生成器
        try:
            title_gen = BilibiliTitleGenerator(ai_engine)
            results = await title_gen.generate_titles(
                topic="游戏实况",
                keywords=["游戏", "攻略"],
                style="悬念型",
                zone="游戏"
            )
            if results and len(results) > 0:
                log_test("B站Tab", "标题生成功能", True, f"生成了 {len(results)} 个标题")
            else:
                log_test("B站Tab", "标题生成功能", False, "标题生成失败")
        except Exception as e:
            log_test("B站Tab", "标题生成功能", False, str(e))
        
        # 测试2: 标签推荐器
        try:
            tag_rec = BilibiliTagRecommender(ai_engine)
            tags = await tag_rec.recommend_tags(
                title="游戏攻略视频",
                content="这是一个游戏攻略视频",
                zone="游戏",
                count=5
            )
            if tags and len(tags) > 0:
                log_test("B站Tab", "标签推荐功能", True, f"推荐了 {len(tags)} 个标签")
            else:
                log_test("B站Tab", "标签推荐功能", False, "未推荐任何标签")
        except Exception as e:
            log_test("B站Tab", "标签推荐功能", False, str(e))
            
    except Exception as e:
        log_test("B站Tab", "模块加载", False, str(e))


async def test_batch_publisher():
    """测试批量发布系统"""
    print("\n" + "="*60)
    print("测试环节 5: 批量发布系统")
    print("="*60)
    
    try:
        from plugins.batch_publisher.task_manager import BatchPublishManager
        from core.publisher import PublishContent
        
        # 测试1: 任务管理器初始化
        try:
            manager = BatchPublishManager()
            log_test("批量发布Tab", "任务管理器初始化", True)
        except Exception as e:
            log_test("批量发布Tab", "任务管理器初始化", False, str(e))
            return
        
        # 测试2: 内容模型创建
        try:
            content = PublishContent(
                title="测试标题",
                content="测试内容",
                description="测试描述",
                tags=["测试", "自动化"]
            )
            log_test("批量发布Tab", "内容模型创建", True)
        except Exception as e:
            log_test("批量发布Tab", "内容模型创建", False, str(e))
            
    except Exception as e:
        log_test("批量发布Tab", "模块加载", False, str(e))


async def test_settings():
    """测试设置功能"""
    print("\n" + "="*60)
    print("测试环节 6: 设置功能")
    print("="*60)
    
    try:
        from core.ai_engine import AIEngine
        
        # 测试1: AI引擎初始化
        try:
            ai_engine = AIEngine()
            log_test("设置界面", "AI引擎初始化", True)
        except Exception as e:
            log_test("设置界面", "AI引擎初始化", False, str(e))
            return
        
        # 测试2: 配置文件读取
        try:
            import json
            config_path = project_root / "config" / "settings.json"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                log_test("设置界面", "配置文件读取", True, f"配置项数量: {len(config)}")
            else:
                log_test("设置界面", "配置文件读取", False, "配置文件不存在")
        except Exception as e:
            log_test("设置界面", "配置文件读取", False, str(e))
            
    except Exception as e:
        log_test("设置界面", "模块加载", False, str(e))


def generate_report():
    """生成测试报告"""
    print("\n" + "="*60)
    print("测试报告汇总")
    print("="*60)
    
    total_tests = 0
    passed_tests = 0
    
    report_lines = ["# Day 24 GUI 功能测试报告\n"]
    report_lines.append(f"**测试时间**: {asyncio.get_event_loop().time()}\n")
    report_lines.append(f"**测试版本**: v1.17.1\n\n")
    
    for category, tests in test_results.items():
        if not tests:
            continue
            
        category_passed = sum(1 for t in tests if t['passed'])
        category_total = len(tests)
        total_tests += category_total
        passed_tests += category_passed
        
        pass_rate = (category_passed / category_total * 100) if category_total > 0 else 0
        
        print(f"\n{category}: {category_passed}/{category_total} 通过 ({pass_rate:.1f}%)")
        report_lines.append(f"## {category}\n\n")
        report_lines.append(f"**通过率**: {category_passed}/{category_total} ({pass_rate:.1f}%)\n\n")
        
        for test in tests:
            status = "✅" if test['passed'] else "❌"
            print(f"  {status} {test['name']}")
            report_lines.append(f"- {status} **{test['name']}**\n")
            if test['details']:
                print(f"      {test['details']}")
                report_lines.append(f"  - {test['details']}\n")
        report_lines.append("\n")
    
    overall_pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"\n{'='*60}")
    print(f"总计: {passed_tests}/{total_tests} 通过 ({overall_pass_rate:.1f}%)")
    print(f"{'='*60}\n")
    
    report_lines.insert(3, f"**总体通过率**: {passed_tests}/{total_tests} ({overall_pass_rate:.1f}%)\n\n")
    report_lines.append("---\n\n")
    
    # 添加结论
    if overall_pass_rate >= 90:
        conclusion = "✅ **测试通过！** GUI 功能正常，可以进入发布准备阶段。"
    elif overall_pass_rate >= 75:
        conclusion = "⚠️ **基本通过，但有部分问题需要修复。** 建议先修复失败的测试项。"
    else:
        conclusion = "❌ **测试未通过。** 存在较多问题，需要进行修复后重新测试。"
    
    report_lines.append(f"## 测试结论\n\n{conclusion}\n\n")
    
    # 保存报告
    report_path = project_root / "Day24_GUI测试报告.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.writelines(report_lines)
    
    print(f"测试报告已保存到: {report_path}")
    
    return overall_pass_rate


async def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("🚀 JieDimension Toolkit - Day 24 GUI 功能测试")
    print("="*60)
    print(f"版本: v1.17.1")
    print(f"测试类型: 功能模块测试")
    print("="*60)
    
    try:
        # 运行所有测试
        await test_environment()
        await test_xiaohongshu_module()
        await test_zhihu_module()
        await test_bilibili_module()
        await test_batch_publisher()
        await test_settings()
        
        # 生成报告
        pass_rate = generate_report()
        
        # 返回测试结果
        return pass_rate >= 75
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

