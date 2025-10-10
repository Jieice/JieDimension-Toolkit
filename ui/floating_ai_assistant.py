"""
浮动AI助手窗口
固定在主窗口右下角，始终可见
"""

import customtkinter as ctk
from tkinter import messagebox
import asyncio
import threading
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class FloatingAIAssistant(ctk.CTkToplevel):
    """浮动AI助手"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.parent = parent
        self.is_minimized = False
        self.chat_history = []
        
        # 窗口配置
        self.title("AI助手")
        self.geometry("380x550")
        self.resizable(False, False)
        
        # 始终在最上层
        self.attributes('-topmost', True)
        
        # 设置位置（右下角）
        self._position_window()
        
        # 创建界面
        self._create_ui()
        
        # 欢迎消息
        self._add_ai_message("你好！我是AI助手。\n\n我可以调用工具帮你：\n• 分析爆款\n• 生成内容\n• 处理视频\n\n随时问我！")
        
        # 关闭窗口时最小化而不是关闭
        self.protocol("WM_DELETE_WINDOW", self._minimize)
    
    def _position_window(self):
        """定位到右下角"""
        self.update_idletasks()
        
        # 获取主窗口位置
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # 计算位置（主窗口右下角内）
        x = parent_x + parent_width - 400  # 距离右边20px
        y = parent_y + parent_height - 600  # 距离底部50px
        
        self.geometry(f"380x550+{x}+{y}")
    
    def _create_ui(self):
        """创建界面"""
        # 标题栏
        header = ctk.CTkFrame(self, fg_color=("gray85", "gray20"), height=50)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)
        header.grid_propagate(False)
        
        # 标题
        title = ctk.CTkLabel(
            header,
            text="🤖 AI助手",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.grid(row=0, column=0, padx=15, pady=12, sticky="w")
        
        # AI引擎选择（小型）
        self.ai_provider_var = ctk.StringVar(value="自动")
        ai_selector = ctk.CTkOptionMenu(
            header,
            variable=self.ai_provider_var,
            values=["自动", "Ollama", "Gemini"],
            width=90,
            height=28,
            font=ctk.CTkFont(size=11)
        )
        ai_selector.grid(row=0, column=1, padx=5, pady=12, sticky="e")
        
        # 最小化按钮
        min_btn = ctk.CTkButton(
            header,
            text="—",
            width=30,
            height=28,
            command=self._minimize,
            fg_color="transparent",
            hover_color=("gray70", "gray30")
        )
        min_btn.grid(row=0, column=2, padx=(0, 10), pady=12)
        
        # 聊天显示
        self.chat_display = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(size=13),
            wrap="word"
        )
        self.chat_display.grid(row=1, column=0, padx=15, pady=(10, 10), sticky="nsew")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # 输入区
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)
        
        self.input_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="问我任何问题...",
            height=40,
            font=ctk.CTkFont(size=13)
        )
        self.input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.input_entry.bind("<Return>", lambda e: self._send_message())
        
        self.send_btn = ctk.CTkButton(
            input_frame,
            text="发送",
            width=70,
            height=40,
            command=self._send_message
        )
        self.send_btn.grid(row=0, column=1)
    
    def _minimize(self):
        """最小化窗口"""
        self.withdraw()
        self.is_minimized = True
    
    def show(self):
        """显示窗口"""
        self.deiconify()
        self.is_minimized = False
        self._position_window()  # 重新定位
        self.lift()  # 置顶
    
    def _add_message(self, sender: str, message: str):
        """添加消息"""
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"\n{sender}:\n{message}\n", "message")
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")
    
    def _add_ai_message(self, message: str):
        """AI消息"""
        self._add_message("🤖 AI", message)
        self.chat_history.append({"role": "assistant", "content": message})
    
    def _add_user_message(self, message: str):
        """用户消息"""
        self._add_message("👤 你", message)
        self.chat_history.append({"role": "user", "content": message})
    
    def _send_message(self):
        """发送消息"""
        message = self.input_entry.get().strip()
        if not message:
            return
        
        self._add_user_message(message)
        self.input_entry.delete(0, "end")
        
        self.send_btn.configure(state="disabled", text="思考...")
        
        thread = threading.Thread(target=self._process_message, args=(message,), daemon=True)
        thread.start()
    
    def _process_message(self, user_message: str):
        """处理消息"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            from core.tool_executor import get_tool_executor
            from core.ai_engine import AIEngine, TaskComplexity, AIProvider
            
            tool_executor = get_tool_executor()
            ai_engine = AIEngine()
            
            tools_desc = tool_executor.get_tools_description()
            
            context = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in self.chat_history[-4:]
            ])
            
            prompt = f"""你是JieDimension Toolkit的AI助手。

{tools_desc}

用户需求可以用工具完成时，回复：
[TOOL: 工具名] 简短说明

否则正常回复（简洁友好）。

{context}

用户: {user_message}

AI:"""
            
            # 根据选择的AI
            selected = self.ai_provider_var.get()
            if selected == "自动":
                result = loop.run_until_complete(
                    ai_engine.generate(prompt=prompt, complexity=TaskComplexity.MEDIUM)
                )
            else:
                provider_map = {
                    "Ollama": AIProvider.OLLAMA,
                    "Gemini": AIProvider.GEMINI
                }
                provider = provider_map.get(selected, AIProvider.OLLAMA)
                result = loop.run_until_complete(
                    ai_engine.generate_with_provider(prompt=prompt, provider=provider)
                )
            
            reply = result.content if hasattr(result, 'content') else str(result)
            
            # 调用工具
            if "[TOOL:" in reply:
                tool_result = loop.run_until_complete(self._execute_tool(reply, user_message))
                self._add_ai_message(tool_result)
            else:
                self._add_ai_message(reply)
                
        except Exception as e:
            self._add_ai_message(f"抱歉：{str(e)}")
        finally:
            self.send_btn.configure(state="normal", text="发送")
            if loop:
                loop.close()
    
    async def _execute_tool(self, reply: str, user_message: str) -> str:
        """执行工具"""
        from core.tool_executor import get_tool_executor
        tool_executor = get_tool_executor()
        
        try:
            # 小红书标题
            if "generate_xiaohongshu_title" in reply:
                topic = user_message.replace("帮我生成", "").replace("小红书标题", "").replace("主题是", "").replace("，", "").strip()
                result = await tool_executor.execute_tool(
                    "generate_xiaohongshu_title",
                    {"topic": topic or "美食", "style": "种草"}
                )
                
                if result.get('success'):
                    titles = result['result']
                    text = f"✅ 小红书标题（{topic or '美食'}）：\n\n"
                    for i, t in enumerate(titles, 1):
                        text += f"{i}. {t}\n"
                    return text
            
            # B站热门
            elif "scrape_bilibili_hot" in reply:
                result = await tool_executor.execute_tool("scrape_bilibili_hot", {"limit": 5})
                if result.get('success'):
                    videos = result['result']
                    text = "✅ B站热门：\n\n"
                    for i, v in enumerate(videos[:3], 1):
                        text += f"{i}. {v.get('title')}\n   {v.get('play'):,}播放\n\n"
                    return text
            
            return reply
            
        except Exception as e:
            return f"工具失败：{str(e)}"

