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
        self.title("JieDimension Toolkit v1.17.2 - AI驱动的多平台内容发布工具")
        self.geometry("1280x800")  # 调整为更通用的大小
        
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
        
        # 内嵌AI助手
        self.ai_assistant_frame = None
        self.ai_visible = False
        
        # 窗口关闭事件
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _center_window(self):
        """窗口居中显示"""
        self.update_idletasks()
        
        # 获取屏幕尺寸
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # 获取窗口尺寸
        window_width = 1280
        window_height = 800
        
        # 计算居中位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def _create_sidebar(self):
        """创建侧边栏（可滚动）"""
        # 侧边栏外层容器
        sidebar_container = ctk.CTkFrame(self, width=250, corner_radius=0)
        sidebar_container.grid(row=0, column=0, sticky="nsew")
        sidebar_container.grid_rowconfigure(0, weight=1)
        sidebar_container.grid_columnconfigure(0, weight=1)
        
        # 侧边栏滚动框架
        self.sidebar = ctk.CTkScrollableFrame(
            sidebar_container, 
            width=230,
            corner_radius=0,
            fg_color="transparent"
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_columnconfigure(0, weight=1)
        
        # Logo 区域
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        logo_label = ctk.CTkLabel(
            logo_frame,
            text="🚀 JieDimension",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        logo_label.pack()
        
        version_label = ctk.CTkLabel(
            logo_frame,
            text="Toolkit v1.17.2",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        version_label.pack()
        
        # AI助手按钮（顶部）
        ai_btn = ctk.CTkButton(
            self.sidebar,
            text="🤖 AI助手",
            command=self.toggle_ai_assistant,
            height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=("blue", "darkblue"),
            hover_color=("lightblue", "navy")
        )
        ai_btn.grid(row=1, column=0, padx=15, pady=10, sticky="ew")
        
        # 分隔线
        separator = ctk.CTkFrame(self.sidebar, height=2, fg_color="gray30")
        separator.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        # 菜单按钮和分组状态
        self.menu_buttons = []
        self.group_expanded = {}  # 分组展开状态
        self.group_items = {}  # 分组包含的菜单项
        
        # 重组菜单：分离文章发布和商品发布
        menus = [
            ("🏠 仪表板", self.show_dashboard, None),
            ("separator", None, "📝 文章内容"),
            ("📝 小红书", self.show_xiaohongshu, "文章内容"),
            ("📖 知乎", self.show_zhihu, "文章内容"),
            ("🎬 B站", self.show_bilibili, "文章内容"),
            ("🚀 批量文章", self.show_batch_publish, "文章内容"),
            ("separator", None, "📦 商品发布"),
            ("📦 闲鱼商品", self.show_xianyu, "商品发布"),
            ("📊 商品管理", self.show_management, "商品发布"),
            ("separator", None, "🎥 视频制作"),
            ("🎬 视频生产", self.show_video_production, "视频制作"),
            ("🤖 AI助手", self.show_ai_assistant, "视频制作"),
            ("separator", None, "🔧 工具"),
            ("🌐 浏览器", self.show_browser_control, "工具"),
            ("🔐 API配置", self.show_api_config, "工具"),
            ("⚙️ 设置", self.show_settings, "工具"),
        ]
        
        current_row = 3  # 从3开始，因为0=logo, 1=AI按钮, 2=分隔线
        current_group = None
        
        for item in menus:
            if item[0] == "separator":
                # 创建可折叠的分组标签
                if item[2]:  # 有标题
                    group_name = item[2]
                    self.group_expanded[group_name] = True  # 默认展开
                    self.group_items[group_name] = []
                    current_group = group_name
                    
                    # 创建分组标题（可点击）
                    group_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
                    group_frame.grid(row=current_row, column=0, padx=15, pady=(15, 5), sticky="ew")
                    
                    # 展开/收缩图标
                    icon_label = ctk.CTkLabel(
                        group_frame,
                        text="▼",
                        font=ctk.CTkFont(size=10),
                        text_color="gray50",
                        cursor="hand2"
                    )
                    icon_label.pack(side="left", padx=(5, 5))
                    
                    # 标题
                    title_label = ctk.CTkLabel(
                        group_frame,
                        text=item[2],
                        font=ctk.CTkFont(size=12, weight="bold"),
                        text_color="gray50",
                        cursor="hand2"
                    )
                    title_label.pack(side="left")
                    
                    # 绑定点击事件
                    icon_label.bind("<Button-1>", lambda e, g=group_name, i=icon_label: self._toggle_group(g, i))
                    title_label.bind("<Button-1>", lambda e, g=group_name, i=icon_label: self._toggle_group(g, i))
                    group_frame.bind("<Button-1>", lambda e, g=group_name, i=icon_label: self._toggle_group(g, i))
                    
                    current_row += 1
            else:
                # 创建菜单按钮
                text, command, group = item
                btn = ctk.CTkButton(
                    self.sidebar,
                    text=text,
                    command=command,
                    anchor="w",
                    height=40,
                    font=ctk.CTkFont(size=14),
                    fg_color="transparent",
                    text_color=("gray10", "gray90"),
                    hover_color=("gray70", "gray30")
                )
                btn.grid(row=current_row, column=0, padx=15, pady=3, sticky="ew")
                self.menu_buttons.append(btn)
                
                # 记录分组关系
                if current_group:
                    self.group_items[current_group].append(btn)
                
                current_row += 1
        
        # 底部留白（让菜单可以滚动）
        self.sidebar.grid_rowconfigure(current_row, weight=1)
        
        # 分隔线
        separator2 = ctk.CTkFrame(self.sidebar, height=2, fg_color="gray30")
        separator2.grid(row=current_row+1, column=0, padx=20, pady=10, sticky="ew")
        
        # 左下角迷你仪表盘
        self._create_mini_dashboard(current_row+2)
        
        # 状态指示区域
        status_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        status_frame.grid(row=current_row+3, column=0, padx=15, pady=(5, 5), sticky="ew")
        
        # AI状态
        self.ai_status_label = ctk.CTkLabel(
            status_frame,
            text="🤖 AI: 就绪",
            font=ctk.CTkFont(size=11),
            text_color="green"
        )
        self.ai_status_label.pack(anchor="w", pady=1)
        
        # 数据库状态
        self.db_status_label = ctk.CTkLabel(
            status_frame,
            text="💾 数据库: 正常",
            font=ctk.CTkFont(size=11),
            text_color="green"
        )
        self.db_status_label.pack(anchor="w", pady=1)
        
        # 版权信息（放在最底部）
        copyright_label = ctk.CTkLabel(
            self.sidebar,
            text="© 2025 JieDimension Studio",
            font=ctk.CTkFont(size=9),
            text_color="gray50"
        )
        copyright_label.grid(row=current_row+4, column=0, padx=15, pady=(5, 15), sticky="s")
    
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
    
    def _toggle_group(self, group_name: str, icon_label):
        """展开/收缩分组"""
        is_expanded = self.group_expanded.get(group_name, True)
        
        # 切换状态
        self.group_expanded[group_name] = not is_expanded
        
        # 更新图标
        icon_label.configure(text="▼" if not is_expanded else "▶")
        
        # 显示/隐藏该分组下的菜单项
        for btn in self.group_items.get(group_name, []):
            if not is_expanded:
                btn.grid()  # 展开
            else:
                btn.grid_remove()  # 收缩
    
    def _create_mini_dashboard(self, row):
        """创建左下角迷你仪表盘"""
        # 迷你仪表盘框架
        mini_dash = ctk.CTkFrame(
            self.sidebar,
            fg_color=("gray85", "gray20"),
            corner_radius=10
        )
        mini_dash.grid(row=row, column=0, padx=10, pady=10, sticky="ew")
        
        # 标题（可点击）
        title_label = ctk.CTkLabel(
            mini_dash,
            text="📊 今日统计",
            font=ctk.CTkFont(size=12, weight="bold"),
            cursor="hand2"
        )
        title_label.pack(pady=(8, 5))
        title_label.bind("<Button-1>", lambda e: self.show_dashboard())
        
        # 统计数据
        self.mini_gen_count = ctk.CTkLabel(
            mini_dash,
            text="生成: 0次",
            font=ctk.CTkFont(size=11),
            text_color="gray60"
        )
        self.mini_gen_count.pack(anchor="w", padx=15, pady=2)
        
        self.mini_success_rate = ctk.CTkLabel(
            mini_dash,
            text="成功率: 0%",
            font=ctk.CTkFont(size=11),
            text_color="gray60"
        )
        self.mini_success_rate.pack(anchor="w", padx=15, pady=2)
        
        # 点击提示
        click_hint = ctk.CTkLabel(
            mini_dash,
            text="点击查看详情 →",
            font=ctk.CTkFont(size=10),
            text_color="gray50",
            cursor="hand2"
        )
        click_hint.pack(pady=(5, 8))
        click_hint.bind("<Button-1>", lambda e: self.show_dashboard())
        
        # 整个框架可点击
        mini_dash.bind("<Button-1>", lambda e: self.show_dashboard())
        
        # 启动自动更新
        self._update_mini_dashboard()
    
    def _update_mini_dashboard(self):
        """更新迷你仪表盘数据"""
        try:
            # 这里可以从数据库获取实际数据
            # 现在使用模拟数据
            import random
            self.mini_gen_count.configure(text=f"生成: {random.randint(0, 50)}次")
            self.mini_success_rate.configure(text=f"成功率: {random.randint(80, 100)}%")
        except:
            pass
        
        # 每30秒更新一次
        self.after(30000, self._update_mini_dashboard)
    
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
        self._highlight_menu(4)  # 修正索引（批量文章）
        
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
        self._highlight_menu(5)  # 修正索引
        
        from plugins.xianyu.ui.publish_tab import XianyuPublishTab
        xianyu_tab = XianyuPublishTab(self.content)
        xianyu_tab.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
    
    def show_xiaohongshu(self):
        """显示小红书模块"""
        self._clear_content()
        self._highlight_menu(1)  # 修正索引
        
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
        self._highlight_menu(2)  # 修正索引
        
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
        self._highlight_menu(3)  # 修正索引
        
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
    
    def show_video_production(self):
        """显示视频生产模块"""
        self._clear_content()
        self._highlight_menu(7)  # 修正索引（视频生产）
        
        try:
            from plugins.video_producer.ui.video_tab import VideoProductionTab
            video_tab = VideoProductionTab(self.content)
            video_tab.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        except Exception as e:
            error_label = ctk.CTkLabel(
                self.content,
                text=f"❌ 加载失败：{str(e)}",
                font=ctk.CTkFont(size=16),
                text_color="red"
            )
            error_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def toggle_ai_assistant(self):
        """切换AI助手显示/隐藏"""
        if self.ai_visible:
            # 隐藏
            if self.ai_assistant_frame:
                self.ai_assistant_frame.place_forget()
            self.ai_visible = False
        else:
            # 显示
            if not self.ai_assistant_frame:
                self._create_embedded_ai()
            
            # 定位到右下角（在主窗口内）
            self.ai_assistant_frame.place(
                relx=1.0,
                rely=1.0,
                anchor="se",
                x=-20,  # 距离右边20px
                y=-20   # 距离底部20px
            )
            self.ai_visible = True
            self.ai_assistant_frame.lift()  # 置顶
    
    def _create_embedded_ai(self):
        """创建内嵌AI助手"""
        try:
            from ui.ai_chat_window import AIChatWindow
            
            # 创建容器框架
            self.ai_assistant_frame = ctk.CTkFrame(
                self,
                width=380,
                height=550,
                corner_radius=10
            )
            
            # 创建聊天组件
            chat = AIChatWindow(self.ai_assistant_frame)
            chat.pack(fill="both", expand=True)
            
        except Exception as e:
            print(f"创建AI助手失败：{e}")
    
    def show_ai_assistant(self):
        """兼容旧菜单调用"""
        self.toggle_ai_assistant()
    
    def show_api_config(self):
        """显示API配置"""
        self._clear_content()
        self._highlight_menu(9)  # API配置
        
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
        self._highlight_menu(10)  # 设置
        
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

