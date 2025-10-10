"""测试图文视频生成"""
import asyncio
from plugins.video_producer.video_generator import VideoGenerator

async def main():
    print("="*60)
    print("🎬 测试图文视频生成")
    print("="*60)
    
    generator = VideoGenerator()
    
    # 测试脚本片段
    script_segments = [
        "大家好！今天教你一个超实用的技巧",
        "这个方法可以让手机电池续航提升50%",
        "第一步：进入设置，关闭后台刷新",
        "第二步：调整屏幕亮度为自动",
        "就这么简单！记得点赞关注哦！"
    ]
    
    print(f"\n📝 脚本片段: {len(script_segments)}个")
    for i, seg in enumerate(script_segments, 1):
        print(f"{i}. {seg}")
    
    print("\n🎬 开始生成视频...")
    print("⏰ 预计需要1-2分钟，请耐心等待...")
    
    try:
        output_path = await generator.generate_text_video(
            script_segments=script_segments,
            title="手机省电技巧",
            output_name="test_video_01.mp4"
        )
        
        print(f"\n✅ 视频生成成功！")
        print(f"📁 保存位置: {output_path}")
        print(f"📊 视频信息:")
        print(f"   - 时长: {len(script_segments) * 5}秒")
        print(f"   - 分辨率: 1080x1920 (竖屏)")
        print(f"   - 帧率: 30fps")
        
    except Exception as e:
        print(f"\n❌ 生成失败: {e}")
        print("\n可能原因:")
        print("1. FFmpeg未安装")
        print("2. 字体文件缺失")
        print("3. 权限问题")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())

