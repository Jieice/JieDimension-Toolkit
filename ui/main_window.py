"""
JieDimension Toolkit - 主窗口
基于 CustomTkinter 的现代化界面
Version: 1.0.0
"""

import customtkinter as ctk
import os
import sys
from typing import Optional

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class MainWindow(ctk.CTk):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        
        # 窗口配置
        self.title("JieDimension Toolkit v1.17.1 - AI驱动的多平台内容发布工具")
        self.geometry("1400x900")
        
        # 居中显示
        self._center_window()
        
        # 设置主题
        ctk.set_appearance_mode("dark")  # dark/light/system
        ctk.set_default_color_theme("blue")  # blue/green/dark-blue
        
        # 配置网格布局
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # 创建UI组件
        self._create_sidebar()
        self._create_content_area()
        
        # 默认显示仪表板
        self.show_dashboard()
        
        # 窗口关闭事件
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _center_window(self):
        """窗口居中显示"""
        self.update_idletasks()
        
        # 获取屏幕尺寸
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # 获取窗口尺寸
        window_width = 1400
        window_height = 900
        
        # 计算居中位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def _create_sidebar(self):
        """创建侧边栏"""
        # 侧边栏框架
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)  # 底部留空
        
        # Logo 区域
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=20, pady=(30, 20), sticky="ew")
        
        logo_label = ctk.CTkLabel(
            logo_frame,
            text="🚀 JieDimension",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        logo_label.pack()
        
        version_label = ctk.CTkLabel(
            logo_frame,
            text="Toolkit v1.0",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        version_label.pack()
        
        # 分隔线
        separator = ctk.CTkFrame(self.sidebar, height=2, fg_color="gray30")
        separator.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        # 菜单按钮
        self.menu_buttons = []
        
        menus = [
            ("🏠 仪表板", self.show_dashboard),
            ("🚀 批量发布", self.show_batch_publish),
            ("📦 闲鱼发布", self.show_xianyu),
            ("📝 小红书", self.show_xiaohongshu),
            ("📖 知乎", self.show_zhihu),
            ("🎬 B站", self.show_bilibili),
            ("🌐 浏览器控制", self.show_browser_control),
            ("📊 管理", self.show_management),
            ("🤖 AI助手", self.show_ai_assistant),
            ("🔐 API配置", self.show_api_config),
            ("⚙️ 设置", self.show_settings),
            ("🔄 检查更新", self.check_for_updates),
        ]
        
        for idx, (text, command) in enumerate(menus):
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=command,
                anchor="w",
                height=45,
                font=ctk.CTkFont(size=15),
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30")
            )
            btn.grid(row=idx+2, column=0, padx=15, pady=5, sticky="ew")
            self.menu_buttons.append(btn)
        
        # 分隔线
        separator2 = ctk.CTkFrame(self.sidebar, height=2, fg_color="gray30")
        separator2.grid(row=len(menus)+2, column=0, padx=20, pady=10, sticky="ew")
        
        # 状态指示区域
        status_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        status_frame.grid(row=11, column=0, padx=20, pady=20, sticky="ew")
        
        # AI状态
        self.ai_status_label = ctk.CTkLabel(
            status_frame,
            text="🤖 AI: 就绪",
            font=ctk.CTkFont(size=12),
            text_color="green"
        )
        self.ai_status_label.pack(anchor="w", pady=2)
        
        # 数据库状态
        self.db_status_label = ctk.CTkLabel(
            status_frame,
            text="💾 数据库: 正常",
            font=ctk.CTkFont(size=12),
            text_color="green"
        )
        self.db_status_label.pack(anchor="w", pady=2)
        
        # 版权信息
        copyright_label = ctk.CTkLabel(
            self.sidebar,
            text="© 2025 JieDimension Studio",
            font=ctk.CTkFont(size=10),
            text_color="gray50"
        )
        copyright_label.grid(row=12, column=0, padx=20, pady=(0, 20))
    
    def _create_content_area(self):
        """创建内容区域"""
        # 内容框架
        self.content = ctk.CTkFrame(self, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)
    
    def _clear_content(self):
        """清空内容区域"""
        for widget in self.content.winfo_children():
            widget.destroy()
    
    def _highlight_menu(self, index: int):
        """高亮选中的菜单"""
        for i, btn in enumerate(self.menu_buttons):
            if i == index:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color="transparent")
    
    # ===== 页面切换方法 =====
    
    def show_dashboard(self):
        """显示仪表板"""
        self._clear_content()
        self._highlight_menu(0)
        
        from ui.dashboard import Dashboard
        dashboard = Dashboard(self.content)
        dashboard.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
    
    def show_batch_publish(self):
        """显示批量发布模块"""
        self._clear_content()
        self._highlight_menu(1)
        
        try:
            from plugins.batch_publisher.ui.batch_tab import BatchPublishTab
            batch_tab = BatchPublishTab(self.content)
            batch_tab.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        except Exception as e:
            error_label = ctk.CTkLabel(
                self.content,
                text=f"❌ 批量发布模块加载失败\n\n{str(e)}",
                font=ctk.CTkFont(size=16),
                text_color="red"
            )
            error_label.place(relx=0.5, rely=0.5, anchor="center")
            print(f"Error loading batch publish: {e}")
    
    def show_xianyu(self):
        """显示闲鱼模块"""
        self._clear_content()
        self._highlight_menu(2)
        
        from plugins.xianyu.ui.publish_tab import XianyuPublishTab
        xianyu_tab = XianyuPublishTab(self.content)
        xianyu_tab.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
    
    def show_xiaohongshu(self):
        """显示小红书模块"""
        self._clear_content()
        self._highlight_menu(3)
        
        try:
            from plugins.xiaohongshu.ui.xiaohongshu_tab import XiaohongshuTab
            
            # 创建小红书插件界面
            xiaohongshu_tab = XiaohongshuTab(self.content)
            xiaohongshu_tab.pack(fill="both", expand=True, padx=10, pady=10)
        
        except Exception as e:
            print(f"❌ 小红书模块加载失败: {str(e)}")
            import traceback
            traceback.print_exc()
            
            error_label = ctk.CTkLabel(
                self.content,
                text=f"❌ 小红书模块加载失败\n\n{str(e)}",
                font=ctk.CTkFont(size=16),
                text_color="red"
            )
            error_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def show_zhihu(self):
        """显示知乎模块"""
        self._clear_content()
        self._highlight_menu(4)
        
        try:
            from plugins.zhihu.ui.zhihu_tab import ZhihuTab
            
            # 创建知乎插件界面
            zhihu_tab = ZhihuTab(self.content)
            zhihu_tab.pack(fill="both", expand=True, padx=10, pady=10)
        
        except Exception as e:
            print(f"❌ 知乎模块加载失败: {str(e)}")
            import traceback
            traceback.print_exc()
            
            error_label = ctk.CTkLabel(
                self.content,
                text=f"❌ 知乎模块加载失败\n\n{str(e)}",
                font=ctk.CTkFont(size=16),
                text_color="red"
            )
            error_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def show_bilibili(self):
        """显示B站模块"""
        self._clear_content()
        self._highlight_menu(5)
        
        try:
            from plugins.bilibili.ui.bilibili_tab import BilibiliTab
            from core.ai_engine import AIEngine
            
            # 获取AI引擎实例
            ai_engine = AIEngine()
            
            # 创建B站插件界面
            bilibili_tab = BilibiliTab(self.content, ai_engine=ai_engine)
            bilibili_tab.pack(fill="both", expand=True, padx=10, pady=10)
        
        except Exception as e:
            # 如果加载失败，显示错误信息
            error_label = ctk.CTkLabel(
                self.content,
                text=f"⚠️ B站模块加载失败\n\n{str(e)}",
                font=ctk.CTkFont(size=18),
                text_color="red"
            )
            error_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def show_browser_control(self):
        """显示浏览器控制面板"""
        self._clear_content()
        self._highlight_menu(6)
        
        try:
            from ui.browser_control_panel import BrowserControlPanel
            browser_panel = BrowserControlPanel(self.content)
            browser_panel.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        except ImportError as e:
            error_label = ctk.CTkLabel(
                self.content,
                text=f"❌ 浏览器控制面板加载失败\n\n缺少依赖: Playwright\n\n安装方法:\npip install playwright\nplaywright install chromium",
                font=ctk.CTkFont(size=16),
                text_color="red",
                justify="left"
            )
            error_label.place(relx=0.5, rely=0.5, anchor="center")
            print(f"Error loading browser control: {e}")
        except Exception as e:
            error_label = ctk.CTkLabel(
                self.content,
                text=f"❌ 浏览器控制面板加载失败\n\n{str(e)}",
                font=ctk.CTkFont(size=16),
                text_color="red"
            )
            error_label.place(relx=0.5, rely=0.5, anchor="center")
            print(f"Error loading browser control: {e}")
    
    def show_management(self):
        """显示管理界面（发布历史和配置）"""
        self._clear_content()
        self._highlight_menu(7)
        
        try:
            # 创建标签页系统
            tabview = ctk.CTkTabview(self.content)
            tabview.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
            
            # 添加标签页
            history_tab = tabview.add("📜 发布历史")
            config_tab = tabview.add("⚙️ 选择器配置")
            
            # 加载发布历史
            try:
                from plugins.xianyu.ui.publish_history import PublishHistoryPanel
                history_panel = PublishHistoryPanel(history_tab)
                history_panel.pack(fill="both", expand=True)
            except Exception as e:
                error_label = ctk.CTkLabel(
                    history_tab,
                    text=f"❌ 发布历史加载失败\n\n{str(e)}",
                    font=ctk.CTkFont(size=14),
                    text_color="red"
                )
                error_label.pack(expand=True)
                print(f"Error loading history panel: {e}")
            
            # 加载选择器配置
            try:
                from plugins.xianyu.ui.selector_config import SelectorConfigPanel
                config_panel = SelectorConfigPanel(config_tab)
                config_panel.pack(fill="both", expand=True)
            except Exception as e:
                error_label = ctk.CTkLabel(
                    config_tab,
                    text=f"❌ 选择器配置加载失败\n\n{str(e)}",
                    font=ctk.CTkFont(size=14),
                    text_color="red"
                )
                error_label.pack(expand=True)
                print(f"Error loading config panel: {e}")
            
        except Exception as e:
            error_label = ctk.CTkLabel(
                self.content,
                text=f"❌ 管理界面加载失败\n\n{str(e)}",
                font=ctk.CTkFont(size=16),
                text_color="red"
            )
            error_label.place(relx=0.5, rely=0.5, anchor="center")
            print(f"Error loading management: {e}")
    
    def show_ai_assistant(self):
        """显示AI助手"""
        self._clear_content()
        self._highlight_menu(8)
        
        placeholder = ctk.CTkLabel(
            self.content,
            text="🤖 AI助手\n\n即将推出...\n\n支持智能对话、内容生成、批量处理",
            font=ctk.CTkFont(size=24),
            text_color="gray50"
        )
        placeholder.place(relx=0.5, rely=0.5, anchor="center")
    
    def show_api_config(self):
        """显示API配置"""
        self._clear_content()
        self._highlight_menu(9)
        
        try:
            from ui.api_config_panel import APIConfigPanel
            api_panel = APIConfigPanel(self.content)
            api_panel.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        except Exception as e:
            error_label = ctk.CTkLabel(
                self.content,
                text=f"❌ API配置模块加载失败\n\n{str(e)}",
                font=ctk.CTkFont(size=16),
                text_color="red"
            )
            error_label.place(relx=0.5, rely=0.5, anchor="center")
            print(f"Error loading API config: {e}")
    
    def check_for_updates(self):
        """检查更新"""
        self._highlight_menu(11)
        
        # 显示检查中提示
        import tkinter.messagebox as messagebox
        
        try:
            from utils.updater import UpdateChecker
            
            # 创建检查器
            checker = UpdateChecker()
            
            # 检查更新
            update_info = checker.check_for_updates(timeout=10)
            
            if update_info:
                # 有新版本
                message = f"""✨ 发现新版本！

当前版本: v{update_info['current']}
最新版本: v{update_info['version']}

📝 更新内容:
{update_info['notes'][:300]}...

是否前往下载页面？"""
                
                result = messagebox.askyesno("发现新版本", message)
                if result:
                    checker.open_download_page()
            else:
                # 已是最新版本
                messagebox.showinfo(
                    "检查更新", 
                    f"✅ 当前已是最新版本！\n\n版本: v{checker.current_version}"
                )
        
        except Exception as e:
            messagebox.showerror(
                "检查更新失败", 
                f"无法检查更新:\n{str(e)}\n\n请检查网络连接"
            )
    
    def show_settings(self):
        """显示设置"""
        self._clear_content()
        self._highlight_menu(10)
        
        from ui.settings_window import SettingsPanel
        settings = SettingsPanel(self.content)
        settings.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
    
    def _on_closing(self):
        """窗口关闭事件"""
        # 可以在这里添加保存设置、清理资源等操作
        self.destroy()


# ===== 测试函数 =====

def main():
    """测试主窗口"""
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()

