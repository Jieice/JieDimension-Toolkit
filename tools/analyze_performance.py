"""
性能分析工具
分析数据库查询、UI渲染、内存使用等性能指标
"""

import asyncio
import time
import psutil
import os
import sys
from typing import Dict, List, Any

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import Database


class PerformanceAnalyzer:
    """性能分析器"""
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())
    
    def get_memory_usage(self) -> Dict[str, float]:
        """获取内存使用情况"""
        memory_info = self.process.memory_info()
        return {
            "rss_mb": memory_info.rss / 1024 / 1024,  # 物理内存
            "vms_mb": memory_info.vms / 1024 / 1024,  # 虚拟内存
        }
    
    def get_cpu_usage(self) -> float:
        """获取CPU使用率"""
        return self.process.cpu_percent(interval=0.1)
    
    async def measure_query_time(self, query_func, *args, **kwargs) -> tuple:
        """测量查询时间"""
        start_time = time.time()
        result = await query_func(*args, **kwargs)
        elapsed = time.time() - start_time
        return result, elapsed


async def analyze_database_performance():
    """分析数据库性能"""
    
    print("\n" + "="*70)
    print("📊 数据库查询性能分析")
    print("="*70)
    
    analyzer = PerformanceAnalyzer()
    db = Database()
    
    try:
        await db.connect()
        
        # 测试不同查询的性能
        queries = [
            ("全部任务", "get_tasks", {}),
            ("按状态筛选", "get_tasks", {"status": "completed"}),
            ("按类型筛选", "get_tasks", {"type": "xianyu_publish"}),
            ("按平台筛选", "get_tasks", {"platform": "xianyu"}),
            ("组合条件1", "get_tasks", {"status": "completed", "type": "xianyu_publish"}),
            ("组合条件2", "get_tasks", {"status": "completed", "platform": "xianyu"}),
            ("全部条件", "get_tasks", {
                "status": "completed", 
                "type": "xianyu_publish",
                "platform": "xianyu"
            }),
        ]
        
        print(f"\n{'查询类型':<15} | {'结果数':<8} | {'耗时':<12} | {'内存(MB)':<10}")
        print("-"*70)
        
        for query_name, method_name, params in queries:
            # 记录初始内存
            mem_before = analyzer.get_memory_usage()
            
            # 执行查询
            method = getattr(db, method_name)
            result, elapsed = await analyzer.measure_query_time(method, **params)
            
            # 记录结束内存
            mem_after = analyzer.get_memory_usage()
            mem_used = mem_after["rss_mb"] - mem_before["rss_mb"]
            
            # 显示结果
            result_count = len(result) if isinstance(result, list) else 1
            print(f"{query_name:<15} | {result_count:<8} | {elapsed*1000:>8.2f}ms | {mem_used:>+8.2f}")
        
        # 测试AI使用统计
        print("\n" + "-"*70)
        print("AI使用统计查询:")
        
        ai_queries = [
            ("AI统计摘要", "get_ai_stats_summary", {}),
            ("全部时间", "get_ai_stats_summary", {}),
        ]
        
        for query_name, method_name, params in ai_queries:
            method = getattr(db, method_name)
            result, elapsed = await analyzer.measure_query_time(method, **params)
            
            print(f"  {query_name:<12} : {elapsed*1000:>8.2f}ms")
        
        # 总体性能评估
        print("\n" + "="*70)
        print("📈 性能评估:")
        
        avg_query_time = sum(elapsed for _, elapsed in [
            await analyzer.measure_query_time(db.get_tasks) for _ in range(10)
        ]) / 10
        
        print(f"  平均查询时间: {avg_query_time*1000:.2f}ms")
        
        if avg_query_time < 0.01:
            print("  评估: ✅ 优秀 (< 10ms)")
        elif avg_query_time < 0.05:
            print("  评估: ✅ 良好 (< 50ms)")
        elif avg_query_time < 0.1:
            print("  评估: ⚠️  一般 (< 100ms)")
        else:
            print("  评估: ❌ 需要优化 (> 100ms)")
        
        print("="*70)
    
    finally:
        await db.close()


