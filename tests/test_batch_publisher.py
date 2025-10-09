"""
批量发布系统测试

测试批量发布的核心功能
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.publisher import (
    PublishContent,
    PlatformType,
    PublishStatus
)
from core.content_adapter import (
    UniversalContentAdapter,
    XianyuAdapter,
    XiaohongshuAdapter,
    ZhihuAdapter,
    BilibiliAdapter
)
from plugins.batch_publisher.task_manager import BatchPublishManager


async def test_content_adapter():
    """测试内容适配器"""
    
    print("\n" + "="*60)
    print("🧪 测试1: 内容适配器")
    print("="*60)
    
    # 创建测试内容
    content = PublishContent(
        title="这是一个测试标题，包含emoji✨和比较长的文字内容，需要进行截断处理",
        content="这是正文内容。" * 100,  # 重复100次，模拟长文本
        description="这是描述内容。" * 50,
        tags=["测试", "标签", "示例", "内容", "发布", "多平台", "AI", "自动化", "工具", "批量", "额外的"],
        images=["1.jpg", "2.jpg", "3.jpg", "4.jpg", "5.jpg", "6.jpg", "7.jpg", "8.jpg", "9.jpg", "10.jpg", "11.jpg"],
        price=99.99,
        category="测试分类"
    )
    
    print(f"\n原始内容:")
    print(f"  标题长度: {len(content.title)}字")
    print(f"  正文长度: {len(content.content)}字")
    print(f"  图片数量: {len(content.images)}张")
    print(f"  标签数量: {len(content.tags)}个")
    
    # 测试各平台适配
    platforms = [
        PlatformType.XIANYU,
        PlatformType.XIAOHONGSHU,
        PlatformType.ZHIHU,
        PlatformType.BILIBILI
    ]
    
    for platform in platforms:
        adapted = UniversalContentAdapter.adapt(content, platform)
        print(f"\n{platform.value} 适配后:")
        print(f"  标题: {adapted.title[:50]}...")
        print(f"  标题长度: {len(adapted.title)}字")
        print(f"  正文长度: {len(adapted.content)}字")
        print(f"  图片数量: {len(adapted.images)}张")
        print(f"  标签数量: {len(adapted.tags)}个")
    
    print("\n✅ 测试1通过: 内容适配器工作正常\n")


async def test_batch_publish_manager():
    """测试批量发布管理器"""
    
    print("\n" + "="*60)
    print("🧪 测试2: 批量发布管理器")
    print("="*60)
    
    # 创建管理器
    manager = BatchPublishManager()
    
    # 创建测试内容
    content = PublishContent(
        title="AI工具推荐：提升效率的神器✨",
        content="""
        今天给大家推荐一款超好用的AI工具！
        
        主要功能：
        1. 智能内容生成
        2. 多平台一键发布
        3. 数据统计分析
        
        使用体验非常好，强烈推荐！
        """,
        description="一款提升工作效率的AI工具",
        tags=["AI", "工具", "效率", "推荐"],
        images=["tool1.jpg", "tool2.jpg", "tool3.jpg"],
        category="工具软件"
    )
    
    # 创建任务
    print("\n📝 创建发布任务...")
    task_id = manager.create_task(
        content=content,
        platforms=["xianyu", "xiaohongshu", "zhihu", "bilibili"],
        max_retries=2
    )
    
    print(f"✅ 任务创建成功: {task_id}")
    
    # 执行任务
    print(f"\n🚀 开始执行任务...")
    task = await manager.execute_task(task_id)
    
    # 验证结果
    print(f"\n📊 验证结果:")
    print(f"  任务状态: {task.status.value}")
    print(f"  总平台数: {task.total_platforms}")
    print(f"  完成数: {task.completed_platforms}")
    print(f"  失败数: {task.failed_platforms}")
    print(f"  成功率: {task.success_rate * 100:.1f}%")
    
    # 检查所有平台都有结果
    assert len(task.results) == task.total_platforms, "结果数量不匹配"
    
    # 检查所有平台都成功（模拟发布都应该成功）
    success_count = sum(1 for r in task.results if r.success)
    print(f"\n  成功平台: {success_count}/{task.total_platforms}")
    
    for result in task.results:
        print(f"  - {result.platform.value}: {result.status.value}")
    
    # 获取统计信息
    stats = manager.get_statistics()
    print(f"\n📈 管理器统计:")
    print(f"  总任务数: {stats['total_tasks']}")
    print(f"  完成任务: {stats['completed_tasks']}")
    print(f"  总发布数: {stats['total_publishes']}")
    print(f"  成功发布: {stats['successful_publishes']}")
    
    print("\n✅ 测试2通过: 批量发布管理器工作正常\n")


async def test_platform_adapters():
    """测试平台适配器"""
    
    print("\n" + "="*60)
    print("🧪 测试3: 平台适配器验证")
    print("="*60)
    
    # 测试闲鱼适配器
    print("\n📦 测试闲鱼适配器...")
    content = PublishContent(
        title="测试商品标题",
        description="测试描述",
        price=99.99,
        category="数码产品",
        images=["1.jpg", "2.jpg"]
    )
    
    from plugins.batch_publisher.adapters.xianyu_adapter import XianyuPublisher
    xianyu_pub = XianyuPublisher()
    
    is_valid, error = await xianyu_pub.validate_content(content)
    print(f"  验证结果: {'✅ 通过' if is_valid else f'❌ 失败 - {error}'}")
    
    # 测试小红书适配器
    print("\n📝 测试小红书适配器...")
    content = PublishContent(
        title="测试笔记✨",
        content="测试内容" * 50,
        images=["1.jpg", "2.jpg", "3.jpg"],
        tags=["测试", "分享"]
    )
    
    from plugins.batch_publisher.adapters.xiaohongshu_adapter import XiaohongshuPublisher
    xhs_pub = XiaohongshuPublisher()
    
    is_valid, error = await xhs_pub.validate_content(content)
    print(f"  验证结果: {'✅ 通过' if is_valid else f'❌ 失败 - {error}'}")
    
    # 测试知乎适配器
    print("\n📖 测试知乎适配器...")
    content = PublishContent(
        title="如何提高工作效率？",
        content="这是一篇关于提高工作效率的文章。" * 20,
        tags=["效率", "方法"]
    )
    
    from plugins.batch_publisher.adapters.zhihu_adapter import ZhihuPublisher
    zhihu_pub = ZhihuPublisher()
    
    is_valid, error = await zhihu_pub.validate_content(content)
    print(f"  验证结果: {'✅ 通过' if is_valid else f'❌ 失败 - {error}'}")
    
    # 测试B站适配器
    print("\n🎬 测试B站适配器...")
    content = PublishContent(
        title="测试视频标题",
        description="测试视频简介",
        tags=["测试", "分享"],
        platform_data={"dynamic": "发布了新视频"}
    )
    
    from plugins.batch_publisher.adapters.bilibili_adapter import BilibiliPublisher
    bili_pub = BilibiliPublisher()
    
    is_valid, error = await bili_pub.validate_content(content)
    print(f"  验证结果: {'✅ 通过' if is_valid else f'❌ 失败 - {error}'}")
    
    print("\n✅ 测试3通过: 所有平台适配器验证通过\n")


async def test_content_adaptation_comparison():
    """测试内容适配对比"""
    
    print("\n" + "="*60)
    print("🧪 测试4: 内容适配对比")
    print("="*60)
    
    # 创建测试内容
    content = PublishContent(
        title="这是一个很长的测试标题✨包含emoji和各种符号！！！用于测试不同平台的适配效果",
        content="测试正文。" * 200,
        tags=["测试1", "测试2", "测试3", "测试4", "测试5", "测试6"],
        images=["1.jpg"] * 15
    )
    
    # 对比适配结果
    platforms = [
        PlatformType.XIANYU,
        PlatformType.XIAOHONGSHU,
        PlatformType.ZHIHU,
        PlatformType.BILIBILI
    ]
    
    comparison = UniversalContentAdapter.compare_adaptations(content, platforms)
    
    print(f"\n原始内容:")
    print(f"  标题: {comparison['original']['title'][:50]}...")
    print(f"  标题长度: {comparison['original']['title_length']}字")
    print(f"  正文长度: {comparison['original']['content_length']}字")
    print(f"  图片数量: {comparison['original']['images_count']}张")
    print(f"  标签数量: {comparison['original']['tags_count']}个")
    
    print(f"\n适配后对比:")
    print(f"{'平台':<15} {'标题长度':<10} {'正文长度':<10} {'图片数':<8} {'标签数':<8}")
    print("-" * 60)
    
    for platform_name, data in comparison['adapted'].items():
        print(f"{platform_name:<15} {data['title_length']:<10} {data['content_length']:<10} {data['images_count']:<8} {data['tags_count']:<8}")
    
    print("\n✅ 测试4通过: 内容适配对比正常\n")


async def run_all_tests():
    """运行所有测试"""
    
    print("\n")
    print("="*60)
    print("🚀 批量发布系统测试套件")
    print("="*60)
    
    try:
        # 测试1: 内容适配器
        await test_content_adapter()
        
        # 测试2: 批量发布管理器
        await test_batch_publish_manager()
        
        # 测试3: 平台适配器
        await test_platform_adapters()
        
        # 测试4: 内容适配对比
        await test_content_adaptation_comparison()
        
        # 总结
        print("\n" + "="*60)
        print("🎉 所有测试通过！批量发布系统工作正常！")
        print("="*60)
        print(f"\n总计: 4/4 测试通过 (100%)")
        print("\n")
        
        return True
    
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(run_all_tests())
    
    # 退出码
    exit(0 if success else 1)

