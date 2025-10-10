"""
视频生产Tab - 简化版（左右分栏+固定输出）
"""

import customtkinter as ctk
from tkinter import messagebox
import asyncio
import threading
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))


class VideoProductionTabSimple(ctk.CTkFrame):
    """视频生产界面 - 简化版"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # 配置网格
        self.grid_columnconfigure(0, weight=2)  # 左栏
        self.grid_columnconfigure(1, weight=3)  # 右栏
        self.grid_rowconfigure(0, weight=1)
        
        # 创建界面
        self._create_ui()
    
    def _create_ui(self):
        """创建UI"""
        # === 左栏：控制面板（可滚动）===
        left_panel = ctk.CTkScrollableFrame(self, fg_color=("gray95", "gray15"))
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        
        # 标题
        ctk.CTkLabel(
            left_panel,
            text="🎬 视频生产",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(padx=20, pady=(20, 15))
        
        # 1. 主题输入
        input_frame = self._create_section(left_panel, "✍️ 视频主题")
        self.topic_entry = ctk.CTkEntry(input_frame, placeholder_text="例如：健康饮食", height=40)
        self.topic_entry.pack(fill="x", padx=15, pady=(0, 15))
        
        # 2. 视觉设置（可折叠）
        settings_frame = self._create_collapsible_section(left_panel, "🎨 视觉设置")
        
        # 预设方案（快捷选择）
        preset_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        preset_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        self.preset_var = ctk.StringVar(value="默认")
        ctk.CTkLabel(preset_frame, text="预设:").pack(side="left", padx=(0, 10))
        preset_menu = ctk.CTkOptionMenu(
            preset_frame, 
            variable=self.preset_var, 
            values=["默认", "简约", "动感", "商务"],
            command=self._apply_preset,
            width=120
        )
        preset_menu.pack(side="left")
        
        # 详细设置（默认隐藏，点击"高级"展开）
        self.show_advanced = False
        advanced_btn = ctk.CTkButton(
            settings_frame,
            text="▶ 高级设置",
            command=self._toggle_advanced,
            fg_color="transparent",
            hover_color=("gray80", "gray25"),
            height=28,
            font=ctk.CTkFont(size=12)
        )
        advanced_btn.pack(padx=15, pady=(0, 15), anchor="w")
        
        # 高级设置区域（默认隐藏）
        self.advanced_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        # 不pack，点击时才显示
        
        # 3. 发布
        publish_frame = self._create_section(left_panel, "🚀 发布平台")
        self.bilibili_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(publish_frame, text="B站", variable=self.bilibili_var).pack(padx=15, pady=5, anchor="w")
        
        # === 右栏：主工作区 ===
        right_panel = ctk.CTkFrame(self)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        right_panel.grid_rowconfigure(1, weight=1)
        
        # 操作按钮
        btn_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)
        
        self.ref_btn = self._create_action_btn(btn_frame, "🔍 参考热门", self._reference, "left")
        self.gen_btn = self._create_action_btn(btn_frame, "📝 生成脚本", self._generate, "left")
        self.vid_btn = self._create_action_btn(btn_frame, "🎬 生成视频", self._make_video, "left", "green")
        
        # 脚本编辑
        ctk.CTkLabel(
            right_panel,
            text="📝 视频脚本（可编辑）",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(padx=20, anchor="w")
        
        self.script_box = ctk.CTkTextbox(right_panel, font=ctk.CTkFont(size=13), height=200)
        self.script_box.pack(fill="both", expand=True, padx=20, pady=(10, 15))
        
        # 固定输出区（底部）
        output_label = ctk.CTkLabel(
            right_panel,
            text="📊 输出台",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        output_label.pack(padx=20, anchor="w")
        
        self.output_box = ctk.CTkTextbox(right_panel, font=ctk.CTkFont(size=12), height=180, fg_color=("gray95", "gray15"))
        self.output_box.pack(fill="x", padx=20, pady=(10, 20))
        self.output_box.insert("1.0", "💡 所有操作结果将显示在这里...\n\n点击按钮开始使用！")
    
    def _create_section(self, parent, title):
        """创建区域"""
        frame = ctk.CTkFrame(parent, fg_color=("gray90", "gray20"))
        frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(padx=15, pady=(12, 10), anchor="w")
        
        return frame
    
    def _create_collapsible_section(self, parent, title):
        """创建可折叠区域"""
        frame = ctk.CTkFrame(parent, fg_color=("gray90", "gray20"))
        frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(padx=15, pady=(12, 10), anchor="w")
        
        return frame
    
    def _toggle_advanced(self):
        """切换高级设置"""
        # TODO: 实现折叠/展开
        pass
    
    def _apply_preset(self, preset_name):
        """应用预设方案"""
        presets = {
            "默认": {"font": "微软雅黑", "size": 70, "bg": "渐变"},
            "简约": {"font": "黑体", "size": 60, "bg": "纯色"},
            "动感": {"font": "微软雅黑", "size": 80, "bg": "渐变"},
            "商务": {"font": "宋体", "size": 65, "bg": "纯色"}
        }
        
        preset = presets.get(preset_name, presets["默认"])
        self.font_var.set(preset["font"])
        self.font_size_var.set(preset["size"])
        self.bg_var.set(preset["bg"])
        
        self._show_output(f"✅ 已应用'{preset_name}'预设")
    
    def _create_action_btn(self, parent, text, command, side, color=None):
        """创建操作按钮"""
        btn = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=130,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=color if color else None
        )
        btn.pack(side=side, padx=5)
        return btn
    
    def _show_output(self, message, append=False):
        """显示输出（固定位置）"""
        if not append:
            self.output_box.delete("1.0", "end")
        self.output_box.insert("end" if append else "1.0", message + "\n")
        self.output_box.see("end")
    
    def _reference(self):
        """参考热门"""
        self._show_output("🔍 正在抓取热门内容...")
        self.ref_btn.configure(state="disabled", text="抓取中...")
        
        def work():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                from plugins.video_producer.content_scraper import ContentScraper
                scraper = ContentScraper()
                videos = loop.run_until_complete(scraper.scrape_bilibili_hot(5))
                
                if videos:
                    result = f"✅ B站热门视频：\n\n"
                    for i, v in enumerate(videos[:3], 1):
                        result += f"{i}. {v.get('title')}\n   {v.get('play'):,}播放\n\n"
                    self._show_output(result)
                else:
                    self._show_output("❌ 抓取失败")
            except Exception as e:
                self._show_output(f"❌ 错误：{str(e)}")
            finally:
                self.ref_btn.configure(state="normal", text="🔍 参考热门")
                loop.close()
        
        threading.Thread(target=work, daemon=True).start()
    
    def _generate(self):
        """生成脚本"""
        topic = self.topic_entry.get().strip()
        if not topic:
            self._show_output("⚠️ 请先输入主题")
            return
        
        self._show_output(f"📝 正在生成'{topic}'的脚本...")
        self.gen_btn.configure(state="disabled", text="生成中...")
        
        def work():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                from plugins.video_producer.ai_analyzer import AIContentAnalyzer
                from core.ai_engine import AIEngine
                
                analyzer = AIContentAnalyzer(AIEngine())
                points = loop.run_until_complete(analyzer.extract_key_points(topic, 5))
                script = loop.run_until_complete(analyzer.generate_video_script(points))
                
                # 显示到脚本编辑框
                self.script_box.delete("1.0", "end")
                for seg in script.get('segments', []):
                    self.script_box.insert("end", seg + "\n")
                
                self._show_output(f"✅ 脚本已生成！共{len(script.get('segments', []))}个片段\n\n可在上方编辑修改")
            except Exception as e:
                self._show_output(f"❌ 生成失败：{str(e)}")
            finally:
                self.gen_btn.configure(state="normal", text="📝 生成脚本")
                loop.close()
        
        threading.Thread(target=work, daemon=True).start()
    
    def _make_video(self):
        """生成视频"""
        script = self.script_box.get("1.0", "end").strip()
        if not script:
            self._show_output("⚠️ 请先生成或输入脚本")
            return
        
        segments = [s.strip() for s in script.split('\n') if s.strip()]
        if not segments:
            self._show_output("⚠️ 脚本为空")
            return
        
        self._show_output(f"🎬 正在生成视频（{len(segments)}个片段）...\n预计90秒")
        self.vid_btn.configure(state="disabled", text="生成中...", fg_color="gray")
        
        def work():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                from plugins.video_producer.video_generator import VideoGenerator
                import time
                
                gen = VideoGenerator()
                path = loop.run_until_complete(
                    gen.generate_text_video(
                        segments,
                        font_name=self.font_var.get(),
                        font_size=self.font_size_var.get(),
                        bg_style=self.bg_var.get(),
                        output_name=f"video_{int(time.time())}.mp4"
                    )
                )
                
                self._show_output(f"✅ 视频生成成功！\n📁 {path}\n\n字体:{self.font_var.get()} {self.font_size_var.get()}px")
            except Exception as e:
                self._show_output(f"❌ 失败：{str(e)}")
            finally:
                self.vid_btn.configure(state="normal", text="🎬 生成视频", fg_color="green")
                loop.close()
        
        threading.Thread(target=work, daemon=True).start()

