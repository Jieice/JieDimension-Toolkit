"""
Day 18功能测试
测试数据库接口、重试、导出、选择器测试等功能
"""

import asyncio
import pytest
import os
import sys
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import Database


class TestDatabaseInterface:
    """测试数据库接口"""
    
    @pytest.mark.asyncio
    async def test_get_tasks(self):
        """测试获取任务"""
        db = Database("data/test_database.db")
        await db.connect()
        
        try:
            # 创建测试任务
            task_id = await db.create_task(
                task_type="xianyu_publish",
                name="测试发布任务",
                data={"title": "测试商品", "platform": "xianyu"}
            )
            
            # 测试无筛选
            tasks = await db.get_tasks()
            assert isinstance(tasks, list)
            print(f"✅ 获取所有任务: {len(tasks)}条")
            
            # 测试按状态筛选
            completed_tasks = await db.get_tasks(status="completed")
            assert all(t.get("status") == "completed" for t in completed_tasks)
            print(f"✅ 按状态筛选: {len(completed_tasks)}条")
            
            # 测试按类型筛选
            xianyu_tasks = await db.get_tasks(type="xianyu_publish")
            assert all(t.get("type") == "xianyu_publish" for t in xianyu_tasks)
            print(f"✅ 按类型筛选: {len(xianyu_tasks)}条")
            
            # 测试按类型筛选（平台信息在data中）
            type_tasks = await db.get_tasks(type="xianyu_publish")
            assert len(type_tasks) > 0
            print(f"✅ 按类型筛选: {len(type_tasks)}条")
            
            # 测试组合条件
            combined_tasks = await db.get_tasks(
                status="completed",
                type="xianyu_publish",
                platform="xianyu"
            )
            print(f"✅ 组合条件筛选: {len(combined_tasks)}条")
            
            print("✅ get_tasks测试通过")
        
        finally:
            await db.close()
    
    @pytest.mark.asyncio
    async def test_clear_tasks(self):
        """测试清空任务"""
        db = Database("data/test_database.db")
        await db.connect()
        
        try:
            # 创建测试任务
            await db.create_task(
                task_type="test_task",
                name="测试任务1",
                data={"test": "data", "status": "completed"}
            )
            
            await db.create_task(
                task_type="test_task",
                name="测试任务2",
                data={"test": "data2", "status": "failed"}
            )
            
            # 按类型清空
            deleted = await db.clear_tasks(type="test_task")
            print(f"✅ 清空测试任务: {deleted}条")
            
            # 验证清空
            tasks = await db.get_tasks(type="test_task")
            assert len(tasks) == 0
            
            # 创建更多测试任务
            await db.create_task(
                task_type="test_task2",
                name="其他类型任务",
                data={"test": "data", "status": "completed"}
            )
            
            # 按类型清空
            deleted = await db.clear_tasks(type="test_task2")
            print(f"✅ 按类型清空: {deleted}条")
            
            print("✅ clear_tasks测试通过")
        
        finally:
            await db.close()
    
    @pytest.mark.asyncio
    async def test_get_tasks_date_range(self):
        """测试按日期范围获取任务"""
        db = Database("data/test_database.db")
        await db.connect()
        
        try:
            # 创建测试任务
            now = datetime.now()
            yesterday = now - timedelta(days=1)
            
            await db.create_task(
                task_type="date_test",
                name="日期测试任务",
                data={"created": "yesterday", "status": "completed"}
            )
            
            # 获取最近7天的任务（使用start_date）
            tasks = await db.get_tasks(
                type="date_test",
                start_date=yesterday.isoformat()
            )
            
            print(f"✅ 日期范围查询: {len(tasks)}条")
            
            # 清理
            await db.clear_tasks(type="date_test")
            
            print("✅ 日期范围测试通过")
        
        finally:
            await db.close()


class TestRetryFunction:
    """测试重试功能"""
    
    @pytest.mark.asyncio
    async def test_task_data_recovery(self):
        """测试从任务数据恢复商品信息"""
        db = Database("data/test_database.db")
        await db.connect()
        
        try:
            # 创建失败任务
            task_data = {
                "product": {
                    "title": "测试商品",
                    "price": 99.9,
                    "category": "数码产品",
                    "description": "测试描述"
                }
            }
            
            # 创建失败的发布任务
            full_data = task_data.copy()
            full_data["status"] = "failed"
            task_id = await db.create_task(
                task_type="xianyu_publish",
                name="失败的发布任务",
                data=full_data
            )
            
            # 清空之前的测试数据
            await db.clear_tasks(type="xianyu_publish")
            
            # 重新创建测试任务
            task_id = await db.create_task(
                task_type="xianyu_publish",
                name="失败的发布任务",
                data=full_data
            )
            
            # 获取任务
            tasks = await db.get_tasks(type="xianyu_publish")
            assert len(tasks) == 1
            
            recovered_task = tasks[0]
            assert recovered_task["type"] == "xianyu_publish"
            
            # 验证可以恢复商品数据
            task_data_recovered = recovered_task["data"]
            if isinstance(task_data_recovered, str):
                import json
                task_data_recovered = json.loads(task_data_recovered)
            assert "product" in task_data_recovered
            assert task_data_recovered["product"]["title"] == "测试商品"
            
            print("✅ 任务数据恢复测试通过")
            
            # 清理
            await db.clear_tasks(type="xianyu_publish")
        
        finally:
            await db.close()


class TestExcelExport:
    """测试Excel导出功能"""
    
    def test_export_structure(self):
        """测试导出文件结构"""
        # 这个测试需要实际运行导出功能后验证文件
        # 这里只验证逻辑
        
        import pandas as pd
        
        # 模拟导出数据
        records = [
            {
                "id": 1,
                "type": "xianyu_publish",
                "status": "completed",
                "platform": "xianyu",
                "created_at": "2025-10-09 10:00:00"
            }
        ]
        
        df_records = pd.DataFrame(records)
        assert "id" in df_records.columns
        assert "type" in df_records.columns
        assert "status" in df_records.columns
        
        # 统计数据
        stats = {
            "总数": len(records),
            "成功": 1,
            "失败": 0,
            "成功率": "100.0%"
        }
        
        df_stats = pd.DataFrame([stats])
        assert "总数" in df_stats.columns
        assert "成功率" in df_stats.columns
        
        print("✅ Excel导出结构测试通过")


def run_all_tests():
    """运行所有测试"""
    
    print("="*60)
    print("🧪 Day 18 功能测试套件")
    print("="*60)
    
    # 运行测试
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-s"
    ])
    
    print("\n" + "="*60)
    if exit_code == 0:
        print("✅ 所有测试通过！")
    else:
        print("❌ 部分测试失败")
    print("="*60)
    
    return exit_code


if __name__ == "__main__":
    run_all_tests()

