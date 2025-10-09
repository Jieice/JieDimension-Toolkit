# ui/api_config_panel.py

"""
API配置面板 - 管理各平台的API密钥和认证
"""

import customtkinter as ctk
from tkinter import messagebox
import asyncio
import sys
import os
from typing import Dict, Any, Optional

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.auth_manager import AuthManager


class APIConfigPanel(ctk.CTkScrollableFrame):
    """API配置面板"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # 配置网格
        self.grid_columnconfigure(0, weight=1)
        
        # 初始化认证管理器（延迟加载）
        self.auth_manager = None
        self._auth_manager_initialized = False
        
        # 存储输入框引用
        self.api_inputs: Dict[str, Dict[str, Any]] = {}
        
        # 创建界面
        self._create_header()
        self._create_platform_sections()
        self._create_credentials_list()
        self._create_actions()
        
        # 延迟初始化认证管理器
        self.after(100, self._delayed_init_auth_manager)
    
    def _delayed_init_auth_manager(self):
        """延迟初始化认证管理器"""
        import threading
        
        def init_in_thread():
            import asyncio
            try:
                # 创建新的事件循环
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # 初始化认证管理器
                self.auth_manager = AuthManager()
                loop.run_until_complete(self.auth_manager.load_credentials())
                
                self._auth_manager_initialized = True
                
                # 在主线程更新UI
                self.after(0, self._update_credentials_display)
                
                loop.close()
            except Exception as e:
                print(f"❌ 初始化认证管理器失败: {e}")
        
        # 在后台线程运行
        thread = threading.Thread(target=init_in_thread, daemon=True)
        thread.start()
    
    def _update_credentials_display(self):
        """更新凭证显示"""
        if self._auth_manager_initialized and hasattr(self, 'credentials_text'):
            self._sync_refresh_credentials_list()
    
    def _create_header(self):
        """创建顶部标题栏"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=30, pady=(30, 20), sticky="ew")
        
        # 标题
        title = ctk.CTkLabel(
            header_frame,
            text="🔐 API配置中心",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title.pack(side="left")
        
        # 说明
        desc = ctk.CTkLabel(
            header_frame,
            text="配置各平台的API密钥，实现真实发布功能",
            font=ctk.CTkFont(size=14),
            text_color="gray60"
        )
        desc.pack(side="left", padx=20)
    
    def _create_platform_sections(self):
        """创建平台配置区域"""
        
        # B站配置
        self._create_bilibili_section()
        
        # 闲鱼配置
        self._create_xianyu_section()
        
        # 小红书配置
        self._create_xiaohongshu_section()
        
        # 知乎配置
        self._create_zhihu_section()
    
    def _create_bilibili_section(self):
        """创建B站API配置区域"""
        
        section_title = ctk.CTkLabel(
            self,
            text="📺 B站 API配置",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w"
        )
        section_title.grid(row=1, column=0, padx=30, pady=(20, 10), sticky="w")
        
        # 配置卡片
        frame = ctk.CTkFrame(self, fg_color=("gray85", "gray20"), corner_radius=15)
        frame.grid(row=2, column=0, padx=30, pady=10, sticky="ew")
        frame.grid_columnconfigure(1, weight=1)
        
        # 说明
        info = ctk.CTkLabel(
            frame,
            text="🔗 申请地址: https://member.bilibili.com/platform/api\n"
                 "需要申请B站开发者账号，获取API密钥后填写",
            font=ctk.CTkFont(size=12),
            text_color="gray60",
            justify="left"
        )
        info.grid(row=0, column=0, columnspan=3, padx=20, pady=(15, 10), sticky="w")
        
        # Access Key
        access_label = ctk.CTkLabel(
            frame,
            text="Access Key:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        access_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        access_entry = ctk.CTkEntry(
            frame,
            placeholder_text="输入B站 Access Key",
            width=300,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        access_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # Secret Key
        secret_label = ctk.CTkLabel(
            frame,
            text="Secret Key:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        secret_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        
        secret_entry = ctk.CTkEntry(
            frame,
            placeholder_text="输入B站 Secret Key",
            show="●",
            width=300,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        secret_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        
        # SESSDATA (可选)
        sessdata_label = ctk.CTkLabel(
            frame,
            text="SESSDATA (可选):",
            font=ctk.CTkFont(size=14)
        )
        sessdata_label.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        
        sessdata_entry = ctk.CTkEntry(
            frame,
            placeholder_text="从浏览器Cookie中获取",
            width=300,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        sessdata_entry.grid(row=3, column=1, padx=10, pady=10, sticky="ew")
        
        # 按钮组
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.grid(row=1, column=2, rowspan=3, padx=10, pady=10)
        
        # 测试按钮
        test_btn = ctk.CTkButton(
            button_frame,
            text="🔍 测试连接",
            width=120,
            height=35,
            font=ctk.CTkFont(size=13),
            command=lambda: self._test_bilibili_connection(
                access_entry.get(),
                secret_entry.get(),
                sessdata_entry.get()
            )
        )
        test_btn.pack(pady=5)
        
        # 保存按钮
        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 保存配置",
            width=120,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color="green",
            hover_color="darkgreen",
            command=lambda: self._save_bilibili_config(
                access_entry.get(),
                secret_entry.get(),
                sessdata_entry.get()
            )
        )
        save_btn.pack(pady=5)
        
        # 存储输入框引用
        self.api_inputs["bilibili"] = {
            "access_key": access_entry,
            "secret_key": secret_entry,
            "sessdata": sessdata_entry
        }
    
    def _create_xianyu_section(self):
        """创建闲鱼配置区域"""
        
        section_title = ctk.CTkLabel(
            self,
            text="🛒 闲鱼配置",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w"
        )
        section_title.grid(row=3, column=0, padx=30, pady=(20, 10), sticky="w")
        
        # 配置卡片
        frame = ctk.CTkFrame(self, fg_color=("gray85", "gray20"), corner_radius=15)
        frame.grid(row=4, column=0, padx=30, pady=10, sticky="ew")
        frame.grid_columnconfigure(1, weight=1)
        
        # 说明
        info = ctk.CTkLabel(
            frame,
            text="⚠️ 闲鱼没有公开API，使用浏览器自动化方式\n"
                 "首次使用需要手动登录一次，之后会保存Cookie自动登录",
            font=ctk.CTkFont(size=12),
            text_color="orange",
            justify="left"
        )
        info.grid(row=0, column=0, columnspan=3, padx=20, pady=(15, 10), sticky="w")
        
        # Cookie文件路径
        cookie_label = ctk.CTkLabel(
            frame,
            text="Cookie保存路径:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        cookie_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        cookie_entry = ctk.CTkEntry(
            frame,
            placeholder_text="config/xianyu_cookies.json",
            width=300,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        cookie_entry.insert(0, "config/xianyu_cookies.json")
        cookie_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # 按钮组
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.grid(row=1, column=2, padx=10, pady=10)
        
        # 启动浏览器按钮
        launch_btn = ctk.CTkButton(
            button_frame,
            text="🌐 启动浏览器登录",
            width=140,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color="blue",
            hover_color="darkblue",
            command=lambda: self._launch_xianyu_browser(cookie_entry.get())
        )
        launch_btn.pack(pady=5)
        
        # 存储输入框引用
        self.api_inputs["xianyu"] = {
            "cookie_path": cookie_entry
        }
    
    def _create_xiaohongshu_section(self):
        """创建小红书配置区域"""
        
        section_title = ctk.CTkLabel(
            self,
            text="📝 小红书配置",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w"
        )
        section_title.grid(row=5, column=0, padx=30, pady=(20, 10), sticky="w")
        
        # 配置卡片
        frame = ctk.CTkFrame(self, fg_color=("gray85", "gray20"), corner_radius=15)
        frame.grid(row=6, column=0, padx=30, pady=10, sticky="ew")
        
        # 说明
        info = ctk.CTkLabel(
            frame,
            text="🚧 小红书API集成开发中...\n"
                 "目前支持内容生成，发布功能即将上线",
            font=ctk.CTkFont(size=13),
            text_color="gray60",
            justify="left"
        )
        info.pack(padx=20, pady=30)
    
    def _create_zhihu_section(self):
        """创建知乎配置区域"""
        
        section_title = ctk.CTkLabel(
            self,
            text="📖 知乎配置",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w"
        )
        section_title.grid(row=7, column=0, padx=30, pady=(20, 10), sticky="w")
        
        # 配置卡片
        frame = ctk.CTkFrame(self, fg_color=("gray85", "gray20"), corner_radius=15)
        frame.grid(row=8, column=0, padx=30, pady=10, sticky="ew")
        
        # 说明
        info = ctk.CTkLabel(
            frame,
            text="🚧 知乎API集成开发中...\n"
                 "目前支持内容生成，发布功能即将上线",
            font=ctk.CTkFont(size=13),
            text_color="gray60",
            justify="left"
        )
        info.pack(padx=20, pady=30)
    
    def _create_credentials_list(self):
        """创建已配置凭证列表"""
        
        section_title = ctk.CTkLabel(
            self,
            text="📋 已配置的平台",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w"
        )
        section_title.grid(row=9, column=0, padx=30, pady=(20, 10), sticky="w")
        
        # 列表卡片
        frame = ctk.CTkFrame(self, fg_color=("gray85", "gray20"), corner_radius=15)
        frame.grid(row=10, column=0, padx=30, pady=10, sticky="ew")
        
        # 文本框
        self.credentials_text = ctk.CTkTextbox(
            frame,
            height=150,
            font=ctk.CTkFont(size=13, family="Consolas")
        )
        self.credentials_text.pack(padx=20, pady=20, fill="both", expand=True)
        
        # 刷新按钮
        refresh_btn = ctk.CTkButton(
            frame,
            text="🔄 刷新列表",
            width=120,
            height=35,
            command=self._sync_refresh_credentials_list
        )
        refresh_btn.pack(padx=20, pady=(0, 20))
    
    def _create_actions(self):
        """创建底部操作按钮"""
        
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=11, column=0, padx=30, pady=30, sticky="ew")
        
        # 帮助文档按钮
        help_btn = ctk.CTkButton(
            action_frame,
            text="📚 查看API申请指南",
            width=180,
            height=40,
            font=ctk.CTkFont(size=14),
            command=self._show_help
        )
        help_btn.pack(side="left", padx=10)
        
        # 清除所有凭证按钮
        clear_btn = ctk.CTkButton(
            action_frame,
            text="🗑️ 清除所有凭证",
            width=180,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="red",
            hover_color="darkred",
            command=self._clear_all_credentials
        )
        clear_btn.pack(side="right", padx=10)
    
    # ========== 辅助函数 ==========
    
    def _run_async_in_thread(self, async_func, *args):
        """在后台线程运行异步函数"""
        import threading
        
        def run():
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(async_func(*args))
            finally:
                loop.close()
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
    
    def _sync_refresh_credentials_list(self):
        """同步刷新凭证列表"""
        if not self._auth_manager_initialized or not self.auth_manager:
            self.credentials_text.delete("1.0", "end")
            self.credentials_text.insert("1.0", "⏳ 正在初始化认证管理器...")
            return
        
        import threading
        
        def refresh_in_thread():
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                platforms = loop.run_until_complete(self.auth_manager.list_platforms())
                
                # 在主线程更新UI
                self.after(0, lambda: self._display_platforms(platforms))
            except Exception as e:
                self.after(0, lambda: self._display_error(str(e)))
            finally:
                loop.close()
        
        thread = threading.Thread(target=refresh_in_thread, daemon=True)
        thread.start()
    
    def _display_platforms(self, platforms):
        """显示平台列表"""
        self.credentials_text.delete("1.0", "end")
        
        if not platforms:
            self.credentials_text.insert("1.0", "暂无已配置的平台\n\n请在上方配置API密钥")
            return
        
        # 显示平台信息
        text = "已配置的平台：\n\n"
        for platform in platforms:
            status = "✅ 有效" if not platform["expired"] else "⚠️ 已过期"
            text += f"• {platform['platform'].upper()}\n"
            text += f"  认证类型: {platform['auth_type']}\n"
            text += f"  状态: {status}\n"
            text += f"  创建时间: {platform['created_at']}\n\n"
        
        self.credentials_text.insert("1.0", text)
    
    def _display_error(self, error_msg):
        """显示错误"""
        self.credentials_text.delete("1.0", "end")
        self.credentials_text.insert("1.0", f"❌ 获取凭证列表失败：{error_msg}")
    
    # ========== 事件处理 ==========
    
    def _test_bilibili_connection(
        self,
        access_key: str,
        secret_key: str,
        sessdata: str
    ):
        """测试B站连接"""
        
        if not access_key or not secret_key:
            messagebox.showwarning("输入错误", "请输入Access Key和Secret Key")
            return
        
        # 在后台线程测试连接
        self._run_async_in_thread(
            self._async_test_bilibili,
            access_key, secret_key, sessdata
        )
    
    async def _async_test_bilibili(
        self,
        access_key: str,
        secret_key: str,
        sessdata: str
    ):
        """异步测试B站连接"""
        
        try:
            from plugins.bilibili.api_client import BilibiliAPIClient
            
            # 创建客户端
            client = BilibiliAPIClient(
                access_key=access_key,
                secret_key=secret_key,
                sessdata=sessdata if sessdata else None
            )
            
            # 测试获取用户信息
            user_info = await client.get_user_info()
            
            await client.close()
            
            if user_info:
                messagebox.showinfo(
                    "连接成功",
                    f"✅ B站API连接成功！\n\n"
                    f"用户信息已获取"
                )
            else:
                messagebox.showwarning(
                    "连接失败",
                    "⚠️ API连接失败\n\n"
                    "可能原因：\n"
                    "1. API密钥无效\n"
                    "2. 网络连接问题\n"
                    "3. API权限不足"
                )
        
        except Exception as e:
            messagebox.showerror(
                "测试失败",
                f"❌ 测试B站连接时出错：\n\n{str(e)}"
            )
    
    def _save_bilibili_config(
        self,
        access_key: str,
        secret_key: str,
        sessdata: str
    ):
        """保存B站配置"""
        
        if not access_key or not secret_key:
            messagebox.showwarning("输入错误", "请输入Access Key和Secret Key")
            return
        
        # 在后台线程保存配置
        self._run_async_in_thread(
            self._async_save_bilibili,
            access_key, secret_key, sessdata
        )
    
    async def _async_save_bilibili(
        self,
        access_key: str,
        secret_key: str,
        sessdata: str
    ):
        """异步保存B站配置"""
        
        try:
            credentials = {
                "access_key": access_key,
                "secret_key": secret_key
            }
            
            if sessdata:
                credentials["sessdata"] = sessdata
            
            # 保存凭证（2小时过期）
            await self.auth_manager.set_credentials(
                platform="bilibili",
                auth_type="api_key",
                credentials=credentials,
                expires_in=7200
            )
            
            messagebox.showinfo(
                "保存成功",
                "✅ B站API配置已保存！\n\n"
                "配置将在2小时后过期，届时需要重新配置"
            )
            
            # 刷新凭证列表
            self.after(0, self._sync_refresh_credentials_list)
        
        except Exception as e:
            messagebox.showerror(
                "保存失败",
                f"❌ 保存配置时出错：\n\n{str(e)}"
            )
    
    def _launch_xianyu_browser(self, cookie_path: str):
        """启动闲鱼浏览器"""
        
        messagebox.showinfo(
            "浏览器自动化",
            "🌐 即将启动浏览器...\n\n"
            "请在浏览器中完成闲鱼登录\n"
            "登录成功后，Cookie将自动保存\n"
            "下次发布时将自动使用已保存的Cookie"
        )
        
        # 在后台线程启动浏览器
        self._run_async_in_thread(self._async_launch_xianyu, cookie_path)
    
    async def _async_launch_xianyu(self, cookie_path: str):
        """异步启动闲鱼浏览器"""
        
        try:
            from core.browser_automation import XianyuAutomation
            
            # 创建自动化实例
            automation = XianyuAutomation(headless=False)
            
            # 启动浏览器
            await automation.start()
            
            # 登录
            success = await automation.login(cookies_file=cookie_path)
            
            if success:
                messagebox.showinfo(
                    "登录成功",
                    "✅ 闲鱼登录成功！\n\n"
                    f"Cookie已保存到：{cookie_path}\n"
                    "下次发布时将自动使用此Cookie"
                )
            else:
                messagebox.showwarning(
                    "登录失败",
                    "⚠️ 闲鱼登录超时或失败\n\n"
                    "请重试"
                )
            
            # 关闭浏览器
            await automation.stop()
        
        except ImportError:
            messagebox.showerror(
                "缺少依赖",
                "❌ 缺少Playwright依赖\n\n"
                "请运行以下命令安装：\n"
                "pip install playwright\n"
                "playwright install chromium"
            )
        except Exception as e:
            messagebox.showerror(
                "启动失败",
                f"❌ 启动浏览器时出错：\n\n{str(e)}"
            )
    
    def _show_help(self):
        """显示帮助文档"""
        
        help_text = """
        📚 API申请指南
        
        【B站】
        1. 访问 https://member.bilibili.com/platform
        2. 申请成为创作者
        3. 在创作中心申请API权限
        4. 获取Access Key和Secret Key
        
        【闲鱼】
        - 无需API，使用浏览器自动化
        - 首次使用需要手动登录
        - Cookie会自动保存
        
        【小红书/知乎】
        - 功能开发中，敬请期待
        
        更多详情请查看项目文档
        """
        
        messagebox.showinfo("API申请指南", help_text)
    
    def _clear_all_credentials(self):
        """清除所有凭证"""
        
        result = messagebox.askyesno(
            "确认清除",
            "⚠️ 确定要清除所有已保存的凭证吗？\n\n"
            "此操作不可撤销！"
        )
        
        if result:
            # 在后台线程清除凭证
            self._run_async_in_thread(self._async_clear_all)
    
    async def _async_clear_all(self):
        """异步清除所有凭证"""
        
        try:
            platforms = await self.auth_manager.list_platforms()
            
            for platform in platforms:
                await self.auth_manager.remove_credentials(platform["platform"])
            
            messagebox.showinfo(
                "清除成功",
                "✅ 所有凭证已清除"
            )
            
            # 刷新列表
            self.after(0, self._sync_refresh_credentials_list)
        
        except Exception as e:
            messagebox.showerror(
                "清除失败",
                f"❌ 清除凭证时出错：\n\n{str(e)}"
            )
