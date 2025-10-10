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


class VideoProductionTab(ctk.CTkScrollableFrame):
    """视频生产界面（可滚动）"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
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
        
        # 操作按钮（提前到这里）
        self._create_actions()
        
        # 结果显示（中间位置）
        self._create_result_section()
        
        # 爆款分析选项
        self._create_analysis_section()
        
        # 视频生成设置
        self._create_generation_section()
        
        # 发布设置
        self._create_publish_section()
    
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
        label.grid(row=0, column=0, columnspan=3, padx=15, pady=(15, 10), sticky="w")
        
        # 选择内容源
        self.source_var = ctk.StringVar(value="bilibili")
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
            radio.grid(row=1, column=i, padx=15, pady=5, sticky="w")
        
        # 内容板块选择
        ctk.CTkLabel(
            frame,
            text="板块分类:",
            font=ctk.CTkFont(size=14)
        ).grid(row=2, column=0, padx=15, pady=(10, 5), sticky="w")
        
        self.category_var = ctk.StringVar(value="全部")
        category_menu = ctk.CTkOptionMenu(
            frame,
            variable=self.category_var,
            values=["全部", "科技", "游戏", "娱乐", "美食", "知识", "生活", "动画"],
            width=150
        )
        category_menu.grid(row=2, column=1, padx=15, pady=(10, 15), sticky="w")
    
    def _create_analysis_section(self):
        """创建爆款分析区域"""
        frame = ctk.CTkFrame(self, fg_color=("gray90", "gray20"))
        frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        
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
        frame.grid(row=5, column=0, padx=20, pady=10, sticky="ew")
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
        ctk.CTkLabel(frame, text="视频风格:").grid(row=3, column=0, padx=15, pady=5, sticky="w")
        self.style_var = ctk.StringVar(value="解说")
        ctk.CTkOptionMenu(frame, variable=self.style_var, values=["解说", "吐槽", "严肃", "幽默"]).grid(row=3, column=1, padx=15, pady=5, sticky="w")
        
        # 字体选择
        ctk.CTkLabel(frame, text="字体:").grid(row=4, column=0, padx=15, pady=5, sticky="w")
        self.font_var = ctk.StringVar(value="微软雅黑")
        ctk.CTkOptionMenu(frame, variable=self.font_var, values=["微软雅黑", "黑体", "宋体", "楷体"]).grid(row=4, column=1, padx=15, pady=5, sticky="w")
        
        # 字体大小
        ctk.CTkLabel(frame, text="字体大小:").grid(row=5, column=0, padx=15, pady=5, sticky="w")
        self.font_size_var = ctk.StringVar(value="70")
        font_size_slider = ctk.CTkSlider(frame, from_=40, to=120, variable=self.font_size_var, width=150)
        font_size_slider.grid(row=5, column=1, padx=15, pady=5, sticky="w")
        
        # 背景风格
        ctk.CTkLabel(frame, text="背景风格:").grid(row=6, column=0, padx=15, pady=5, sticky="w")
        self.bg_style_var = ctk.StringVar(value="渐变")
        ctk.CTkOptionMenu(frame, variable=self.bg_style_var, values=["渐变", "纯色", "自定义图片"]).grid(row=6, column=1, padx=15, pady=5, sticky="w")
        
        # 表情包开关
        self.use_emoji_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(frame, text="添加表情包装饰", variable=self.use_emoji_var).grid(row=7, column=0, columnspan=2, padx=15, pady=(5, 15), sticky="w")
    
    def _create_publish_section(self):
        """创建发布设置区域"""
        frame = ctk.CTkFrame(self, fg_color=("gray90", "gray20"))
        frame.grid(row=6, column=0, padx=20, pady=(10, 30), sticky="ew")  # 底部留30px空间
        
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
        """创建操作按钮（放在顶部，避免被遮挡）"""
        frame = ctk.CTkFrame(self, fg_color=("gray90", "gray20"))
        frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)
        
        # 提示标签
        ctk.CTkLabel(
            frame,
            text="⚡ 快速操作",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")
        
        # 按钮容器
        buttons_frame = ctk.CTkFrame(frame, fg_color="transparent")
        buttons_frame.grid(row=1, column=0, padx=15, pady=(0, 15))
        
        # 分析按钮
        self.analyze_btn = ctk.CTkButton(
            buttons_frame,
            text="🔍 分析爆款",
            command=self._analyze_viral,
            width=150,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.analyze_btn.pack(side="left", padx=5)
        
        # 生成按钮
        self.generate_btn = ctk.CTkButton(
            buttons_frame,
            text="🎬 生成视频",
            command=self._generate_video,
            width=150,
            height=45,
            fg_color="green",
            hover_color="darkgreen",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.generate_btn.pack(side="left", padx=5)
        
        # 发布按钮
        self.publish_btn = ctk.CTkButton(
            buttons_frame,
            text="🚀 一键发布",
            command=self._publish_video,
            width=150,
            height=45,
            fg_color="orange",
            hover_color="darkorange",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.publish_btn.pack(side="left", padx=5)
    
    def _create_result_section(self):
        """创建结果显示区域"""
        frame = ctk.CTkFrame(self, fg_color=("gray90", "gray20"))
        frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        label = ctk.CTkLabel(
            frame,
            text="📊 分析结果",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        label.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")
        
        # 结果文本框（固定高度，避免被遮挡）
        self.result_text = ctk.CTkTextbox(
            frame,
            font=ctk.CTkFont(size=13),
            wrap="word",
            height=300
        )
        self.result_text.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")
    
    def _analyze_viral(self):
        """分析爆款"""
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", "🔍 正在分析爆款内容...\n请稍候...")
        
        # 在后台线程运行
        thread = threading.Thread(target=self._do_analyze, daemon=True)
        thread.start()
    
    def _do_analyze(self):
        """后台分析"""
        try:
            # 创建事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 导入模块
            from plugins.video_producer.content_scraper import ContentScraper
            from plugins.video_producer.viral_analyzer import ViralAnalyzer
            from core.ai_engine import AIEngine
            
            # 抓取内容
            scraper = ContentScraper()
            source = self.source_var.get()
            
            if source == "bilibili":
                videos = loop.run_until_complete(scraper.scrape_bilibili_hot(limit=5))
                if not videos:
                    self.result_text.delete("1.0", "end")
                    self.result_text.insert("1.0", "❌ 抓取失败，请检查网络")
                    return
                
                # 分析第一个视频
                video = videos[0]
                result = f"📊 B站热门视频分析\n\n"
                result += f"标题：{video.get('title')}\n"
                result += f"播放：{video.get('play'):,}\n"
                result += f"点赞：{video.get('like'):,}\n"
                result += f"作者：{video.get('author')}\n\n"
                
                # 爆款分析
                if self.analyze_title_var.get():
                    analyzer = ViralAnalyzer(AIEngine())
                    title_analysis = loop.run_until_complete(
                        analyzer.analyze_title(video.get('title'), video)
                    )
                    
                    result += f"🔍 标题分析：\n"
                    result += f"- Hook: {', '.join(title_analysis.get('hooks', []))}\n"
                    result += f"- 评分: {title_analysis.get('score')}/100\n"
                    result += f"- 建议: {title_analysis.get('suggestions', ['无'])[0]}\n\n"
                    
                    if title_analysis.get('ai_insights'):
                        result += f"💡 AI分析:\n{title_analysis.get('ai_insights')}\n\n"
                
                # 显示所有热门视频
                result += f"\n📋 其他热门视频:\n\n"
                for i, v in enumerate(videos[1:], 2):
                    result += f"{i}. {v.get('title')}\n"
                    result += f"   {v.get('play'):,}播放 | {v.get('like'):,}点赞\n\n"
                
                self.result_text.delete("1.0", "end")
                self.result_text.insert("1.0", result)
            
        except Exception as e:
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", f"❌ 分析失败：{str(e)}")
        finally:
            if loop:
                loop.close()
    
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

