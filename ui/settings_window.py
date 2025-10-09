"""
JieDimension Toolkit - 设置界面
AI模型配置、主题切换、系统设置
Version: 1.0.0
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import json
import os
import sys
import threading
from typing import Dict, Any

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class SettingsPanel(ctk.CTkScrollableFrame):
    """设置面板"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # 配置网格
        self.grid_columnconfigure(0, weight=1)
        
        # 优化滚动性能
        self._setup_smooth_scroll()
        
        # 配置文件路径
        self.config_path = "config/settings.json"
        self.settings = self._load_settings()
        
        # 创建界面
        self._create_header()
        self._create_appearance_section()
        self._create_ai_section()
        self._create_database_section()
        self._create_update_section()
        self._create_actions()
    
    def _create_header(self):
        """创建顶部标题栏"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=30, pady=(30, 20), sticky="ew")
        
        # 标题
        title = ctk.CTkLabel(
            header_frame,
            text="⚙️ 系统设置",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title.grid(row=0, column=0, sticky="w")
    
    def _create_appearance_section(self):
        """创建外观设置区域"""
        # 标题
        section_title = ctk.CTkLabel(
            self,
            text="🎨 外观设置",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w"
        )
        section_title.grid(row=1, column=0, padx=30, pady=(20, 10), sticky="w")
        
        # 设置卡片
        appearance_frame = ctk.CTkFrame(self, fg_color=("gray85", "gray20"), corner_radius=15)
        appearance_frame.grid(row=2, column=0, padx=30, pady=10, sticky="ew")
        appearance_frame.grid_columnconfigure(1, weight=1)
        
        # 主题模式
        theme_label = ctk.CTkLabel(
            appearance_frame,
            text="🌓 主题模式",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        theme_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        theme_desc = ctk.CTkLabel(
            appearance_frame,
            text="选择界面的主题模式",
            font=ctk.CTkFont(size=12),
            text_color="gray60"
        )
        theme_desc.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")
        
        # 主题选择器
        self.theme_var = ctk.StringVar(value=self.settings.get("theme", "dark"))
        theme_menu = ctk.CTkOptionMenu(
            appearance_frame,
            values=["dark", "light", "system"],
            variable=self.theme_var,
            command=self._change_theme,
            width=200,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        theme_menu.grid(row=0, column=1, rowspan=2, padx=20, pady=20, sticky="e")
        
        # 分隔线
        separator = ctk.CTkFrame(appearance_frame, height=2, fg_color="gray30")
        separator.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        
        # 颜色主题
        color_label = ctk.CTkLabel(
            appearance_frame,
            text="🎨 颜色主题",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        color_label.grid(row=3, column=0, padx=20, pady=(10, 10), sticky="w")
        
        color_desc = ctk.CTkLabel(
            appearance_frame,
            text="选择界面的颜色主题",
            font=ctk.CTkFont(size=12),
            text_color="gray60"
        )
        color_desc.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="w")
        
        # 颜色选择器
        self.color_var = ctk.StringVar(value=self.settings.get("color_theme", "blue"))
        color_menu = ctk.CTkOptionMenu(
            appearance_frame,
            values=["blue", "green", "dark-blue"],
            variable=self.color_var,
            command=self._change_color_theme,
            width=200,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        color_menu.grid(row=3, column=1, rowspan=2, padx=20, pady=20, sticky="e")
    
    def _create_ai_section(self):
        """创建AI设置区域"""
        # 标题
        section_title = ctk.CTkLabel(
            self,
            text="🤖 AI引擎设置",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w"
        )
        section_title.grid(row=3, column=0, padx=30, pady=(20, 10), sticky="w")
        
        # 设置卡片
        ai_frame = ctk.CTkFrame(self, fg_color=("gray85", "gray20"), corner_radius=15)
        ai_frame.grid(row=4, column=0, padx=30, pady=10, sticky="ew")
        ai_frame.grid_columnconfigure(1, weight=1)
        
        # Ollama地址
        ollama_label = ctk.CTkLabel(
            ai_frame,
            text="🌐 Ollama服务地址",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        ollama_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        ollama_desc = ctk.CTkLabel(
            ai_frame,
            text="配置Ollama API服务器地址",
            font=ctk.CTkFont(size=12),
            text_color="gray60"
        )
        ollama_desc.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")
        
        # Ollama地址输入框
        self.ollama_url_entry = ctk.CTkEntry(
            ai_frame,
            placeholder_text="http://localhost:11434",
            width=300,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        self.ollama_url_entry.insert(0, self.settings.get("ollama_url", "http://localhost:11434"))
        self.ollama_url_entry.grid(row=0, column=1, rowspan=2, padx=20, pady=20, sticky="e")
        
        # 分隔线
        separator = ctk.CTkFrame(ai_frame, height=2, fg_color="gray30")
        separator.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        
        # AI模型选择
        model_label = ctk.CTkLabel(
            ai_frame,
            text="🧠 AI模型",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        model_label.grid(row=3, column=0, padx=20, pady=(10, 10), sticky="w")
        
        model_desc = ctk.CTkLabel(
            ai_frame,
            text="选择默认使用的AI模型",
            font=ctk.CTkFont(size=12),
            text_color="gray60"
        )
        model_desc.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="w")
        
        # 模型选择器
        self.model_var = ctk.StringVar(value=self.settings.get("ai_model", "deepseek-r1:1.5b"))
        model_menu = ctk.CTkOptionMenu(
            ai_frame,
            values=[
                "deepseek-r1:1.5b",
                "qwen2.5:1.5b",
                "llama3.2:1b",
                "gemma2:2b",
                "phi3:latest"
            ],
            variable=self.model_var,
            width=300,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        model_menu.grid(row=3, column=1, rowspan=2, padx=20, pady=20, sticky="e")
        
        # 分隔线
        separator2 = ctk.CTkFrame(ai_frame, height=2, fg_color="gray30")
        separator2.grid(row=5, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        
        # 温度设置
        temp_label = ctk.CTkLabel(
            ai_frame,
            text="🌡️ 温度参数",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        temp_label.grid(row=6, column=0, padx=20, pady=(10, 10), sticky="w")
        
        temp_desc = ctk.CTkLabel(
            ai_frame,
            text="控制AI输出的随机性（0-1，越高越随机）",
            font=ctk.CTkFont(size=12),
            text_color="gray60"
        )
        temp_desc.grid(row=7, column=0, padx=20, pady=(0, 20), sticky="w")
        
        # 温度滑块容器
        temp_container = ctk.CTkFrame(ai_frame, fg_color="transparent")
        temp_container.grid(row=6, column=1, rowspan=2, padx=20, pady=20, sticky="e")
        
        self.temp_value_label = ctk.CTkLabel(
            temp_container,
            text=f"{self.settings.get('temperature', 0.7):.1f}",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=40
        )
        self.temp_value_label.pack(side="right", padx=(10, 0))
        
        self.temp_slider = ctk.CTkSlider(
            temp_container,
            from_=0,
            to=1,
            width=250,
            command=self._update_temp_label
        )
        self.temp_slider.set(self.settings.get('temperature', 0.7))
        self.temp_slider.pack(side="right")
        
        # 分隔线
        separator3 = ctk.CTkFrame(ai_frame, height=2, fg_color="gray30")
        separator3.grid(row=8, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        
        # Gemini API密钥
        gemini_label = ctk.CTkLabel(
            ai_frame,
            text="✨ Gemini API密钥",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        gemini_label.grid(row=9, column=0, padx=20, pady=(10, 10), sticky="w")
        
        gemini_desc = ctk.CTkLabel(
            ai_frame,
            text="Google Gemini API密钥（可选，用于复杂任务）",
            font=ctk.CTkFont(size=12),
            text_color="gray60"
        )
        gemini_desc.grid(row=10, column=0, padx=20, pady=(0, 10), sticky="w")
        
        # API密钥输入框容器
        gemini_container = ctk.CTkFrame(ai_frame, fg_color="transparent")
        gemini_container.grid(row=9, column=1, rowspan=2, padx=20, pady=20, sticky="e")
        
        # API密钥输入框
        self.gemini_key_entry = ctk.CTkEntry(
            gemini_container,
            placeholder_text="输入Gemini API密钥...",
            width=250,
            height=35,
            font=ctk.CTkFont(size=13),
            show="*"  # 隐藏输入内容
        )
        current_key = self.settings.get("gemini_api_key", "")
        if current_key:
            self.gemini_key_entry.insert(0, current_key)
        self.gemini_key_entry.pack(side="left", padx=(0, 10))
        
        # 测试按钮
        self.test_gemini_btn = ctk.CTkButton(
            gemini_container,
            text="🔍 测试",
            width=60,
            height=35,
            font=ctk.CTkFont(size=13),
            command=self._test_gemini_connection
        )
        self.test_gemini_btn.pack(side="left")
        
        # 帮助文本
        gemini_help = ctk.CTkLabel(
            ai_frame,
            text="💡 获取免费API密钥：https://makersuite.google.com/app/apikey",
            font=ctk.CTkFont(size=11),
            text_color="gray50",
            anchor="w"
        )
        gemini_help.grid(row=11, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="w")
        
        # === Day 7新增：Claude配置 ===
        
        # 分隔线
        separator4 = ctk.CTkFrame(ai_frame, height=2, fg_color="gray30")
        separator4.grid(row=12, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        
        # Claude API密钥
        claude_label = ctk.CTkLabel(
            ai_frame,
            text="🤖 Claude API密钥",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        claude_label.grid(row=13, column=0, padx=20, pady=(10, 10), sticky="w")
        
        claude_desc = ctk.CTkLabel(
            ai_frame,
            text="Anthropic Claude API密钥（可选，高质量任务）",
            font=ctk.CTkFont(size=12),
            text_color="gray60"
        )
        claude_desc.grid(row=14, column=0, padx=20, pady=(0, 10), sticky="w")
        
        # API密钥输入框容器
        claude_container = ctk.CTkFrame(ai_frame, fg_color="transparent")
        claude_container.grid(row=13, column=1, rowspan=2, padx=20, pady=20, sticky="e")
        
        # API密钥输入框
        self.claude_key_entry = ctk.CTkEntry(
            claude_container,
            placeholder_text="输入Claude API密钥...",
            width=250,
            height=35,
            font=ctk.CTkFont(size=13),
            show="*"  # 隐藏输入内容
        )
        current_claude_key = self.settings.get("claude_api_key", "")
        if current_claude_key:
            self.claude_key_entry.insert(0, current_claude_key)
        self.claude_key_entry.pack(side="left", padx=(0, 10))
        
        # 测试按钮
        self.test_claude_btn = ctk.CTkButton(
            claude_container,
            text="🔍 测试",
            width=60,
            height=35,
            font=ctk.CTkFont(size=13),
            command=self._test_claude_connection
        )
        self.test_claude_btn.pack(side="left")
        
        # 帮助文本
        claude_help = ctk.CTkLabel(
            ai_frame,
            text="💡 获取API密钥：https://console.anthropic.com/",
            font=ctk.CTkFont(size=11),
            text_color="gray50",
            anchor="w"
        )
        claude_help.grid(row=15, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="w")
        
        # === Day 7新增：文心一言配置 ===
        
        # 分隔线
        separator5 = ctk.CTkFrame(ai_frame, height=2, fg_color="gray30")
        separator5.grid(row=16, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        
        # 文心一言API密钥
        ernie_label = ctk.CTkLabel(
            ai_frame,
            text="🇨🇳 文心一言 API Key",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        ernie_label.grid(row=17, column=0, padx=20, pady=(10, 10), sticky="w")
        
        ernie_desc = ctk.CTkLabel(
            ai_frame,
            text="百度文心一言API密钥（可选，中文任务优势）",
            font=ctk.CTkFont(size=12),
            text_color="gray60"
        )
        ernie_desc.grid(row=18, column=0, padx=20, pady=(0, 10), sticky="w")
        
        # API Key输入框容器
        ernie_api_container = ctk.CTkFrame(ai_frame, fg_color="transparent")
        ernie_api_container.grid(row=17, column=1, rowspan=2, padx=20, pady=20, sticky="e")
        
        # API Key输入框
        self.ernie_api_key_entry = ctk.CTkEntry(
            ernie_api_container,
            placeholder_text="输入API Key...",
            width=250,
            height=35,
            font=ctk.CTkFont(size=13),
            show="*"
        )
        current_ernie_api_key = self.settings.get("ernie_api_key", "")
        if current_ernie_api_key:
            self.ernie_api_key_entry.insert(0, current_ernie_api_key)
        self.ernie_api_key_entry.pack(side="left", padx=(0, 10))
        
        # 测试按钮
        self.test_ernie_btn = ctk.CTkButton(
            ernie_api_container,
            text="🔍 测试",
            width=60,
            height=35,
            font=ctk.CTkFont(size=13),
            command=self._test_ernie_connection
        )
        self.test_ernie_btn.pack(side="left")
        
        # 文心一言Secret Key
        ernie_secret_label = ctk.CTkLabel(
            ai_frame,
            text="🔐 文心一言 Secret Key",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        ernie_secret_label.grid(row=19, column=0, padx=20, pady=(10, 10), sticky="w")
        
        ernie_secret_desc = ctk.CTkLabel(
            ai_frame,
            text="百度文心一言Secret Key（与API Key配套使用）",
            font=ctk.CTkFont(size=12),
            text_color="gray60"
        )
        ernie_secret_desc.grid(row=20, column=0, padx=20, pady=(0, 10), sticky="w")
        
        # Secret Key输入框
        self.ernie_secret_key_entry = ctk.CTkEntry(
            ai_frame,
            placeholder_text="输入Secret Key...",
            width=310,
            height=35,
            font=ctk.CTkFont(size=13),
            show="*"
        )
        current_ernie_secret_key = self.settings.get("ernie_secret_key", "")
        if current_ernie_secret_key:
            self.ernie_secret_key_entry.insert(0, current_ernie_secret_key)
        self.ernie_secret_key_entry.grid(row=19, column=1, rowspan=2, padx=20, pady=20, sticky="e")
        
        # 帮助文本
        ernie_help = ctk.CTkLabel(
            ai_frame,
            text="💡 获取密钥：https://cloud.baidu.com/product/wenxinworkshop",
            font=ctk.CTkFont(size=11),
            text_color="gray50",
            anchor="w"
        )
        ernie_help.grid(row=21, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="w")
    
    def _create_database_section(self):
        """创建数据库设置区域"""
        # 标题
        section_title = ctk.CTkLabel(
            self,
            text="💾 数据库设置",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w"
        )
        section_title.grid(row=5, column=0, padx=30, pady=(20, 10), sticky="w")
        
        # 设置卡片
        db_frame = ctk.CTkFrame(self, fg_color=("gray85", "gray20"), corner_radius=15)
        db_frame.grid(row=6, column=0, padx=30, pady=10, sticky="ew")
        db_frame.grid_columnconfigure(1, weight=1)
        
        # 数据库路径
        db_label = ctk.CTkLabel(
            db_frame,
            text="📂 数据库路径",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        db_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        db_desc = ctk.CTkLabel(
            db_frame,
            text="SQLite数据库文件位置",
            font=ctk.CTkFont(size=12),
            text_color="gray60"
        )
        db_desc.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")
        
        # 路径显示和选择
        path_container = ctk.CTkFrame(db_frame, fg_color="transparent")
        path_container.grid(row=0, column=1, rowspan=2, padx=20, pady=20, sticky="e")
        
        self.db_path_label = ctk.CTkLabel(
            path_container,
            text=self.settings.get("db_path", "data/database.db"),
            font=ctk.CTkFont(size=12),
            text_color="gray60",
            width=250,
            anchor="e"
        )
        self.db_path_label.pack(side="left", padx=(0, 10))
        
        browse_btn = ctk.CTkButton(
            path_container,
            text="浏览",
            command=self._browse_database,
            width=80,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        browse_btn.pack(side="left")
    
    def _create_update_section(self):
        """创建更新检查区域"""
        # 标题
        section_title = ctk.CTkLabel(
            self,
            text="🔄 版本更新",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w"
        )
        section_title.grid(row=7, column=0, padx=30, pady=(20, 10), sticky="w")
        
        # 设置卡片
        update_frame = ctk.CTkFrame(self, fg_color=("gray85", "gray20"), corner_radius=15)
        update_frame.grid(row=8, column=0, padx=30, pady=10, sticky="ew")
        update_frame.grid_columnconfigure(1, weight=1)
        
        # 当前版本
        version_label = ctk.CTkLabel(
            update_frame,
            text="📌 当前版本",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        version_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        
        current_version = ctk.CTkLabel(
            update_frame,
            text="v1.17.2",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("green", "lightgreen")
        )
        current_version.grid(row=0, column=1, padx=20, pady=(20, 5), sticky="e")
        
        # 更新说明
        update_desc = ctk.CTkLabel(
            update_frame,
            text="点击检查更新可自动下载并安装最新版本",
            font=ctk.CTkFont(size=12),
            text_color="gray60"
        )
        update_desc.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 15), sticky="w")
        
        # 按钮区域
        buttons_container = ctk.CTkFrame(update_frame, fg_color="transparent")
        buttons_container.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")
        
        # 检查更新按钮
        check_btn = ctk.CTkButton(
            buttons_container,
            text="🔍 检查更新",
            command=self._check_for_updates,
            width=140,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        check_btn.pack(side="left", padx=5)
        
        # 一键更新按钮
        auto_update_btn = ctk.CTkButton(
            buttons_container,
            text="⚡ 一键更新",
            command=self._auto_update,
            width=140,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color=("orange", "darkorange"),
            hover_color=("darkorange", "orange")
        )
        auto_update_btn.pack(side="left", padx=5)
    
    def _create_actions(self):
        """创建操作按钮区域"""
        # 按钮容器
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.grid(row=9, column=0, padx=30, pady=(30, 30), sticky="ew")
        actions_frame.grid_columnconfigure(0, weight=1)
        
        # 按钮区域
        buttons_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        buttons_frame.grid(row=0, column=0, sticky="e")
        
        # 重置按钮
        reset_btn = ctk.CTkButton(
            buttons_frame,
            text="🔄 重置为默认",
            command=self._reset_settings,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="gray50",
            hover_color="gray40"
        )
        reset_btn.pack(side="left", padx=5)
        
        # 保存按钮
        save_btn = ctk.CTkButton(
            buttons_frame,
            text="💾 保存设置",
            command=self._save_settings,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        save_btn.pack(side="left", padx=5)
    
    def _load_settings(self) -> Dict[str, Any]:
        """加载设置"""
        default_settings = {
            "theme": "dark",
            "color_theme": "blue",
            "ollama_url": "http://localhost:11434",
            "ai_model": "deepseek-r1:1.5b",
            "temperature": 0.7,
            "db_path": "data/database.db",
            "gemini_api_key": ""
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    default_settings.update(loaded_settings)
        except Exception as e:
            print(f"加载设置失败: {e}")
        
        return default_settings
    
    def _save_settings(self):
        """保存设置"""
        try:
            # 更新设置
            self.settings["theme"] = self.theme_var.get()
            self.settings["color_theme"] = self.color_var.get()
            self.settings["ollama_url"] = self.ollama_url_entry.get()
            self.settings["ai_model"] = self.model_var.get()
            self.settings["temperature"] = self.temp_slider.get()
            self.settings["db_path"] = self.db_path_label.cget("text")
            self.settings["gemini_api_key"] = self.gemini_key_entry.get()
            
            # Day 7新增：保存Claude和文心一言配置
            self.settings["claude_api_key"] = self.claude_key_entry.get()
            self.settings["ernie_api_key"] = self.ernie_api_key_entry.get()
            self.settings["ernie_secret_key"] = self.ernie_secret_key_entry.get()
            
            # 确保config目录存在
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # 保存到文件
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("成功", "设置已保存！\n\n部分设置可能需要重启应用后生效。")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存设置失败：{str(e)}")
    
    def _reset_settings(self):
        """重置设置"""
        if not messagebox.askyesno("确认", "确定要重置所有设置为默认值吗？"):
            return
        
        # 重置为默认值
        self.theme_var.set("dark")
        self.color_var.set("blue")
        self.ollama_url_entry.delete(0, "end")
        self.ollama_url_entry.insert(0, "http://localhost:11434")
        self.model_var.set("deepseek-r1:1.5b")
        self.temp_slider.set(0.7)
        self.gemini_key_entry.delete(0, "end")
        
        # Day 7新增：重置Claude和文心一言配置
        self.claude_key_entry.delete(0, "end")
        self.ernie_api_key_entry.delete(0, "end")
        self.ernie_secret_key_entry.delete(0, "end")
        
        self.db_path_label.configure(text="data/database.db")
        
        # 应用主题
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        messagebox.showinfo("完成", "设置已重置为默认值")
    
    def _change_theme(self, theme: str):
        """切换主题"""
        ctk.set_appearance_mode(theme)
    
    def _change_color_theme(self, color: str):
        """切换颜色主题"""
        messagebox.showinfo(
            "提示",
            f"颜色主题将更改为 {color}\n\n需要重启应用后生效。"
        )
    
    def _update_temp_label(self, value):
        """更新温度标签"""
        self.temp_value_label.configure(text=f"{float(value):.1f}")
    
    def _setup_smooth_scroll(self):
        """设置平滑滚动"""
        try:
            # 减少滚动灵敏度，防止撕裂
            if hasattr(self, '_parent_canvas'):
                self._parent_canvas.bind_all("<MouseWheel>", self._on_smooth_scroll, add="+")
        except Exception:
            pass
    
    def _on_smooth_scroll(self, event):
        """平滑滚动处理"""
        try:
            # 减少滚动速度（除以3而不是默认的1）
            scroll_amount = -1 * int(event.delta / 120)
            self._parent_canvas.yview_scroll(scroll_amount, "units")
            return "break"
        except Exception:
            pass
    
    def _browse_database(self):
        """浏览数据库文件"""
        file_path = filedialog.asksaveasfilename(
            title="选择数据库文件",
            defaultextension=".db",
            filetypes=[
                ("SQLite数据库", "*.db"),
                ("所有文件", "*.*")
            ],
            initialfile="database.db"
        )
        
        if file_path:
            self.db_path_label.configure(text=file_path)
    
    def _check_for_updates(self):
        """检查更新"""
        try:
            from utils.updater import UpdateChecker
            
            # 显示检查中提示
            messagebox.showinfo("检查更新", "正在检查更新，请稍候...")
            
            checker = UpdateChecker()
            update_info = checker.check_for_updates()
            
            if update_info:
                # 发现新版本
                message = f"""发现新版本！

