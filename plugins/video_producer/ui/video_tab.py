"""
视频生产Tab - GUI界面
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import asyncio
import threading
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))


class VideoProductionTab(ctk.CTkFrame):
    """视频生产界面"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # 配置网格
        self.grid_columnconfigure(0, weight=1)
        
        # 创建界面
        self._create_ui()
    
    def _create_ui(self):
        """创建用户界面"""
        # 标题
        title_label = ctk.CTkLabel(
            self,
            text="🎬 自动化视频生产",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # 内容源选择
        self._create_source_section()
        
        # 爆款分析
        self._create_analysis_section()
        
        # 视频生成
        self._create_generation_section()
        
        # 发布设置
        self._create_publish_section()
        
        # 操作按钮
        self._create_actions()
        
        # 结果显示
        self._create_result_section()
    
    def _create_source_section(self):
        """创建内容源选择区域"""
        frame = ctk.CTkFrame(self, fg_color=("gray90", "gray20"))
        frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        frame.grid_columnconfigure(1, weight=1)
        
        label = ctk.CTkLabel(
            frame,
            text="📝 内容源",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        label.grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 10), sticky="w")
        
        # 选择内容源
        self.source_var = ctk.StringVar(value="zhihu")
        sources = [
            ("知乎热榜", "zhihu"),
            ("B站热门", "bilibili"),
            ("今日头条", "toutiao")
        ]
        
        for i, (text, value) in enumerate(sources):
            radio = ctk.CTkRadioButton(
                frame,
                text=text,
                variable=self.source_var,
                value=value
            )
            radio.grid(row=1, column=i, padx=15, pady=(0, 15), sticky="w")
    
    def _create_analysis_section(self):
        """创建爆款分析区域"""
        frame = ctk.CTkFrame(self, fg_color=("gray90", "gray20"))
        frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        label = ctk.CTkLabel(
            frame,
            text="🔍 爆款分析",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        label.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")
        
        # 分析选项
        self.analyze_title_var = ctk.BooleanVar(value=True)
        self.analyze_content_var = ctk.BooleanVar(value=True)
        self.analyze_data_var = ctk.BooleanVar(value=True)
        
        ctk.CTkCheckBox(
            frame,
            text="分析标题吸引力",
            variable=self.analyze_title_var
        ).grid(row=1, column=0, padx=15, pady=5, sticky="w")
        
        ctk.CTkCheckBox(
            frame,
            text="分析内容质量",
            variable=self.analyze_content_var
        ).grid(row=2, column=0, padx=15, pady=5, sticky="w")
        
        ctk.CTkCheckBox(
            frame,
            text="分析数据表现",
            variable=self.analyze_data_var
        ).grid(row=3, column=0, padx=15, pady=(5, 15), sticky="w")
    
    def _create_generation_section(self):
        """创建视频生成区域"""
        frame = ctk.CTkFrame(self, fg_color=("gray90", "gray20"))
        frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        frame.grid_columnconfigure(1, weight=1)
        
        label = ctk.CTkLabel(
            frame,
            text="🎥 视频设置",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        label.grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 10), sticky="w")
        
        # 视频数量
        ctk.CTkLabel(frame, text="生成数量:").grid(row=1, column=0, padx=15, pady=5, sticky="w")
        self.video_count_var = ctk.StringVar(value="2")
        ctk.CTkEntry(frame, textvariable=self.video_count_var, width=100).grid(row=1, column=1, padx=15, pady=5, sticky="w")
        
        # 视频时长
        ctk.CTkLabel(frame, text="视频时长:").grid(row=2, column=0, padx=15, pady=5, sticky="w")
        self.duration_var = ctk.StringVar(value="60秒")
        ctk.CTkOptionMenu(frame, variable=self.duration_var, values=["30秒", "60秒", "90秒"]).grid(row=2, column=1, padx=15, pady=5, sticky="w")
        
        # 视频风格
        ctk.CTkLabel(frame, text="视频风格:").grid(row=3, column=0, padx=15, pady=(5, 15), sticky="w")
        self.style_var = ctk.StringVar(value="解说")
        ctk.CTkOptionMenu(frame, variable=self.style_var, values=["解说", "吐槽", "严肃", "幽默"]).grid(row=3, column=1, padx=15, pady=(5, 15), sticky="w")
    
    def _create_publish_section(self):
        """创建发布设置区域"""
        frame = ctk.CTkFrame(self, fg_color=("gray90", "gray20"))
        frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        
        label = ctk.CTkLabel(
            frame,
            text="🚀 发布平台",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        label.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")
        
        # 平台选择
        self.publish_bilibili_var = ctk.BooleanVar(value=True)
        self.publish_douyin_var = ctk.BooleanVar(value=False)
        
        ctk.CTkCheckBox(
            frame,
            text="B站",
            variable=self.publish_bilibili_var
        ).grid(row=1, column=0, padx=15, pady=5, sticky="w")
        
        ctk.CTkCheckBox(
            frame,
            text="抖音",
            variable=self.publish_douyin_var
        ).grid(row=2, column=0, padx=15, pady=(5, 15), sticky="w")
    
    def _create_actions(self):
        """创建操作按钮"""
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=5, column=0, padx=20, pady=20, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)
        
        buttons_frame = ctk.CTkFrame(frame, fg_color="transparent")
        buttons_frame.grid(row=0, column=0)
        
        # 分析按钮
        ctk.CTkButton(
            buttons_frame,
            text="🔍 分析爆款",
            command=self._analyze_viral,
            width=150,
            height=40
        ).pack(side="left", padx=5)
        
        # 生成按钮
        ctk.CTkButton(
            buttons_frame,
            text="🎬 生成视频",
            command=self._generate_video,
            width=150,
            height=40,
            fg_color="green",
            hover_color="darkgreen"
        ).pack(side="left", padx=5)
        
        # 发布按钮
        ctk.CTkButton(
            buttons_frame,
            text="🚀 一键发布",
            command=self._publish_video,
            width=150,
            height=40,
            fg_color="orange",
            hover_color="darkorange"
        ).pack(side="left", padx=5)
    
    def _create_result_section(self):
        """创建结果显示区域"""
        frame = ctk.CTkFrame(self, fg_color=("gray90", "gray20"))
        frame.grid(row=6, column=0, padx=20, pady=10, sticky="nsew")
        self.grid_rowconfigure(6, weight=1)
        
        label = ctk.CTkLabel(
            frame,
            text="📊 结果",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        label.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")
        
        # 结果文本框
        self.result_text = ctk.CTkTextbox(
            frame,
            font=ctk.CTkFont(size=13),
            wrap="word"
        )
        self.result_text.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
        frame.grid_rowconfigure(1, weight=1)
    
    def _analyze_viral(self):
        """分析爆款"""
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", "🔍 正在分析爆款内容...\n请稍候...")
        
        # TODO: 实际分析逻辑
        thread = threading.Thread(target=self._do_analyze, daemon=True)
        thread.start()
    
    def _do_analyze(self):
        """后台分析"""
        # TODO: 调用实际分析功能
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", "✅ 分析完成！\n\n功能开发中...")
    
    def _generate_video(self):
        """生成视频"""
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", "🎬 正在生成视频...\n请稍候...")
        
        # TODO: 实际生成逻辑
    
    def _publish_video(self):
        """发布视频"""
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", "🚀 正在发布视频...\n请稍候...")
        
        # TODO: 实际发布逻辑

