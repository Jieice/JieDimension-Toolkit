"""
JieDimension Toolkit - 仪表板
显示统计数据、快捷操作和最近任务
Version: 1.0.0
"""

import customtkinter as ctk
from tkinter import ttk
import asyncio
import os
import sys
from typing import Dict, List
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.database import Database
from ui.charts import ChartGenerator, embed_chart_in_frame
from utils.export import ExcelReportExporter
from tkinter import filedialog, messagebox


class StatCard(ctk.CTkFrame):
    """统计卡片组件"""
    
    def __init__(self, parent, title: str, value: str, icon: str, color: str = "blue"):
        super().__init__(parent, fg_color=("gray85", "gray20"), corner_radius=15)
        
        # 配置网格
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        
        # 图标
        icon_label = ctk.CTkLabel(
            self,
            text=icon,
            font=ctk.CTkFont(size=40),
            width=60
        )
        icon_label.grid(row=0, column=0, rowspan=2, padx=(20, 10), pady=20, sticky="w")
        
        # 标题
        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=14),
            text_color="gray60"
        )
        title_label.grid(row=0, column=1, padx=(0, 20), pady=(20, 0), sticky="w")
        
        # 数值
        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=color
        )
        self.value_label.grid(row=1, column=1, padx=(0, 20), pady=(0, 20), sticky="w")
    
    def update_value(self, value: str):
        """更新数值"""
        self.value_label.configure(text=value)


