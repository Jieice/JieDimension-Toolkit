"""
数据库功能测试
测试Day 4和Day 5新增的数据库方法
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.database import Database


async def test_count_products():
    """测试商品统计功能"""
    print("\n" + "=" * 60)
    print("🧪 测试: count_products() - 商品统计")
    print("=" * 60)
    
    db = Database()
    await db.connect()
    
    # 测试总数统计
    total = await db.count_products()
    print(f"✅ 总商品数: {total}")
    
    # 测试平台筛选
    xianyu_count = await db.count_products(platform="xianyu")
    print(f"✅ 闲鱼商品数: {xianyu_count}")
    
    await db.close()
    return True


async def test_get_tasks_by_date_range():
    """测试任务时间范围查询"""
    print("\n" + "=" * 60)
    print("🧪 测试: get_tasks_by_date_range() - 任务时间查询")
    print("=" * 60)
    
    db = Database()
    await db.connect()
    
    # 查询最近7天的任务
    from datetime import datetime, timedelta
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    tasks = await db.get_tasks_by_date_range(start_date, end_date)
    print(f"✅ 找到 {len(tasks)} 个最近7天的任务")
    
    # 测试状态筛选
    completed_tasks = await db.get_tasks_by_date_range(
        start_date, end_date, status="completed"
    )
    print(f"✅ 其中已完成: {len(completed_tasks)} 个")
    
    await db.close()
    return True


async def test_get_ai_stats_summary():
    """测试AI统计摘要"""
    print("\n" + "=" * 60)
    print("🧪 测试: get_ai_stats_summary() - AI统计摘要")
    print("=" * 60)
    
    db = Database()
    await db.connect()
    
    # 获取全部统计
    stats = await db.get_ai_stats_summary()
    print(f"\n📊 AI统计摘要:")
    print(f"   总调用次数: {stats.get('total_calls', 0)}")
    print(f"   成功次数: {stats.get('successful_calls', 0)}")
    print(f"   失败次数: {stats.get('failed_calls', 0)}")
    print(f"   成功率: {stats.get('success_rate', 0):.1f}%")
    avg_latency = stats.get('avg_latency', 0) or 0
    print(f"   平均延迟: {avg_latency:.2f}s")
    
    # 获取Ollama统计（使用get_ai_stats方法）
    ollama_stats_list = await db.get_ai_stats(provider="ollama", days=7)
    print(f"\n🤖 Ollama统计（最近7天）:")
    if ollama_stats_list:
        ollama_stat = ollama_stats_list[0]
        success_rate = (ollama_stat['success_count'] / ollama_stat['total_calls'] * 100) if ollama_stat['total_calls'] > 0 else 0
        print(f"   调用次数: {ollama_stat.get('total_calls', 0)}")
        print(f"   成功率: {success_rate:.1f}%")
        ollama_latency = ollama_stat.get('avg_latency', 0) or 0
        print(f"   平均延迟: {ollama_latency:.2f}s")
    else:
        print(f"   调用次数: 0")
    
    # 获取Gemini统计
    gemini_stats_list = await db.get_ai_stats(provider="gemini", days=7)
    print(f"\n✨ Gemini统计（最近7天）:")
    if gemini_stats_list:
        gemini_stat = gemini_stats_list[0]
        success_rate = (gemini_stat['success_count'] / gemini_stat['total_calls'] * 100) if gemini_stat['total_calls'] > 0 else 0
        print(f"   调用次数: {gemini_stat.get('total_calls', 0)}")
        print(f"   成功率: {success_rate:.1f}%")
    else:
        print(f"   调用次数: 0")
    
    print(f"\n✅ AI统计摘要测试通过")
    
    await db.close()
    return True


async def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("🚀 数据库功能测试套件")
    print("=" * 60)
    print("📅 Day 4-5 新增方法测试")
    print("=" * 60)
    
    results = []
    
    # 测试1: count_products
    try:
        result = await test_count_products()
        results.append(("count_products", result))
    except Exception as e:
        print(f"❌ count_products 测试失败: {e}")
        results.append(("count_products", False))
    
    # 测试2: get_tasks_by_date_range
    try:
        result = await test_get_tasks_by_date_range()
        results.append(("get_tasks_by_date_range", result))
    except Exception as e:
        print(f"❌ get_tasks_by_date_range 测试失败: {e}")
        results.append(("get_tasks_by_date_range", False))
    
    # 测试3: get_ai_stats_summary
    try:
        result = await test_get_ai_stats_summary()
        results.append(("get_ai_stats_summary", result))
    except Exception as e:
        print(f"❌ get_ai_stats_summary 测试失败: {e}")
        results.append(("get_ai_stats_summary", False))
    
    # 打印总结
    print("\n" + "=" * 60)
    print("📋 测试报告")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {test_name}")
    
    print("-" * 60)
    print(f"总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！数据库功能正常！")
    else:
        print(f"\n⚠️ 有 {total - passed} 个测试失败")
    
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

