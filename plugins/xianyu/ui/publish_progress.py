"""
JieDimension Toolkit - 发布进度展示组件
实时显示闲鱼发布的9个步骤进度
Version: 1.0.0 (Day 16)
"""

import customtkinter as ctk
from typing import Optional, Dict, List
from enum import Enum


class StepStatus(Enum):
    """步骤状态枚举"""
    PENDING = "pending"      # 等待中
    RUNNING = "running"      # 进行中
    SUCCESS = "success"      # 成功
    FAILED = "failed"        # 失败
    SKIPPED = "skipped"      # 跳过


class PublishStep:
    """发布步骤数据类"""
    
    def __init__(self, index: int, name: str, description: str = ""):
        self.index = index
        self.name = name
        self.description = description
        self.status = StepStatus.PENDING
        self.message = ""
        self.elapsed_time = 0.0


class PublishProgressPanel(ctk.CTkFrame):
    """发布进度面板 - 显示详细的发布步骤"""
    
    # 定义9个发布步骤
    PUBLISH_STEPS = [
        {"name": "打开发布页面", "desc": "导航到闲鱼发布页面"},
        {"name": "上传图片", "desc": "上传商品图片"},
        {"name": "填写标题", "desc": "填写商品标题"},
        {"name": "填写价格", "desc": "填写商品价格"},
        {"name": "填写描述", "desc": "填写商品描述"},
        {"name": "选择分类", "desc": "选择商品分类"},
        {"name": "提交发布", "desc": "点击发布按钮"},
        {"name": "等待完成", "desc": "等待发布处理"},
        {"name": "验证结果", "desc": "验证发布成功"}
    ]
    
    # 状态图标
    STATUS_ICONS = {
        StepStatus.PENDING: "⏸️",
        StepStatus.RUNNING: "🔄",
        StepStatus.SUCCESS: "✅",
        StepStatus.FAILED: "❌",
        StepStatus.SKIPPED: "⏭️"
    }
    
    # 状态颜色
    STATUS_COLORS = {
        StepStatus.PENDING: "gray60",
        StepStatus.RUNNING: "blue",
        StepStatus.SUCCESS: "green",
        StepStatus.FAILED: "red",
        StepStatus.SKIPPED: "orange"
    }
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # 配置
        self.configure(fg_color=("gray90", "gray25"), corner_radius=10)
        self.grid_columnconfigure(0, weight=1)
        
        # 步骤数据
        self.steps: List[PublishStep] = []
        self.step_widgets: Dict[int, Dict] = {}
        
        # 创建界面
        self._create_header()
        self._create_steps()
        
        # 初始化步骤
        self.reset()
    
    def _create_header(self):
        """创建顶部标题"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # 标题
        title_label = ctk.CTkLabel(
            header_frame,
            text="📊 发布进度",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        # 总体状态
        self.overall_status_label = ctk.CTkLabel(
            header_frame,
            text="准备就绪",
            font=ctk.CTkFont(size=12),
            text_color="gray60",
            anchor="e"
        )
        self.overall_status_label.grid(row=0, column=1, sticky="e")
    
    def _create_steps(self):
        """创建步骤列表"""
        # 步骤容器
        steps_container = ctk.CTkFrame(self, fg_color="transparent")
        steps_container.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 15))
        steps_container.grid_columnconfigure(1, weight=1)
        
        for idx, step_info in enumerate(self.PUBLISH_STEPS):
            # 创建步骤对象
            step = PublishStep(idx, step_info["name"], step_info["desc"])
            self.steps.append(step)
            
            # 步骤框架
            step_frame = ctk.CTkFrame(
                steps_container,
                fg_color=("gray85", "gray20"),
                corner_radius=8,
                height=50
            )
            step_frame.grid(row=idx, column=0, sticky="ew", padx=5, pady=2)
            step_frame.grid_columnconfigure(2, weight=1)
            step_frame.grid_propagate(False)  # 固定高度
            
            # 步骤图标
            icon_label = ctk.CTkLabel(
                step_frame,
                text=self.STATUS_ICONS[StepStatus.PENDING],
                font=ctk.CTkFont(size=18),
                width=40
            )
            icon_label.grid(row=0, column=0, padx=(10, 5), pady=10)
            
            # 步骤序号
            number_label = ctk.CTkLabel(
                step_frame,
                text=f"{idx + 1}.",
                font=ctk.CTkFont(size=12, weight="bold"),
                width=25,
                text_color="gray60"
            )
            number_label.grid(row=0, column=1, padx=(0, 5), pady=10)
            
            # 步骤名称
            name_label = ctk.CTkLabel(
                step_frame,
                text=step_info["name"],
                font=ctk.CTkFont(size=13),
                anchor="w"
            )
            name_label.grid(row=0, column=2, sticky="w", padx=5, pady=10)
            
            # 状态消息（初始隐藏）
            message_label = ctk.CTkLabel(
                step_frame,
                text="",
                font=ctk.CTkFont(size=11),
                text_color="gray50",
                anchor="e"
            )
            message_label.grid(row=0, column=3, sticky="e", padx=(5, 10), pady=10)
            
            # 保存控件引用
            self.step_widgets[idx] = {
                "frame": step_frame,
                "icon": icon_label,
                "name": name_label,
                "message": message_label
            }
    
    def reset(self):
        """重置所有步骤状态"""
        for step in self.steps:
            step.status = StepStatus.PENDING
            step.message = ""
            step.elapsed_time = 0.0
        
        # 更新UI
        for idx, widgets in self.step_widgets.items():
            self._update_step_ui(idx)
        
        self.overall_status_label.configure(
            text="准备就绪",
            text_color="gray60"
        )
    
    def update_step(
        self,
        step_index: int,
        status: StepStatus,
        message: str = "",
        elapsed_time: float = 0.0
    ):
        """
        更新步骤状态
        
        Args:
            step_index: 步骤索引（0-8）
            status: 步骤状态
            message: 状态消息
            elapsed_time: 耗时（秒）
        """
        if step_index < 0 or step_index >= len(self.steps):
            return
        
        step = self.steps[step_index]
        step.status = status
        step.message = message
        step.elapsed_time = elapsed_time
        
        # 更新UI
        self._update_step_ui(step_index)
        self._update_overall_status()
    
    def _update_step_ui(self, step_index: int):
        """更新步骤UI显示"""
        if step_index not in self.step_widgets:
            return
        
        step = self.steps[step_index]
        widgets = self.step_widgets[step_index]
        
        # 更新图标
        widgets["icon"].configure(text=self.STATUS_ICONS[step.status])
        
        # 更新颜色
        color = self.STATUS_COLORS[step.status]
        widgets["name"].configure(text_color=color)
        
        # 更新消息
        if step.message:
            if step.elapsed_time > 0:
                message_text = f"{step.message} ({step.elapsed_time:.1f}s)"
            else:
                message_text = step.message
            widgets["message"].configure(text=message_text, text_color=color)
        else:
            widgets["message"].configure(text="")
        
        # 高亮当前进行中的步骤
        if step.status == StepStatus.RUNNING:
            widgets["frame"].configure(fg_color=("lightblue", "darkblue"))
        else:
            widgets["frame"].configure(fg_color=("gray85", "gray20"))
    
    def _update_overall_status(self):
        """更新总体状态"""
        # 统计各状态数量
        pending_count = sum(1 for s in self.steps if s.status == StepStatus.PENDING)
        running_count = sum(1 for s in self.steps if s.status == StepStatus.RUNNING)
        success_count = sum(1 for s in self.steps if s.status == StepStatus.SUCCESS)
        failed_count = sum(1 for s in self.steps if s.status == StepStatus.FAILED)
        
        total = len(self.steps)
        
        # 更新总体状态
        if failed_count > 0:
            self.overall_status_label.configure(
                text=f"❌ 失败 ({failed_count}个步骤失败)",
                text_color="red"
            )
        elif running_count > 0:
            self.overall_status_label.configure(
                text=f"🔄 进行中... ({success_count}/{total})",
                text_color="blue"
            )
        elif success_count == total:
            self.overall_status_label.configure(
                text=f"✅ 全部完成 ({success_count}/{total})",
                text_color="green"
            )
        elif pending_count == total:
            self.overall_status_label.configure(
                text="准备就绪",
                text_color="gray60"
            )
        else:
            self.overall_status_label.configure(
                text=f"进度: {success_count}/{total}",
                text_color="gray60"
            )
    
    def start_publish(self):
        """开始发布（重置并显示准备状态）"""
        self.reset()
        self.overall_status_label.configure(
            text="🚀 开始发布...",
            text_color="blue"
        )
    
    def finish_publish(self, success: bool, message: str = ""):
        """
        完成发布
        
        Args:
            success: 是否成功
            message: 完成消息
        """
        if success:
            self.overall_status_label.configure(
                text=f"✅ 发布成功！{message}",
                text_color="green"
            )
        else:
            self.overall_status_label.configure(
                text=f"❌ 发布失败：{message}",
                text_color="red"
            )


# ===== 测试函数 =====

def main():
    """测试发布进度面板"""
    import time
    import random
    
    root = ctk.CTk()
    root.title("发布进度测试")
    root.geometry("600x700")
    ctk.set_appearance_mode("dark")
    
    # 创建进度面板
    progress_panel = PublishProgressPanel(root)
    progress_panel.pack(fill="both", expand=True, padx=20, pady=20)
    
    # 测试按钮
    def test_progress():
        """模拟发布流程"""
        progress_panel.start_publish()
        
        def run_steps():
            for idx in range(len(PublishProgressPanel.PUBLISH_STEPS)):
                # 更新为进行中
                root.after(
                    idx * 1000,
                    lambda i=idx: progress_panel.update_step(
                        i,
                        StepStatus.RUNNING,
                        "处理中..."
                    )
                )
                
                # 随机成功或失败
                is_success = random.random() > 0.1  # 90%成功率
                
                if is_success:
                    root.after(
                        (idx + 1) * 1000 - 200,
                        lambda i=idx: progress_panel.update_step(
                            i,
                            StepStatus.SUCCESS,
                            "完成",
                            round(random.uniform(0.5, 2.0), 1)
                        )
                    )
                else:
                    root.after(
                        (idx + 1) * 1000 - 200,
                        lambda i=idx: progress_panel.update_step(
                            i,
                            StepStatus.FAILED,
                            "操作失败",
                            round(random.uniform(0.5, 1.5), 1)
                        )
                    )
                    # 失败后停止
                    root.after(
                        (idx + 1) * 1000,
                        lambda: progress_panel.finish_publish(False, "步骤执行失败")
                    )
                    return
            
            # 全部成功
            root.after(
                len(PublishProgressPanel.PUBLISH_STEPS) * 1000 + 200,
                lambda: progress_panel.finish_publish(True, "")
            )
        
        run_steps()
    
    btn_frame = ctk.CTkFrame(root)
    btn_frame.pack(fill="x", padx=20, pady=(0, 20))
    
    test_btn = ctk.CTkButton(
        btn_frame,
        text="🧪 测试发布流程",
        command=test_progress,
        height=40,
        font=ctk.CTkFont(size=14, weight="bold")
    )
    test_btn.pack(side="left", padx=5)
    
    reset_btn = ctk.CTkButton(
        btn_frame,
        text="🔄 重置",
        command=progress_panel.reset,
        height=40,
        font=ctk.CTkFont(size=14),
        fg_color="gray50",
        hover_color="gray40"
    )
    reset_btn.pack(side="left", padx=5)
    
    root.mainloop()


if __name__ == "__main__":
    main()

