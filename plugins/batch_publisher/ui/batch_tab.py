"""
批量发布界面

提供跨平台一键发布的图形界面
"""

import customtkinter as ctk
import asyncio
import threading
from typing import Optional
from tkinter import messagebox

from core.publisher import PublishContent, PlatformType
from plugins.batch_publisher.task_manager import BatchPublishManager, PublishTask


class BatchPublishTab(ctk.CTkFrame):
    """批量发布选项卡"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # 批量发布管理器
        self.manager = BatchPublishManager()
        
        # 当前任务
        self.current_task: Optional[PublishTask] = None
        self.current_task_id: Optional[str] = None
        
        # 创建UI
        self._create_ui()
        
        # 注册进度回调
        self.manager.add_progress_callback(self._on_progress_update)
    
    def _create_ui(self):
        """创建用户界面"""
        
        # 配置网格
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # 主滚动区域
        scroll_frame = ctk.CTkScrollableFrame(self)
        scroll_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # 标题
        title_label = ctk.CTkLabel(
            scroll_frame,
            text="🚀 批量发布系统",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # 内容输入区
        self._create_content_input_section(scroll_frame)
        
        # 平台选择区
        self._create_platform_selection_section(scroll_frame)
        
        # 高级设置区
        self._create_advanced_settings_section(scroll_frame)
        
        # 操作按钮区
        self._create_action_buttons_section(scroll_frame)
        
        # 进度显示区
        self._create_progress_section(scroll_frame)
        
        # 结果展示区
        self._create_results_section(scroll_frame)
    
    def _create_content_input_section(self, parent):
        """创建内容输入区"""
        
        section = ctk.CTkFrame(parent, fg_color=("gray90", "gray17"))
        section.pack(fill="x", padx=10, pady=10)
        
        # 标题
        section_title = ctk.CTkLabel(
            section,
            text="📝 发布内容",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        section_title.pack(anchor="w", padx=15, pady=10)
        
        # 标题输入
        title_frame = ctk.CTkFrame(section, fg_color="transparent")
        title_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            title_frame,
            text="标题:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 10))
        
        self.title_entry = ctk.CTkEntry(
            title_frame,
            placeholder_text="输入发布标题...",
            height=35
        )
        self.title_entry.pack(side="left", fill="x", expand=True)
        
        # 内容输入
        content_label = ctk.CTkLabel(
            section,
            text="正文内容:",
            font=ctk.CTkFont(size=13)
        )
        content_label.pack(anchor="w", padx=15, pady=(10, 5))
        
        self.content_text = ctk.CTkTextbox(
            section,
            height=150,
            font=ctk.CTkFont(size=12)
        )
        self.content_text.pack(fill="x", padx=15, pady=(0, 10))
        
        # 描述/简介输入
        desc_label = ctk.CTkLabel(
            section,
            text="描述/简介（可选）:",
            font=ctk.CTkFont(size=13)
        )
        desc_label.pack(anchor="w", padx=15, pady=(5, 5))
        
        self.description_text = ctk.CTkTextbox(
            section,
            height=80,
            font=ctk.CTkFont(size=12)
        )
        self.description_text.pack(fill="x", padx=15, pady=(0, 10))
        
        # 标签输入
        tags_frame = ctk.CTkFrame(section, fg_color="transparent")
        tags_frame.pack(fill="x", padx=15, pady=(5, 10))
        
        ctk.CTkLabel(
            tags_frame,
            text="标签（用逗号分隔）:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 10))
        
        self.tags_entry = ctk.CTkEntry(
            tags_frame,
            placeholder_text="例如：技术,教程,分享",
            height=35
        )
        self.tags_entry.pack(side="left", fill="x", expand=True)
    
    def _create_platform_selection_section(self, parent):
        """创建平台选择区"""
        
        section = ctk.CTkFrame(parent, fg_color=("gray90", "gray17"))
        section.pack(fill="x", padx=10, pady=10)
        
        # 标题
        section_title = ctk.CTkLabel(
            section,
            text="🌐 目标平台",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        section_title.pack(anchor="w", padx=15, pady=10)
        
        # 平台复选框
        platforms_frame = ctk.CTkFrame(section, fg_color="transparent")
        platforms_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        # 平台列表
        self.platform_vars = {}
        platforms = [
            ("🛒 闲鱼", "xianyu", "二手交易、虚拟产品"),
            ("📝 小红书", "xiaohongshu", "生活分享、种草笔记"),
            ("📖 知乎", "zhihu", "专业问答、深度文章"),
            ("🎬 B站", "bilibili", "视频动态、创作分享"),
        ]
        
        for idx, (name, platform_id, desc) in enumerate(platforms):
            # 复选框变量
            var = ctk.BooleanVar(value=False)
            self.platform_vars[platform_id] = var
            
            # 平台卡片
            platform_card = ctk.CTkFrame(platforms_frame, fg_color=("gray85", "gray20"))
            platform_card.grid(row=idx // 2, column=idx % 2, padx=5, pady=5, sticky="ew")
            
            # 复选框和名称
            checkbox = ctk.CTkCheckBox(
                platform_card,
                text=name,
                variable=var,
                font=ctk.CTkFont(size=14, weight="bold")
            )
            checkbox.pack(anchor="w", padx=10, pady=(10, 0))
            
            # 描述
            desc_label = ctk.CTkLabel(
                platform_card,
                text=desc,
                font=ctk.CTkFont(size=11),
                text_color="gray"
            )
            desc_label.pack(anchor="w", padx=10, pady=(0, 10))
        
        # 配置列权重
        platforms_frame.grid_columnconfigure(0, weight=1)
        platforms_frame.grid_columnconfigure(1, weight=1)
        
        # 快捷选择按钮
        quick_select_frame = ctk.CTkFrame(section, fg_color="transparent")
        quick_select_frame.pack(fill="x", padx=15, pady=(5, 10))
        
        ctk.CTkButton(
            quick_select_frame,
            text="全选",
            width=100,
            command=self._select_all_platforms
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            quick_select_frame,
            text="取消全选",
            width=100,
            command=self._deselect_all_platforms
        ).pack(side="left", padx=5)
    
    def _create_advanced_settings_section(self, parent):
        """创建高级设置区"""
        
        section = ctk.CTkFrame(parent, fg_color=("gray90", "gray17"))
        section.pack(fill="x", padx=10, pady=10)
        
        # 标题
        section_title = ctk.CTkLabel(
            section,
            text="⚙️ 高级设置",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        section_title.pack(anchor="w", padx=15, pady=10)
        
        # 重试次数
        retry_frame = ctk.CTkFrame(section, fg_color="transparent")
        retry_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            retry_frame,
            text="失败重试次数:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 10))
        
        self.retry_var = ctk.IntVar(value=3)
        self.retry_slider = ctk.CTkSlider(
            retry_frame,
            from_=0,
            to=5,
            number_of_steps=5,
            variable=self.retry_var
        )
        self.retry_slider.pack(side="left", fill="x", expand=True, padx=10)
        
        self.retry_label = ctk.CTkLabel(
            retry_frame,
            text="3次",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.retry_label.pack(side="left")
        
        # 更新标签
        self.retry_var.trace_add("write", self._update_retry_label)
        
        # 说明文本
        info_label = ctk.CTkLabel(
            section,
            text="💡 发布失败时会自动重试，提高成功率",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        info_label.pack(anchor="w", padx=15, pady=(0, 10))
    
    def _create_action_buttons_section(self, parent):
        """创建操作按钮区"""
        
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=20)
        
        # 开始发布按钮
        self.publish_button = ctk.CTkButton(
            button_frame,
            text="🚀 开始发布",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            command=self._on_publish_click
        )
        self.publish_button.pack(side="left", fill="x", expand=True, padx=5)
        
        # 清空按钮
        ctk.CTkButton(
            button_frame,
            text="🗑️ 清空",
            font=ctk.CTkFont(size=14),
            height=45,
            width=100,
            fg_color="gray",
            command=self._on_clear_click
        ).pack(side="left", padx=5)
    
    def _create_progress_section(self, parent):
        """创建进度显示区"""
        
        self.progress_frame = ctk.CTkFrame(parent, fg_color=("gray90", "gray17"))
        self.progress_frame.pack(fill="x", padx=10, pady=10)
        self.progress_frame.pack_forget()  # 初始隐藏
        
        # 标题
        ctk.CTkLabel(
            self.progress_frame,
            text="📊 发布进度",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=10)
        
        # 进度条
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            height=25
        )
        self.progress_bar.pack(fill="x", padx=15, pady=(0, 10))
        self.progress_bar.set(0)
        
        # 状态文本
        self.progress_status_label = ctk.CTkLabel(
            self.progress_frame,
            text="准备开始...",
            font=ctk.CTkFont(size=12)
        )
        self.progress_status_label.pack(anchor="w", padx=15, pady=(0, 10))
    
    def _create_results_section(self, parent):
        """创建结果展示区"""
        
        self.results_frame = ctk.CTkFrame(parent, fg_color=("gray90", "gray17"))
        self.results_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.results_frame.pack_forget()  # 初始隐藏
        
        # 标题
        ctk.CTkLabel(
            self.results_frame,
            text="📋 发布结果",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=10)
        
        # 结果文本框
        self.results_text = ctk.CTkTextbox(
            self.results_frame,
            height=200,
            font=ctk.CTkFont(family="Courier", size=11)
        )
        self.results_text.pack(fill="both", expand=True, padx=15, pady=(0, 10))
    
    def _select_all_platforms(self):
        """全选平台"""
        for var in self.platform_vars.values():
            var.set(True)
    
    def _deselect_all_platforms(self):
        """取消全选"""
        for var in self.platform_vars.values():
            var.set(False)
    
    def _update_retry_label(self, *args):
        """更新重试次数标签"""
        value = self.retry_var.get()
        self.retry_label.configure(text=f"{value}次")
    
    def _on_publish_click(self):
        """点击发布按钮"""
        
        # 验证输入
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showerror("错误", "请输入标题")
            return
        
        # 获取选中的平台
        selected_platforms = [
            platform_id 
            for platform_id, var in self.platform_vars.items() 
            if var.get()
        ]
        
        if not selected_platforms:
            messagebox.showerror("错误", "请至少选择一个平台")
            return
        
        # 收集内容
        content = PublishContent(
            title=title,
            content=self.content_text.get("1.0", "end").strip(),
            description=self.description_text.get("1.0", "end").strip(),
            tags=self.tags_entry.get().strip()
        )
        
        # 创建任务
        try:
            max_retries = self.retry_var.get()
            self.current_task_id = self.manager.create_task(
                content=content,
                platforms=selected_platforms,
                max_retries=max_retries
            )
            
            # 显示进度区域
            self.progress_frame.pack(fill="x", padx=10, pady=10, before=self.results_frame)
            self.progress_bar.set(0)
            self.progress_status_label.configure(text="准备开始...")
            
            # 禁用发布按钮
            self.publish_button.configure(state="disabled", text="发布中...")
            
            # 在后台线程执行任务
            thread = threading.Thread(target=self._execute_task_thread)
            thread.daemon = True
            thread.start()
        
        except Exception as e:
            messagebox.showerror("错误", f"创建任务失败: {e}")
    
    def _execute_task_thread(self):
        """在后台线程执行任务"""
        try:
            # 创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 执行任务
            task = loop.run_until_complete(
                self.manager.execute_task(self.current_task_id)
            )
            
            # 关闭循环
            loop.close()
            
            # 保存任务
            self.current_task = task
            
            # 在主线程显示结果
            self.after(0, self._show_results)
        
        except Exception as e:
            print(f"❌ 任务执行错误: {e}")
            self.after(0, lambda: messagebox.showerror("错误", f"发布失败: {e}"))
            self.after(0, self._reset_ui)
    
    def _on_progress_update(self, task_id: str, progress: float, status: str):
        """进度更新回调（在后台线程调用）"""
        if task_id == self.current_task_id:
            # 在主线程更新UI
            self.after(0, lambda: self._update_progress_ui(progress, status))
    
    def _update_progress_ui(self, progress: float, status: str):
        """更新进度UI（主线程）"""
        self.progress_bar.set(progress / 100)
        self.progress_status_label.configure(text=status)
    
    def _show_results(self):
        """显示发布结果"""
        if not self.current_task:
            return
        
        # 显示结果区域
        self.results_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 清空文本框
        self.results_text.delete("1.0", "end")
        
        # 生成结果文本
        task = self.current_task
        result_text = f"{'='*50}\n"
        result_text += f"📊 发布完成摘要\n"
        result_text += f"{'='*50}\n\n"
        result_text += f"标题: {task.content.title}\n"
        result_text += f"目标平台: {task.total_platforms}个\n"
        result_text += f"成功: {task.completed_platforms - task.failed_platforms}个\n"
        result_text += f"失败: {task.failed_platforms}个\n"
        result_text += f"成功率: {task.success_rate * 100:.1f}%\n\n"
        
        result_text += f"详细结果:\n"
        result_text += f"{'-'*50}\n"
        
        for result in task.results:
            status_icon = "✅" if result.success else "❌"
            result_text += f"\n{status_icon} {result.platform.value.upper()}\n"
            result_text += f"   状态: {result.status.value}\n"
            
            if result.post_url:
                result_text += f"   链接: {result.post_url}\n"
            
            if result.duration > 0:
                result_text += f"   耗时: {result.duration:.2f}秒\n"
            
            if result.error:
                result_text += f"   错误: {result.error}\n"
        
        # 插入文本
        self.results_text.insert("1.0", result_text)
        
        # 重置UI
        self._reset_ui()
        
        # 显示完成消息
        success_count = task.completed_platforms - task.failed_platforms
        if task.failed_platforms == 0:
            messagebox.showinfo("成功", f"🎉 发布成功！内容已发布到 {success_count} 个平台。")
        elif success_count > 0:
            messagebox.showwarning("部分成功", f"发布部分成功：{success_count} 个成功，{task.failed_platforms} 个失败。")
        else:
            messagebox.showerror("失败", "❌ 发布失败，所有平台都未成功。")
    
    def _reset_ui(self):
        """重置UI状态"""
        self.publish_button.configure(state="normal", text="🚀 开始发布")
    
    def _on_clear_click(self):
        """点击清空按钮"""
        self.title_entry.delete(0, "end")
        self.content_text.delete("1.0", "end")
        self.description_text.delete("1.0", "end")
        self.tags_entry.delete(0, "end")
        self._deselect_all_platforms()
        
        # 隐藏进度和结果区域
        self.progress_frame.pack_forget()
        self.results_frame.pack_forget()

