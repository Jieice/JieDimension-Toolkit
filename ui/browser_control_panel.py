# ui/browser_control_panel.py

"""
浏览器控制面板 - 管理浏览器自动化
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import asyncio
import threading
from typing import Optional
from pathlib import Path
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.browser_automation import BrowserAutomation, XianyuAutomation


class BrowserControlPanel(ctk.CTkFrame):
    """浏览器控制面板"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # 配置网格
        self.grid_columnconfigure(0, weight=1)
        
        # 浏览器实例
        self.browser: Optional[XianyuAutomation] = None
        self.browser_running = False
        self.event_loop: Optional[asyncio.AbstractEventLoop] = None
        
        # Cookie文件路径
        self.cookies_file = "data/xianyu_cookies.json"
        
        # 创建界面
        self._create_header()
        self._create_controls()
        self._create_status_section()
        self._create_log_section()
        
    def _create_header(self):
        """创建标题"""
        
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        # 标题
        title = ctk.CTkLabel(
            header_frame,
            text="🌐 浏览器自动化控制台",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(side="left", padx=20, pady=15)
        
        # 说明
        desc = ctk.CTkLabel(
            header_frame,
            text="管理闲鱼自动化浏览器 - 登录、发布、调试",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        desc.pack(side="left", padx=10)
    
    def _create_controls(self):
        """创建控制区"""
        
        controls_frame = ctk.CTkFrame(self)
        controls_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        controls_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # 浏览器控制
        browser_frame = ctk.CTkFrame(controls_frame, fg_color=("gray90", "gray17"))
        browser_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(
            browser_frame,
            text="🚀 浏览器控制",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10))
        
        self.start_btn = ctk.CTkButton(
            browser_frame,
            text="▶️ 启动浏览器",
            command=self._start_browser,
            width=180,
            height=40
        )
        self.start_btn.pack(pady=5)
        
        self.stop_btn = ctk.CTkButton(
            browser_frame,
            text="⏹️ 停止浏览器",
            command=self._stop_browser,
            width=180,
            height=40,
            state="disabled"
        )
        self.stop_btn.pack(pady=5)
        
        # Headless模式开关
        self.headless_var = ctk.BooleanVar(value=False)
        self.headless_switch = ctk.CTkSwitch(
            browser_frame,
            text="无头模式 (Headless)",
            variable=self.headless_var,
            onvalue=True,
            offvalue=False
        )
        self.headless_switch.pack(pady=(10, 15))
        
        # 登录控制
        login_frame = ctk.CTkFrame(controls_frame, fg_color=("gray90", "gray17"))
        login_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(
            login_frame,
            text="🔐 登录管理",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10))
        
        self.login_btn = ctk.CTkButton(
            login_frame,
            text="📱 登录闲鱼",
            command=self._login_xianyu,
            width=180,
            height=40,
            state="disabled"
        )
        self.login_btn.pack(pady=5)
        
        self.save_cookies_btn = ctk.CTkButton(
            login_frame,
            text="💾 保存Cookie",
            command=self._save_cookies,
            width=180,
            height=40,
            state="disabled"
        )
        self.save_cookies_btn.pack(pady=5)
        
        self.load_cookies_btn = ctk.CTkButton(
            login_frame,
            text="📂 加载Cookie",
            command=self._load_cookies,
            width=180,
            height=40,
            state="disabled"
        )
        self.load_cookies_btn.pack(pady=(5, 15))
        
        # 调试工具
        debug_frame = ctk.CTkFrame(controls_frame, fg_color=("gray90", "gray17"))
        debug_frame.grid(row=0, column=2, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(
            debug_frame,
            text="🔧 调试工具",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10))
        
        self.screenshot_btn = ctk.CTkButton(
            debug_frame,
            text="📸 截图",
            command=self._take_screenshot,
            width=180,
            height=40,
            state="disabled"
        )
        self.screenshot_btn.pack(pady=5)
        
        self.open_url_btn = ctk.CTkButton(
            debug_frame,
            text="🔗 打开URL",
            command=self._open_url,
            width=180,
            height=40,
            state="disabled"
        )
        self.open_url_btn.pack(pady=5)
        
        self.clear_log_btn = ctk.CTkButton(
            debug_frame,
            text="🗑️ 清空日志",
            command=self._clear_log,
            width=180,
            height=40
        )
        self.clear_log_btn.pack(pady=(5, 15))
    
    def _create_status_section(self):
        """创建状态区"""
        
        status_frame = ctk.CTkFrame(self)
        status_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        
        ctk.CTkLabel(
            status_frame,
            text="📊 状态信息",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        # 状态标签
        status_info_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_info_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # 浏览器状态
        self.browser_status_label = ctk.CTkLabel(
            status_info_frame,
            text="浏览器: ⚫ 未启动",
            font=ctk.CTkFont(size=14),
            anchor="w"
        )
        self.browser_status_label.pack(anchor="w", pady=2)
        
        # 登录状态
        self.login_status_label = ctk.CTkLabel(
            status_info_frame,
            text="登录状态: ⚫ 未登录",
            font=ctk.CTkFont(size=14),
            anchor="w"
        )
        self.login_status_label.pack(anchor="w", pady=2)
        
        # Cookie状态
        self.cookie_status_label = ctk.CTkLabel(
            status_info_frame,
            text="Cookie: ⚫ 无",
            font=ctk.CTkFont(size=14),
            anchor="w"
        )
        self.cookie_status_label.pack(anchor="w", pady=2)
    
    def _create_log_section(self):
        """创建日志区"""
        
        log_frame = ctk.CTkFrame(self)
        log_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=(10, 20))
        self.grid_rowconfigure(3, weight=1)
        
        ctk.CTkLabel(
            log_frame,
            text="📝 操作日志",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        # 日志文本框
        self.log_textbox = ctk.CTkTextbox(
            log_frame,
            height=200,
            font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.log_textbox.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # 初始日志
        self._log("🎯 浏览器控制面板已就绪")
        self._log("💡 提示: 先启动浏览器,然后登录闲鱼账号")
    
    def _log(self, message: str):
        """添加日志"""
        
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_textbox.insert("end", log_message)
        self.log_textbox.see("end")
    
    def _start_browser(self):
        """启动浏览器"""
        
        if self.browser_running:
            messagebox.showwarning("警告", "浏览器已经在运行中")
            return
        
        self._log("🚀 正在启动浏览器...")
        
        # 在后台线程中运行异步操作
        def run_async():
            # 创建新的事件循环
            self.event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.event_loop)
            
            try:
                # 创建浏览器实例
                headless = self.headless_var.get()
                self.browser = XianyuAutomation(headless=headless)
                
                # 启动浏览器
                self.event_loop.run_until_complete(self.browser.start())
                
                # 更新UI
                self.after(0, self._on_browser_started)
                
                # 保持事件循环运行
                self.event_loop.run_forever()
                
            except Exception as e:
                self.after(0, lambda: self._log(f"❌ 启动失败: {e}"))
                self.after(0, lambda: messagebox.showerror("错误", f"浏览器启动失败:\n{e}"))
            finally:
                if self.event_loop:
                    self.event_loop.close()
        
        # 启动线程
        thread = threading.Thread(target=run_async, daemon=True)
        thread.start()
    
    def _on_browser_started(self):
        """浏览器启动完成"""
        
        self.browser_running = True
        self._log("✅ 浏览器启动成功")
        
        # 更新状态
        self.browser_status_label.configure(text="浏览器: 🟢 运行中")
        
        # 更新按钮状态
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.login_btn.configure(state="normal")
        self.save_cookies_btn.configure(state="normal")
        self.load_cookies_btn.configure(state="normal")
        self.screenshot_btn.configure(state="normal")
        self.open_url_btn.configure(state="normal")
        self.headless_switch.configure(state="disabled")
    
    def _stop_browser(self):
        """停止浏览器"""
        
        if not self.browser_running:
            messagebox.showwarning("警告", "浏览器未运行")
            return
        
        self._log("⏹️ 正在停止浏览器...")
        
        # 在后台线程中停止
        def stop_async():
            try:
                if self.browser and self.event_loop:
                    # 在事件循环中停止浏览器
                    future = asyncio.run_coroutine_threadsafe(
                        self.browser.stop(),
                        self.event_loop
                    )
                    future.result(timeout=5)
                    
                    # 停止事件循环
                    self.event_loop.call_soon_threadsafe(self.event_loop.stop)
                
                # 更新UI
                self.after(0, self._on_browser_stopped)
                
            except Exception as e:
                self.after(0, lambda: self._log(f"❌ 停止失败: {e}"))
        
        thread = threading.Thread(target=stop_async, daemon=True)
        thread.start()
    
    def _on_browser_stopped(self):
        """浏览器停止完成"""
        
        self.browser_running = False
        self.browser = None
        self.event_loop = None
        self._log("✅ 浏览器已停止")
        
        # 更新状态
        self.browser_status_label.configure(text="浏览器: ⚫ 未启动")
        self.login_status_label.configure(text="登录状态: ⚫ 未登录")
        
        # 更新按钮状态
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.login_btn.configure(state="disabled")
        self.save_cookies_btn.configure(state="disabled")
        self.load_cookies_btn.configure(state="disabled")
        self.screenshot_btn.configure(state="disabled")
        self.open_url_btn.configure(state="disabled")
        self.headless_switch.configure(state="normal")
    
    def _login_xianyu(self):
        """登录闲鱼"""
        
        if not self.browser_running or not self.browser:
            messagebox.showwarning("警告", "请先启动浏览器")
            return
        
        self._log("🔐 开始登录流程...")
        self._log("📱 请在浏览器中完成登录(扫码或密码)")
        
        # 在后台线程中登录
        def login_async():
            try:
                # 尝试加载已保存的Cookie
                cookies_path = Path(self.cookies_file)
                cookies_file = str(cookies_path) if cookies_path.exists() else None
                
                # 执行登录
                future = asyncio.run_coroutine_threadsafe(
                    self.browser.login(cookies_file),
                    self.event_loop
                )
                success = future.result(timeout=120)  # 最多等待2分钟
                
                # 更新UI
                if success:
                    self.after(0, self._on_login_success)
                else:
                    self.after(0, lambda: self._log("❌ 登录失败或超时"))
                    
            except Exception as e:
                self.after(0, lambda: self._log(f"❌ 登录错误: {e}"))
        
        thread = threading.Thread(target=login_async, daemon=True)
        thread.start()
    
    def _on_login_success(self):
        """登录成功"""
        
        self._log("✅ 登录成功!")
        self.login_status_label.configure(text="登录状态: 🟢 已登录")
        messagebox.showinfo("成功", "闲鱼登录成功!")
    
    def _save_cookies(self):
        """保存Cookie"""
        
        if not self.browser_running or not self.browser:
            messagebox.showwarning("警告", "请先启动浏览器")
            return
        
        self._log("💾 正在保存Cookie...")
        
        def save_async():
            try:
                # 确保目录存在
                Path(self.cookies_file).parent.mkdir(parents=True, exist_ok=True)
                
                # 保存Cookie
                future = asyncio.run_coroutine_threadsafe(
                    self.browser.save_cookies(self.cookies_file),
                    self.event_loop
                )
                future.result(timeout=5)
                
                # 更新UI
                self.after(0, lambda: self._log(f"✅ Cookie已保存到: {self.cookies_file}"))
                self.after(0, lambda: self.cookie_status_label.configure(
                    text=f"Cookie: 🟢 已保存 ({Path(self.cookies_file).name})"
                ))
                self.after(0, lambda: messagebox.showinfo("成功", "Cookie保存成功!"))
                
            except Exception as e:
                self.after(0, lambda: self._log(f"❌ 保存失败: {e}"))
        
        thread = threading.Thread(target=save_async, daemon=True)
        thread.start()
    
    def _load_cookies(self):
        """加载Cookie"""
        
        if not self.browser_running or not self.browser:
            messagebox.showwarning("警告", "请先启动浏览器")
            return
        
        # 选择Cookie文件
        file_path = filedialog.askopenfilename(
            title="选择Cookie文件",
            initialdir="data",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            return
        
        self._log(f"📂 正在加载Cookie: {file_path}")
        
        def load_async():
            try:
                # 加载Cookie
                future = asyncio.run_coroutine_threadsafe(
                    self.browser.load_cookies(file_path),
                    self.event_loop
                )
                success = future.result(timeout=5)
                
                # 更新UI
                if success:
                    self.after(0, lambda: self._log("✅ Cookie加载成功"))
                    self.after(0, lambda: self.cookie_status_label.configure(
                        text=f"Cookie: 🟢 已加载 ({Path(file_path).name})"
                    ))
                    self.after(0, lambda: messagebox.showinfo("成功", "Cookie加载成功!"))
                else:
                    self.after(0, lambda: self._log("❌ Cookie加载失败"))
                
            except Exception as e:
                self.after(0, lambda: self._log(f"❌ 加载失败: {e}"))
        
        thread = threading.Thread(target=load_async, daemon=True)
        thread.start()
    
    def _take_screenshot(self):
        """截图"""
        
        if not self.browser_running or not self.browser:
            messagebox.showwarning("警告", "请先启动浏览器")
            return
        
        # 选择保存路径
        file_path = filedialog.asksaveasfilename(
            title="保存截图",
            initialdir="data/temp",
            defaultextension=".png",
            filetypes=[("PNG图片", "*.png"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            return
        
        self._log(f"📸 正在截图...")
        
        def screenshot_async():
            try:
                # 截图
                future = asyncio.run_coroutine_threadsafe(
                    self.browser.screenshot(file_path),
                    self.event_loop
                )
                success = future.result(timeout=5)
                
                # 更新UI
                if success:
                    self.after(0, lambda: self._log(f"✅ 截图已保存: {file_path}"))
                    self.after(0, lambda: messagebox.showinfo("成功", f"截图已保存:\n{file_path}"))
                
            except Exception as e:
                self.after(0, lambda: self._log(f"❌ 截图失败: {e}"))
        
        thread = threading.Thread(target=screenshot_async, daemon=True)
        thread.start()
    
    def _open_url(self):
        """打开URL"""
        
        if not self.browser_running or not self.browser:
            messagebox.showwarning("警告", "请先启动浏览器")
            return
        
        # 输入对话框
        from tkinter import simpledialog
        url = simpledialog.askstring(
            "打开URL",
            "请输入要访问的网址:",
            initialvalue="https://2.taobao.com"
        )
        
        if not url:
            return
        
        self._log(f"🔗 正在打开: {url}")
        
        def goto_async():
            try:
                # 导航
                future = asyncio.run_coroutine_threadsafe(
                    self.browser.goto(url),
                    self.event_loop
                )
                future.result(timeout=30)
                
                # 更新UI
                self.after(0, lambda: self._log(f"✅ 已打开: {url}"))
                
            except Exception as e:
                self.after(0, lambda: self._log(f"❌ 打开失败: {e}"))
        
        thread = threading.Thread(target=goto_async, daemon=True)
        thread.start()
    
    def _clear_log(self):
        """清空日志"""
        
        self.log_textbox.delete("1.0", "end")
        self._log("🗑️ 日志已清空")
    
    def __del__(self):
        """析构函数 - 确保浏览器关闭"""
        
        if self.browser_running and self.browser:
            try:
                if self.event_loop and self.event_loop.is_running():
                    self.event_loop.call_soon_threadsafe(self.event_loop.stop)
            except:
                pass


# 测试代码
if __name__ == "__main__":
    import customtkinter as ctk
    
    # 设置主题
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # 创建测试窗口
    root = ctk.CTk()
    root.title("浏览器控制面板测试")
    root.geometry("1000x800")
    
    # 创建控制面板
    panel = BrowserControlPanel(root)
    panel.pack(fill="both", expand=True)
    
    # 运行
    root.mainloop()
