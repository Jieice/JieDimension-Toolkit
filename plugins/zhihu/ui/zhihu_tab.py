"""
JieDimension Toolkit - 知乎插件UI界面
提供标题生成、内容生成、SEO优化等功能的图形界面
Version: 1.0.0
"""

import customtkinter as ctk
import asyncio
import sys
import os
from typing import Optional
import threading

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from plugins.zhihu.title_generator import ZhihuTitleGenerator
from plugins.zhihu.seo_optimizer import SEOOptimizer
from plugins.zhihu.content_generator import ZhihuContentGenerator


class ZhihuTab(ctk.CTkFrame):
    """知乎插件UI界面"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # 初始化组件
        self.title_generator = None
        self.seo_optimizer = SEOOptimizer()
        self.content_generator = None
        
        # 创建界面
        self._create_ui()
    
    def _create_ui(self):
        """创建用户界面"""
        
        # 配置网格
        self.grid_columnconfigure(0, weight=1)
        
        # 标题
        title_label = ctk.CTkLabel(
            self,
            text="📖 知乎内容生成器",
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
        
        # 文章主题
        topic_label = ctk.CTkLabel(input_frame, text="文章主题：")
        topic_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.topic_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="例如：如何高效学习Python编程",
            width=400
        )
        self.topic_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # 关键词
        keywords_label = ctk.CTkLabel(input_frame, text="关键词：")
        keywords_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        self.keywords_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="用逗号分隔，例如：Python,编程,学习方法",
            width=400
        )
        self.keywords_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # 文章类型
        type_label = ctk.CTkLabel(input_frame, text="文章类型：")
        type_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        
        self.type_var = ctk.StringVar(value="问答型")
        self.type_menu = ctk.CTkOptionMenu(
            input_frame,
            variable=self.type_var,
            values=["问答型", "分析型", "指南型", "总结型", "经验型"]
        )
        self.type_menu.grid(row=2, column=1, padx=10, pady=10, sticky="w")
    
    def _create_options_section(self):
        """创建生成选项"""
        
        options_frame = ctk.CTkFrame(self)
        options_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        options_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # 标题风格
        style_frame = ctk.CTkFrame(options_frame)
        style_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        style_label = ctk.CTkLabel(
            style_frame,
            text="标题风格",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        style_label.pack(pady=5)
        
        self.style_var = ctk.StringVar(value="问答型")
        style_options = ["问答型", "分析型", "指南型", "总结型", "经验型"]
        for style in style_options:
            radio = ctk.CTkRadioButton(
                style_frame,
                text=style,
                variable=self.style_var,
                value=style
            )
            radio.pack(pady=2, padx=10, anchor="w")
        
        # 生成数量
        count_frame = ctk.CTkFrame(options_frame)
        count_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        count_label = ctk.CTkLabel(
            count_frame,
            text="生成数量",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        count_label.pack(pady=5)
        
        self.count_var = ctk.StringVar(value="5")
        count_slider = ctk.CTkSlider(
            count_frame,
            from_=3,
            to=10,
            number_of_steps=7,
            command=self._on_count_change
        )
        count_slider.set(5)
        count_slider.pack(pady=10, padx=10, fill="x")
        
        self.count_label = ctk.CTkLabel(
            count_frame,
            text="5 个标题",
            font=ctk.CTkFont(size=14)
        )
        self.count_label.pack(pady=5)
        
        # 字数设置
        wordcount_frame = ctk.CTkFrame(options_frame)
        wordcount_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        
        wordcount_label = ctk.CTkLabel(
            wordcount_frame,
            text="文章字数",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        wordcount_label.pack(pady=5)
        
        self.wordcount_var = ctk.StringVar(value="1500")
        wordcount_options = ["500", "1000", "1500", "2000", "3000"]
        for count in wordcount_options:
            radio = ctk.CTkRadioButton(
                wordcount_frame,
                text=f"{count} 字",
                variable=self.wordcount_var,
                value=count
            )
            radio.pack(pady=2, padx=10, anchor="w")
    
    def _create_result_section(self):
        """创建结果展示区域"""
        
        result_frame = ctk.CTkFrame(self)
        result_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        result_frame.grid_rowconfigure(1, weight=1)
        result_frame.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        
        # 结果标签
        result_label = ctk.CTkLabel(
            result_frame,
            text="生成结果",
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
        self.result_text.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        # 默认提示
        self.result_text.insert("1.0", "点击下方按钮开始生成内容...\n\n" + 
                                "功能说明：\n" +
                                "• 生成标题：生成5-10个专业的知乎标题\n" +
                                "• 生成大纲：生成文章结构大纲\n" +
                                "• 生成全文：生成完整的文章内容\n" +
                                "• SEO优化：优化关键词布局和密度\n" +
                                "• 复制结果：一键复制生成的内容")
        self.result_text.configure(state="disabled")
    
    def _create_actions(self):
        """创建操作按钮"""
        
        action_frame = ctk.CTkFrame(self)
        action_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        action_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        # 生成标题按钮
        self.generate_title_btn = ctk.CTkButton(
            action_frame,
            text="🎯 生成标题",
            command=self._on_generate_title,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        )
        self.generate_title_btn.grid(row=0, column=0, padx=5, pady=10, sticky="ew")
        
        # 生成大纲按钮
        self.generate_outline_btn = ctk.CTkButton(
            action_frame,
            text="📋 生成大纲",
            command=self._on_generate_outline,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            fg_color=("#3B8ED0", "#1F6AA5")
        )
        self.generate_outline_btn.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        
        # 生成全文按钮
        self.generate_full_btn = ctk.CTkButton(
            action_frame,
            text="📝 生成全文",
            command=self._on_generate_full,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            fg_color=("#2E8B57", "#228B22")
        )
        self.generate_full_btn.grid(row=0, column=2, padx=5, pady=10, sticky="ew")
        
        # SEO优化按钮
        self.seo_optimize_btn = ctk.CTkButton(
            action_frame,
            text="🔍 SEO优化",
            command=self._on_seo_optimize,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            fg_color=("#FF8C00", "#FF6347")
        )
        self.seo_optimize_btn.grid(row=0, column=3, padx=5, pady=10, sticky="ew")
        
        # 复制结果按钮
        self.copy_btn = ctk.CTkButton(
            action_frame,
            text="📋 复制结果",
            command=self._on_copy_result,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            fg_color=("#808080", "#696969")
        )
        self.copy_btn.grid(row=0, column=4, padx=5, pady=10, sticky="ew")
    
    def _on_count_change(self, value):
        """标题数量滑块改变"""
        count = int(value)
        self.count_var.set(str(count))
        self.count_label.configure(text=f"{count} 个标题")
    
    def _on_generate_title(self):
        """生成标题"""
        # 获取输入
        topic = self.topic_entry.get().strip()
        if not topic:
            self._show_result("⚠️ 请输入文章主题")
            return
        
        keywords_text = self.keywords_entry.get().strip()
        keywords = [k.strip() for k in keywords_text.split(',') if k.strip()] if keywords_text else []
        
        style = self.style_var.get()
        count = int(self.count_var.get())
        
        # 禁用按钮
        self._disable_buttons()
        self._show_result("🔄 正在生成标题...\n请稍候...")
        
        # 在后台线程运行
        thread = threading.Thread(
            target=self._generate_titles_async,
            args=(topic, keywords, style, count)
        )
        thread.daemon = True
        thread.start()
    
    def _generate_titles_async(self, topic, keywords, style, count):
        """异步生成标题"""
        try:
            # 创建事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 初始化生成器
            if not self.title_generator:
                from core.ai_engine import AIEngine
                self.title_generator = ZhihuTitleGenerator(ai_engine=AIEngine())
            
            # 生成标题
            titles = loop.run_until_complete(
                self.title_generator.generate_title(
                    topic=topic,
                    keywords=keywords,
                    style=style,
                    use_ai=True,
                    count=count
                )
            )
            
            # 显示结果
            result_text = f"📖 知乎标题生成结果\n\n"
            result_text += f"主题：{topic}\n"
            result_text += f"风格：{style}\n"
            result_text += f"关键词：{', '.join(keywords) if keywords else '无'}\n"
            result_text += "="*50 + "\n\n"
            
            for i, title in enumerate(titles, 1):
                result_text += f"{i}. {title}\n\n"
                
                # 分析质量
                analysis = self.title_generator.analyze_title_quality(title)
                result_text += f"   质量评分：{analysis['score']}/100 ({analysis['level']})\n"
                if analysis['suggestions']:
                    result_text += f"   优化建议：{'; '.join(analysis['suggestions'])}\n"
                result_text += "\n"
            
            self._show_result(result_text)
            
        except Exception as e:
            self._show_result(f"❌ 生成失败: {str(e)}")
        
        finally:
            self._enable_buttons()
            if loop:
                loop.close()
    
    def _on_generate_outline(self):
        """生成大纲"""
        topic = self.topic_entry.get().strip()
        if not topic:
            self._show_result("⚠️ 请输入文章主题")
            return
        
        keywords_text = self.keywords_entry.get().strip()
        keywords = [k.strip() for k in keywords_text.split(',') if k.strip()] if keywords_text else []
        article_type = self.type_var.get()
        
        self._disable_buttons()
        self._show_result("🔄 正在生成大纲...\n请稍候...")
        
        thread = threading.Thread(
            target=self._generate_outline_async,
            args=(topic, keywords, article_type)
        )
        thread.daemon = True
        thread.start()
    
    def _generate_outline_async(self, topic, keywords, article_type):
        """异步生成大纲"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            if not self.content_generator:
                from core.ai_engine import AIEngine
                self.content_generator = ZhihuContentGenerator(ai_engine=AIEngine())
            
            outline = loop.run_until_complete(
                self.content_generator.generate_outline(
                    topic=topic,
                    article_type=article_type,
                    keywords=keywords
                )
            )
            
            result_text = f"📋 文章大纲\n\n"
            result_text += f"主题：{topic}\n"
            result_text += f"类型：{article_type}\n"
            result_text += f"关键词：{', '.join(keywords) if keywords else '无'}\n"
            result_text += "="*50 + "\n\n"
            result_text += outline.get('content', '生成失败')
            
            self._show_result(result_text)
            
        except Exception as e:
            self._show_result(f"❌ 生成失败: {str(e)}")
        
        finally:
            self._enable_buttons()
            if loop:
                loop.close()
    
    def _on_generate_full(self):
        """生成全文"""
        topic = self.topic_entry.get().strip()
        if not topic:
            self._show_result("⚠️ 请输入文章主题")
            return
        
        keywords_text = self.keywords_entry.get().strip()
        keywords = [k.strip() for k in keywords_text.split(',') if k.strip()] if keywords_text else []
        article_type = self.type_var.get()
        word_count = int(self.wordcount_var.get())
        
        self._disable_buttons()
        self._show_result(f"🔄 正在生成 {word_count} 字文章...\n这可能需要1-2分钟，请耐心等候...")
        
        thread = threading.Thread(
            target=self._generate_full_async,
            args=(topic, keywords, article_type, word_count)
        )
        thread.daemon = True
        thread.start()
    
    def _generate_full_async(self, topic, keywords, article_type, word_count):
        """异步生成全文"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            if not self.content_generator:
                from core.ai_engine import AIEngine
                self.content_generator = ZhihuContentGenerator(ai_engine=AIEngine())
            
            article = loop.run_until_complete(
                self.content_generator.generate_full_article(
                    topic=topic,
                    article_type=article_type,
                    keywords=keywords,
                    word_count=word_count
                )
            )
            
            self._show_result(article['full_content'])
            
        except Exception as e:
            self._show_result(f"❌ 生成失败: {str(e)}")
        
        finally:
            self._enable_buttons()
            if loop:
                loop.close()
    
    def _on_seo_optimize(self):
        """SEO优化"""
        # 获取当前结果
        current_text = self.result_text.get("1.0", "end-1c").strip()
        
        if not current_text or "请输入" in current_text:
            self._show_result("⚠️ 请先生成内容再进行SEO优化")
            return
        
        keywords_text = self.keywords_entry.get().strip()
        keywords = [k.strip() for k in keywords_text.split(',') if k.strip()] if keywords_text else []
        
        if not keywords:
            self._show_result("⚠️ 请输入关键词以进行SEO优化")
            return
        
        # SEO分析
        result_text = "🔍 SEO优化分析\n\n"
        result_text += "="*50 + "\n\n"
        
        # 关键词密度分析
        density = self.seo_optimizer.analyze_keyword_density(current_text, keywords)
        result_text += "📊 关键词密度分析：\n\n"
        for word, data in density.items():
            result_text += f"• {word}: {data['density']}% ({data['status']})\n"
            result_text += f"  出现次数：{data['count']}\n"
        result_text += "\n"
        
        # 可读性检查
        readability = self.seo_optimizer.check_readability(current_text)
        result_text += "📖 可读性分析：\n\n"
        result_text += f"• 评分：{readability['score']}/100 ({readability['level']})\n"
        result_text += f"• 总字数：{readability['total_chars']}\n"
        result_text += f"• 句子数：{readability['sentences']}\n"
        result_text += f"• 段落数：{readability['paragraphs']}\n"
        result_text += f"• 平均句长：{readability['avg_sentence_length']}字\n"
        
        if readability['issues']:
            result_text += "\n优化建议：\n"
            for issue in readability['issues']:
                result_text += f"  ⚠️ {issue}\n"
        
        result_text += "\n" + "="*50 + "\n\n"
        result_text += "原文内容：\n\n" + current_text
        
        self._show_result(result_text)
    
    def _on_copy_result(self):
        """复制结果"""
        result = self.result_text.get("1.0", "end-1c")
        
        # 复制到剪贴板
        self.clipboard_clear()
        self.clipboard_append(result)
        
        # 临时提示
        original_text = self.copy_btn.cget("text")
        self.copy_btn.configure(text="✅ 已复制")
        self.after(2000, lambda: self.copy_btn.configure(text=original_text))
    
    def _show_result(self, text):
        """显示结果"""
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", text)
        self.result_text.configure(state="disabled")
    
    def _disable_buttons(self):
        """禁用所有按钮"""
        self.generate_title_btn.configure(state="disabled")
        self.generate_outline_btn.configure(state="disabled")
        self.generate_full_btn.configure(state="disabled")
        self.seo_optimize_btn.configure(state="disabled")
    
    def _enable_buttons(self):
        """启用所有按钮"""
        self.generate_title_btn.configure(state="normal")
        self.generate_outline_btn.configure(state="normal")
        self.generate_full_btn.configure(state="normal")
        self.seo_optimize_btn.configure(state="normal")


# 测试代码
def test_zhihu_tab():
    """测试知乎UI界面"""
    
    # 创建主窗口
    app = ctk.CTk()
    app.title("知乎插件测试")
    app.geometry("800x700")
    
    # 设置主题
    ctk.set_appearance_mode("dark")
    
    # 创建知乎Tab
    zhihu_tab = ZhihuTab(app)
    zhihu_tab.pack(fill="both", expand=True, padx=10, pady=10)
    
    # 运行
    app.mainloop()


if __name__ == "__main__":
    test_zhihu_tab()