async def analyze_memory_usage():
    """分析内存使用"""
    
    print("\n" + "="*70)
    print("💾 内存使用分析")
    print("="*70)
    
    analyzer = PerformanceAnalyzer()
    
    # 初始内存
    initial_mem = analyzer.get_memory_usage()
    print(f"\n初始内存:")
    print(f"  物理内存: {initial_mem['rss_mb']:.2f} MB")
    print(f"  虚拟内存: {initial_mem['vms_mb']:.2f} MB")
    
    # 模拟加载大量数据
    db = Database()
    await db.connect()
    
    print(f"\n加载数据库后:")
    after_db_mem = analyzer.get_memory_usage()
    print(f"  物理内存: {after_db_mem['rss_mb']:.2f} MB (+{after_db_mem['rss_mb'] - initial_mem['rss_mb']:.2f})")
    
    # 执行一些查询
    for _ in range(10):
        await db.get_tasks()
    
    print(f"\n执行10次查询后:")
    after_query_mem = analyzer.get_memory_usage()
    print(f"  物理内存: {after_query_mem['rss_mb']:.2f} MB (+{after_query_mem['rss_mb'] - after_db_mem['rss_mb']:.2f})")
    
    await db.close()
    
    # CPU使用
    cpu_usage = analyzer.get_cpu_usage()
    print(f"\nCPU使用率: {cpu_usage:.1f}%")
    
    # 评估
    print("\n" + "-"*70)
    print("评估:")
    if after_query_mem['rss_mb'] < 100:
        print("  ✅ 内存使用优秀 (< 100 MB)")
    elif after_query_mem['rss_mb'] < 200:
        print("  ✅ 内存使用良好 (< 200 MB)")
    elif after_query_mem['rss_mb'] < 500:
        print("  ⚠️  内存使用一般 (< 500 MB)")
    else:
        print("  ❌ 内存使用较高 (> 500 MB)")
    
    print("="*70)


async def analyze_index_effectiveness():
    """分析数据库索引效果"""
    
    print("\n" + "="*70)
    print("🔍 数据库索引分析")
    print("="*70)
    
    db = Database()
    await db.connect()
    
    try:
        # 使用EXPLAIN QUERY PLAN分析查询计划
        queries = [
            ("按状态查询", "SELECT * FROM tasks WHERE status = ?", ("completed",)),
            ("按类型查询", "SELECT * FROM tasks WHERE type = ?", ("xianyu_publish",)),
            ("复合查询", "SELECT * FROM tasks WHERE status = ? AND type = ?", 
             ("completed", "xianyu_publish")),
        ]
        
        print(f"\n{'查询类型':<15} | {'索引使用情况'}")
        print("-"*70)
        
        for query_name, sql, params in queries:
            explain_sql = f"EXPLAIN QUERY PLAN {sql}"
            cursor = await db.conn.execute(explain_sql, params)
            plan = await cursor.fetchall()
            
            # 检查是否使用了索引
            plan_str = str(plan)
            if "USING INDEX" in plan_str.upper():
                status = "✅ 使用索引"
            elif "SCAN" in plan_str.upper():
                status = "⚠️  全表扫描"
            else:
                status = "❓ 未知"
            
            print(f"{query_name:<15} | {status}")
        
        print("\n" + "-"*70)
        print("建议:")
        print("  - 确保常用字段已创建索引")
        print("  - 复合查询考虑创建复合索引")
        print("  - 定期运行 ANALYZE 更新统计信息")
        print("="*70)
    
    finally:
        await db.close()


def print_system_info():
    """打印系统信息"""
    
    print("\n" + "="*70)
    print("💻 系统信息")
    print("="*70)
    
    # CPU信息
    cpu_count = psutil.cpu_count()
    cpu_freq = psutil.cpu_freq()
    print(f"\nCPU:")
    print(f"  核心数: {cpu_count}")
    if cpu_freq:
        print(f"  频率: {cpu_freq.current:.0f} MHz")
    
    # 内存信息
    memory = psutil.virtual_memory()
    print(f"\n内存:")
    print(f"  总量: {memory.total / 1024 / 1024 / 1024:.2f} GB")
    print(f"  已用: {memory.used / 1024 / 1024 / 1024:.2f} GB ({memory.percent}%)")
    print(f"  可用: {memory.available / 1024 / 1024 / 1024:.2f} GB")
    
    # 磁盘信息
    disk = psutil.disk_usage('.')
    print(f"\n磁盘:")
    print(f"  总量: {disk.total / 1024 / 1024 / 1024:.2f} GB")
    print(f"  已用: {disk.used / 1024 / 1024 / 1024:.2f} GB ({disk.percent}%)")
    print(f"  可用: {disk.free / 1024 / 1024 / 1024:.2f} GB")
    
    print("="*70)


async def main():
    """主函数"""
    
    print("\n" + "="*70)
    print("🚀 JieDimension Toolkit - 性能分析工具")
    print("="*70)
    
    # 系统信息
    print_system_info()
    
    # 数据库性能
    await analyze_database_performance()
    
    # 内存使用
    await analyze_memory_usage()
    
    # 索引分析
    await analyze_index_effectiveness()
    
    print("\n" + "="*70)
    print("✅ 性能分析完成！")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())

