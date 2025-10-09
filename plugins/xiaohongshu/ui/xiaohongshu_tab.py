"""
JieDimension Toolkit - 小红书插件UI界面
提供标题生成、内容优化、标签推荐等功能的图形界面
Version: 1.0.0
"""

import customtkinter as ctk
import asyncio
import sys
import os
import threading
from typing import Optional

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from plugins.xiaohongshu.title_generator import XiaohongshuTitleGenerator, TitleStyle
from plugins.xiaohongshu.emoji_optimizer import EmojiOptimizer
from plugins.xiaohongshu.topic_recommender import TopicTagRecommender


class XiaohongshuTab(ctk.CTkFrame):
    """小红书插件UI界面"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # 初始化组件
        self.title_generator = None
        self.emoji_optimizer = EmojiOptimizer()
        self.topic_recommender = None
        
        # 创建界面
        self._create_ui()
    
    def _create_ui(self):
        """创建用户界面"""
        
        # 配置网格
        self.grid_columnconfigure(0, weight=1)
        
        # 标题
        title_label = ctk.CTkLabel(
            self,
            text="📝 小红书内容生成器",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # 输入区域
        self._create_input_section()
        
        # 生成选项
        self._create_options_section()
        
        # 结果展示
        self._create_result_section()
        
        # 操作按钮
        self._create_actions()
    
    def _create_input_section(self):
        """创建输入区域"""
        
        input_frame = ctk.CTkFrame(self)
        input_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        input_frame.grid_columnconfigure(1, weight=1)
        
        # 主题输入
        topic_label = ctk.CTkLabel(input_frame, text="笔记主题：")
        topic_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.topic_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="例如：夏日防晒推荐",
            width=400
        )
        self.topic_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # 关键词输入
        keywords_label = ctk.CTkLabel(input_frame, text="关键词：")
        keywords_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        self.keywords_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="用逗号分隔，例如：防晒霜,学生党,平价",
            width=400
        )
        self.keywords_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # 内容分类
        category_label = ctk.CTkLabel(input_frame, text="内容分类：")
        category_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        
        self.category_var = ctk.StringVar(value="美妆")
        self.category_menu = ctk.CTkOptionMenu(
            input_frame,
            variable=self.category_var,
            values=["美妆", "美食", "穿搭", "旅行", "健身", "学习", "生活", "好物"]
        )
        self.category_menu.grid(row=2, column=1, padx=10, pady=10, sticky="w")
    
    def _create_options_section(self):
        """创建生成选项区域"""
        
        options_frame = ctk.CTkFrame(self)
        options_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        options_frame.grid_columnconfigure(1, weight=1)
        
        # 标题风格
        style_label = ctk.CTkLabel(options_frame, text="标题风格：")
        style_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.style_var = ctk.StringVar(value="种草")
        self.style_menu = ctk.CTkOptionMenu(
            options_frame,
            variable=self.style_var,
            values=["种草", "教程", "分享", "测评", "疑问", "经验"]
        )
        self.style_menu.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Emoji强度
        emoji_label = ctk.CTkLabel(options_frame, text="Emoji强度：")
        emoji_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        self.emoji_var = ctk.StringVar(value="medium")
        self.emoji_menu = ctk.CTkOptionMenu(
            options_frame,
            variable=self.emoji_var,
            values=["low", "medium", "high"]
        )
        self.emoji_menu.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # 标签数量
        tags_label = ctk.CTkLabel(options_frame, text="标签数量：")
        tags_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        
        self.tags_var = ctk.StringVar(value="5")
        self.tags_menu = ctk.CTkOptionMenu(
            options_frame,
            variable=self.tags_var,
            values=["3", "5", "8", "10"]
        )
        self.tags_menu.grid(row=2, column=1, padx=10, pady=10, sticky="w")
    
    def _create_result_section(self):
        """创建结果展示区域"""
        
        result_frame = ctk.CTkFrame(self)
        result_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        self.grid_rowconfigure(3, weight=1)
        result_frame.grid_columnconfigure(0, weight=1)
        result_frame.grid_rowconfigure(1, weight=1)
        
        # 结果标签
        result_label = ctk.CTkLabel(
            result_frame,
            text="📋 生成结果",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        result_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # 结果文本框
        self.result_text = ctk.CTkTextbox(
            result_frame,
            width=600,
            height=300,
            font=ctk.CTkFont(size=13)
        )
        self.result_text.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    
    def _create_actions(self):
        """创建操作按钮区域"""
        
        action_frame = ctk.CTkFrame(self)
        action_frame.grid(row=4, column=0, padx=20, pady=20, sticky="ew")
        action_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # 生成标题按钮
        generate_title_btn = ctk.CTkButton(
            action_frame,
            text="🎯 生成标题",
            command=self._on_generate_title,
            height=40
        )
        generate_title_btn.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # 推荐标签按钮
        recommend_tags_btn = ctk.CTkButton(
            action_frame,
            text="🏷️ 推荐标签",
            command=self._on_recommend_tags,
            height=40
        )
        recommend_tags_btn.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # 复制结果按钮
        copy_btn = ctk.CTkButton(
            action_frame,
            text="📋 复制结果",
            command=self._on_copy_result,
            height=40,
            fg_color="gray",
            hover_color="darkgray"
        )
        copy_btn.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
    
    def _on_generate_title(self):
        """生成标题按钮点击事件"""
        
        # 获取输入
        topic = self.topic_entry.get().strip()
        keywords_str = self.keywords_entry.get().strip()
        
        if not topic:
            self._show_result("❌ 请输入笔记主题")
            return
        
        # 解析关键词
        keywords = [k.strip() for k in keywords_str.split(',') if k.strip()] if keywords_str else [topic]
        
        # 获取风格
        style = self.style_var.get()
        
        # 显示加载状态
        self._show_result("⏳ 正在生成标题...\n请稍候...")
        
        # 在后台线程运行
        thread = threading.Thread(
            target=self._generate_titles_async,
            args=(topic, keywords, style)
        )
        thread.daemon = True
        thread.start()
    
    def _generate_titles_async(self, topic, keywords, style):
        """异步生成标题"""
        try:
            # 创建事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 初始化生成器
            if not self.title_generator:
                from core.ai_engine import AIEngine
                self.title_generator = XiaohongshuTitleGenerator(AIEngine())
            
            # 获取风格枚举
            style_map = {
                "种草": TitleStyle.ZHONGCAO,
                "教程": TitleStyle.JIAOCHENG,
                "分享": TitleStyle.FENXIANG,
                "测评": TitleStyle.PINGCE,
                "疑问": TitleStyle.YILIAO,
                "经验": TitleStyle.JINGYAN,
            }
            title_style = style_map.get(style, TitleStyle.ZHONGCAO)
            
            # 生成多个标题
            titles = loop.run_until_complete(
                self.title_generator.generate_multiple_titles(
                    topic=topic,
                    keywords=keywords,
                    count=5,
                    style=title_style
                )
            )
            
            # 显示结果
            result = "✨ 生成的标题（选择一个使用）：\n\n"
            for i, title in enumerate(titles, 1):
                result += f"{i}. {title}\n"
            
            self._show_result(result)
            
        except Exception as e:
            self._show_result(f"❌ 生成失败：{str(e)}")
        
        finally:
            if loop:
                loop.close()
    
    def _on_recommend_tags(self):
        """推荐标签按钮点击事件"""
        
        # 获取输入
        topic = self.topic_entry.get().strip()
        
        if not topic:
            self._show_result("❌ 请输入笔记主题")
            return
        
        # 获取参数
        category = self.category_var.get()
        max_tags = int(self.tags_var.get())
        
        # 显示加载状态
        self._show_result("⏳ 正在推荐标签...\n请稍候...")
        
        # 在后台线程运行
        thread = threading.Thread(
            target=self._recommend_tags_async,
            args=(topic, category, max_tags)
        )
        thread.daemon = True
        thread.start()
    
    def _recommend_tags_async(self, topic, category, max_tags):
        """异步推荐标签"""
        try:
            # 创建事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 初始化推荐器
            if not self.topic_recommender:
                from core.ai_engine import AIEngine
                self.topic_recommender = TopicTagRecommender(AIEngine())
            
            # 推荐标签
            tags = loop.run_until_complete(
                self.topic_recommender.recommend_tags(
                    content=topic,
                    category=category,
                    max_tags=max_tags
                )
            )
            
            # 显示结果
            result = "🏷️ 推荐的话题标签：\n\n"
            result += " ".join(tags)
            result += "\n\n💡 复制后可直接粘贴到小红书笔记中"
            
            self._show_result(result)
            
        except Exception as e:
            self._show_result(f"❌ 推荐失败：{str(e)}")
        
        finally:
            if loop:
                loop.close()
    
    def _on_copy_result(self):
        """复制结果按钮点击事件"""
        
        result = self.result_text.get("1.0", "end-1c")
        
        if result.strip():
            # 复制到剪贴板
            self.clipboard_clear()
            self.clipboard_append(result)
            self._show_result(result + "\n\n✅ 已复制到剪贴板")
        else:
            self._show_result("❌ 没有内容可复制")
    
    def _show_result(self, text: str):
        """显示结果"""
        
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", text)


# 测试函数
def test_xiaohongshu_ui():
    """测试小红书UI"""
    
    # 创建主窗口
    app = ctk.CTk()
    app.title("小红书内容生成器 - 测试")
    app.geometry("800x700")
    
    # 设置主题
    ctk.set_appearance_mode("dark")
    
    # 创建小红书界面
    tab = XiaohongshuTab(app)
    tab.pack(fill="both", expand=True)
    
    # 运行
    app.mainloop()


if __name__ == "__main__":
    test_xiaohongshu_ui()

