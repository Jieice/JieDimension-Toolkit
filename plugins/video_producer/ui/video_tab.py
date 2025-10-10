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
        """创建用户界面（左右分栏）"""
        # 配置左右两栏
        self.grid_columnconfigure(0, weight=1)  # 左栏
        self.grid_columnconfigure(1, weight=1)  # 右栏
        
        # 标题（横跨两栏）
        title_label = ctk.CTkLabel(
            self,
            text="🎬 自动化视频生产",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10))
        
        # === 左栏：输入和设置 ===
        self._create_left_column()
        
        # === 右栏：脚本编辑和结果 ===
        self._create_right_column()
    
    def _create_left_column(self):
        """创建左栏（输入和设置）"""
        # 左栏容器
        left_container = ctk.CTkFrame(self, fg_color="transparent")
        left_container.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=10)
        left_container.grid_columnconfigure(0, weight=1)
        
        row = 0
        
        # 内容输入
        self._create_content_input_section_v2(left_container, row)
        row += 1
        
        # 参考热门（可选）
        self._create_source_section_v2(left_container, row)
        row += 1
        
        # 视频设置
        self._create_generation_section_v2(left_container, row)
        row += 1
        
        # 发布设置
        self._create_publish_section_v2(left_container, row)
    
    def _create_right_column(self):
        """创建右栏（脚本和结果）"""
        # 右栏容器
        right_container = ctk.CTkFrame(self, fg_color="transparent")
        right_container.grid(row=1, column=1, sticky="nsew", padx=(10, 20), pady=10)
        right_container.grid_columnconfigure(0, weight=1)
        right_container.grid_rowconfigure(1, weight=1)  # 脚本编辑区可扩展
        right_container.grid_rowconfigure(2, weight=1)  # 分析结果可扩展
        
        # 操作按钮（顶部）
        self._create_actions_v2(right_container)
        
        # 脚本编辑
        self._create_script_editor_v2(right_container)
        
        # 分析结果
        self._create_analysis_section_v2(right_container)
    
    def _create_workflow_section(self):
        """创建工作流程选择"""
        frame = ctk.CTkFrame(self, fg_color=("gray85", "gray15"))
        frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        label = ctk.CTkLabel(
            frame,
            text="🔄 工作流程",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        label.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")
        
        self.workflow_var = ctk.StringVar(value="自定义")
        
        workflows = [
            ("自定义创作", "自定义"),
            ("参考热门", "参考"),
            ("完全自动", "自动")
        ]
        
        for i, (text, value) in enumerate(workflows):
            radio = ctk.CTkRadioButton(
                frame,
                text=text,
                variable=self.workflow_var,
                value=value
            )
            radio.grid(row=1, column=i, padx=15, pady=(0, 15), sticky="w")
    
    def _create_content_input_section(self):
        """创建内容输入区域"""
        frame = ctk.CTkFrame(self, fg_color=("gray90", "gray20"))
        frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        frame.grid_columnconfigure(1, weight=1)
        
        label = ctk.CTkLabel(
            frame,
            text="✍️ 内容输入",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        label.grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 10), sticky="w")
        
        # 视频主题
        ctk.CTkLabel(frame, text="视频主题:").grid(row=1, column=0, padx=15, pady=5, sticky="w")
        self.topic_entry = ctk.CTkEntry(frame, placeholder_text="例如：手机省电技巧", width=300)
        self.topic_entry.grid(row=1, column=1, padx=15, pady=5, sticky="w")
        
        # 生成脚本按钮
        gen_script_btn = ctk.CTkButton(
            frame,
            text="🤖 AI生成脚本",
            command=self._generate_script,
            width=120,
            height=30
        )
        gen_script_btn.grid(row=2, column=0, columnspan=2, padx=15, pady=(5, 15))
    
    def _create_source_section(self):
        """创建内容源选择区域（可选，用于参考）"""
        frame = ctk.CTkFrame(self, fg_color=("gray90", "gray20"))
        frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        frame.grid_columnconfigure(1, weight=1)
        
        label = ctk.CTkLabel(
            frame,
            text="📝 参考热门（可选）",
            font=ctk.CTkFont(size=14, weight="bold")
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
        """创建爆款分析结果显示"""
        frame = ctk.CTkFrame(self, fg_color=("gray90", "gray20"))
        frame.grid(row=8, column=0, padx=20, pady=10, sticky="ew")
        
        label = ctk.CTkLabel(
            frame,
            text="🔍 分析结果",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        label.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")
        
        # 分析结果文本框
        self.analysis_text = ctk.CTkTextbox(
            frame,
            font=ctk.CTkFont(size=13),
            wrap="word",
            height=250
        )
        self.analysis_text.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")
        
        # 分析选项（简化）
        options_frame = ctk.CTkFrame(frame, fg_color="transparent")
        options_frame.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="w")
        
        self.analyze_title_var = ctk.BooleanVar(value=True)
        self.analyze_data_var = ctk.BooleanVar(value=True)
        
        ctk.CTkCheckBox(options_frame, text="分析标题", variable=self.analyze_title_var).pack(side="left", padx=5)
        ctk.CTkCheckBox(options_frame, text="分析数据", variable=self.analyze_data_var).pack(side="left", padx=5)
    
    def _create_generation_section(self):
        """创建视频生成区域"""
        frame = ctk.CTkFrame(self, fg_color=("gray90", "gray20"))
        frame.grid(row=6, column=0, padx=20, pady=10, sticky="ew")
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
        self.font_size_var = ctk.IntVar(value=70)  # 改为IntVar
        
        size_frame = ctk.CTkFrame(frame, fg_color="transparent")
        size_frame.grid(row=5, column=1, padx=15, pady=5, sticky="w")
        
        font_size_slider = ctk.CTkSlider(size_frame, from_=40, to=120, variable=self.font_size_var, width=120)
        font_size_slider.pack(side="left", padx=(0, 10))
        
        size_label = ctk.CTkLabel(size_frame, textvariable=self.font_size_var, width=40)
        size_label.pack(side="left")
        
        # 背景风格
        ctk.CTkLabel(frame, text="背景风格:").grid(row=6, column=0, padx=15, pady=5, sticky="w")
        self.bg_style_var = ctk.StringVar(value="渐变")
        ctk.CTkOptionMenu(frame, variable=self.bg_style_var, values=["渐变", "纯色", "自定义图片"]).grid(row=6, column=1, padx=15, pady=5, sticky="w")
        
        # 表情包开关
        self.use_emoji_var = ctk.BooleanVar(value=False)  # 默认关闭（因为还没素材）
        ctk.CTkCheckBox(frame, text="添加表情包装饰", variable=self.use_emoji_var).grid(row=7, column=0, columnspan=2, padx=15, pady=5, sticky="w")
        
        # 素材库管理按钮
        asset_btn = ctk.CTkButton(
            frame,
            text="📦 管理素材库",
            command=self._open_asset_manager,
            width=120,
            height=30,
            fg_color="transparent",
            border_width=1
        )
        asset_btn.grid(row=8, column=0, columnspan=2, padx=15, pady=(5, 15))
    
    def _create_publish_section(self):
        """创建发布设置区域"""
        frame = ctk.CTkFrame(self, fg_color=("gray90", "gray20"))
        frame.grid(row=7, column=0, padx=20, pady=(10, 30), sticky="ew")  # 底部留30px空间
        
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
    
    def _create_script_editor(self):
        """创建脚本编辑区域"""
        frame = ctk.CTkFrame(self, fg_color=("gray90", "gray20"))
        frame.grid(row=5, column=0, padx=20, pady=10, sticky="ew")
        
        label = ctk.CTkLabel(
            frame,
            text="📝 视频脚本（可编辑）",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        label.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")
        
        # 脚本编辑框
        self.script_text = ctk.CTkTextbox(
            frame,
            font=ctk.CTkFont(size=13),
            wrap="word",
            height=200
        )
        self.script_text.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="ew")
        
        # 提示
        hint = ctk.CTkLabel(
            frame,
            text="💡 每行一个片段，一行约5秒。可以直接编辑修改。",
            font=ctk.CTkFont(size=11),
            text_color="gray50"
        )
        hint.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="w")
    
    def _create_actions(self):
        """创建操作按钮"""
        frame = ctk.CTkFrame(self, fg_color=("gray90", "gray20"))
        frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
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
        
        # 参考热门按钮（原分析爆款）
        self.analyze_btn = ctk.CTkButton(
            buttons_frame,
            text="🔍 参考热门",
            command=self._analyze_viral,
            width=140,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.analyze_btn.pack(side="left", padx=5)
        
        # 生成脚本按钮
        self.gen_script_btn = ctk.CTkButton(
            buttons_frame,
            text="📝 生成脚本",
            command=self._generate_script,
            width=140,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.gen_script_btn.pack(side="left", padx=5)
        
        # 生成视频按钮
        self.generate_btn = ctk.CTkButton(
            buttons_frame,
            text="🎬 生成视频",
            command=self._generate_video,
            width=140,
            height=45,
            fg_color="green",
            hover_color="darkgreen",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.generate_btn.pack(side="left", padx=5)
    
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
        self.analysis_text = ctk.CTkTextbox(
            frame,
            font=ctk.CTkFont(size=13),
            wrap="word",
            height=300
        )
        self.analysis_text.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")
    
    def _analyze_viral(self):
        """分析爆款（参考热门）"""
        self.analysis_text.delete("1.0", "end")
        self.analysis_text.insert("1.0", "🔍 正在分析热门内容...\n请稍候...")
        
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
                    self.analysis_text.delete("1.0", "end")
                    self.analysis_text.insert("1.0", "❌ 抓取失败，请检查网络")
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
                
                self.analysis_text.delete("1.0", "end")
                self.analysis_text.insert("1.0", result)
            
        except Exception as e:
            self.analysis_text.delete("1.0", "end")
            self.analysis_text.insert("1.0", f"❌ 分析失败：{str(e)}")
        finally:
            if loop:
                loop.close()
    
    def _generate_video(self):
        """生成视频"""
        self.analysis_text.delete("1.0", "end")
        self.analysis_text.insert("1.0", "🎬 正在生成视频...\n请稍候...")
        
        # 禁用按钮
        self.generate_btn.configure(state="disabled", text="生成中...")
        
        # 在后台线程运行
        thread = threading.Thread(target=self._do_generate_video, daemon=True)
        thread.start()
    
    def _generate_script(self):
        """生成脚本"""
        topic = self.topic_entry.get().strip()
        if not topic:
            messagebox.showwarning("提示", "请输入视频主题")
            return
        
        self.gen_script_btn.configure(state="disabled", text="生成中...")
        
        thread = threading.Thread(target=self._do_generate_script, args=(topic,), daemon=True)
        thread.start()
    
    def _do_generate_script(self, topic: str):
        """后台生成脚本"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            from plugins.video_producer.ai_analyzer import AIContentAnalyzer
            from core.ai_engine import AIEngine
            
            analyzer = AIContentAnalyzer(AIEngine())
            
            # 生成要点
            points = loop.run_until_complete(analyzer.extract_key_points(topic, num_points=5))
            
            # 生成脚本
            script = loop.run_until_complete(analyzer.generate_video_script(points, style=self.style_var.get()))
            
            # 显示到编辑框（按行分割）
            segments = script.get('segments', [])
            self.script_text.delete("1.0", "end")
            for seg in segments:
                self.script_text.insert("end", seg + "\n")
            
            # 提示
            messagebox.showinfo("成功", f"脚本已生成！共{len(segments)}个片段\n\n可以直接编辑修改，然后生成视频")
            
        except Exception as e:
            messagebox.showerror("失败", f"脚本生成失败：{str(e)}")
        finally:
            self.gen_script_btn.configure(state="normal", text="📝 生成脚本")
            if loop:
                loop.close()
    
    def _do_generate_video(self):
        """后台生成视频"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            from plugins.video_producer.video_generator import VideoGenerator
            
            # 从脚本编辑框获取脚本（每行一个片段）
            script_content = self.script_text.get("1.0", "end").strip()
            if not script_content:
                self.script_text.insert("1.0", "请先生成或输入脚本！\n\n点击📝生成脚本，或手动输入")
                return
            
            # 按行分割
            script_segments = [line.strip() for line in script_content.split('\n') if line.strip()]
            
            if not script_segments:
                messagebox.showwarning("提示", "脚本为空！")
                return
            
            # 获取GUI参数
            font_name = self.font_var.get()
            font_size = self.font_size_var.get()
            use_emoji = self.use_emoji_var.get()
            bg_style = self.bg_style_var.get()
            
            # 生成视频
            generator = VideoGenerator()
            output_path = loop.run_until_complete(
                generator.generate_text_video(
                    script_segments=test_segments,
                    font_name=font_name,
                    font_size=font_size,
                    use_emoji=use_emoji,
                    bg_style=bg_style,
                    output_name=f"video_{asyncio.get_event_loop().time():.0f}.mp4"
                )
            )
            
            # 显示结果
            result = f"✅ 视频生成成功！\n\n"
            result += f"📁 保存位置：\n{output_path}\n\n"
            result += f"⚙️ 使用参数：\n"
            result += f"- 字体：{font_name}\n"
            result += f"- 字体大小：{font_size}\n"
            result += f"- 背景：{bg_style}\n"
            result += f"- 表情包：{'开启' if use_emoji else '关闭'}\n\n"
            result += f"💡 提示：视频已保存到data/videos目录"
            
            self.analysis_text.delete("1.0", "end")
            self.analysis_text.insert("1.0", result)
            
        except Exception as e:
            self.analysis_text.delete("1.0", "end")
            self.analysis_text.insert("1.0", f"❌ 生成失败：{str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            # 恢复按钮
            self.generate_btn.configure(state="normal", text="🎬 生成视频")
            if loop:
                loop.close()
    
    def _open_asset_manager(self):
        """打开素材库管理"""
        from tkinter import filedialog
        import os
        
        # 打开素材目录
        asset_dir = os.path.abspath("data/assets")
        if os.path.exists(asset_dir):
            os.startfile(asset_dir)
            self.analysis_text.delete("1.0", "end")
            self.analysis_text.insert("1.0", f"📦 素材库已打开：\n{asset_dir}\n\n请将素材放到对应文件夹：\n\nemojis/ - 表情包\nbackgrounds/ - 背景图\nmusic/ - 背景音乐\n\n支持的格式：\nPNG、JPG、MP3")
        else:
            messagebox.showwarning("提示", "素材目录不存在")
    
    def _publish_video(self):
        """发布视频"""
        self.analysis_text.delete("1.0", "end")
        self.analysis_text.insert("1.0", "🚀 正在发布视频...\n功能开发中...")

