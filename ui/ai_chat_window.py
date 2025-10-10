"""
AI助手聊天窗口
用户通过对话操控工具和剪映
"""

import customtkinter as ctk
from tkinter import messagebox
import asyncio
import threading
from typing import List, Dict
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class AIChatWindow(ctk.CTkFrame):
    """AI助手聊天界面"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # 配置网格
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # 聊天历史
        self.chat_history = []
        
        # 创建界面
        self._create_ui()
        
        # 欢迎消息
        self._add_ai_message("你好！我是AI助手。\n\n我可以帮你：\n• 分析视频爆款原因\n• 生成视频脚本\n• 操控剪映剪辑\n• 批量处理内容\n\n请告诉我你想做什么？")
    
    def _create_ui(self):
        """创建用户界面"""
        # 标题栏
        header = ctk.CTkFrame(self, fg_color=("gray85", "gray20"), height=60)
        header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header.grid_columnconfigure(1, weight=1)
        header.grid_propagate(False)
        
        # 标题
        title = ctk.CTkLabel(
            header,
            text="🤖 AI助手",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # 清空按钮
        clear_btn = ctk.CTkButton(
            header,
            text="🗑️ 清空",
            width=80,
            height=35,
            command=self._clear_chat,
            fg_color="transparent",
            border_width=1
        )
        clear_btn.grid(row=0, column=1, padx=20, pady=15, sticky="e")
        
        # 聊天显示区域（可滚动）
        self.chat_display = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(size=14),
            wrap="word",
            state="disabled"
        )
        self.chat_display.grid(row=1, column=0, padx=20, pady=(10, 10), sticky="nsew")
        
        # 输入区域
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)
        
        # 输入框
        self.input_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="输入你的问题或指令...",
            height=50,
            font=ctk.CTkFont(size=14)
        )
        self.input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.input_entry.bind("<Return>", lambda e: self._send_message())
        
        # 发送按钮
        self.send_btn = ctk.CTkButton(
            input_frame,
            text="发送",
            width=100,
            height=50,
            command=self._send_message,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.send_btn.grid(row=0, column=1)
        
        # 快捷指令区域
        shortcuts_frame = ctk.CTkFrame(self, fg_color=("gray90", "gray20"))
        shortcuts_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        ctk.CTkLabel(
            shortcuts_frame,
            text="💡 快捷指令",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=0, columnspan=3, padx=15, pady=(10, 5), sticky="w")
        
        shortcuts = [
            "分析B站热门视频",
            "生成60秒视频脚本",
            "剪辑视频加字幕"
        ]
        
        for i, text in enumerate(shortcuts):
            btn = ctk.CTkButton(
                shortcuts_frame,
                text=text,
                width=150,
                height=30,
                fg_color="transparent",
                border_width=1,
                command=lambda t=text: self._use_shortcut(t)
            )
            btn.grid(row=1, column=i, padx=10, pady=(0, 10))
    
    def _add_message(self, sender: str, message: str, color: str = None):
        """添加消息到聊天显示"""
        self.chat_display.configure(state="normal")
        
        # 发送者标签
        self.chat_display.insert("end", f"\n{sender}:\n", "sender")
        
        # 消息内容
        self.chat_display.insert("end", f"{message}\n", "message")
        
        # 滚动到底部
        self.chat_display.see("end")
        
        self.chat_display.configure(state="disabled")
    
    def _add_ai_message(self, message: str):
        """添加AI回复"""
        self._add_message("🤖 AI助手", message)
        self.chat_history.append({"role": "assistant", "content": message})
    
    def _add_user_message(self, message: str):
        """添加用户消息"""
        self._add_message("👤 你", message)
        self.chat_history.append({"role": "user", "content": message})
    
    def _send_message(self):
        """发送消息"""
        message = self.input_entry.get().strip()
        if not message:
            return
        
        # 显示用户消息
        self._add_user_message(message)
        
        # 清空输入框
        self.input_entry.delete(0, "end")
        
        # 禁用发送按钮
        self.send_btn.configure(state="disabled", text="思考中...")
        
        # 在后台处理
        thread = threading.Thread(target=self._process_message, args=(message,), daemon=True)
        thread.start()
    
    def _process_message(self, user_message: str):
        """处理用户消息"""
        try:
            # 创建事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 导入工具执行器
            from core.tool_executor import get_tool_executor
            from core.ai_engine import AIEngine, TaskComplexity
            
            tool_executor = get_tool_executor()
            ai_engine = AIEngine()
            
            # 获取可用工具列表
            tools_desc = tool_executor.get_tools_description()
            
            # 构建提示词（包含工具信息）
            context = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in self.chat_history[-4:]  # 最近4轮对话
            ])
            
            prompt = f"""你是JieDimension Toolkit的AI助手，可以调用工具帮助用户。

