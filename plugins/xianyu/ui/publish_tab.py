"""
JieDimension Toolkit - 闲鱼发布界面
支持导入商品、AI优化、批量发布
支持真实发布/模拟发布、Cookie状态管理
Version: 1.1.0 (Day 16)
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import asyncio
import os
import sys
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from plugins.xianyu.data_importer import DataImporter
from plugins.xianyu.publisher import XianyuPublisher
from core.database import Database
from core.browser_automation import XianyuAutomation


class ProductCard(ctk.CTkFrame):
    """商品卡片组件"""
    
    def __init__(self, parent, product: Dict[str, Any], index: int):
        super().__init__(parent, fg_color=("gray90", "gray25"), corner_radius=10)
        
        self.product = product
        self.index = index
        
        # 配置网格
        self.grid_columnconfigure(1, weight=1)
        
        # 序号
        number_label = ctk.CTkLabel(
            self,
            text=f"#{index + 1}",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=40,
            text_color="gray60"
        )
        number_label.grid(row=0, column=0, rowspan=3, padx=(15, 10), pady=15, sticky="n")
        
        # 标题
        title_text = product.get('title', '未知标题')
        if len(title_text) > 60:
            title_text = title_text[:60] + "..."
        
        title_label = ctk.CTkLabel(
            self,
            text=title_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        title_label.grid(row=0, column=1, padx=(0, 15), pady=(15, 5), sticky="ew")
        
        # 分类和价格
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.grid(row=1, column=1, padx=(0, 15), pady=5, sticky="w")
        
        category = ctk.CTkLabel(
            info_frame,
            text=f"📂 {product.get('category', '未分类')}",
            font=ctk.CTkFont(size=12),
            text_color="gray60"
        )
        category.pack(side="left", padx=(0, 15))
        
        price = ctk.CTkLabel(
            info_frame,
            text=f"💰 ¥{product.get('price', 0)}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="orange"
        )
        price.pack(side="left", padx=(0, 15))
        
        # 库存
        quantity = product.get('quantity', 1)
        stock = ctk.CTkLabel(
            info_frame,
            text=f"📦 库存: {quantity}",
            font=ctk.CTkFont(size=12),
            text_color="gray60"
        )
        stock.pack(side="left")
        
        # 描述预览
        desc_text = product.get('description', '无描述')
        if len(desc_text) > 80:
            desc_text = desc_text[:80] + "..."
        
        desc_label = ctk.CTkLabel(
            self,
            text=desc_text,
            font=ctk.CTkFont(size=11),
            text_color="gray50",
            anchor="w",
            wraplength=700
        )
        desc_label.grid(row=2, column=1, padx=(0, 15), pady=(5, 15), sticky="ew")
        
        # 状态标签
        self.status_label = ctk.CTkLabel(
            self,
            text="⏳ 等待",
            font=ctk.CTkFont(size=11),
            width=80,
            text_color="gray60"
        )
        self.status_label.grid(row=0, column=2, rowspan=3, padx=15, pady=15)
    
    def update_status(self, status: str, color: str = "gray60"):
        """更新状态"""
        self.status_label.configure(text=status, text_color=color)


class XianyuPublishTab(ctk.CTkScrollableFrame):
    """闲鱼发布界面"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # 配置网格
        self.grid_columnconfigure(0, weight=1)
        
        # 数据
        self.products: List[Dict[str, Any]] = []
        self.product_cards: List[ProductCard] = []
        self.importer = DataImporter()
        self.publisher = XianyuPublisher()
        self.db = Database()
        
        # 发布配置
        self.cookies_file = "data/xianyu_cookies.json"
        self.use_browser = False  # 默认使用模拟模式
        self.headless = False  # 默认显示浏览器窗口
        
        # 创建界面
        self._create_header()
        self._create_control_panel()
        self._create_publish_config_panel()  # 新增：发布配置面板
        self._create_products_area()
        self._create_progress_area()
        
        # 检查Cookie状态
        self._check_cookie_status()
    
    def _create_header(self):
        """创建顶部标题栏"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=30, pady=(30, 20), sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)
        
        # 标题
        title = ctk.CTkLabel(
            header_frame,
            text="📦 闲鱼商品发布",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title.grid(row=0, column=0, sticky="w")
        
        # 商品数量
        self.count_label = ctk.CTkLabel(
            header_frame,
            text="已加载 0 个商品",
            font=ctk.CTkFont(size=14),
            text_color="gray60"
        )
        self.count_label.grid(row=0, column=1, sticky="e")
    
    def _create_control_panel(self):
        """创建控制面板"""
        control_frame = ctk.CTkFrame(self, fg_color=("gray85", "gray20"), corner_radius=15)
        control_frame.grid(row=1, column=0, padx=30, pady=10, sticky="ew")
        control_frame.grid_columnconfigure(2, weight=1)
        
        # 文件选择按钮
        select_btn = ctk.CTkButton(
            control_frame,
            text="📁 选择Excel文件",
            command=self._select_file,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="blue",
            hover_color="darkblue"
        )
        select_btn.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        # AI优化开关
        self.ai_optimize_var = ctk.BooleanVar(value=True)
        ai_checkbox = ctk.CTkCheckBox(
            control_frame,
            text="🤖 启用AI优化（标题+描述）",
            variable=self.ai_optimize_var,
            font=ctk.CTkFont(size=13),
            onvalue=True,
            offvalue=False
        )
        ai_checkbox.grid(row=0, column=1, padx=15, pady=15, sticky="w")
        
        # 操作按钮区域
        action_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        action_frame.grid(row=0, column=3, padx=15, pady=15, sticky="e")
        
        # 清空按钮
        clear_btn = ctk.CTkButton(
            action_frame,
            text="🗑️ 清空",
            command=self._clear_products,
            width=100,
            height=40,
            font=ctk.CTkFont(size=13),
            fg_color="gray50",
            hover_color="gray40"
        )
        clear_btn.pack(side="left", padx=5)
        
        # 开始处理按钮
        self.process_btn = ctk.CTkButton(
            action_frame,
            text="🚀 开始处理",
            command=self._start_processing,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        self.process_btn.pack(side="left", padx=5)
        self.process_btn.configure(state="disabled")
    
    def _create_publish_config_panel(self):
        """创建发布配置面板"""
        config_frame = ctk.CTkFrame(self, fg_color=("gray85", "gray20"), corner_radius=15)
        config_frame.grid(row=2, column=0, padx=30, pady=10, sticky="ew")
        config_frame.grid_columnconfigure(1, weight=1)
        
        # 标题
        title_label = ctk.CTkLabel(
            config_frame,
            text="⚙️ 发布配置",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        title_label.grid(row=0, column=0, columnspan=4, padx=20, pady=(15, 10), sticky="w")
        
        # 第一行：发布模式
        mode_label = ctk.CTkLabel(
            config_frame,
            text="发布模式:",
            font=ctk.CTkFont(size=13),
            width=80,
            anchor="w"
        )
        mode_label.grid(row=1, column=0, padx=(20, 10), pady=10, sticky="w")
        
        # 模式选择开关
        self.use_browser_var = ctk.BooleanVar(value=False)
        self.mode_switch = ctk.CTkSwitch(
            config_frame,
            text="真实浏览器发布",
            variable=self.use_browser_var,
            command=self._on_mode_changed,
            font=ctk.CTkFont(size=13)
        )
        self.mode_switch.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # 模式提示
        self.mode_hint = ctk.CTkLabel(
            config_frame,
            text="📝 当前：模拟发布（用于测试）",
            font=ctk.CTkFont(size=12),
            text_color="gray60",
            anchor="w"
        )
        self.mode_hint.grid(row=1, column=2, padx=10, pady=10, sticky="w")
        
        # 第二行：Cookie状态
        cookie_label = ctk.CTkLabel(
            config_frame,
            text="登录状态:",
            font=ctk.CTkFont(size=13),
            width=80,
            anchor="w"
        )
        cookie_label.grid(row=2, column=0, padx=(20, 10), pady=10, sticky="w")
        
        # Cookie状态显示
        self.cookie_status_label = ctk.CTkLabel(
            config_frame,
            text="🔒 未登录",
            font=ctk.CTkFont(size=13),
            text_color="gray",
            anchor="w"
        )
        self.cookie_status_label.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        # 登录按钮
        self.login_btn = ctk.CTkButton(
            config_frame,
            text="🌐 登录闲鱼",
            width=120,
            height=32,
            command=self._on_login,
            font=ctk.CTkFont(size=13),
            fg_color="orange",
            hover_color="darkorange"
        )
        self.login_btn.grid(row=2, column=2, padx=10, pady=10, sticky="w")
        
        # 刷新Cookie状态按钮
        refresh_btn = ctk.CTkButton(
            config_frame,
            text="🔄",
            width=40,
            height=32,
            command=self._check_cookie_status,
            font=ctk.CTkFont(size=13),
            fg_color="gray50",
            hover_color="gray40"
        )
        refresh_btn.grid(row=2, column=3, padx=(5, 20), pady=10, sticky="w")
        
        # 第三行：浏览器设置
        browser_label = ctk.CTkLabel(
            config_frame,
            text="浏览器:",
            font=ctk.CTkFont(size=13),
            width=80,
            anchor="w"
        )
        browser_label.grid(row=3, column=0, padx=(20, 10), pady=(10, 15), sticky="w")
        
        # 无头模式开关
        self.headless_var = ctk.BooleanVar(value=False)
        headless_checkbox = ctk.CTkCheckBox(
            config_frame,
            text="无头模式（后台运行）",
            variable=self.headless_var,
            command=self._on_headless_changed,
            font=ctk.CTkFont(size=12)
        )
        headless_checkbox.grid(row=3, column=1, columnspan=2, padx=10, pady=(10, 15), sticky="w")
    
    def _on_mode_changed(self):
        """发布模式切换"""
        self.use_browser = self.use_browser_var.get()
        
        if self.use_browser:
            self.mode_hint.configure(
                text="🚀 当前：真实发布（将实际发布到闲鱼）",
                text_color="green"
            )
            # 检查Cookie状态
            self._check_cookie_status()
        else:
            self.mode_hint.configure(
                text="📝 当前：模拟发布（用于测试）",
                text_color="gray60"
            )
    
    def _on_headless_changed(self):
        """无头模式切换"""
        self.headless = self.headless_var.get()
    
    def _check_cookie_status(self):
        """检查Cookie状态"""
        try:
            cookies_path = Path(self.cookies_file)
            
            if not cookies_path.exists():
                self.cookie_status_label.configure(
                    text="🔒 未登录",
                    text_color="gray"
                )
                return
            
            # 读取Cookie文件
            with open(cookies_path, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            if not cookies:
                self.cookie_status_label.configure(
                    text="🔒 未登录",
                    text_color="gray"
                )
                return
            
            # 检查Cookie是否包含关键字段
            # 注意：实际过期时间检查需要更复杂的逻辑
            self.cookie_status_label.configure(
                text="✅ 已登录",
                text_color="green"
            )
            
        except Exception as e:
            print(f"检查Cookie状态失败: {e}")
            self.cookie_status_label.configure(
                text="⚠️ 状态未知",
                text_color="orange"
            )
    
    def _on_login(self):
        """登录闲鱼"""
        # 在新线程中打开浏览器登录
        thread = threading.Thread(target=self._login_thread)
        thread.daemon = True
        thread.start()
    
    def _login_thread(self):
        """登录线程"""
        try:
            # 创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 运行异步登录
            loop.run_until_complete(self._async_login())
            
        except Exception as e:
            print(f"登录出错: {e}")
            self.after(0, lambda: messagebox.showerror("错误", f"登录失败：{str(e)}"))
    
    async def _async_login(self):
        """异步登录"""
        try:
            self.after(0, lambda: self.login_btn.configure(state="disabled", text="登录中..."))
            
            # 创建自动化实例
            automation = XianyuAutomation(headless=False)
            await automation.start()
            
            # 执行登录
            success = await automation.login(self.cookies_file, force_login=True)
            
            await automation.stop()
            
            if success:
                self.after(0, lambda: messagebox.showinfo(
                    "登录成功",
                    "已成功登录闲鱼！\nCookie已保存，可以开始真实发布。"
                ))
                self.after(0, self._check_cookie_status)
            else:
                self.after(0, lambda: messagebox.showerror(
                    "登录失败",
                    "登录闲鱼失败，请重试。"
                ))
            
        except Exception as e:
            print(f"登录失败: {e}")
            self.after(0, lambda: messagebox.showerror("错误", f"登录失败：{str(e)}"))
        finally:
            self.after(0, lambda: self.login_btn.configure(state="normal", text="🌐 登录闲鱼"))
    
    def _create_products_area(self):
        """创建商品展示区域"""
        # 标题
        section_title = ctk.CTkLabel(
            self,
            text="📋 商品列表",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w"
        )
        section_title.grid(row=3, column=0, padx=30, pady=(20, 10), sticky="w")
        
        # 商品列表容器
        self.products_container = ctk.CTkFrame(self, fg_color="transparent")
        self.products_container.grid(row=4, column=0, padx=30, pady=10, sticky="ew")
        self.products_container.grid_columnconfigure(0, weight=1)
        
        # 空状态提示
        self.empty_label = ctk.CTkLabel(
            self.products_container,
            text="📂 请先选择Excel文件导入商品",
            font=ctk.CTkFont(size=16),
            text_color="gray60"
        )
        self.empty_label.grid(row=0, column=0, pady=50)
    
    def _create_progress_area(self):
        """创建进度显示区域"""
        progress_frame = ctk.CTkFrame(self, fg_color=("gray85", "gray20"), corner_radius=15)
        progress_frame.grid(row=5, column=0, padx=30, pady=(10, 30), sticky="ew")
        progress_frame.grid_columnconfigure(0, weight=1)
        
        # 进度标题
        self.progress_title = ctk.CTkLabel(
            progress_frame,
            text="📊 处理进度",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        self.progress_title.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")
        
        # 进度条
        self.progress_bar = ctk.CTkProgressBar(
            progress_frame,
            height=20,
            corner_radius=10
        )
        self.progress_bar.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.progress_bar.set(0)
        
        # 进度文字
        self.progress_text = ctk.CTkLabel(
            progress_frame,
            text="0 / 0 (0%)",
            font=ctk.CTkFont(size=13),
            text_color="gray60"
        )
        self.progress_text.grid(row=2, column=0, padx=20, pady=(0, 15), sticky="w")
    
    def _select_file(self):
        """选择文件"""
        file_path = filedialog.askopenfilename(
            title="选择Excel文件",
            filetypes=[
                ("Excel文件", "*.xlsx *.xls"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            self._load_products(file_path)
    
    def _load_products(self, file_path: str):
        """加载商品数据"""
        try:
            # 导入数据
            self.products = self.importer.import_from_excel(file_path)
            
            if not self.products:
                messagebox.showwarning("警告", "Excel文件中没有有效的商品数据")
                return
            
            # 更新界面
            self._display_products()
            self.count_label.configure(text=f"已加载 {len(self.products)} 个商品")
            self.process_btn.configure(state="normal")
            
            messagebox.showinfo(
                "导入成功",
                f"成功导入 {len(self.products)} 个商品！\n\n点击'开始处理'进行AI优化和发布。"
            )
            
        except Exception as e:
            messagebox.showerror("错误", f"导入失败：{str(e)}")
    
    def _display_products(self):
        """显示商品列表"""
        # 清空现有商品卡片
        for widget in self.products_container.winfo_children():
            widget.destroy()
        
        self.product_cards = []
        
        # 创建商品卡片
        for idx, product in enumerate(self.products):
            card = ProductCard(self.products_container, product, idx)
            card.grid(row=idx, column=0, pady=5, sticky="ew")
            self.product_cards.append(card)
    
    def _clear_products(self):
        """清空商品列表"""
        if self.products and not messagebox.askyesno(
            "确认",
            "确定要清空所有商品吗？"
        ):
            return
        
        self.products = []
        self.product_cards = []
        
        # 清空界面
        for widget in self.products_container.winfo_children():
            widget.destroy()
        
        # 显示空状态
        self.empty_label = ctk.CTkLabel(
            self.products_container,
            text="📂 请先选择Excel文件导入商品",
            font=ctk.CTkFont(size=16),
            text_color="gray60"
        )
        self.empty_label.grid(row=0, column=0, pady=50)
        
        # 重置状态
        self.count_label.configure(text="已加载 0 个商品")
        self.process_btn.configure(state="disabled")
        self.progress_bar.set(0)
        self.progress_text.configure(text="0 / 0 (0%)")
    
    def _start_processing(self):
        """开始处理"""
        if not self.products:
            messagebox.showwarning("警告", "请先导入商品数据")
            return
        
        # 禁用按钮
        self.process_btn.configure(state="disabled")
        
        # 在新线程中运行异步任务
        thread = threading.Thread(target=self._process_products_thread)
        thread.daemon = True
        thread.start()
    
    def _process_products_thread(self):
        """处理商品的线程函数"""
        try:
            # 创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 运行异步处理
            loop.run_until_complete(self._process_products())
            
        except Exception as e:
            print(f"处理出错: {e}")
            self.after(0, lambda: messagebox.showerror("错误", f"处理失败：{str(e)}"))
        finally:
            # 重新启用按钮
            self.after(0, lambda: self.process_btn.configure(state="normal"))
    
    async def _process_products(self):
        """异步处理所有商品"""
        try:
            await self.db.connect()
            
            total = len(self.products)
            use_ai = self.ai_optimize_var.get()
            
            # 显示发布模式
            mode_text = "真实发布" if self.use_browser else "模拟发布"
            print(f"\n{'='*60}")
            print(f"开始批量处理 - 模式: {mode_text}")
            print(f"AI优化: {'开启' if use_ai else '关闭'}")
            print(f"{'='*60}\n")
            
            for idx, product in enumerate(self.products):
                # 更新进度
                progress = (idx + 1) / total
                self.after(0, lambda p=progress: self.progress_bar.set(p))
                self.after(0, lambda i=idx, t=total: self.progress_text.configure(
                    text=f"{i + 1} / {t} ({int((i + 1) / t * 100)}%) - {mode_text}"
                ))
                
                # 更新卡片状态
                self.after(0, lambda c=self.product_cards[idx]: c.update_status("🔄 处理中...", "blue"))
                
                try:
                    # AI优化
                    if use_ai:
                        optimized_product = await self.publisher.optimize_product(product)
                    else:
                        optimized_product = product
                    
                    # 发布商品（根据模式选择）
                    if self.use_browser:
                        # 真实发布
                        result = await self.publisher.publish_product(
                            optimized_product,
                            use_browser=True,
                            cookies_file=self.cookies_file,
                            headless=self.headless,
                            enable_retry=True
                        )
                        
                        if not result.get("success", False):
                            raise Exception(result.get("error", "发布失败"))
                        
                        product_url = result.get("url", "")
                        product_id_str = result.get("product_id", "")
                    else:
                        # 模拟发布（仅保存到数据库）
                        product_url = ""
                        product_id_str = ""
                    
                    # 保存到数据库
                    product_id = await self.db.create_product(
                        platform="xianyu",
                        title=optimized_product["title"],
                        description=optimized_product.get("description", ""),
                        price=optimized_product.get("price", 0),
                        category=optimized_product.get("category", ""),
                        images=optimized_product.get("images", ""),
                        metadata={
                            **optimized_product,
                            "product_url": product_url,
                            "xianyu_id": product_id_str,
                            "publish_mode": mode_text
                        }
                    )
                    
                    # 创建任务记录
                    task_name = f"发布商品: {optimized_product['title'][:30]}"
                    await self.db.create_task(
                        platform="xianyu",
                        task_type="publish",
                        task_name=task_name,
                        status="completed",
                        metadata={
                            "product_id": product_id,
                            "product_url": product_url,
                            "publish_mode": mode_text
                        }
                    )
                    
                    # 更新卡片状态
                    status_text = f"✅ 已发布" if self.use_browser else "✅ 已保存"
                    self.after(0, lambda c=self.product_cards[idx], s=status_text: c.update_status(s, "green"))
                    
                except Exception as e:
                    print(f"处理商品 #{idx + 1} 失败: {e}")
                    self.after(0, lambda c=self.product_cards[idx]: c.update_status("❌ 失败", "red"))
            
            # 完成提示
            success_msg = (
                f"已处理 {total} 个商品！\n\n"
                f"发布模式: {mode_text}\n"
                f"{'AI优化: 已启用' if use_ai else 'AI优化: 未启用'}\n"
                f"{'商品已发布到闲鱼' if self.use_browser else '数据已保存到数据库'}"
            )
            self.after(0, lambda msg=success_msg: messagebox.showinfo("完成", msg))
            
        except Exception as e:
            print(f"处理商品失败: {e}")
            self.after(0, lambda: messagebox.showerror("错误", f"处理失败：{str(e)}"))
        finally:
            await self.db.close()


# ===== 测试函数 =====

def main():
    """测试闲鱼发布界面"""
    root = ctk.CTk()
    root.title("闲鱼发布测试")
    root.geometry("1200x800")
    ctk.set_appearance_mode("dark")
    
    tab = XianyuPublishTab(root)
    tab.pack(fill="both", expand=True, padx=20, pady=20)
    
    root.mainloop()


if __name__ == "__main__":
    main()

