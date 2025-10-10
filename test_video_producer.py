"""
测试视频生产插件功能
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from plugins.video_producer.content_scraper import ContentScraper
from plugins.video_producer.viral_analyzer import ViralAnalyzer
from plugins.video_producer.ai_analyzer import AIContentAnalyzer
from core.ai_engine import AIEngine


async def test_content_scraper():
    """测试内容抓取"""
    print("=" * 60)
    print("🧪 测试内容抓取")
    print("=" * 60)
    
    scraper = ContentScraper()
    
    # 测试知乎热榜
    print("\n📝 抓取知乎热榜...")
    zhihu_articles = await scraper.scrape_zhihu_hot(limit=3)
    
    if zhihu_articles:
        print(f"✅ 成功抓取{len(zhihu_articles)}条")
        for i, article in enumerate(zhihu_articles, 1):
            print(f"\n{i}. {article.get('title')}")
            print(f"   热度: {article.get('热度')}")
    else:
        print("❌ 抓取失败")
    
    # 测试B站热门
    print("\n🎬 抓取B站热门...")
    bilibili_videos = await scraper.scrape_bilibili_hot(limit=3)
    
    if bilibili_videos:
        print(f"✅ 成功抓取{len(bilibili_videos)}条")
        for i, video in enumerate(bilibili_videos, 1):
            print(f"\n{i}. {video.get('title')}")
            print(f"   播放: {video.get('play'):,} | 点赞: {video.get('like'):,}")
    else:
        print("❌ 抓取失败")


async def test_viral_analyzer():
    """测试爆款分析"""
    print("\n" + "=" * 60)
    print("🧪 测试爆款分析")
    print("=" * 60)
    
    ai_engine = AIEngine()
    analyzer = ViralAnalyzer(ai_engine)
    
    # 测试标题分析
    test_title = "震惊！这个方法让我7天涨粉10万，太牛了"
    
    print(f"\n📝 分析标题: {test_title}")
    result = await analyzer.analyze_title(test_title, {'play': 100000, 'like': 5000})
    
    print(f"\n关键词: {result.get('keywords')}")
    print(f"Hook: {result.get('hooks')}")
    print(f"结构: {result.get('structure')}")
    print(f"评分: {result.get('score')}/100")
    print(f"建议: {result.get('suggestions')}")
    
    if result.get('ai_insights'):
        print(f"\n🤖 AI分析:\n{result.get('ai_insights')}")


async def test_ai_analyzer():
    """测试AI内容分析"""
    print("\n" + "=" * 60)
    print("🧪 测试AI内容分析")
    print("=" * 60)
    
    ai_engine = AIEngine()
    analyzer = AIContentAnalyzer(ai_engine)
    
    # 测试文章
    test_content = """
    人工智能正在改变我们的生活方式。从智能手机到自动驾驶，
    AI技术已经渗透到各个领域。特别是最近ChatGPT的爆火，
    让更多人认识到AI的强大能力。那么普通人如何利用AI提升效率？
    本文将分享5个实用技巧。
    """
    
    print("\n📝 提取核心要点...")
    points = await analyzer.extract_key_points(test_content, num_points=3)
    
    if points:
        print(f"✅ 提取{len(points)}个要点:")
        for i, point in enumerate(points, 1):
            print(f"{i}. {point}")
    
    # 生成视频脚本
    if points:
        print("\n🎬 生成视频脚本...")
        script = await analyzer.generate_video_script(points, style="解说")
        
        if script:
            print(f"\n脚本（{len(script.get('full_script', ''))}字）:")
            print(script.get('full_script'))
            print(f"\n分为{len(script.get('segments', []))}个片段")


async def main():
    """主测试函数"""
    print("\n🎬 视频生产插件 - 功能测试")
    print("=" * 60)
    
    try:
        # 测试1: 内容抓取
        await test_content_scraper()
        
        # 测试2: 爆款分析
        await test_viral_analyzer()
        
        # 测试3: AI分析
        await test_ai_analyzer()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