当前版本: v{update_info['current']}
最新版本: v{update_info['version']}
发布日期: {update_info.get('date', '未知')}

更新内容:
{update_info.get('notes', '')[:300]}...

是否立即下载并更新？"""
                
                if messagebox.askyesno("发现新版本", message):
                    self._auto_update()
                else:
                    # 打开下载页面
                    checker.open_download_page()
            else:
                messagebox.showinfo("检查更新", "✅ 当前已是最新版本！")
                
        except Exception as e:
            messagebox.showerror("错误", f"检查更新失败：{str(e)}")
    
    def _auto_update(self):
        """一键自动更新"""
        try:
            from utils.updater import UpdateChecker
            import threading
            
            # 确认更新
            if not messagebox.askyesno(
                "确认更新", 
                "即将开始自动更新：\n\n"
                "1. 下载最新版本\n"
                "2. 备份当前版本\n"
                "3. 安装新版本\n"
                "4. 自动重启应用\n\n"
                "更新过程中应用会自动退出，是否继续？"
            ):
                return
            
            checker = UpdateChecker()
            
            # 先检查是否有更新
            if not checker.latest_info:
                update_info = checker.check_for_updates()
                if not update_info:
                    messagebox.showinfo("提示", "当前已是最新版本，无需更新！")
                    return
            
            # 显示更新进度对话框
            progress_window = ctk.CTkToplevel(self)
            progress_window.title("正在更新")
            progress_window.geometry("400x200")
            progress_window.transient(self.master)
            progress_window.grab_set()
            
            # 进度标签
            status_label = ctk.CTkLabel(
                progress_window,
                text="正在准备更新...",
                font=ctk.CTkFont(size=14)
            )
            status_label.pack(pady=20)
            
            # 进度条
            progress_bar = ctk.CTkProgressBar(progress_window, width=350)
            progress_bar.pack(pady=10)
            progress_bar.set(0)
            
            def update_progress(downloaded, total):
                """更新进度"""
                if total > 0:
                    progress = downloaded / total
                    progress_bar.set(progress)
                    status_label.configure(
                        text=f"正在下载: {downloaded/1024/1024:.1f}MB / {total/1024/1024:.1f}MB"
                    )
            
            def do_update():
                """后台执行更新"""
                try:
                    status_label.configure(text="🔍 检查更新...")
                    progress_bar.set(0.1)
                    
                    # 下载更新
                    status_label.configure(text="📥 下载更新包...")
                    zip_path = checker.download_update(progress_callback=update_progress)
                    
                    if not zip_path:
                        progress_window.destroy()
                        messagebox.showerror("错误", "下载更新失败！")
                        return
                    
                    status_label.configure(text="🔧 安装更新...")
                    progress_bar.set(0.9)
                    
                    # 安装更新
                    success = checker.install_update(zip_path)
                    
                    if success:
                        status_label.configure(text="✅ 更新完成！应用即将重启...")
                        progress_bar.set(1.0)
                        self.master.after(1000, self.master.quit)  # 1秒后退出
                    else:
                        progress_window.destroy()
                        messagebox.showerror("错误", "安装更新失败！")
                        
                except Exception as e:
                    progress_window.destroy()
                    messagebox.showerror("错误", f"更新失败：{str(e)}")
            
            # 在后台线程执行更新
            thread = threading.Thread(target=do_update, daemon=True)
            thread.start()
            
        except Exception as e:
            messagebox.showerror("错误", f"启动更新失败：{str(e)}")
    
    def _test_gemini_connection(self):
        """测试Gemini API连接"""
        api_key = self.gemini_key_entry.get().strip()
        
        if not api_key:
            messagebox.showwarning("警告", "请先输入Gemini API密钥！")
            return
        
        # 禁用按钮，显示测试中
        self.test_gemini_btn.configure(text="测试中...", state="disabled")
        self.update()
        
        try:
            # 导入Gemini库
            import google.generativeai as genai
            
            # 配置API密钥
            genai.configure(api_key=api_key)
            
            # 创建模型
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # 测试简单生成
            response = model.generate_content("Say 'Hello'")
            
            if response and response.text:
                messagebox.showinfo(
                    "成功",
                    "✅ Gemini API连接成功！\n\n"
                    f"测试响应: {response.text[:50]}...\n\n"
                    "记得点击'保存设置'按钮保存API密钥。"
                )
            else:
                messagebox.showwarning("警告", "连接成功，但响应为空")
                
        except ImportError:
            messagebox.showerror(
                "错误",
                "❌ 未安装Gemini库！\n\n"
                "请在终端运行：\n"
                "pip install google-generativeai"
            )
        except Exception as e:
            error_msg = str(e)
            if "API key not valid" in error_msg or "INVALID_ARGUMENT" in error_msg:
                messagebox.showerror("错误", "❌ API密钥无效！\n\n请检查密钥是否正确。")
            elif "quota" in error_msg.lower():
                messagebox.showerror("错误", "❌ API配额已用完！\n\n请稍后再试。")
            else:
                messagebox.showerror("错误", f"❌ 连接失败：\n\n{error_msg}")
        finally:
            # 恢复按钮状态
            self.test_gemini_btn.configure(text="🔍 测试", state="normal")
    
    def _test_claude_connection(self):
        """测试Claude API连接（Day 7新增）"""
        api_key = self.claude_key_entry.get().strip()
        
        if not api_key:
            messagebox.showwarning("警告", "请先输入Claude API密钥！")
            return
        
        # 禁用按钮，显示测试中
        self.test_claude_btn.configure(text="测试中...", state="disabled")
        self.update()
        
        try:
            import asyncio
            from core.ai_engine import AIEngine, AIConfig
            
            # 创建配置
            config = AIConfig(claude_api_key=api_key)
            engine = AIEngine(config)
            
            # 异步测试
            async def test():
                response = await engine._call_claude(
                    prompt="Say 'Hello' in one word"
                )
                return response
            
            # 运行测试
            response = asyncio.run(test())
            
            if response.success:
                messagebox.showinfo(
                    "成功",
                    "✅ Claude API连接成功！\n\n"
                    f"测试响应: {response.content[:50]}...\n"
                    f"耗时: {response.latency:.2f}秒\n\n"
                    "记得点击'保存设置'按钮保存API密钥。"
                )
            else:
                error_msg = response.error or "未知错误"
                if "401" in error_msg or "authentication" in error_msg.lower():
                    messagebox.showerror("错误", "❌ API密钥无效！\n\n请检查密钥是否正确。")
                elif "quota" in error_msg.lower() or "rate" in error_msg.lower():
                    messagebox.showerror("错误", "❌ API配额已用完或请求过频！\n\n请稍后再试。")
                else:
                    messagebox.showerror("错误", f"❌ 连接失败：\n\n{error_msg}")
                    
        except Exception as e:
            messagebox.showerror("错误", f"❌ 测试异常：\n\n{str(e)}")
        finally:
            # 恢复按钮状态
            self.test_claude_btn.configure(text="🔍 测试", state="normal")
    
    def _test_ernie_connection(self):
        """测试文心一言API连接（Day 7新增）"""
        api_key = self.ernie_api_key_entry.get().strip()
        secret_key = self.ernie_secret_key_entry.get().strip()
        
        if not api_key or not secret_key:
            messagebox.showwarning("警告", "请先输入文心一言的API Key和Secret Key！")
            return
        
        # 禁用按钮，显示测试中
        self.test_ernie_btn.configure(text="测试中...", state="disabled")
        self.update()
        
        try:
            import asyncio
            from core.ai_engine import AIEngine, AIConfig
            
            # 创建配置
            config = AIConfig(
                ernie_api_key=api_key,
                ernie_secret_key=secret_key
            )
            engine = AIEngine(config)
            
            # 异步测试
            async def test():
                # 先获取access_token
                access_token = await engine._get_ernie_access_token()
                if not access_token:
                    return None, "无法获取access_token"
                
                # 测试调用
                response = await engine._call_ernie(
                    prompt="用一句话说'你好'"
                )
                return response, None
            
            # 运行测试
            response, error = asyncio.run(test())
            
            if error:
                messagebox.showerror("错误", f"❌ {error}\n\n请检查API Key和Secret Key是否正确。")
            elif response and response.success:
                messagebox.showinfo(
                    "成功",
                    "✅ 文心一言API连接成功！\n\n"
                    f"测试响应: {response.content[:50]}...\n"
                    f"耗时: {response.latency:.2f}秒\n\n"
                    "记得点击'保存设置'按钮保存API密钥。"
                )
            else:
                error_msg = response.error if response else "未知错误"
                if "invalid" in error_msg.lower() or "error_code" in error_msg.lower():
                    messagebox.showerror("错误", f"❌ API密钥无效或配置错误！\n\n{error_msg}")
                else:
                    messagebox.showerror("错误", f"❌ 连接失败：\n\n{error_msg}")
                    
        except Exception as e:
            messagebox.showerror("错误", f"❌ 测试异常：\n\n{str(e)}")
        finally:
            # 恢复按钮状态
            self.test_ernie_btn.configure(text="🔍 测试", state="normal")


# ===== 测试函数 =====

def main():
    """测试设置界面"""
    root = ctk.CTk()
    root.title("设置测试")
    root.geometry("1000x800")
    ctk.set_appearance_mode("dark")
    
    settings = SettingsPanel(root)
    settings.pack(fill="both", expand=True)
    
    root.mainloop()


if __name__ == "__main__":
    main()

