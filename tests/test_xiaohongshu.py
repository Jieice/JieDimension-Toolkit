"""
JieDimension Toolkit - 小红书插件测试
测试标题生成、Emoji优化、话题推荐功能
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from plugins.xiaohongshu.title_generator import XiaohongshuTitleGenerator, TitleStyle
from plugins.xiaohongshu.emoji_optimizer import EmojiOptimizer
from plugins.xiaohongshu.topic_recommender import TopicTagRecommender


async def test_title_generator():
    """测试标题生成器"""
    print("\n" + "="*60)
    print("🧪 测试1：标题生成器")
    print("="*60)
    
    generator = XiaohongshuTitleGenerator()
    
    # 测试种草风格
    print("\n📝 测试种草风格标题生成...")
    title = await generator.generate_title(
        topic="夏日防晒",
        keywords=["防晒霜", "学生党", "平价"],
        style=TitleStyle.ZHONGCAO,
        use_template=True  # 使用模板快速生成
    )
    print(f"生成标题: {title}")
    assert len(title) > 0, "标题不能为空"
    print("✅ 通过")
    
    # 测试教程风格
    print("\n📝 测试教程风格标题生成...")
    title2 = await generator.generate_title(
        topic="化妆技巧",
        keywords=["新手", "底妆"],
        style=TitleStyle.JIAOCHENG,
        use_template=True
    )
    print(f"生成标题: {title2}")
    assert len(title2) > 0, "标题不能为空"
    print("✅ 通过")
    
    # 测试emoji检测
    print("\n📝 测试emoji检测...")
    has_emoji = generator._has_emoji("测试标题 ✨")
    assert has_emoji == True, "应该检测到emoji"
    has_emoji2 = generator._has_emoji("测试标题")
    assert has_emoji2 == False, "不应该检测到emoji"
    print("✅ 通过")


def test_emoji_optimizer():
    """测试Emoji优化器"""
    print("\n" + "="*60)
    print("🧪 测试2：Emoji优化器")
    print("="*60)
    
    optimizer = EmojiOptimizer()
    
    # 测试美妆内容优化
    print("\n📝 测试美妆内容emoji插入...")
    text1 = "这款口红真的太好用了！颜色超级显白。"
    optimized1 = optimizer.optimize_emoji(text1, "美妆", "medium")
    print(f"原文: {text1}")
    print(f"优化后: {optimized1}")
    assert len(optimized1) > len(text1), "优化后应该增加了emoji"
    print("✅ 通过")
    
    # 测试标题emoji优化
    print("\n📝 测试标题emoji优化...")
    title = "学生党平价护肤品分享"
    optimized_title = optimizer.optimize_title_emoji(title, "好物")
    print(f"原标题: {title}")
    print(f"优化后: {optimized_title}")
    assert optimizer._has_emoji_at_end(optimized_title), "标题末尾应该有emoji"
    print("✅ 通过")
    
    # 测试情感emoji
    print("\n📝 测试情感emoji添加...")
    text2 = "收到礼物的那一刻"
    with_emotion = optimizer.add_emotion_emoji(text2, "开心")
    print(f"原文: {text2}")
    print(f"添加情感: {with_emotion}")
    assert len(with_emotion) > len(text2), "应该添加了emoji"
    print("✅ 通过")


async def test_topic_recommender():
    """测试话题推荐器"""
    print("\n" + "="*60)
    print("🧪 测试3：话题推荐器")
    print("="*60)
    
    recommender = TopicTagRecommender()
    
    # 测试分类检测
    print("\n📝 测试内容分类检测...")
    content1 = "今天分享一个化妆技巧，口红怎么涂更好看"
    category = recommender._detect_category(content1)
    print(f"内容: {content1}")
    print(f"检测分类: {category}")
    assert category == "美妆", f"应该检测为美妆，实际为{category}"
    print("✅ 通过")
    
    # 测试热门话题匹配
    print("\n📝 测试热门话题匹配...")
    content2 = "分享我的化妆心得"
    tags = recommender._match_hot_topics(content2, "美妆")
    print(f"内容: {content2}")
    print(f"匹配话题: {tags[:3]}")
    assert len(tags) > 0, "应该匹配到话题"
    print("✅ 通过")
    
    # 测试完整推荐
    print("\n📝 测试完整话题推荐...")
    content3 = "周末在家做了蛋糕，烘焙真有趣"
    tags2 = await recommender.recommend_tags(
        content=content3,
        max_tags=5,
        use_ai=False  # 不使用AI，快速测试
    )
    print(f"内容: {content3}")
    print(f"推荐标签: {tags2}")
    assert len(tags2) > 0, "应该推荐至少1个标签"
    print("✅ 通过")
    
    # 测试季节话题
    print("\n📝 测试季节话题获取...")
    seasonal = recommender._get_seasonal_topics()
    print(f"当前季节话题: {seasonal[:3]}")
    assert len(seasonal) > 0, "应该有季节话题"
    print("✅ 通过")


async def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🚀 JieDimension Toolkit - 小红书插件测试套件")
    print("="*60)
    
    try:
        # 测试标题生成器
        await test_title_generator()
        
        # 测试Emoji优化器
        test_emoji_optimizer()
        
        # 测试话题推荐器
        await test_topic_recommender()
        
        # 总结
        print("\n" + "="*60)
        print("✅ 所有测试通过！")
        print("="*60)
        print("\n📊 测试统计:")
        print("  - 标题生成器: 3/3 通过")
        print("  - Emoji优化器: 3/3 通过")
        print("  - 话题推荐器: 4/4 通过")
        print("  - 总计: 10/10 通过 (100%)")
        print("\n🎉 小红书插件测试完成！")
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return False
    except Exception as e:
        print(f"\n❌ 测试错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

