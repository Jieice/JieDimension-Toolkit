"""
JieDimension Toolkit - 发布历史管理界面
显示历史发布记录、统计数据、支持重新发布和导出报告
Version: 1.0.0
"""

import customtkinter as ctk
from typing import List, Dict, Any, Optional, Callable
import asyncio
from datetime import datetime, timedelta
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from core.database import Database


class PublishHistoryPanel(ctk.CTkFrame):
    """发布历史管理面板"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.db = Database()
        self.tasks = []
        self.current_filter = "all"  # all, success, failed
        self.current_time_filter = "7days"  # 7days, 30days, all
        
        # 创建界面
        self._create_ui()
    
    def _create_ui(self):
        """创建界面"""
        
        # 顶部标题栏
        self._create_header()
        
        # 统计面板
        self._create_stats_panel()
        
        # 筛选面板
        self._create_filter_panel()
        
        # 历史记录列表
        self._create_history_list()
        
        # 底部操作按钮
        self._create_bottom_buttons()
    
    def _create_header(self):
        """创建标题栏"""
        
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📜 发布历史",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left", padx=15, pady=15)
        
        # 刷新按钮
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="🔄 刷新",
            command=lambda: asyncio.create_task(self.load_history()),
            width=100
        )
        refresh_btn.pack(side="right", padx=15, pady=15)
    
    def _create_stats_panel(self):
        """创建统计面板"""
        
        stats_frame = ctk.CTkFrame(self)
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        # 统计卡片容器
        cards_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
        cards_frame.pack(fill="x", padx=15, pady=15)
        
        # 配置网格
        for i in range(4):
            cards_frame.grid_columnconfigure(i, weight=1)
        
        # 总数
        self.total_card = self._create_stat_card(
            cards_frame,
            "📊 总发布数",
            "0",
            "gray"
        )
        self.total_card.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # 成功数
        self.success_card = self._create_stat_card(
            cards_frame,
            "✅ 成功",
            "0",
            "green"
        )
        self.success_card.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # 失败数
        self.failed_card = self._create_stat_card(
            cards_frame,
            "❌ 失败",
            "0",
            "red"
        )
        self.failed_card.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        
        # 成功率
        self.rate_card = self._create_stat_card(
            cards_frame,
            "📈 成功率",
            "0%",
            "blue"
        )
        self.rate_card.grid(row=0, column=3, padx=10, pady=10, sticky="ew")
    
    def _create_stat_card(
        self,
        parent,
        title: str,
        value: str,
        color: str
    ) -> ctk.CTkFrame:
        """创建统计卡片"""
        
        card = ctk.CTkFrame(parent)
        
        # 标题
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        title_label.pack(pady=(15, 5))
        
        # 数值
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=color
        )
        value_label.pack(pady=(0, 15))
        
        # 保存引用以便更新
        card.value_label = value_label
        
        return card
    
    def _create_filter_panel(self):
        """创建筛选面板"""
        
        filter_frame = ctk.CTkFrame(self)
        filter_frame.pack(fill="x", padx=20, pady=10)
        
        # 左侧：状态筛选
        left_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        left_frame.pack(side="left", padx=15, pady=10)
        
        status_label = ctk.CTkLabel(
            left_frame,
            text="状态:",
            font=ctk.CTkFont(size=13)
        )
        status_label.pack(side="left", padx=5)
        
        self.status_filter = ctk.CTkSegmentedButton(
            left_frame,
            values=["全部", "成功", "失败"],
            command=self._on_status_filter_changed
        )
        self.status_filter.set("全部")
        self.status_filter.pack(side="left", padx=5)
        
        # 右侧：时间筛选
        right_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        right_frame.pack(side="right", padx=15, pady=10)
        
        time_label = ctk.CTkLabel(
            right_frame,
            text="时间:",
            font=ctk.CTkFont(size=13)
        )
        time_label.pack(side="left", padx=5)
        
        self.time_filter = ctk.CTkSegmentedButton(
            right_frame,
            values=["7天", "30天", "全部"],
            command=self._on_time_filter_changed
        )
        self.time_filter.set("7天")
        self.time_filter.pack(side="left", padx=5)
    
    def _create_history_list(self):
        """创建历史记录列表"""
        
        # 列表容器（可滚动）
        self.list_frame = ctk.CTkScrollableFrame(self, label_text="发布记录")
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    def _create_bottom_buttons(self):
        """创建底部按钮"""
        
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(fill="x", padx=20, pady=20)
        
        # 导出报告按钮
        export_btn = ctk.CTkButton(
            btn_frame,
            text="📊 导出Excel报告",
            command=self._export_report,
            width=150
        )
        export_btn.pack(side="left", padx=5)
        
        # 清空历史按钮
        clear_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️ 清空历史",
            command=self._clear_history,
            fg_color="red",
            hover_color="darkred",
            width=120
        )
        clear_btn.pack(side="right", padx=5)
    
    async def load_history(self):
        """加载发布历史"""
        
        try:
            # 连接数据库
            await self.db.connect()
            
            # 构建查询条件
            filters = {
                "type": "xianyu_publish"
            }
            
            # 时间筛选
            if self.current_time_filter == "7days":
                start_date = datetime.now() - timedelta(days=7)
                filters["start_date"] = start_date.isoformat()
            elif self.current_time_filter == "30days":
                start_date = datetime.now() - timedelta(days=30)
                filters["start_date"] = start_date.isoformat()
            
            # 状态筛选
            status_map = {
                "all": None,
                "success": "completed",
                "failed": "failed"
            }
            status = status_map.get(self.current_filter)
            if status:
                filters["status"] = status
            
            # 查询任务记录
            self.tasks = await self.db.get_tasks(**filters)
            
            # 更新统计
            self._update_stats()
            
            # 更新列表
            self._update_list()
            
            await self.db.close()
            
        except Exception as e:
            print(f"❌ 加载历史失败: {e}")
            
            # 显示错误消息
            error_label = ctk.CTkLabel(
                self.list_frame,
                text=f"加载失败: {e}",
                font=ctk.CTkFont(size=14),
                text_color="red"
            )
            error_label.pack(pady=50)
    
    def _update_stats(self):
        """更新统计数据"""
        
        if not self.tasks:
            self.total_card.value_label.configure(text="0")
            self.success_card.value_label.configure(text="0")
            self.failed_card.value_label.configure(text="0")
            self.rate_card.value_label.configure(text="0%")
            return
        
        # 计算统计
        total = len(self.tasks)
        success = sum(1 for t in self.tasks if t.get("status") == "completed")
        failed = sum(1 for t in self.tasks if t.get("status") == "failed")
        rate = (success / total * 100) if total > 0 else 0
        
        # 更新卡片
        self.total_card.value_label.configure(text=str(total))
        self.success_card.value_label.configure(text=str(success))
        self.failed_card.value_label.configure(text=str(failed))
        self.rate_card.value_label.configure(text=f"{rate:.1f}%")
    
    def _update_list(self):
        """更新列表"""
        
        # 清空列表
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        if not self.tasks:
            # 显示空状态
            empty_label = ctk.CTkLabel(
                self.list_frame,
                text="📭 暂无发布记录",
                font=ctk.CTkFont(size=16),
                text_color="gray"
            )
            empty_label.pack(pady=50)
            return
        
        # 显示任务列表
        for task in self.tasks:
            self._create_task_item(task)
    
    def _create_task_item(self, task: Dict[str, Any]):
        """创建任务项"""
        
        item_frame = ctk.CTkFrame(self.list_frame)
        item_frame.pack(fill="x", pady=5, padx=10)
        
        # 左侧：状态图标
        status = task.get("status", "pending")
        status_icons = {
            "completed": "✅",
            "failed": "❌",
            "running": "⏳",
            "pending": "⏸️"
        }
        status_icon = status_icons.get(status, "❓")
        
        icon_label = ctk.CTkLabel(
            item_frame,
            text=status_icon,
            font=ctk.CTkFont(size=20)
        )
        icon_label.pack(side="left", padx=15, pady=10)
        
        # 中间：任务信息
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # 从任务数据中提取商品标题
        import json
        try:
            data = json.loads(task.get("data", "{}"))
            title = data.get("product", {}).get("title", "未知商品")
        except:
            title = "未知商品"
        
        # 标题
        title_label = ctk.CTkLabel(
            info_frame,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        title_label.pack(anchor="w")
        
        # 详细信息
        created_at = task.get("created_at", "")
        progress = task.get("progress", 0)
        
        detail_text = f"时间: {created_at} | 进度: {progress}%"
        
        if status == "failed":
            error = task.get("error", "未知错误")
            detail_text += f" | 错误: {error}"
        elif status == "completed":
            result = json.loads(task.get("result", "{}"))
            post_url = result.get("post_url", "")
            if post_url:
                detail_text += f" | URL: {post_url}"
        
        detail_label = ctk.CTkLabel(
            info_frame,
            text=detail_text,
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="w"
        )
        detail_label.pack(anchor="w")
        
        # 右侧：操作按钮
        if status == "failed":
            retry_btn = ctk.CTkButton(
                item_frame,
                text="🔄 重试",
                command=lambda t=task: self._retry_task(t),
                width=80,
                height=32
            )
            retry_btn.pack(side="right", padx=10)
        
        # 详情按钮
        detail_btn = ctk.CTkButton(
            item_frame,
            text="ℹ️",
            command=lambda t=task: self._show_task_detail(t),
            width=40,
            height=32
        )
        detail_btn.pack(side="right", padx=5)
    
    def _retry_task(self, task: Dict[str, Any]):
        """重试任务"""
        
        # 在后台线程中运行异步重试
        import threading
        
        def run_retry():
            import asyncio
            try:
                # 创建新的事件循环
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self._async_retry_task(task))
            finally:
                loop.close()
        
        # 启动后台线程
        thread = threading.Thread(target=run_retry, daemon=True)
        thread.start()
    
    async def _async_retry_task(self, task: Dict[str, Any]):
        """异步重试任务"""
        
        try:
            # 1. 从任务数据中提取商品信息
            import json
            data = task.get("data", {})
            if isinstance(data, str):
                data = json.loads(data)
            
            product = data.get("product", {})
            
            if not product:
                self._show_message("重试失败", "任务数据中没有商品信息", "error")
                return
            
            # 2. 创建发布器
            from plugins.xianyu.publisher import XianyuPublisher
            from core.ai_engine import AIEngine
            
            ai_engine = AIEngine()
            publisher = XianyuPublisher(ai_engine)
            
            # 3. 重新发布
            print(f"🔄 重试发布: {product.get('title')}")
            
            result = await publisher.publish_product(
                product,
                use_browser=True,
                enable_retry=False  # 避免重复重试
            )
            
            # 4. 显示结果
            if result.get("success"):
                self._show_message(
                    "重试成功", 
                    f"✅ 商品已重新发布！\n\n标题: {product.get('title')}\nURL: {result.get('post_url', '暂无')}", 
                    "success"
                )
            else:
                self._show_message(
                    "重试失败", 
                    f"❌ 发布失败\n\n标题: {product.get('title')}\n错误: {result.get('error', '未知错误')}", 
                    "error"
                )
            
            # 5. 刷新历史（在主线程中）
            self.after(100, lambda: self._schedule_async_task(self.load_history()))
            
        except Exception as e:
            print(f"❌ 重试失败: {e}")
            import traceback
            traceback.print_exc()
            self._show_message("重试失败", f"重试出错: {str(e)}", "error")
    
    def _show_task_detail(self, task: Dict[str, Any]):
        """显示任务详情"""
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("任务详情")
        dialog.geometry("600x500")
        
        # 详情容器（可滚动）
        detail_frame = ctk.CTkScrollableFrame(dialog)
        detail_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 显示所有任务信息
        import json
        
        # 基本信息
        info_items = [
            ("任务ID", task.get("id", "")),
            ("状态", task.get("status", "")),
            ("类型", task.get("type", "")),
            ("进度", f"{task.get('progress', 0)}%"),
            ("创建时间", task.get("created_at", "")),
            ("开始时间", task.get("started_at", "")),
            ("完成时间", task.get("completed_at", "")),
        ]
        
        for label_text, value in info_items:
            item_frame = ctk.CTkFrame(detail_frame)
            item_frame.pack(fill="x", pady=5)
            
            label = ctk.CTkLabel(
                item_frame,
                text=f"{label_text}:",
                font=ctk.CTkFont(size=12, weight="bold"),
                width=100,
                anchor="w"
            )
            label.pack(side="left", padx=10, pady=5)
            
            value_label = ctk.CTkLabel(
                item_frame,
                text=str(value),
                font=ctk.CTkFont(size=12),
                anchor="w"
            )
            value_label.pack(side="left", fill="x", expand=True, padx=10, pady=5)
        
        # 数据详情
        if task.get("data"):
            data_label = ctk.CTkLabel(
                detail_frame,
                text="任务数据:",
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w"
            )
            data_label.pack(anchor="w", padx=10, pady=(15, 5))
            
            data_text = ctk.CTkTextbox(detail_frame, height=150)
            data_text.pack(fill="x", padx=10, pady=5)
            data_text.insert("1.0", task.get("data", ""))
            data_text.configure(state="disabled")
        
        # 结果详情
        if task.get("result"):
            result_label = ctk.CTkLabel(
                detail_frame,
                text="任务结果:",
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w"
            )
            result_label.pack(anchor="w", padx=10, pady=(15, 5))
            
            result_text = ctk.CTkTextbox(detail_frame, height=100)
            result_text.pack(fill="x", padx=10, pady=5)
            result_text.insert("1.0", task.get("result", ""))
            result_text.configure(state="disabled")
        
        # 错误信息
        if task.get("error"):
            error_label = ctk.CTkLabel(
                detail_frame,
                text="错误信息:",
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w",
                text_color="red"
            )
            error_label.pack(anchor="w", padx=10, pady=(15, 5))
            
            error_text = ctk.CTkTextbox(detail_frame, height=80)
            error_text.pack(fill="x", padx=10, pady=5)
            error_text.insert("1.0", task.get("error", ""))
            error_text.configure(state="disabled")
        
        # 关闭按钮
        close_btn = ctk.CTkButton(
            dialog,
            text="关闭",
            command=dialog.destroy
        )
        close_btn.pack(pady=10)
    
    def _on_status_filter_changed(self, value: str):
        """状态筛选改变"""
        
        filter_map = {
            "全部": "all",
            "成功": "success",
            "失败": "failed"
        }
        
        self.current_filter = filter_map.get(value, "all")
        asyncio.create_task(self.load_history())
    
    def _on_time_filter_changed(self, value: str):
        """时间筛选改变"""
        
        filter_map = {
            "7天": "7days",
            "30天": "30days",
            "全部": "all"
        }
        
        self.current_time_filter = filter_map.get(value, "7days")
        asyncio.create_task(self.load_history())
    
    def _export_report(self):
        """导出Excel报告"""
        
        if not self.tasks:
            # 显示提示
            dialog = ctk.CTkToplevel(self)
            dialog.title("导出报告")
            dialog.geometry("300x150")
            
            label = ctk.CTkLabel(
                dialog,
                text="没有可导出的数据",
                font=ctk.CTkFont(size=14)
            )
            label.pack(expand=True)
            
            btn = ctk.CTkButton(
                dialog,
                text="关闭",
                command=dialog.destroy
            )
            btn.pack(pady=20)
            return
        
        # 在后台线程中运行异步导出
        import threading
        
        def run_export():
            import asyncio
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self._async_export_report())
            finally:
                loop.close()
        
        thread = threading.Thread(target=run_export, daemon=True)
        thread.start()
    
    async def _async_export_report(self):
        """异步导出Excel报告"""
        
        try:
            import pandas as pd
            from tkinter import filedialog
            from datetime import datetime
            import json
            
            # 1. 选择保存路径
            file_path = filedialog.asksaveasfilename(
                title="导出报告",
                defaultextension=".xlsx",
                filetypes=[("Excel文件", "*.xlsx")],
                initialfile=f"发布历史报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            
            if not file_path:
                return
            
            # 2. 准备数据
            data = []
            for task in self.tasks:
                task_data = task.get("data", {})
                if isinstance(task_data, str):
                    task_data = json.loads(task_data)
                
                product = task_data.get("product", {})
                
                result_data = task.get("result", {})
                if isinstance(result_data, str):
                    result_data = json.loads(result_data)
                
                data.append({
                    "任务ID": task.get("id"),
                    "商品标题": product.get("title", ""),
                    "价格": product.get("price", 0),
                    "分类": product.get("category", ""),
                    "状态": task.get("status"),
                    "进度": f"{task.get('progress', 0):.1f}%",
                    "创建时间": task.get("created_at", ""),
                    "完成时间": task.get("completed_at", ""),
                    "商品URL": result_data.get("post_url", ""),
                    "错误信息": task.get("error", "")
                })
            
            # 3. 创建DataFrame
            df = pd.DataFrame(data)
            
            # 4. 计算统计数据
            total_count = len(self.tasks)
            success_count = sum(1 for t in self.tasks if t.get("status") == "completed")
            failed_count = sum(1 for t in self.tasks if t.get("status") == "failed")
            success_rate = (success_count / total_count * 100) if total_count > 0 else 0
            
            # 5. 写入Excel
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # 任务列表工作表
                df.to_excel(writer, sheet_name='发布记录', index=False)
                
                # 统计摘要工作表
                stats = {
                    "指标": ["总发布数", "成功数", "失败数", "成功率"],
                    "数值": [
                        total_count,
                        success_count,
                        failed_count,
                        f"{success_rate:.1f}%"
                    ]
                }
                stats_df = pd.DataFrame(stats)
                stats_df.to_excel(writer, sheet_name='统计摘要', index=False)
                
                # 按状态分组统计
                if total_count > 0:
                    status_counts = {}
                    for task in self.tasks:
                        status = task.get("status", "unknown")
                        status_counts[status] = status_counts.get(status, 0) + 1
                    
                    status_data = {
                        "状态": list(status_counts.keys()),
                        "数量": list(status_counts.values())
                    }
                    status_df = pd.DataFrame(status_data)
                    status_df.to_excel(writer, sheet_name='状态分布', index=False)
            
            self._show_message(
                "导出成功", 
                f"✅ 报告已保存到:\n{file_path}\n\n导出了 {total_count} 条记录", 
                "success"
            )
            
        except Exception as e:
            print(f"❌ 导出失败: {e}")
            import traceback
            traceback.print_exc()
            self._show_message("导出失败", f"无法导出报告: {str(e)}", "error")
    
    def _clear_history(self):
        """清空历史"""
        
        # 确认对话框
        dialog = ctk.CTkToplevel(self)
        dialog.title("确认清空")
        dialog.geometry("400x200")
        
        label = ctk.CTkLabel(
            dialog,
            text="⚠️ 确定要清空所有历史记录吗？\n此操作不可恢复！",
            font=ctk.CTkFont(size=14),
            text_color="red"
        )
        label.pack(expand=True)
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="取消",
            command=dialog.destroy,
            fg_color="gray"
        )
        cancel_btn.pack(side="left", padx=10)
        
        confirm_btn = ctk.CTkButton(
            btn_frame,
            text="确认清空",
            command=lambda: self._start_clear_history(dialog),
            fg_color="red"
        )
        confirm_btn.pack(side="right", padx=10)
    
    def _start_clear_history(self, dialog):
        """启动清空历史任务"""
        
        # 在后台线程中运行
        import threading
        
        def run_clear():
            import asyncio
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self._do_clear_history(dialog))
            finally:
                loop.close()
        
        thread = threading.Thread(target=run_clear, daemon=True)
        thread.start()
    
    async def _do_clear_history(self, dialog):
        """执行清空历史"""
        
        try:
            await self.db.connect()
            
            # 清空闲鱼发布任务
            await self.db.clear_tasks(type="xianyu_publish")
            
            await self.db.close()
            
            # 在主线程中关闭对话框
            self.after(100, dialog.destroy)
            
            # 重新加载（在主线程中）
            self.after(200, lambda: self._schedule_async_task(self.load_history()))
            
            print("✅ 历史记录已清空")
            
            # 显示成功消息
            self.after(300, lambda: self._show_message(
                "清空成功", 
                "✅ 所有历史记录已清空", 
                "success"
            ))
            
        except Exception as e:
            print(f"❌ 清空失败: {e}")
            import traceback
            traceback.print_exc()
            
            # 在主线程中关闭对话框并显示错误
            self.after(100, dialog.destroy)
            self.after(200, lambda: self._show_message(
                "清空失败", 
                f"清空历史记录时出错: {str(e)}", 
                "error"
            ))


# 测试代码
if __name__ == "__main__":
    # 创建测试应用
    app = ctk.CTk()
    app.geometry("1200x800")
    app.title("发布历史测试")
    
    # 创建历史面板
    history_panel = PublishHistoryPanel(app)
    history_panel.pack(fill="both", expand=True)
    
    # 加载历史（异步）
    async def init():
        await history_panel.load_history()
    
    # 运行初始化
    app.after(100, lambda: asyncio.run(init()))
    
    app.mainloop()

