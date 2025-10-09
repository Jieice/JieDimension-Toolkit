"""
JieDimension Toolkit - 选择器配置界面
管理和配置浏览器自动化的CSS选择器
Version: 1.0.0
"""

import customtkinter as ctk
from typing import Dict, Any, Optional
import json
import os
from datetime import datetime


class SelectorConfigPanel(ctk.CTkFrame):
    """选择器配置面板"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.config_file = "config/xianyu_selectors.json"
        self.selectors = {}
        self.modified = False
        
        # 创建界面
        self._create_ui()
        
        # 加载配置
        self.load_config()
    
    def _create_ui(self):
        """创建界面"""
        
        # 顶部标题栏
        self._create_header()
        
        # 选择器编辑区域
        self._create_selector_editor()
        
        # 底部按钮
        self._create_bottom_buttons()
    
    def _create_header(self):
        """创建标题栏"""
        
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # 标题
        title_label = ctk.CTkLabel(
            header_frame,
            text="⚙️ 选择器配置",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left", padx=15, pady=15)
        
        # 说明
        info_label = ctk.CTkLabel(
            header_frame,
            text="配置浏览器自动化的CSS选择器（闲鱼页面更新时需要调整）",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        info_label.pack(side="left", padx=15, pady=15)
        
        # 状态指示器
        self.status_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="right", padx=15, pady=15)
    
    def _create_selector_editor(self):
        """创建选择器编辑器"""
        
        # 编辑器容器（可滚动）
        self.editor_frame = ctk.CTkScrollableFrame(self, label_text="选择器列表")
        self.editor_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # 选择器分类
        categories = {
            "登录相关": [
                ("user_info", "用户信息元素", ".user-info, .user-name, .avatar"),
            ],
            "发布页面": [
                ("image_upload", "图片上传输入框", "input[type='file']"),
                ("title_input", "标题输入框", "input[placeholder*='标题'], input[name='title']"),
                ("price_input", "价格输入框", "input[placeholder*='价格'], input[name='price']"),
                ("desc_input", "描述输入框", "textarea[placeholder*='描述'], textarea[name='description']"),
                ("category_btn", "分类按钮", "button.category-btn, .category-select"),
                ("publish_btn", "发布按钮", "button.publish-btn, button[type='submit']"),
            ],
            "发布结果": [
                ("success_indicator", "成功提示元素", ".success, [class*='success']"),
            ]
        }
        
        self.selector_entries = {}
        
        for category, items in categories.items():
            # 分类标题
            category_frame = ctk.CTkFrame(self.editor_frame)
            category_frame.pack(fill="x", pady=10, padx=10)
            
            category_label = ctk.CTkLabel(
                category_frame,
                text=f"📁 {category}",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            category_label.pack(anchor="w", padx=15, pady=10)
            
            # 选择器项
            for key, description, default_value in items:
                self._create_selector_item(
                    category_frame,
                    key,
                    description,
                    default_value
                )
    
    def _create_selector_item(
        self,
        parent,
        key: str,
        description: str,
        default_value: str
    ):
        """创建选择器项"""
        
        item_frame = ctk.CTkFrame(parent)
        item_frame.pack(fill="x", padx=15, pady=5)
        
        # 左侧：标签和描述
        left_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        
        # 键名
        key_label = ctk.CTkLabel(
            left_frame,
            text=key,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        key_label.pack(anchor="w")
        
        # 描述
        desc_label = ctk.CTkLabel(
            left_frame,
            text=description,
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="w"
        )
        desc_label.pack(anchor="w")
        
        # 右侧：输入框和按钮
        right_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        right_frame.pack(side="right", padx=10, pady=10)
        
        # 输入框
        entry = ctk.CTkEntry(
            right_frame,
            width=400,
            placeholder_text=default_value
        )
        entry.pack(side="left", padx=5)
        entry.insert(0, default_value)
        entry.bind("<KeyRelease>", lambda e: self._on_selector_changed())
        
        # 保存引用
        self.selector_entries[key] = entry
        
        # 测试按钮
        test_btn = ctk.CTkButton(
            right_frame,
            text="🧪 测试",
            command=lambda k=key: self._test_selector(k),
            width=80
        )
        test_btn.pack(side="left", padx=5)
    
    def _create_bottom_buttons(self):
        """创建底部按钮"""
        
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(fill="x", padx=20, pady=20)
        
        # 左侧按钮
        left_frame = ctk.CTkFrame(btn_frame, fg_color="transparent")
        left_frame.pack(side="left")
        
        # 重置按钮
        reset_btn = ctk.CTkButton(
            left_frame,
            text="🔄 重置默认",
            command=self._reset_to_default,
            fg_color="gray",
            width=120
        )
        reset_btn.pack(side="left", padx=5)
        
        # 导入按钮
        import_btn = ctk.CTkButton(
            left_frame,
            text="📥 导入",
            command=self._import_config,
            width=100
        )
        import_btn.pack(side="left", padx=5)
        
        # 导出按钮
        export_btn = ctk.CTkButton(
            left_frame,
            text="📤 导出",
            command=self._export_config,
            width=100
        )
        export_btn.pack(side="left", padx=5)
        
        # 右侧按钮
        right_frame = ctk.CTkFrame(btn_frame, fg_color="transparent")
        right_frame.pack(side="right")
        
        # 测试全部按钮
        test_all_btn = ctk.CTkButton(
            right_frame,
            text="🧪 测试全部",
            command=self._test_all_selectors,
            fg_color="orange",
            width=120
        )
        test_all_btn.pack(side="left", padx=5)
        
        # 保存按钮
        self.save_btn = ctk.CTkButton(
            right_frame,
            text="💾 保存配置",
            command=self.save_config,
            fg_color="green",
            hover_color="darkgreen",
            width=120
        )
        self.save_btn.pack(side="left", padx=5)
    
    def load_config(self):
        """加载配置"""
        
        try:
            # 尝试从文件加载
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.selectors = json.load(f)
                
                # 更新输入框
                for key, entry in self.selector_entries.items():
                    if key in self.selectors:
                        entry.delete(0, "end")
                        entry.insert(0, self.selectors[key])
                
                self._update_status("✅ 配置已加载", "green")
            else:
                # 使用默认配置
                self._load_default_config()
                self._update_status("ℹ️ 使用默认配置", "blue")
            
            self.modified = False
            
        except Exception as e:
            print(f"❌ 加载配置失败: {e}")
            self._update_status(f"❌ 加载失败: {e}", "red")
    
    def _load_default_config(self):
        """加载默认配置"""
        
        # 从输入框的默认值构建配置
        self.selectors = {}
        for key, entry in self.selector_entries.items():
            self.selectors[key] = entry.get()
    
    def save_config(self):
        """保存配置"""
        
        try:
            # 从输入框收集选择器
            self.selectors = {}
            for key, entry in self.selector_entries.items():
                value = entry.get().strip()
                if value:
                    self.selectors[key] = value
            
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            # 添加元数据
            config_data = {
                "version": "1.0",
                "updated_at": datetime.now().isoformat(),
                "selectors": self.selectors
            }
            
            # 保存到文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self.modified = False
            self._update_status("✅ 配置已保存", "green")
            
            print(f"✅ 配置已保存到: {self.config_file}")
            
        except Exception as e:
            print(f"❌ 保存配置失败: {e}")
            self._update_status(f"❌ 保存失败: {e}", "red")
    
    def _on_selector_changed(self):
        """选择器改变"""
        
        self.modified = True
        self._update_status("⚠️ 有未保存的更改", "orange")
    
    def _update_status(self, text: str, color: str):
        """更新状态"""
        
        self.status_label.configure(text=text, text_color=color)
    
    def _reset_to_default(self):
        """重置为默认配置"""
        
        # 确认对话框
        dialog = ctk.CTkToplevel(self)
        dialog.title("确认重置")
        dialog.geometry("400x200")
        
        label = ctk.CTkLabel(
            dialog,
            text="⚠️ 确定要重置为默认配置吗？\n当前配置将被覆盖！",
            font=ctk.CTkFont(size=14)
        )
        label.pack(expand=True)
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="取消",
            command=dialog.destroy,
            fg_color="gray"
        )
        cancel_btn.pack(side="left", padx=10)
        
        confirm_btn = ctk.CTkButton(
            btn_frame,
            text="确认重置",
            command=lambda: self._do_reset(dialog),
            fg_color="orange"
        )
        confirm_btn.pack(side="right", padx=10)
    
    def _do_reset(self, dialog):
        """执行重置"""
        
        self._load_default_config()
        self.modified = True
        self._update_status("⚠️ 已重置为默认配置（未保存）", "orange")
        dialog.destroy()
    
    def _test_selector(self, key: str):
        """测试选择器"""
        
        selector = self.selector_entries[key].get().strip()
        
        if not selector:
            self._show_message("测试选择器", "选择器不能为空", "error")
            return
        
        # 在后台线程中运行测试
        import threading
        
        def run_test():
            import asyncio
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self._async_test_selector(key, selector))
            finally:
                loop.close()
        
        thread = threading.Thread(target=run_test, daemon=True)
        thread.start()
    
    async def _async_test_selector(self, key: str, selector: str):
        """异步测试选择器"""
        
        print(f"🧪 测试选择器: {key} = {selector}")
        
        browser = None
        
        try:
            from core.browser_automation import BrowserAutomation
            
            # 创建浏览器实例
            browser = BrowserAutomation(headless=False)
            
            # 启动浏览器
            await browser.start()
            print("✅ 浏览器已启动")
            
            # 打开闲鱼页面
            await browser.goto("https://2.taobao.com")
            print("✅ 已打开闲鱼页面")
            
            await asyncio.sleep(3)  # 等待页面加载
            
            # 测试选择器
            element = await browser.page.query_selector(selector)
            
            if element:
                # 高亮元素
                await browser.page.evaluate("""
                    (selector) => {
                        const el = document.querySelector(selector);
                        if (el) {
                            el.style.border = '3px solid red';
                            el.style.backgroundColor = 'yellow';
                            el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        }
                    }
                """, selector)
                
                # 获取元素信息
                element_text = await browser.page.evaluate("""
                    (selector) => {
                        const el = document.querySelector(selector);
                        if (el) {
                            return {
                                tag: el.tagName,
                                text: el.textContent?.trim().substring(0, 50) || '',
                                visible: el.offsetWidth > 0 && el.offsetHeight > 0
                            };
                        }
                        return null;
                    }
                """, selector)
                
                print(f"✅ 找到元素: {element_text}")
                
                # 显示成功消息
                success_msg = f"✅ 选择器有效！\n\n键: {key}\n选择器: {selector}\n\n元素信息:\n"
                success_msg += f"标签: {element_text.get('tag', 'N/A')}\n"
                success_msg += f"文本: {element_text.get('text', 'N/A')}\n"
                success_msg += f"可见: {'是' if element_text.get('visible') else '否'}\n\n"
                success_msg += "元素已在浏览器中高亮显示（红色边框+黄色背景）"
                
                self._show_message("测试成功", success_msg, "success")
                
            else:
                print(f"❌ 未找到元素")
                
                self._show_message(
                    "测试失败",
                    f"❌ 未找到元素\n\n键: {key}\n选择器: {selector}\n\n请检查选择器是否正确",
                    "error"
                )
        
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            
            self._show_message(
                "测试失败",
                f"❌ 测试出错\n\n键: {key}\n选择器: {selector}\n\n错误: {str(e)}",
                "error"
            )
        
        finally:
            # 关闭浏览器（延迟15秒，让用户看到高亮）
            if browser:
                await asyncio.sleep(15)
                await browser.stop()
                print("✅ 浏览器已关闭")
    
    def _test_all_selectors(self):
        """测试所有选择器"""
        
        # TODO: 实现批量测试逻辑
        print("测试所有选择器...")
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("测试所有选择器")
        dialog.geometry("600x500")
        
        # 测试结果列表
        result_frame = ctk.CTkScrollableFrame(dialog)
        result_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 显示待测试项
        for key, entry in self.selector_entries.items():
            selector = entry.get().strip()
            
            item_frame = ctk.CTkFrame(result_frame)
            item_frame.pack(fill="x", pady=5)
            
            status_label = ctk.CTkLabel(
                item_frame,
                text="⏳",
                font=ctk.CTkFont(size=16)
            )
            status_label.pack(side="left", padx=10, pady=5)
            
            key_label = ctk.CTkLabel(
                item_frame,
                text=f"{key}: {selector[:50]}...",
                font=ctk.CTkFont(size=12)
            )
            key_label.pack(side="left", fill="x", expand=True, padx=10, pady=5)
        
        # 提示
        hint_label = ctk.CTkLabel(
            dialog,
            text="批量测试功能开发中...",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        hint_label.pack(pady=10)
        
        # 关闭按钮
        close_btn = ctk.CTkButton(
            dialog,
            text="关闭",
            command=dialog.destroy
        )
        close_btn.pack(pady=10)
    
    def _import_config(self):
        """导入配置"""
        
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            title="选择配置文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 提取选择器
            if "selectors" in config_data:
                selectors = config_data["selectors"]
            else:
                selectors = config_data
            
            # 更新输入框
            for key, value in selectors.items():
                if key in self.selector_entries:
                    self.selector_entries[key].delete(0, "end")
                    self.selector_entries[key].insert(0, value)
            
            self.selectors = selectors
            self.modified = True
            self._update_status("✅ 配置已导入（未保存）", "green")
            
            print(f"✅ 从 {file_path} 导入配置")
            
        except Exception as e:
            print(f"❌ 导入配置失败: {e}")
            self._show_message("导入失败", f"无法导入配置: {e}", "error")
    
    def _export_config(self):
        """导出配置"""
        
        from tkinter import filedialog
        
        # 收集当前配置
        current_config = {}
        for key, entry in self.selector_entries.items():
            value = entry.get().strip()
            if value:
                current_config[key] = value
        
        # 选择保存路径
        file_path = filedialog.asksaveasfilename(
            title="导出配置",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
            initialfile=f"xianyu_selectors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        if not file_path:
            return
        
        try:
            # 添加元数据
            config_data = {
                "version": "1.0",
                "exported_at": datetime.now().isoformat(),
                "selectors": current_config
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self._update_status("✅ 配置已导出", "green")
            print(f"✅ 配置已导出到: {file_path}")
            
        except Exception as e:
            print(f"❌ 导出配置失败: {e}")
            self._show_message("导出失败", f"无法导出配置: {e}", "error")
    
    def _show_message(self, title: str, message: str, msg_type: str = "info"):
        """显示消息对话框"""
        
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("400x200")
        
        # 图标
        icons = {
            "info": "ℹ️",
            "success": "✅",
            "error": "❌",
            "warning": "⚠️"
        }
        icon = icons.get(msg_type, "ℹ️")
        
        label = ctk.CTkLabel(
            dialog,
            text=f"{icon} {message}",
            font=ctk.CTkFont(size=14),
            wraplength=350
        )
        label.pack(expand=True, padx=20)
        
        btn = ctk.CTkButton(
            dialog,
            text="确定",
            command=dialog.destroy
        )
        btn.pack(pady=20)


# 测试代码
if __name__ == "__main__":
    import sys
    import os
    
    # 添加项目根目录到路径
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
    
    # 创建测试应用
    app = ctk.CTk()
    app.geometry("1200x900")
    app.title("选择器配置测试")
    
    # 创建配置面板
    config_panel = SelectorConfigPanel(app)
    config_panel.pack(fill="both", expand=True)
    
    app.mainloop()

