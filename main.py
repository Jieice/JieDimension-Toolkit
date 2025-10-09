"""
JieDimension Toolkit - 主程序入口
AI驱动的多平台内容发布工具
Version: 1.17.2
"""

import sys
import os
import asyncio
import traceback
from pathlib import Path
from datetime import datetime

# ==================== 路径处理 ====================
# PyInstaller打包后的路径处理

def get_base_path():
    """
    获取程序基础路径
    
    Returns:
        Path: 程序基础路径（数据文件存放位置）
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller打包后：exe所在目录
        return Path(sys.executable).parent
    else:
        # 开发环境：main.py所在目录
        return Path(__file__).parent


def get_resource_path(relative_path):
    """
    获取资源文件路径（打包在exe内的文件）
    
    Args:
        relative_path: 相对路径
        
    Returns:
        Path: 绝对路径
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller打包后：临时解压目录
        base_path = Path(sys._MEIPASS)
    else:
        # 开发环境：main.py所在目录
        base_path = Path(__file__).parent
    
    return base_path / relative_path


# 设置全局路径变量
BASE_DIR = get_base_path()
RESOURCE_DIR = get_resource_path("")

# 添加项目根目录到路径
sys.path.insert(0, str(BASE_DIR))
if str(RESOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(RESOURCE_DIR))

# ==================== Windows异步支持 ====================
# 修复Windows下asyncio事件循环问题

if sys.platform == 'win32':
    # Windows下使用WindowsSelectorEventLoopPolicy
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# ==================== 异常处理 ====================

def write_crash_log(exception_info):
    """
    写入崩溃日志
    
    Args:
        exception_info: 异常信息
    """
    try:
        log_dir = BASE_DIR / "data" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"crash_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("JieDimension Toolkit - 崩溃日志\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"版本: v1.17.1\n")
            f.write(f"Python: {sys.version}\n")
            f.write(f"平台: {sys.platform}\n")
            f.write(f"工作目录: {os.getcwd()}\n")
            f.write(f"基础路径: {BASE_DIR}\n")
            f.write(f"资源路径: {RESOURCE_DIR}\n")
            f.write(f"打包模式: {'是' if getattr(sys, 'frozen', False) else '否'}\n")
            f.write("\n" + "=" * 60 + "\n")
            f.write("异常信息:\n")
            f.write("=" * 60 + "\n\n")
            f.write(exception_info)
        
        print(f"\n💾 崩溃日志已保存: {log_file}")
        return log_file
        
    except Exception as e:
        print(f"⚠️  无法写入崩溃日志: {e}")
        return None


# ==================== 主函数 ====================

def main():
    """主函数 - 启动GUI"""
    
    print("=" * 60)
    print("🚀 JieDimension Toolkit v1.17.2 - 热更新测试版")
    print("=" * 60)
    print()
    
    # 显示路径信息（调试用）
    print(f"📂 基础路径: {BASE_DIR}")
    print(f"📦 资源路径: {RESOURCE_DIR}")
    print(f"🔧 打包模式: {'是' if getattr(sys, 'frozen', False) else '否'}")
    print()
    
    print("📦 正在初始化GUI...")
    
    try:
        # 确保必要的目录存在
        (BASE_DIR / "data").mkdir(exist_ok=True)
        (BASE_DIR / "data" / "logs").mkdir(exist_ok=True)
        (BASE_DIR / "data" / "temp").mkdir(exist_ok=True)
        (BASE_DIR / "config").mkdir(exist_ok=True)
        
        print("✅ 目录检查完成")
        
        # 导入并启动GUI
        from ui.main_window import MainWindow
        
        print("✅ GUI已加载")
        print("🎨 正在启动主窗口...")
        print()
        
        # 创建并运行主窗口
        app = MainWindow()
        app.mainloop()
        
        print("\n✅ 程序正常退出")
        
    except ImportError as e:
        error_msg = f"导入错误: {e}\n\n"
        error_msg += "请确保已安装所有依赖:\n"
        error_msg += "  pip install -r requirements.txt\n"
        
        print(f"\n❌ {error_msg}")
        
        # 写入崩溃日志
        write_crash_log(f"{error_msg}\n{traceback.format_exc()}")
        
        input("\n按回车键退出...")
        sys.exit(1)
        
    except Exception as e:
        error_msg = f"启动失败: {e}"
        print(f"\n❌ {error_msg}")
        
        # 获取完整异常信息
        exception_info = traceback.format_exc()
        print("\n异常详情:")
        print(exception_info)
        
        # 写入崩溃日志
        log_file = write_crash_log(exception_info)
        
        if log_file:
            print(f"\n请将日志文件发送给开发者: {log_file}")
        
        input("\n按回车键退出...")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 未捕获的异常: {e}")
        print(traceback.format_exc())
        
        # 最后的保险
        write_crash_log(traceback.format_exc())
        
        input("\n按回车键退出...")
        sys.exit(1)

