"""测试爆款分析功能"""
import asyncio
from plugins.video_producer.viral_analyzer import ViralAnalyzer
from core.ai_engine import AIEngine

async def main():
    print("="*60)
    print("🔍 测试爆款分析")
    print("="*60)
    
    ai_engine = AIEngine()
    analyzer = ViralAnalyzer(ai_engine)
    
    # 测试标题（B站实际热门标题）
    test_title = "看到战绩的超能力 大合集"
    metadata = {'play': 6555126, 'like': 279928}
    
    print(f"\n📝 分析标题: {test_title}")
    print(f"数据: {metadata['play']:,}播放 | {metadata['like']:,}点赞\n")
    
    result = await analyzer.analyze_title(test_title, metadata)
    
    print(f"关键词: {result.get('keywords')}")
    print(f"吸引点: {result.get('hooks')}")
    print(f"结构: {result.get('structure')}")
    print(f"评分: {result.get('score')}/100")
    print(f"建议: {result.get('suggestions')}")
    
    if result.get('ai_insights'):
        print(f"\n🤖 AI深度分析:")
        print(result.get('ai_insights'))
    
    print("\n" + "="*60)
    print("✅ 测试完成")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())