{tools_desc}

如果用户需求可以用工具完成，回复格式：
[TOOL: 工具名] 参数说明

否则正常回复。

上下文：
{context}

用户: {user_message}

AI助手:"""
            
            # 生成回复
            result = loop.run_until_complete(
                ai_engine.generate(
                    prompt=prompt,
                    complexity=TaskComplexity.MEDIUM
                )
            )
            
            # 获取回复文本
            reply = result.content if hasattr(result, 'content') else str(result)
            
            # 检查是否需要调用工具
            if "[TOOL:" in reply:
                # 解析工具调用（传入用户消息用于提取参数）
                tool_result = loop.run_until_complete(self._execute_tool_from_reply(reply, user_message))
                self._add_ai_message(tool_result)
            else:
                # 普通回复
                self._add_ai_message(reply)
            
        except Exception as e:
            self._add_ai_message(f"抱歉，处理失败：{str(e)}")
        
        finally:
            # 恢复发送按钮
            self.send_btn.configure(state="normal", text="发送")
            if loop:
                loop.close()
    
    async def _execute_tool_from_reply(self, reply: str, user_message: str = "") -> str:
        """从AI回复中解析并执行工具"""
        try:
            from core.tool_executor import get_tool_executor
            tool_executor = get_tool_executor()
            
            # 改进的解析逻辑
            if "generate_xiaohongshu_title" in reply:
                # 从用户消息提取主题
                topic = user_message.replace("帮我生成", "").replace("小红书标题", "").replace("主题是", "").strip()
                if not topic:
                    topic = "美食"  # 默认
                
                result = await tool_executor.execute_tool(
                    "generate_xiaohongshu_title",
                    {"topic": topic, "style": "种草"}
                )
                
                if result.get('success'):
                    titles = result['result']
                    result_text = f"✅ 已生成小红书标题（主题：{topic}）：\n\n"
                    for i, title in enumerate(titles, 1):
                        result_text += f"{i}. {title}\n"
                    return result_text
            
            elif "scrape_bilibili_hot" in reply or "B站热门" in reply:
                result = await tool_executor.execute_tool("scrape_bilibili_hot", {"limit": 5})
                if result.get('success'):
                    videos = result['result']
                    result_text = "✅ 已抓取B站热门视频：\n\n"
                    for i, v in enumerate(videos[:3], 1):
                        result_text += f"{i}. {v.get('title')}\n"
                        result_text += f"   {v.get('play'):,}播放 | {v.get('like'):,}点赞\n\n"
                    return result_text
            
            elif "analyze_viral_title" in reply:
                return "请提供要分析的标题，例如：分析标题'XXXX'"
            
            elif "generate_video_script" in reply:
                # 提取主题
                topic = user_message.replace("生成", "").replace("脚本", "").replace("视频", "").strip()
                result = await tool_executor.execute_tool(
                    "generate_video_script",
                    {"topic": topic, "duration": 60}
                )
                
                if result.get('success'):
                    script = result['result']
                    return f"✅ 视频脚本已生成：\n\n{script.get('full_script', '')}"
            
            elif "get_statistics" in reply or "统计" in reply:
                result = await tool_executor.execute_tool("get_statistics", {})
                if result.get('success'):
                    stats = result['result']
                    return f"📊 统计数据：\n总生成：{stats.get('total_generated')}\n成功率：{stats.get('success_rate')}%\n今日：{stats.get('today')}"
            
            else:
                return reply
                
        except Exception as e:
            return f"工具执行失败：{str(e)}"
    
    def _use_shortcut(self, shortcut_text: str):
        """使用快捷指令"""
        self.input_entry.delete(0, "end")
        self.input_entry.insert(0, shortcut_text)
        self._send_message()
    
    def _clear_chat(self):
        """清空聊天记录"""
        if not messagebox.askyesno("确认", "确定清空聊天记录？"):
            return
        
        self.chat_history = []
        self.chat_display.configure(state="normal")
        self.chat_display.delete("1.0", "end")
        self.chat_display.configure(state="disabled")
        
        # 重新添加欢迎消息
        self._add_ai_message("聊天已清空。有什么我可以帮你的吗？")

