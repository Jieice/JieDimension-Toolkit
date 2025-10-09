"""
JieDimension Toolkit - 发布预览对话框
显示商品预览，支持编辑和确认发布
Version: 1.0.0
"""

import customtkinter as ctk
from typing import Dict, Any, Optional, Callable
from PIL import Image
import os


class PublishPreviewDialog(ctk.CTkToplevel):
    """发布预览对话框"""
    
    def __init__(
        self,
        parent,
        product: Dict[str, Any],
        on_confirm: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_edit: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None
    ):
        """
        初始化预览对话框
        
        Args:
            parent: 父窗口
            product: 商品数据
            on_confirm: 确认回调
            on_edit: 编辑回调
        """
        super().__init__(parent)
        
        self.product = product.copy()
        self.on_confirm = on_confirm
        self.on_edit = on_edit
        self.confirmed = False
        
        # 窗口配置
        self.title("商品预览")
        self.geometry("700x800")
        
        # 创建界面
        self._create_ui()
        
        # 居中显示
        self._center_window()
    
    def _create_ui(self):
        """创建界面"""
        
        # 主容器（可滚动）
        main_container = ctk.CTkScrollableFrame(self)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 标题栏
        header_frame = ctk.CTkFrame(main_container)
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📦 商品预览",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=10)
        
        # 商品标题
        self._create_title_section(main_container)
        
        # 价格和分类
        self._create_price_category_section(main_container)
        
        # 描述
        self._create_description_section(main_container)
        
        # 图片
        self._create_images_section(main_container)
        
        # 其他信息
        self._create_info_section(main_container)
        
        # 按钮
        self._create_buttons()
    
    def _create_title_section(self, parent):
        """创建标题区域"""
        
        title_frame = ctk.CTkFrame(parent)
        title_frame.pack(fill="x", pady=10)
        
        # 标签
        label = ctk.CTkLabel(
            title_frame,
            text="商品标题",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        label.pack(anchor="w", padx=15, pady=(10, 5))
        
        # 标题内容
        self.title_text = ctk.CTkTextbox(
            title_frame,
            height=60,
            font=ctk.CTkFont(size=14)
        )
        self.title_text.pack(fill="x", padx=15, pady=(0, 10))
        self.title_text.insert("1.0", self.product.get("title", ""))
        
        # 显示原标题（如果有）
        if self.product.get("title_original"):
            original_label = ctk.CTkLabel(
                title_frame,
                text=f"原标题: {self.product['title_original']}",
                font=ctk.CTkFont(size=11),
                text_color="gray",
                anchor="w"
            )
            original_label.pack(anchor="w", padx=15, pady=(0, 10))
    
    def _create_price_category_section(self, parent):
        """创建价格和分类区域"""
        
        info_frame = ctk.CTkFrame(parent)
        info_frame.pack(fill="x", pady=10)
        
        # 网格布局
        info_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_columnconfigure(1, weight=1)
        
        # 价格
        price_container = ctk.CTkFrame(info_frame, fg_color="transparent")
        price_container.grid(row=0, column=0, sticky="ew", padx=15, pady=10)
        
        price_label = ctk.CTkLabel(
            price_container,
            text="价格",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        price_label.pack(anchor="w")
        
        self.price_entry = ctk.CTkEntry(
            price_container,
            font=ctk.CTkFont(size=18, weight="bold"),
            placeholder_text="0.00"
        )
        self.price_entry.pack(fill="x", pady=(5, 0))
        self.price_entry.insert(0, str(self.product.get("price", 0)))
        
        # 分类
        category_container = ctk.CTkFrame(info_frame, fg_color="transparent")
        category_container.grid(row=0, column=1, sticky="ew", padx=15, pady=10)
        
        category_label = ctk.CTkLabel(
            category_container,
            text="分类",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        category_label.pack(anchor="w")
        
        self.category_entry = ctk.CTkEntry(
            category_container,
            font=ctk.CTkFont(size=14)
        )
        self.category_entry.pack(fill="x", pady=(5, 0))
        self.category_entry.insert(0, self.product.get("category", ""))
    
    def _create_description_section(self, parent):
        """创建描述区域"""
        
        desc_frame = ctk.CTkFrame(parent)
        desc_frame.pack(fill="both", expand=True, pady=10)
        
        # 标签
        label = ctk.CTkLabel(
            desc_frame,
            text="商品描述",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        label.pack(anchor="w", padx=15, pady=(10, 5))
        
        # 描述内容
        self.desc_text = ctk.CTkTextbox(
            desc_frame,
            height=200,
            font=ctk.CTkFont(size=13)
        )
        self.desc_text.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        self.desc_text.insert("1.0", self.product.get("description", ""))
    
    def _create_images_section(self, parent):
        """创建图片区域"""
        
        images = self.product.get("images", [])
        
        if not images:
            return
        
        images_frame = ctk.CTkFrame(parent)
        images_frame.pack(fill="x", pady=10)
        
        # 标签
        label = ctk.CTkLabel(
            images_frame,
            text=f"商品图片 ({len(images)}张)",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        label.pack(anchor="w", padx=15, pady=(10, 5))
        
        # 图片列表
        images_list_frame = ctk.CTkFrame(images_frame, fg_color="transparent")
        images_list_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        for idx, image_path in enumerate(images[:9]):
            image_item = ctk.CTkFrame(images_list_frame)
            image_item.pack(fill="x", pady=2)
            
            # 图片编号和路径
            item_text = f"{idx+1}. {os.path.basename(image_path)}"
            if not os.path.exists(image_path):
                item_text += " ⚠️ (不存在)"
            
            item_label = ctk.CTkLabel(
                image_item,
                text=item_text,
                font=ctk.CTkFont(size=12),
                anchor="w"
            )
            item_label.pack(side="left", padx=10, pady=5)
    
    def _create_info_section(self, parent):
        """创建其他信息区域"""
        
        info_frame = ctk.CTkFrame(parent)
        info_frame.pack(fill="x", pady=10)
        
        # 数量
        quantity_container = ctk.CTkFrame(info_frame, fg_color="transparent")
        quantity_container.pack(fill="x", padx=15, pady=10)
        
        quantity_label = ctk.CTkLabel(
            quantity_container,
            text=f"数量: {self.product.get('quantity', 1)}",
            font=ctk.CTkFont(size=13)
        )
        quantity_label.pack(side="left")
        
        # 状态
        status_label = ctk.CTkLabel(
            quantity_container,
            text=f"| 状态: {self.product.get('status', '待发布')}",
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        status_label.pack(side="left", padx=10)
    
    def _create_buttons(self):
        """创建按钮"""
        
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(fill="x", side="bottom", padx=20, pady=20)
        
        # 取消按钮
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="✖️ 取消",
            command=self._on_cancel,
            fg_color="gray",
            hover_color="darkgray",
            width=120
        )
        cancel_btn.pack(side="left", padx=5)
        
        # 编辑按钮
        if self.on_edit:
            edit_btn = ctk.CTkButton(
                btn_frame,
                text="✏️ 编辑",
                command=self._on_edit_clicked,
                fg_color="orange",
                hover_color="darkorange",
                width=120
            )
            edit_btn.pack(side="left", padx=5)
        
        # 确认发布按钮
        confirm_btn = ctk.CTkButton(
            btn_frame,
            text="✅ 确认发布",
            command=self._on_confirm_clicked,
            fg_color="green",
            hover_color="darkgreen",
            width=150
        )
        confirm_btn.pack(side="right", padx=5)
    
    def _on_cancel(self):
        """取消"""
        self.confirmed = False
        self.destroy()
    
    def _on_edit_clicked(self):
        """编辑点击"""
        
        # 获取当前编辑的内容
        edited_product = self._get_edited_product()
        
        if self.on_edit:
            # 调用编辑回调
            result = self.on_edit(edited_product)
            
            if result:
                # 更新产品数据
                self.product = result
                
                # 刷新显示
                self._refresh_display()
    
    def _on_confirm_clicked(self):
        """确认点击"""
        
        # 获取编辑后的商品数据
        edited_product = self._get_edited_product()
        
        # 调用确认回调
        if self.on_confirm:
            self.on_confirm(edited_product)
        
        self.confirmed = True
        self.destroy()
    
    def _get_edited_product(self) -> Dict[str, Any]:
        """获取编辑后的商品数据"""
        
        edited = self.product.copy()
        
        # 获取编辑的内容
        edited["title"] = self.title_text.get("1.0", "end").strip()
        edited["price"] = float(self.price_entry.get() or 0)
        edited["category"] = self.category_entry.get().strip()
        edited["description"] = self.desc_text.get("1.0", "end").strip()
        
        return edited
    
    def _refresh_display(self):
        """刷新显示"""
        
        # 更新标题
        self.title_text.delete("1.0", "end")
        self.title_text.insert("1.0", self.product.get("title", ""))
        
        # 更新价格
        self.price_entry.delete(0, "end")
        self.price_entry.insert(0, str(self.product.get("price", 0)))
        
        # 更新分类
        self.category_entry.delete(0, "end")
        self.category_entry.insert(0, self.product.get("category", ""))
        
        # 更新描述
        self.desc_text.delete("1.0", "end")
        self.desc_text.insert("1.0", self.product.get("description", ""))
    
    def _center_window(self):
        """窗口居中"""
        self.update_idletasks()
        
        # 获取窗口尺寸
        width = self.winfo_width()
        height = self.winfo_height()
        
        # 获取屏幕尺寸
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # 计算居中位置
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # 设置位置
        self.geometry(f"{width}x{height}+{x}+{y}")


class BatchPreviewDialog(ctk.CTkToplevel):
    """批量预览对话框"""
    
    def __init__(
        self,
        parent,
        products: list,
        on_confirm: Optional[Callable[[list], None]] = None
    ):
        """
        初始化批量预览对话框
        
        Args:
            parent: 父窗口
            products: 商品列表
            on_confirm: 确认回调
        """
        super().__init__(parent)
        
        self.products = products
        self.on_confirm = on_confirm
        self.current_index = 0
        self.confirmed = False
        
        # 窗口配置
        self.title(f"批量预览 ({len(products)} 个商品)")
        self.geometry("800x900")
        
        # 创建界面
        self._create_ui()
        
        # 显示第一个商品
        self._show_current_product()
        
        # 居中显示
        self._center_window()
    
    def _create_ui(self):
        """创建界面"""
        
        # 顶部导航栏
        nav_frame = ctk.CTkFrame(self)
        nav_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # 上一个按钮
        self.prev_btn = ctk.CTkButton(
            nav_frame,
            text="◀ 上一个",
            command=self._prev_product,
            width=100
        )
        self.prev_btn.pack(side="left", padx=5)
        
        # 进度显示
        self.progress_label = ctk.CTkLabel(
            nav_frame,
            text="",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.progress_label.pack(side="left", expand=True)
        
        # 下一个按钮
        self.next_btn = ctk.CTkButton(
            nav_frame,
            text="下一个 ▶",
            command=self._next_product,
            width=100
        )
        self.next_btn.pack(side="right", padx=5)
        
        # 预览容器（可滚动）
        self.preview_container = ctk.CTkScrollableFrame(self)
        self.preview_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # 底部按钮
        self._create_bottom_buttons()
    
    def _create_bottom_buttons(self):
        """创建底部按钮"""
        
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(fill="x", side="bottom", padx=20, pady=20)
        
        # 取消按钮
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="✖️ 取消",
            command=self._on_cancel,
            fg_color="gray",
            hover_color="darkgray",
            width=120
        )
        cancel_btn.pack(side="left", padx=5)
        
        # 确认全部按钮
        confirm_all_btn = ctk.CTkButton(
            btn_frame,
            text=f"✅ 确认全部 ({len(self.products)}个)",
            command=self._on_confirm_all,
            fg_color="green",
            hover_color="darkgreen",
            width=180
        )
        confirm_all_btn.pack(side="right", padx=5)
    
    def _show_current_product(self):
        """显示当前商品"""
        
        # 清空容器
        for widget in self.preview_container.winfo_children():
            widget.destroy()
        
        # 更新进度
        self.progress_label.configure(
            text=f"商品 {self.current_index + 1} / {len(self.products)}"
        )
        
        # 更新按钮状态
        self.prev_btn.configure(state="normal" if self.current_index > 0 else "disabled")
        self.next_btn.configure(state="normal" if self.current_index < len(self.products) - 1 else "disabled")
        
        # 获取当前商品
        product = self.products[self.current_index]
        
        # 显示商品信息
        self._display_product(product)
    
    def _display_product(self, product: Dict[str, Any]):
        """显示商品"""
        
        # 标题
        title_label = ctk.CTkLabel(
            self.preview_container,
            text=product.get("title", ""),
            font=ctk.CTkFont(size=16, weight="bold"),
            wraplength=700,
            anchor="w"
        )
        title_label.pack(anchor="w", pady=10)
        
        # 价格和分类
        info_frame = ctk.CTkFrame(self.preview_container)
        info_frame.pack(fill="x", pady=10)
        
        price_label = ctk.CTkLabel(
            info_frame,
            text=f"💰 ¥{product.get('price', 0)}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="orange"
        )
        price_label.pack(side="left", padx=15, pady=10)
        
        category_label = ctk.CTkLabel(
            info_frame,
            text=f"🏷️ {product.get('category', '')}",
            font=ctk.CTkFont(size=14)
        )
        category_label.pack(side="left", padx=15, pady=10)
        
        # 描述
        desc_frame = ctk.CTkFrame(self.preview_container)
        desc_frame.pack(fill="both", expand=True, pady=10)
        
        desc_label = ctk.CTkLabel(
            desc_frame,
            text="商品描述",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        desc_label.pack(anchor="w", padx=15, pady=(10, 5))
        
        desc_text = ctk.CTkTextbox(
            desc_frame,
            height=250,
            font=ctk.CTkFont(size=13)
        )
        desc_text.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        desc_text.insert("1.0", product.get("description", ""))
        desc_text.configure(state="disabled")
        
        # 图片信息
        images = product.get("images", [])
        if images:
            images_label = ctk.CTkLabel(
                self.preview_container,
                text=f"📸 包含 {len(images)} 张图片",
                font=ctk.CTkFont(size=13),
                text_color="gray"
            )
            images_label.pack(anchor="w", pady=5)
    
    def _prev_product(self):
        """上一个商品"""
        if self.current_index > 0:
            self.current_index -= 1
            self._show_current_product()
    
    def _next_product(self):
        """下一个商品"""
        if self.current_index < len(self.products) - 1:
            self.current_index += 1
            self._show_current_product()
    
    def _on_cancel(self):
        """取消"""
        self.confirmed = False
        self.destroy()
    
    def _on_confirm_all(self):
        """确认全部"""
        
        if self.on_confirm:
            self.on_confirm(self.products)
        
        self.confirmed = True
        self.destroy()
    
    def _center_window(self):
        """窗口居中"""
        self.update_idletasks()
        
        width = self.winfo_width()
        height = self.winfo_height()
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.geometry(f"{width}x{height}+{x}+{y}")


# 测试代码
if __name__ == "__main__":
    import sys
    import os
    
    # 添加项目根目录到路径
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
    
    # 测试数据
    test_product = {
        "title": "【95新】iPhone 13 Pro Max 256G 远峰蓝 🔥 自用爱护 全套配件齐全",
        "title_original": "二手iPhone 13 Pro Max 256G",
        "price": 6999,
        "category": "数码产品",
        "description": """这是一款9成新的iPhone 13 Pro Max，256GB大存储，远峰蓝配色，非常时尚！

【商品亮点】
✨ 成色极佳，无磕碰无划痕
✨ 电池健康度95%以上
✨ 原装充电器、数据线、耳机全套配件
✨ 赠送手机壳和钢化膜

【性能表现】
📱 A15仿生芯片，性能强劲
📸 三摄系统，拍照专业
🔋 续航持久，一天无忧

个人自用，因换新机出售，支持当面验机，可小刀！""",
        "images": [
            "test1.jpg",
            "test2.jpg",
            "test3.jpg"
        ],
        "quantity": 1,
        "status": "待发布"
    }
    
    # 创建测试应用
    app = ctk.CTk()
    app.geometry("400x300")
    app.title("预览对话框测试")
    
    def show_preview():
        dialog = PublishPreviewDialog(
            app,
            test_product,
            on_confirm=lambda p: print(f"确认发布: {p['title']}"),
            on_edit=lambda p: print(f"编辑商品: {p['title']}")
        )
        dialog.grab_set()  # 模态对话框
        app.wait_window(dialog)
        print(f"对话框已关闭，confirmed={dialog.confirmed}")
    
    def show_batch_preview():
        products = [test_product.copy() for _ in range(3)]
        for idx, p in enumerate(products):
            p["title"] = f"商品 {idx+1} - {p['title']}"
        
        dialog = BatchPreviewDialog(
            app,
            products,
            on_confirm=lambda ps: print(f"确认发布 {len(ps)} 个商品")
        )
        dialog.grab_set()
        app.wait_window(dialog)
        print(f"批量对话框已关闭，confirmed={dialog.confirmed}")
    
    # 测试按钮
    btn1 = ctk.CTkButton(
        app,
        text="单个商品预览",
        command=show_preview
    )
    btn1.pack(pady=20)
    
    btn2 = ctk.CTkButton(
        app,
        text="批量商品预览",
        command=show_batch_preview
    )
    btn2.pack(pady=20)
    
    app.mainloop()

