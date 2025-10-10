"""测试AI脚本生成"""
import asyncio
from plugins.video_producer.ai_analyzer import AIContentAnalyzer
from core.ai_engine import AIEngine

async def main():
    print("="*60)
    print("🎬 测试AI脚本生成")
    print("="*60)
    
    ai_engine = AIEngine()
    analyzer = AIContentAnalyzer(ai_engine)
    
    # 测试文章
    test_content = """
    今天分享一个超级实用的技巧！很多人都不知道，
    其实手机有个隐藏功能，可以让电池续航提升50%。
    这个方法我用了一个月，效果真的很明显。
    第一步：进入设置，找到电池选项。
    第二步：关闭后台应用刷新。
    第三步：调整屏幕亮度为自动。
    就这么简单！赶紧试试吧！
    """
    
    # 1. 提取要点
    print("\n📝 提取核心要点...")
    points = await analyzer.extract_key_points(test_content, num_points=3)
    
    if points:
        print(f"✅ 提取{len(points)}个要点:\n")
        for i, point in enumerate(points, 1):
            print(f"{i}. {point}")
    
    # 2. 生成视频脚本
    if points:
        print("\n🎬 生成视频脚本...")
        script = await analyzer.generate_video_script(points, style="解说")
        
        if script:
            print(f"\n脚本（{len(script.get('full_script', ''))}字）:")
            print("-"*60)
            print(script.get('full_script'))
            print("-"*60)
            print(f"\n分为{len(script.get('segments', []))}个片段")
            print(f"预计时长: {script.get('estimated_duration', 0):.1f}秒")
    
    # 3. 生成标题
    print("\n📌 生成吸引标题...")
    titles = await analyzer.generate_title(test_content[:200], platform="douyin")
    
    if titles:
        print(f"\n✅ 生成{len(titles)}个标题:\n")
        for i, title in enumerate(titles, 1):
            print(f"{i}. {title}")
    
    print("\n" + "="*60)
    print("✅ 所有测试完成")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())

