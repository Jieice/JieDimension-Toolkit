"""
测试图表生成功能
测试数据可视化模块的图表生成
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.database import Database
from ui.charts import ChartGenerator


async def test_chart_generation():
    """测试图表生成功能"""
    
    print("\n" + "="*60)
    print("🧪 JieDimension Toolkit - 图表生成测试")
    print("="*60)
    
    # 创建数据库连接
    db = Database("data/database.db")
    await db.connect()
    
    # 创建图表生成器
    generator = ChartGenerator(db)
    
    test_results = []
    
    # ===== 测试1: AI使用趋势图 =====
    print("\n🧪 测试1: AI使用趋势图生成")
    try:
        fig = await generator.create_ai_usage_trend_chart(days=7)
        
        if fig is not None:
            # 保存图表到文件
            output_path = "tests/test_ai_usage_trend.png"
            fig.savefig(output_path, facecolor='#2b2b2b', bbox_inches='tight')
            
            # 检查文件是否存在
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"✅ AI使用趋势图生成成功")
                print(f"   - 保存位置: {output_path}")
                print(f"   - 文件大小: {file_size} bytes")
                test_results.append(("AI使用趋势图", True, f"成功生成 ({file_size} bytes)"))
            else:
                print(f"❌ 图表文件未生成")
                test_results.append(("AI使用趋势图", False, "文件未生成"))
        else:
            print(f"❌ 图表对象为空")
            test_results.append(("AI使用趋势图", False, "图表对象为空"))
            
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        test_results.append(("AI使用趋势图", False, str(e)))
    
    # ===== 测试2: 发布统计图 =====
    print("\n🧪 测试2: 发布统计图生成")
    try:
        fig = await generator.create_publish_stats_chart(days=30)
        
        if fig is not None:
            # 保存图表到文件
            output_path = "tests/test_publish_stats.png"
            fig.savefig(output_path, facecolor='#2b2b2b', bbox_inches='tight')
            
            # 检查文件是否存在
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"✅ 发布统计图生成成功")
                print(f"   - 保存位置: {output_path}")
                print(f"   - 文件大小: {file_size} bytes")
                test_results.append(("发布统计图", True, f"成功生成 ({file_size} bytes)"))
            else:
                print(f"❌ 图表文件未生成")
                test_results.append(("发布统计图", False, "文件未生成"))
        else:
            print(f"❌ 图表对象为空")
            test_results.append(("发布统计图", False, "图表对象为空"))
            
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        test_results.append(("发布统计图", False, str(e)))
    
    # ===== 测试3: 成功率趋势图 =====
    print("\n🧪 测试3: 成功率趋势图生成")
    try:
        fig = await generator.create_success_rate_chart(days=7)
        
        if fig is not None:
            # 保存图表到文件
            output_path = "tests/test_success_rate.png"
            fig.savefig(output_path, facecolor='#2b2b2b', bbox_inches='tight')
            
            # 检查文件是否存在
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"✅ 成功率趋势图生成成功")
                print(f"   - 保存位置: {output_path}")
                print(f"   - 文件大小: {file_size} bytes")
                test_results.append(("成功率趋势图", True, f"成功生成 ({file_size} bytes)"))
            else:
                print(f"❌ 图表文件未生成")
                test_results.append(("成功率趋势图", False, "文件未生成"))
        else:
            print(f"❌ 图表对象为空")
            test_results.append(("成功率趋势图", False, "图表对象为空"))
            
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        test_results.append(("成功率趋势图", False, str(e)))
    
    # ===== 测试4: 数据库查询 =====
    print("\n🧪 测试4: 数据库查询")
    try:
        # 查询AI调用记录
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        ai_calls = await db.get_ai_calls(
            start_date.isoformat(),
            end_date.isoformat()
        )
        
        print(f"✅ 查询到 {len(ai_calls)} 条AI调用记录")
        test_results.append(("数据库查询", True, f"查询到 {len(ai_calls)} 条记录"))
        
        # 显示部分记录
        if ai_calls:
            print(f"   - 最新记录:")
            for call in ai_calls[-3:]:
                print(f"     • {call['provider']}: {call['task_type']} "
                      f"({'成功' if call['success'] else '失败'}) - {call['latency']:.2f}s")
    
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        test_results.append(("数据库查询", False, str(e)))
    
    # 关闭数据库连接
    await db.close()
    
    # ===== 输出测试摘要 =====
    print("\n" + "="*60)
    print("📊 测试摘要")
    print("="*60)
    
    passed = sum(1 for _, success, _ in test_results if success)
    total = len(test_results)
    
    for test_name, success, message in test_results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} - {test_name}: {message}")
    
    print("-" * 60)
    print(f"总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！图表模块工作正常！")
        return True
    else:
        print(f"\n⚠️ 有 {total - passed} 个测试失败")
        return False


def main():
    """运行测试"""
    success = asyncio.run(test_chart_generation())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