class Dashboard(ctk.CTkScrollableFrame):
    """仪表板主界面"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # 配置网格
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        
        # 数据库连接
        self.db = Database()
        
        # 图表生成器
        self.chart_generator = None
        
        # 图表画布
        self.chart_canvases = {}
        
        # 创建界面
        self._create_header()
        self._create_stat_cards()
        self._create_ai_provider_stats()
        self._create_charts_section()
        self._create_quick_actions()
        self._create_recent_tasks()
        
        # 加载数据
        self._load_stats()
    
    def _create_header(self):
        """创建顶部标题栏"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=4, padx=30, pady=(30, 20), sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)
        
        # 标题
        title = ctk.CTkLabel(
            header_frame,
            text="🏠 仪表板",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title.grid(row=0, column=0, sticky="w")
        
        # 当前时间
        now = datetime.now()
        time_text = now.strftime("%Y年%m月%d日 %H:%M")
        time_label = ctk.CTkLabel(
            header_frame,
            text=time_text,
            font=ctk.CTkFont(size=14),
            text_color="gray60"
        )
        time_label.grid(row=0, column=1, sticky="e")
        
        # 导出按钮
        export_btn = ctk.CTkButton(
            header_frame,
            text="📊 导出报告",
            width=110,
            command=self._export_report,
            font=ctk.CTkFont(size=14),
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40")
        )
        export_btn.grid(row=0, column=2, padx=(10, 0))
        
        # 刷新按钮
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="🔄 刷新",
            width=100,
            command=self._load_stats,
            font=ctk.CTkFont(size=14)
        )
        refresh_btn.grid(row=0, column=3, padx=(10, 0))
    
    def _create_stat_cards(self):
        """创建统计卡片区域"""
        # 标题
        section_title = ctk.CTkLabel(
            self,
            text="📊 数据统计",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w"
        )
        section_title.grid(row=1, column=0, columnspan=4, padx=30, pady=(20, 10), sticky="w")
        
        # 创建卡片
        self.stat_cards = {}
        
        cards_config = [
            ("total_products", "商品总数", "📦", "blue"),
            ("published_today", "今日发布", "🚀", "green"),
            ("ai_calls", "AI调用", "🤖", "purple"),
            ("success_rate", "成功率", "✅", "orange")
        ]
        
        for idx, (key, title, icon, color) in enumerate(cards_config):
            card = StatCard(self, title, "0", icon, color)
            card.grid(row=2, column=idx, padx=15, pady=10, sticky="ew")
            self.stat_cards[key] = card
    
    def _create_ai_provider_stats(self):
        """创建AI提供商统计区域"""
        # 标题
        section_title = ctk.CTkLabel(
            self,
            text="🤖 AI提供商使用统计",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w"
        )
        section_title.grid(row=3, column=0, columnspan=4, padx=30, pady=(20, 10), sticky="w")
        
        # 统计卡片容器
        provider_frame = ctk.CTkFrame(self, fg_color="transparent")
        provider_frame.grid(row=4, column=0, columnspan=4, padx=30, pady=10, sticky="ew")
        provider_frame.grid_columnconfigure(0, weight=1)
        provider_frame.grid_columnconfigure(1, weight=1)
        
        # Ollama 统计卡片
        ollama_card = ctk.CTkFrame(provider_frame, fg_color=("gray85", "gray20"), corner_radius=15)
        ollama_card.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        ollama_card.grid_columnconfigure(1, weight=1)
        
        # Ollama 图标和标题
        ollama_header = ctk.CTkFrame(ollama_card, fg_color="transparent")
        ollama_header.grid(row=0, column=0, columnspan=2, padx=20, pady=(15, 10), sticky="ew")
        
        ollama_icon = ctk.CTkLabel(
            ollama_header,
            text="🔵",
            font=ctk.CTkFont(size=24)
        )
        ollama_icon.pack(side="left", padx=(0, 10))
        
        ollama_title = ctk.CTkLabel(
            ollama_header,
            text="Ollama (本地)",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        ollama_title.pack(side="left")
        
        # Ollama 统计数据
        self.ollama_stats_labels = {}
        ollama_stats = [
            ("ollama_calls", "总调用", "0"),
            ("ollama_success", "成功率", "0%"),
            ("ollama_avg_latency", "平均延迟", "0s")
        ]
        
        for idx, (key, label_text, default_value) in enumerate(ollama_stats):
            label = ctk.CTkLabel(
                ollama_card,
                text=label_text,
                font=ctk.CTkFont(size=13),
                text_color="gray60"
            )
            label.grid(row=idx+1, column=0, padx=20, pady=5, sticky="w")
            
            value_label = ctk.CTkLabel(
                ollama_card,
                text=default_value,
                font=ctk.CTkFont(size=16, weight="bold")
            )
            value_label.grid(row=idx+1, column=1, padx=20, pady=5, sticky="e")
            self.ollama_stats_labels[key] = value_label
        
        # 底部间距
        ctk.CTkLabel(ollama_card, text="", height=5).grid(row=4, column=0)
        
        # Gemini 统计卡片
        gemini_card = ctk.CTkFrame(provider_frame, fg_color=("gray85", "gray20"), corner_radius=15)
        gemini_card.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        gemini_card.grid_columnconfigure(1, weight=1)
        
        # Gemini 图标和标题
        gemini_header = ctk.CTkFrame(gemini_card, fg_color="transparent")
        gemini_header.grid(row=0, column=0, columnspan=2, padx=20, pady=(15, 10), sticky="ew")
        
        gemini_icon = ctk.CTkLabel(
            gemini_header,
            text="✨",
            font=ctk.CTkFont(size=24)
        )
        gemini_icon.pack(side="left", padx=(0, 10))
        
        gemini_title = ctk.CTkLabel(
            gemini_header,
            text="Gemini (云端)",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        gemini_title.pack(side="left")
        
        # Gemini 统计数据
        self.gemini_stats_labels = {}
        gemini_stats = [
            ("gemini_calls", "总调用", "0"),
            ("gemini_success", "成功率", "0%"),
            ("gemini_avg_latency", "平均延迟", "0s")
        ]
        
        for idx, (key, label_text, default_value) in enumerate(gemini_stats):
            label = ctk.CTkLabel(
                gemini_card,
                text=label_text,
                font=ctk.CTkFont(size=13),
                text_color="gray60"
            )
            label.grid(row=idx+1, column=0, padx=20, pady=5, sticky="w")
            
            value_label = ctk.CTkLabel(
                gemini_card,
                text=default_value,
                font=ctk.CTkFont(size=16, weight="bold")
            )
            value_label.grid(row=idx+1, column=1, padx=20, pady=5, sticky="e")
            self.gemini_stats_labels[key] = value_label
        
        # 底部间距
        ctk.CTkLabel(gemini_card, text="", height=5).grid(row=4, column=0)
    
    def _create_charts_section(self):
        """创建图表区域"""
        # 标题
        section_title = ctk.CTkLabel(
            self,
            text="📊 数据可视化",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w"
        )
        section_title.grid(row=5, column=0, columnspan=4, padx=30, pady=(20, 10), sticky="w")
        
        # 图表容器
        charts_frame = ctk.CTkFrame(self, fg_color="transparent")
        charts_frame.grid(row=6, column=0, columnspan=4, padx=30, pady=10, sticky="ew")
        charts_frame.grid_columnconfigure(0, weight=1)
        charts_frame.grid_columnconfigure(1, weight=1)
        
        # AI使用趋势图容器
        ai_trend_container = ctk.CTkFrame(charts_frame, fg_color=("gray85", "gray20"), corner_radius=15)
        ai_trend_container.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        ai_trend_container.grid_columnconfigure(0, weight=1)
        ai_trend_container.grid_rowconfigure(1, weight=1)
        
        # 图表标题
        ai_trend_title = ctk.CTkLabel(
            ai_trend_container,
            text="🤖 AI调用趋势",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        ai_trend_title.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        
        # 图表占位区域
        self.ai_trend_chart_frame = ctk.CTkFrame(ai_trend_container, fg_color="transparent")
        self.ai_trend_chart_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # 发布统计图容器
        publish_stats_container = ctk.CTkFrame(charts_frame, fg_color=("gray85", "gray20"), corner_radius=15)
        publish_stats_container.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        publish_stats_container.grid_columnconfigure(0, weight=1)
        publish_stats_container.grid_rowconfigure(1, weight=1)
        
        # 图表标题
        publish_stats_title = ctk.CTkLabel(
            publish_stats_container,
            text="📈 发布统计",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        publish_stats_title.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        
        # 图表占位区域
        self.publish_stats_chart_frame = ctk.CTkFrame(publish_stats_container, fg_color="transparent")
        self.publish_stats_chart_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # 设置图表容器高度
        charts_frame.grid_rowconfigure(0, minsize=350)
    
    def _create_quick_actions(self):
        """创建快捷操作区域"""
        # 标题
        section_title = ctk.CTkLabel(
            self,
            text="⚡ 快捷操作",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w"
        )
        section_title.grid(row=7, column=0, columnspan=4, padx=30, pady=(30, 10), sticky="w")
        
        # 快捷操作卡片
        actions_frame = ctk.CTkFrame(self, fg_color=("gray85", "gray20"), corner_radius=15)
        actions_frame.grid(row=8, column=0, columnspan=4, padx=30, pady=10, sticky="ew")
        actions_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        actions = [
            ("📦 闲鱼发布", "发布新商品到闲鱼", self._goto_xianyu),
            ("🤖 AI优化", "优化商品标题描述", self._goto_ai),
            ("📊 数据导入", "从Excel导入商品", self._goto_import),
            ("⚙️ 系统设置", "配置AI和插件", self._goto_settings),
        ]
        
        for idx, (title, desc, command) in enumerate(actions):
            action_btn = ctk.CTkButton(
                actions_frame,
                text=f"{title}\n{desc}",
                height=80,
                font=ctk.CTkFont(size=14),
                command=command,
                fg_color=("gray70", "gray30"),
                hover_color=("gray60", "gray40")
            )
            action_btn.grid(row=0, column=idx, padx=15, pady=15, sticky="ew")
    
    def _create_recent_tasks(self):
        """创建最近任务列表"""
        # 标题
        section_title = ctk.CTkLabel(
            self,
            text="📝 最近任务",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w"
        )
        section_title.grid(row=9, column=0, columnspan=4, padx=30, pady=(30, 10), sticky="w")
        
        # 任务列表框架
        tasks_frame = ctk.CTkFrame(self, fg_color=("gray85", "gray20"), corner_radius=15)
        tasks_frame.grid(row=10, column=0, columnspan=4, padx=30, pady=(10, 30), sticky="ew")
        tasks_frame.grid_columnconfigure(0, weight=1)
        
        # 表格标题
        header_frame = ctk.CTkFrame(tasks_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=2)
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_columnconfigure(2, weight=1)
        header_frame.grid_columnconfigure(3, weight=1)
        
        headers = ["任务名称", "平台", "状态", "时间"]
        for idx, header in enumerate(headers):
            label = ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="gray60"
            )
            label.grid(row=0, column=idx, padx=10, sticky="w")
        
        # 任务列表容器
        self.tasks_container = ctk.CTkFrame(tasks_frame, fg_color="transparent")
        self.tasks_container.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.tasks_container.grid_columnconfigure(0, weight=1)
    
    def _load_stats(self):
        """加载统计数据"""
        asyncio.run(self._async_load_stats())
    
    async def _async_load_stats(self):
        """异步加载统计数据"""
        try:
            await self.db.connect()
            
            # 创建图表生成器
            if self.chart_generator is None:
                self.chart_generator = ChartGenerator(self.db)
            
            # 获取商品总数
            total_products = await self.db.count_products()
            self.stat_cards["total_products"].update_value(str(total_products))
            
            # 获取今日发布数量（从任务表）
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            tasks = await self.db.get_tasks_by_date_range(
                today_start.isoformat(),
                datetime.now().isoformat()
            )
            published_today = len([t for t in tasks if t['status'] == 'completed'])
            self.stat_cards["published_today"].update_value(str(published_today))
            
            # 获取AI调用次数
            ai_stats = await self.db.get_ai_stats_summary()
            total_calls = ai_stats.get('total_calls', 0)
            self.stat_cards["ai_calls"].update_value(str(total_calls))
            
            # 计算成功率
            if len(tasks) > 0:
                success_count = len([t for t in tasks if t['status'] == 'completed'])
                success_rate = int((success_count / len(tasks)) * 100)
                self.stat_cards["success_rate"].update_value(f"{success_rate}%")
            else:
                self.stat_cards["success_rate"].update_value("0%")
            
            # 加载AI提供商统计
            await self._load_ai_provider_stats()
            
            # 加载图表
            await self._load_charts()
            
            # 加载最近任务
            await self._load_recent_tasks()
            
        except Exception as e:
            print(f"加载统计数据失败: {e}")
        finally:
            await self.db.close()
    
    async def _load_charts(self):
        """加载图表"""
        try:
            # 清除旧图表
            for canvas in self.chart_canvases.values():
                if canvas:
                    canvas.get_tk_widget().destroy()
            self.chart_canvases.clear()
            
            # 生成AI使用趋势图
            try:
                ai_trend_fig = await self.chart_generator.create_ai_usage_trend_chart(days=7)
                ai_trend_canvas = embed_chart_in_frame(self.ai_trend_chart_frame, ai_trend_fig)
                ai_trend_canvas.get_tk_widget().pack(fill="both", expand=True)
                self.chart_canvases['ai_trend'] = ai_trend_canvas
            except Exception as e:
                print(f"加载AI使用趋势图失败: {e}")
            
            # 生成发布统计图
            try:
                publish_stats_fig = await self.chart_generator.create_publish_stats_chart(days=30)
                publish_stats_canvas = embed_chart_in_frame(self.publish_stats_chart_frame, publish_stats_fig)
                publish_stats_canvas.get_tk_widget().pack(fill="both", expand=True)
                self.chart_canvases['publish_stats'] = publish_stats_canvas
            except Exception as e:
                print(f"加载发布统计图失败: {e}")
            
        except Exception as e:
            print(f"加载图表失败: {e}")
    
    async def _load_ai_provider_stats(self):
        """加载AI提供商统计数据"""
        try:
            # 获取Ollama统计
            ollama_stats = await self.db.get_ai_stats(provider="ollama")
            if ollama_stats:
                stats = ollama_stats[0]
                self.ollama_stats_labels["ollama_calls"].configure(
                    text=str(stats.get('total_calls', 0))
                )
                
                total = stats.get('total_calls', 0)
                success = stats.get('success_count', 0)
                success_rate = (success / total * 100) if total > 0 else 0
                self.ollama_stats_labels["ollama_success"].configure(
                    text=f"{success_rate:.1f}%"
                )
                
                avg_latency = stats.get('avg_latency', 0)
                self.ollama_stats_labels["ollama_avg_latency"].configure(
                    text=f"{avg_latency:.2f}s" if avg_latency else "0s"
                )
            
            # 获取Gemini统计
            gemini_stats = await self.db.get_ai_stats(provider="gemini")
            if gemini_stats:
                stats = gemini_stats[0]
                self.gemini_stats_labels["gemini_calls"].configure(
                    text=str(stats.get('total_calls', 0))
                )
                
                total = stats.get('total_calls', 0)
                success = stats.get('success_count', 0)
                success_rate = (success / total * 100) if total > 0 else 0
                self.gemini_stats_labels["gemini_success"].configure(
                    text=f"{success_rate:.1f}%"
                )
                
                avg_latency = stats.get('avg_latency', 0)
                self.gemini_stats_labels["gemini_avg_latency"].configure(
                    text=f"{avg_latency:.2f}s" if avg_latency else "0s"
                )
                
        except Exception as e:
            print(f"加载AI提供商统计失败: {e}")
    
    async def _load_recent_tasks(self):
        """加载最近任务"""
        try:
            # 清空现有任务
            for widget in self.tasks_container.winfo_children():
                widget.destroy()
            
            # 获取最近10个任务
            end_time = datetime.now().isoformat()
            start_time = (datetime.now() - timedelta(days=7)).isoformat()
            tasks = await self.db.get_tasks_by_date_range(start_time, end_time)
            
            # 按时间倒序排序，取前10个
            tasks = sorted(tasks, key=lambda x: x['created_at'], reverse=True)[:10]
            
            if not tasks:
                # 显示空状态
                empty_label = ctk.CTkLabel(
                    self.tasks_container,
                    text="暂无任务记录",
                    font=ctk.CTkFont(size=14),
                    text_color="gray60"
                )
                empty_label.grid(row=0, column=0, pady=20)
                return
            
            # 显示任务列表
            for idx, task in enumerate(tasks):
                task_frame = ctk.CTkFrame(
                    self.tasks_container,
                    fg_color=("gray90", "gray25") if idx % 2 == 0 else "transparent",
                    corner_radius=8
                )
                task_frame.grid(row=idx, column=0, pady=2, sticky="ew")
                task_frame.grid_columnconfigure(0, weight=2)
                task_frame.grid_columnconfigure(1, weight=1)
                task_frame.grid_columnconfigure(2, weight=1)
                task_frame.grid_columnconfigure(3, weight=1)
                
                # 任务名称
                name = ctk.CTkLabel(
                    task_frame,
                    text=task['task_name'][:40] + "..." if len(task['task_name']) > 40 else task['task_name'],
                    font=ctk.CTkFont(size=13),
                    anchor="w"
                )
                name.grid(row=0, column=0, padx=10, pady=10, sticky="w")
                
                # 平台
                platform_icon = {
                    'xianyu': '🐟',
                    'xiaohongshu': '📝',
                    'zhihu': '📖',
                    'bilibili': '🎬'
                }.get(task['platform'], '📦')
                
                platform = ctk.CTkLabel(
                    task_frame,
                    text=f"{platform_icon} {task['platform'].upper()}",
                    font=ctk.CTkFont(size=13)
                )
                platform.grid(row=0, column=1, padx=10, pady=10, sticky="w")
                
                # 状态
                status_config = {
                    'completed': ('✅ 成功', 'green'),
                    'failed': ('❌ 失败', 'red'),
                    'pending': ('⏳ 等待', 'orange'),
                    'processing': ('🔄 处理中', 'blue')
                }
                status_text, status_color = status_config.get(task['status'], ('❓ 未知', 'gray'))
                
                status = ctk.CTkLabel(
                    task_frame,
                    text=status_text,
                    font=ctk.CTkFont(size=13),
                    text_color=status_color
                )
                status.grid(row=0, column=2, padx=10, pady=10, sticky="w")
                
                # 时间
                try:
                    task_time = datetime.fromisoformat(task['created_at'])
                    time_diff = datetime.now() - task_time
                    
                    if time_diff.days > 0:
                        time_text = f"{time_diff.days}天前"
                    elif time_diff.seconds >= 3600:
                        time_text = f"{time_diff.seconds // 3600}小时前"
                    elif time_diff.seconds >= 60:
                        time_text = f"{time_diff.seconds // 60}分钟前"
                    else:
                        time_text = "刚刚"
                except:
                    time_text = "未知"
                
                time_label = ctk.CTkLabel(
                    task_frame,
                    text=time_text,
                    font=ctk.CTkFont(size=12),
                    text_color="gray60"
                )
                time_label.grid(row=0, column=3, padx=10, pady=10, sticky="w")
                
        except Exception as e:
            print(f"加载最近任务失败: {e}")
    
    def _goto_xianyu(self):
        """跳转到闲鱼发布"""
        # 获取主窗口并切换页面
        main_window = self.winfo_toplevel()
        if hasattr(main_window, 'show_xianyu'):
            main_window.show_xianyu()
    
    def _goto_ai(self):
        """跳转到AI助手"""
        main_window = self.winfo_toplevel()
        if hasattr(main_window, 'show_ai_assistant'):
            main_window.show_ai_assistant()
    
    def _goto_import(self):
        """跳转到数据导入（闲鱼页面）"""
        self._goto_xianyu()
    
    def _goto_settings(self):
        """跳转到设置"""
        main_window = self.winfo_toplevel()
        if hasattr(main_window, 'show_settings'):
            main_window.show_settings()
    
    def _export_report(self):
        """导出Excel报告"""
        # 选择保存位置
        default_filename = f"JieDimension_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")],
            initialfile=default_filename
        )
        
        if not filepath:
            return
        
        # 在后台导出
        asyncio.run(self._async_export_report(filepath))
    
    async def _async_export_report(self, filepath: str):
        """异步导出报告"""
        try:
            # 连接数据库
            await self.db.connect()
            
            # 创建导出器
            exporter = ExcelReportExporter(self.db)
            
            # 导出报告
            success = await exporter.export_full_report(filepath, days=30)
            
            # 关闭数据库
            await self.db.close()
            
            # 显示结果
            if success:
                messagebox.showinfo(
                    "导出成功",
                    f"报告已成功导出到:\n{filepath}"
                )
            else:
                messagebox.showerror(
                    "导出失败",
                    "报告导出失败，请查看控制台输出了解详情。"
                )
        except Exception as e:
            messagebox.showerror(
                "导出错误",
                f"导出报告时发生错误:\n{str(e)}"
            )
            print(f"导出错误: {e}")


# ===== 测试函数 =====

def main():
    """测试仪表板"""
    root = ctk.CTk()
    root.title("仪表板测试")
    root.geometry("1200x800")
    ctk.set_appearance_mode("dark")
    
    dashboard = Dashboard(root)
    dashboard.pack(fill="both", expand=True)
    
    root.mainloop()


if __name__ == "__main__":
    main()

