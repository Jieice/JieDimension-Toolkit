"""
批量发布任务管理器

管理发布队列、进度追踪、失败重试等功能
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum

from core.publisher import (
    PublishManager,
    PublishContent,
    PublishResult,
    PlatformType,
    PublishStatus
)
from plugins.batch_publisher.adapters import (
    XianyuPublisher,
    XiaohongshuPublisher,
    ZhihuPublisher,
    BilibiliPublisher
)


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"           # 待处理
    RUNNING = "running"           # 运行中
    COMPLETED = "completed"       # 已完成
    FAILED = "failed"            # 失败
    CANCELLED = "cancelled"       # 已取消


@dataclass
class PublishTask:
    """发布任务"""
    task_id: str                              # 任务ID
    content: PublishContent                   # 发布内容
    platforms: List[PlatformType]             # 目标平台
    status: TaskStatus = TaskStatus.PENDING   # 任务状态
    
    # 进度
    total_platforms: int = 0                  # 总平台数
    completed_platforms: int = 0              # 已完成平台数
    failed_platforms: int = 0                 # 失败平台数
    
    # 结果
    results: List[PublishResult] = field(default_factory=list)
    
    # 时间
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # 重试
    retry_count: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        self.total_platforms = len(self.platforms)
    
    @property
    def progress(self) -> float:
        """进度百分比（0-100）"""
        if self.total_platforms == 0:
            return 0.0
        return (self.completed_platforms / self.total_platforms) * 100
    
    @property
    def is_finished(self) -> bool:
        """任务是否已结束"""
        return self.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_platforms == 0:
            return 0.0
        return (self.completed_platforms - self.failed_platforms) / self.total_platforms
    
    def add_result(self, result: PublishResult):
        """添加发布结果"""
        self.results.append(result)
        self.completed_platforms += 1
        
        if not result.success:
            self.failed_platforms += 1


class BatchPublishManager:
    """
    批量发布管理器
    
    管理多任务、多平台的批量发布
    """
    
    def __init__(self):
        # 发布管理器
        self.publish_manager = PublishManager()
        
        # 注册所有平台发布器
        self._register_publishers()
        
        # 任务队列
        self.tasks: Dict[str, PublishTask] = {}
        self.task_counter = 0
        
        # 进度回调
        self.progress_callbacks: List[Callable] = []
    
    def _register_publishers(self):
        """注册所有平台发布器"""
        publishers = [
            XianyuPublisher(),
            XiaohongshuPublisher(),
            ZhihuPublisher(),
            BilibiliPublisher(),
        ]
        
        for publisher in publishers:
            self.publish_manager.register_publisher(publisher)
    
    def add_progress_callback(self, callback: Callable):
        """
        添加进度回调函数
        
        Args:
            callback: 回调函数，签名为 callback(task_id, progress, status)
        """
        self.progress_callbacks.append(callback)
    
    def _notify_progress(self, task_id: str, progress: float, status: str):
        """通知进度更新"""
        for callback in self.progress_callbacks:
            try:
                callback(task_id, progress, status)
            except Exception as e:
                print(f"⚠️ 进度回调错误: {e}")
    
    def create_task(
        self,
        content: PublishContent,
        platforms: List[str],
        max_retries: int = 3
    ) -> str:
        """
        创建发布任务
        
        Args:
            content: 发布内容
            platforms: 平台名称列表（如 ["xianyu", "xiaohongshu"]）
            max_retries: 最大重试次数
            
        Returns:
            任务ID
        """
        # 生成任务ID
        self.task_counter += 1
        task_id = f"task_{self.task_counter}_{int(datetime.now().timestamp())}"
        
        # 转换平台名称为枚举
        platform_enums = []
        for p in platforms:
            try:
                platform_enums.append(PlatformType(p))
            except ValueError:
                print(f"⚠️ 未知平台: {p}")
        
        if not platform_enums:
            raise ValueError("没有有效的目标平台")
        
        # 创建任务
        task = PublishTask(
            task_id=task_id,
            content=content,
            platforms=platform_enums,
            max_retries=max_retries
        )
        
        self.tasks[task_id] = task
        
        print(f"✅ 创建任务 {task_id}")
        print(f"   内容: {content.title}")
        print(f"   平台: {', '.join([p.value for p in platform_enums])}")
        
        return task_id
    
    async def execute_task(self, task_id: str) -> PublishTask:
        """
        执行发布任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务对象
        """
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"任务不存在: {task_id}")
        
        if task.is_finished:
            print(f"⚠️ 任务已结束: {task_id}")
            return task
        
        # 更新状态
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        self._notify_progress(task_id, 0, "开始发布")
        
        print(f"\n{'='*60}")
        print(f"🚀 开始执行任务: {task_id}")
        print(f"   标题: {task.content.title}")
        print(f"   平台数: {task.total_platforms}")
        print(f"{'='*60}\n")
        
        # 逐个平台发布
        for idx, platform in enumerate(task.platforms):
            try:
                # 发布到单个平台
                result = await self.publish_manager.publish_to_single_platform(
                    content=task.content,
                    platform=platform,
                    max_retries=task.max_retries
                )
                
                # 记录结果
                task.add_result(result)
                
                # 通知进度
                progress = task.progress
                status_msg = f"已完成 {platform.value} ({task.completed_platforms}/{task.total_platforms})"
                self._notify_progress(task_id, progress, status_msg)
                
                # 打印结果
                print(result)
                
                # 延迟（避免频率限制）
                if idx < len(task.platforms) - 1:
                    await asyncio.sleep(1)
            
            except Exception as e:
                # 记录失败
                failed_result = PublishResult(
                    platform=platform,
                    status=PublishStatus.FAILED,
                    error=f"执行异常: {str(e)}"
                )
                task.add_result(failed_result)
                print(f"❌ {platform.value}: {e}")
        
        # 更新任务状态
        task.completed_at = datetime.now()
        
        if task.failed_platforms == 0:
            task.status = TaskStatus.COMPLETED
        elif task.failed_platforms == task.total_platforms:
            task.status = TaskStatus.FAILED
        else:
            task.status = TaskStatus.COMPLETED  # 部分成功也算完成
        
        # 打印摘要
        self._print_task_summary(task)
        
        # 通知完成
        self._notify_progress(task_id, 100, "发布完成")
        
        return task
    
    def _print_task_summary(self, task: PublishTask):
        """打印任务摘要"""
        print(f"\n{'='*60}")
        print(f"📊 任务完成摘要: {task.task_id}")
        print(f"{'='*60}")
        print(f"状态: {task.status.value}")
        print(f"总平台数: {task.total_platforms}")
        print(f"成功: {task.completed_platforms - task.failed_platforms}")
        print(f"失败: {task.failed_platforms}")
        print(f"成功率: {task.success_rate * 100:.1f}%")
        
        if task.started_at and task.completed_at:
            duration = (task.completed_at - task.started_at).total_seconds()
            print(f"耗时: {duration:.2f}秒")
        
        print(f"\n详细结果:")
        for result in task.results:
            status_icon = "✅" if result.success else "❌"
            print(f"  {status_icon} {result.platform.value}: {result.status.value}")
            if result.post_url:
                print(f"     链接: {result.post_url}")
            if result.error:
                print(f"     错误: {result.error}")
        
        print(f"{'='*60}\n")
    
    def get_task(self, task_id: str) -> Optional[PublishTask]:
        """获取任务"""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[PublishTask]:
        """获取所有任务"""
        return list(self.tasks.values())
    
    def get_running_tasks(self) -> List[PublishTask]:
        """获取运行中的任务"""
        return [t for t in self.tasks.values() if t.status == TaskStatus.RUNNING]
    
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功取消
        """
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        if task.status == TaskStatus.RUNNING:
            print(f"⚠️ 任务正在运行，无法立即取消: {task_id}")
            return False
        
        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.now()
        
        print(f"✅ 任务已取消: {task_id}")
        return True
    
    async def execute_batch_tasks(self, task_ids: List[str]) -> List[PublishTask]:
        """
        批量执行任务
        
        Args:
            task_ids: 任务ID列表
            
        Returns:
            任务列表
        """
        results = []
        
        for task_id in task_ids:
            task = await self.execute_task(task_id)
            results.append(task)
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            统计数据
        """
        all_tasks = self.get_all_tasks()
        
        return {
            "total_tasks": len(all_tasks),
            "completed_tasks": sum(1 for t in all_tasks if t.status == TaskStatus.COMPLETED),
            "failed_tasks": sum(1 for t in all_tasks if t.status == TaskStatus.FAILED),
            "running_tasks": sum(1 for t in all_tasks if t.status == TaskStatus.RUNNING),
            "cancelled_tasks": sum(1 for t in all_tasks if t.status == TaskStatus.CANCELLED),
            "total_publishes": sum(t.total_platforms for t in all_tasks),
            "successful_publishes": sum(
                t.completed_platforms - t.failed_platforms for t in all_tasks
            ),
            "failed_publishes": sum(t.failed_platforms for t in all_tasks),
        }


# 便捷函数

async def quick_batch_publish(
    content: PublishContent,
    platforms: List[str],
    progress_callback: Optional[Callable] = None
) -> PublishTask:
    """
    快速批量发布（便捷函数）
    
    Args:
        content: 发布内容
        platforms: 平台列表
        progress_callback: 进度回调
        
    Returns:
        任务对象
    """
    manager = BatchPublishManager()
    
    if progress_callback:
        manager.add_progress_callback(progress_callback)
    
    task_id = manager.create_task(content, platforms)
    task = await manager.execute_task(task_id)
    
    return task

