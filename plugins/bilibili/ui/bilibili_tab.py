"""
B站插件UI界面

功能：
- 标题生成（3种风格）
- 动态生成
- 标签推荐
- 分区优化建议
"""

import customtkinter as ctk
import asyncio
from typing import Optional
from tkinter import messagebox
import threading

from ..title_generator import BilibiliTitleGenerator
from ..dynamic_generator import BilibiliDynamicGenerator
from ..tag_recommender import BilibiliTagRecommender
from ..zone_optimizer import BilibiliZoneOptimizer


class BilibiliTab(ctk.CTkFrame):
    """B站插件UI界面"""
    
    def __init__(self, parent, ai_engine=None):
        super().__init__(parent)
        
        # 初始化生成器
        self.title_gen = BilibiliTitleGenerator(ai_engine)
        self.dynamic_gen = BilibiliDynamicGenerator(ai_engine)
        self.tag_recommender = BilibiliTagRecommender(ai_engine)
        self.zone_optimizer = BilibiliZoneOptimizer()
        
        # 创建界面
        self._create_ui()
    
    def _create_ui(self):
        """创建UI界面"""
        
        # 配置网格
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # 左侧：输入区域
        left_frame = self._create_input_section()
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        
        # 右侧：结果区域
        right_frame = self._create_result_section()
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
    
    def _create_input_section(self) -> ctk.CTkFrame:
        """创建输入区域"""
        
        frame = ctk.CTkFrame(self)
        frame.grid_columnconfigure(0, weight=1)
        
        # 标题
        title_label = ctk.CTkLabel(
            frame,
            text="🎬 B站内容生成器",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(20, 10), sticky="w", padx=20)
        
        # === 基础信息 ===
        info_frame = ctk.CTkFrame(frame)
        info_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        info_frame.grid_columnconfigure(1, weight=1)
        
        # 视频主题
        ctk.CTkLabel(info_frame, text="视频主题:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.topic_entry = ctk.CTkEntry(info_frame, placeholder_text="例如：Python从入门到精通")
        self.topic_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        
        # 关键词
        ctk.CTkLabel(info_frame, text="关键词:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.keywords_entry = ctk.CTkEntry(info_frame, placeholder_text="用逗号分隔，例如：Python,教程,编程")
        self.keywords_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        
        # 视频描述
        ctk.CTkLabel(info_frame, text="视频描述:").grid(row=2, column=0, sticky="nw", padx=10, pady=5)
        self.description_text = ctk.CTkTextbox(info_frame, height=80)
        self.description_text.grid(row=2, column=1, sticky="ew", padx=10, pady=5)
        
        # === 生成选项 ===
        options_frame = ctk.CTkFrame(frame)
        options_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        options_frame.grid_columnconfigure(1, weight=1)
        
        # 分区选择
        ctk.CTkLabel(options_frame, text="视频分区:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.zone_var = ctk.StringVar(value="生活")
        zone_menu = ctk.CTkOptionMenu(
            options_frame,
            variable=self.zone_var,
            values=["游戏", "科技", "知识", "生活", "娱乐"]
        )
        zone_menu.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # 标题风格
        ctk.CTkLabel(options_frame, text="标题风格:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.style_var = ctk.StringVar(value="悬念型")
        style_menu = ctk.CTkOptionMenu(
            options_frame,
            variable=self.style_var,
            values=["悬念型", "教程型", "测评型"]
        )
        style_menu.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        # 生成数量
        ctk.CTkLabel(options_frame, text="标题数量:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.count_var = ctk.StringVar(value="5")
        count_menu = ctk.CTkOptionMenu(
            options_frame,
            variable=self.count_var,
            values=["3", "5", "8", "10"]
        )
        count_menu.grid(row=2, column=1, sticky="w", padx=10, pady=5)
        
        # 使用AI增强
        self.use_ai_var = ctk.BooleanVar(value=True)
        ai_check = ctk.CTkCheckBox(
            options_frame,
            text="使用AI增强生成",
            variable=self.use_ai_var
        )
        ai_check.grid(row=3, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        
        # === 操作按钮 ===
        button_frame = ctk.CTkFrame(frame)
        button_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=20)
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # 生成标题
        self.gen_title_btn = ctk.CTkButton(
            button_frame,
            text="🎯 生成标题",
            command=self._generate_titles,
            height=40
        )
        self.gen_title_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # 生成动态
        self.gen_dynamic_btn = ctk.CTkButton(
            button_frame,
            text="📝 生成动态",
            command=self._generate_dynamic,
            height=40
        )
        self.gen_dynamic_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # 推荐标签
        self.gen_tags_btn = ctk.CTkButton(
            button_frame,
            text="🏷️ 推荐标签",
            command=self._recommend_tags,
            height=40
        )
        self.gen_tags_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        # 分区建议
        zone_suggest_btn = ctk.CTkButton(
            button_frame,
            text="🎯 分区建议",
            command=self._show_zone_suggestions,
            height=40,
            fg_color="gray40"
        )
        zone_suggest_btn.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        
        return frame
    
    def _create_result_section(self) -> ctk.CTkFrame:
        """创建结果区域"""
        
        frame = ctk.CTkFrame(self)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # 标题
        result_label = ctk.CTkLabel(
            frame,
            text="📊 生成结果",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        result_label.grid(row=0, column=0, pady=(20, 10), sticky="w", padx=20)
        
        # 结果文本框
        self.result_text = ctk.CTkTextbox(
            frame,
            font=ctk.CTkFont(size=13),
            wrap="word"
        )
        self.result_text.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        # 操作按钮
        action_frame = ctk.CTkFrame(frame)
        action_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        action_frame.grid_columnconfigure((0, 1), weight=1)
        
        # 复制结果
        copy_btn = ctk.CTkButton(
            action_frame,
            text="📋 复制结果",
            command=self._copy_result,
            height=35
        )
        copy_btn.grid(row=0, column=0, padx=5, sticky="ew")
        
        # 清空
        clear_btn = ctk.CTkButton(
            action_frame,
            text="🗑️ 清空",
            command=self._clear_result,
            height=35,
            fg_color="gray40"
        )
        clear_btn.grid(row=0, column=1, padx=5, sticky="ew")
        
        return frame
    
    # ===== 功能方法 =====
    
    def _generate_titles(self):
        """生成标题"""
        
        # 验证输入
        topic = self.topic_entry.get().strip()
        if not topic:
            messagebox.showwarning("提示", "请输入视频主题！")
            return
        
        # 解析关键词
        keywords_str = self.keywords_entry.get().strip()
        keywords = [kw.strip() for kw in keywords_str.split(",") if kw.strip()] if keywords_str else [topic]
        
        # 获取选项
        zone = self.zone_var.get()
        style = self.style_var.get()
        count = int(self.count_var.get())
        use_ai = self.use_ai_var.get()
        
        # 禁用按钮
        self.gen_title_btn.configure(state="disabled", text="生成中...")
        
        # 异步生成
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                titles = loop.run_until_complete(
                    self.title_gen.generate_titles(
                        topic=topic,
                        keywords=keywords,
                        style=style,
                        zone=zone,
                        count=count,
                        use_ai=use_ai
                    )
                )
                
                # 显示结果
                self._display_titles(titles, style, zone)
                
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("错误", f"生成失败: {e}"))
            finally:
                loop.close()
                # 恢复按钮
                self.after(0, lambda: self.gen_title_btn.configure(
                    state="normal", text="🎯 生成标题"
                ))
        
        # 在后台线程运行
        thread = threading.Thread(target=run_async, daemon=True)
        thread.start()
    
    def _display_titles(self, titles, style, zone):
        """显示标题结果"""
        
        result = f"🎬 B站标题生成结果\n"
        result += f"{'='*50}\n\n"
        result += f"风格：{style} | 分区：{zone}\n\n"
        
        for i, item in enumerate(titles, 1):
            result += f"{i}. {item['title']}\n"
            result += f"   📊 评分: {item['score']}分 | 长度: {item['length']}字\n\n"
        
        result += f"{'='*50}\n"
        result += "💡 提示：选择评分高的标题，或根据需要修改\n"
        
        self._show_result(result)
    
    def _generate_dynamic(self):
        """生成动态"""
        
        topic = self.topic_entry.get().strip()
        description = self.description_text.get("1.0", "end").strip()
        
        if not topic:
            messagebox.showwarning("提示", "请输入视频主题！")
            return
        
        # 提取亮点（简单处理）
        highlights = []
        if description:
            lines = description.split("\n")
            highlights = [line.strip() for line in lines if line.strip()][:3]
        
        if not highlights:
            highlights = [f"精彩内容：{topic}"]
        
        # 标签
        keywords_str = self.keywords_entry.get().strip()
        hashtags = [kw.strip() for kw in keywords_str.split(",") if kw.strip()][:3]
        
        # 禁用按钮
        self.gen_dynamic_btn.configure(state="disabled", text="生成中...")
        
        # 异步生成
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                dynamic = loop.run_until_complete(
                    self.dynamic_gen.generate_short_dynamic(
                        video_title=topic,
                        highlights=highlights,
                        hashtags=hashtags
                    )
                )
                
                # 显示结果
                result = f"📝 B站动态文案\n{'='*50}\n\n{dynamic}\n\n{'='*50}\n"
                result += f"字数: {len(dynamic)}/233\n"
                
                self._show_result(result)
                
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("错误", f"生成失败: {e}"))
            finally:
                loop.close()
                self.after(0, lambda: self.gen_dynamic_btn.configure(
                    state="normal", text="📝 生成动态"
                ))
        
        thread = threading.Thread(target=run_async, daemon=True)
        thread.start()
    
    def _recommend_tags(self):
        """推荐标签"""
        
        topic = self.topic_entry.get().strip()
        description = self.description_text.get("1.0", "end").strip()
        
        if not topic:
            messagebox.showwarning("提示", "请输入视频主题！")
            return
        
        zone = self.zone_var.get()
        use_ai = self.use_ai_var.get()
        
        # 禁用按钮
        self.gen_tags_btn.configure(state="disabled", text="推荐中...")
        
        # 异步推荐
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                tags = loop.run_until_complete(
                    self.tag_recommender.recommend_tags(
                        title=topic,
                        content=description or topic,
                        zone=zone,
                        count=10,
                        use_ai=use_ai
                    )
                )
                
                # 显示结果
                result = f"🏷️ B站标签推荐\n{'='*50}\n\n"
                result += f"分区：{zone} | 推荐{len(tags)}个标签\n\n"
                
                for i, tag_info in enumerate(tags, 1):
                    result += f"{i}. {tag_info['tag']} "
                    result += f"(热度:{tag_info['hot_score']}, 相关:{tag_info['score']})\n"
                
                result += f"\n{'='*50}\n"
                result += "💡 建议选择5-10个标签，包含热门+长尾\n"
                
                self._show_result(result)
                
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("错误", f"推荐失败: {e}"))
            finally:
                loop.close()
                self.after(0, lambda: self.gen_tags_btn.configure(
                    state="normal", text="🏷️ 推荐标签"
                ))
        
        thread = threading.Thread(target=run_async, daemon=True)
        thread.start()
    
    def _show_zone_suggestions(self):
        """显示分区建议"""
        
        topic = self.topic_entry.get().strip()
        description = self.description_text.get("1.0", "end").strip()
        
        if not topic:
            messagebox.showwarning("提示", "请输入视频主题！")
            return
        
        # 推荐分区
        suggestions = self.zone_optimizer.suggest_zone(topic, description or topic)
        
        # 当前分区优化
        current_zone = self.zone_var.get()
        optimize_result = self.zone_optimizer.optimize_for_zone(
            content={"title": topic, "description": description},
            zone=current_zone
        )
        
        # 显示结果
        result = f"🎯 分区建议\n{'='*50}\n\n"
        
        # 推荐分区
        result += "📊 推荐分区（按匹配度排序）：\n\n"
        for i, sug in enumerate(suggestions[:3], 1):
            result += f"{i}. {sug['zone']} - {sug['score']}分\n"
            result += f"   {sug['description']}\n"
            if sug['matched_keywords']:
                result += f"   匹配词: {', '.join(sug['matched_keywords'][:3])}\n"
            result += "\n"
        
        # 当前分区优化
        result += f"\n📝 当前分区（{current_zone}）优化建议：\n\n"
        result += f"匹配度：{optimize_result['score']}分\n\n"
        
        if optimize_result['suggestions']:
            result += "需要改进：\n"
            for sug in optimize_result['suggestions']:
                result += f"  [{sug['priority']}] {sug['type']}: {sug['issue']}\n"
        else:
            result += "✅ 内容与分区匹配良好！\n"
        
        result += f"\n{'='*50}\n"
        
        self._show_result(result)
    
    def _show_result(self, text: str):
        """显示结果"""
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", text)
    
    def _copy_result(self):
        """复制结果"""
        content = self.result_text.get("1.0", "end").strip()
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)
            messagebox.showinfo("成功", "结果已复制到剪贴板！")
        else:
            messagebox.showwarning("提示", "没有可复制的内容！")
    
    def _clear_result(self):
        """清空结果"""
        self.result_text.delete("1.0", "end")

