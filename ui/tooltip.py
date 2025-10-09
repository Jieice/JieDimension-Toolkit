"""
JieDimension Toolkit - Tooltip提示组件
为UI元素添加悬停提示
"""

import customtkinter as ctk


class ToolTip:
    """工具提示类"""
    
    def __init__(self, widget, text: str, delay: int = 500):
        """
        初始化Tooltip
        
        Args:
            widget: 绑定的控件
            text: 提示文本
            delay: 延迟显示时间（毫秒）
        """
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tip_window = None
        self.id = None
        
        # 绑定事件
        self.widget.bind("<Enter>", self._on_enter)
        self.widget.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event=None):
        """鼠标进入"""
        self._schedule()
    
    def _on_leave(self, event=None):
        """鼠标离开"""
        self._unschedule()
        self._hide()
    
    def _schedule(self):
        """计划显示"""
        self._unschedule()
        self.id = self.widget.after(self.delay, self._show)
    
    def _unschedule(self):
        """取消计划"""
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None
    
    def _show(self):
        """显示提示"""
        if self.tip_window:
            return
        
        # 获取控件位置
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        # 创建提示窗口
        self.tip_window = ctk.CTkToplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry(f"+{x}+{y}")
        
        # 提示标签
        label = ctk.CTkLabel(
            self.tip_window,
            text=self.text,
            fg_color=("yellow", "gray20"),
            text_color=("black", "white"),
            corner_radius=6,
            padx=10,
            pady=5
        )
        label.pack()
    
    def _hide(self):
        """隐藏提示"""
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


def create_tooltip(widget, text: str, delay: int = 500):
    """
    便捷函数：为控件创建tooltip
    
    Args:
        widget: 控件
        text: 提示文本
        delay: 延迟（毫秒）
    
    Returns:
        ToolTip实例
    """
    return ToolTip(widget, text, delay)

