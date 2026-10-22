"""
JieDimension Toolkit - 版本更新检查器
支持从GitHub检查和下载更新
"""

import requests
import json
import os
import sys
import webbrowser
import zipfile
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Callable
from packaging import version
import logging

logger = logging.getLogger(__name__)

# 当前版本
CURRENT_VERSION = "1.17.2"

# GitHub仓库信息
GITHUB_REPO = "Jieice/JieDimension-Toolkit"  # 格式: owner/repo
GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
GITHUB_RELEASES = f"https://github.com/{GITHUB_REPO}/releases"

# 更新相关配置
UPDATE_TEMP_DIR = "temp_update"
UPDATE_SCRIPT_NAME = "update_installer.bat"


class UpdateChecker:
    """版本更新检查器"""
    
    def __init__(self):
        self.current_version = CURRENT_VERSION
        self.latest_info = None
    
    def check_for_updates(self, timeout: int = 5) -> Optional[Dict]:
        """
        检查是否有新版本
        
        Args:
            timeout: 请求超时时间
            
        Returns:
            如果有新版本，返回版本信息字典，否则返回None
        """
        try:
            logger.info(f"🔍 检查更新... 当前版本: {self.current_version}")
            
            # 从GitHub API获取最新版本
            response = requests.get(GITHUB_API, timeout=timeout)
            
            if response.status_code != 200:
                logger.warning(f"⚠️ 无法获取版本信息: HTTP {response.status_code}")
                return None
            
            data = response.json()
            
            # 解析版本信息
            latest_version = data.get("tag_name", "").lstrip("v")
            release_name = data.get("name", "")
            release_notes = data.get("body", "")
            download_url = data.get("html_url", GITHUB_RELEASES)
            published_at = data.get("published_at", "")
            
            # 获取下载链接（Windows exe）
            assets = data.get("assets", [])
            exe_download = None
            for asset in assets:
                if asset["name"].endswith(".exe") or asset["name"].endswith(".zip"):
                    exe_download = asset["browser_download_url"]
                    break
            
            logger.info(f"📦 最新版本: {latest_version}")
            
            # 比较版本
            if version.parse(latest_version) > version.parse(self.current_version):
                logger.info("✨ 发现新版本！")
                
                self.latest_info = {
                    "version": latest_version,
                    "name": release_name,
                    "notes": release_notes,
                    "url": download_url,
                    "download": exe_download,
                    "date": published_at,
                    "current": self.current_version
                }
                
                return self.latest_info
            else:
                logger.info("✅ 当前已是最新版本")
                return None
                
        except requests.exceptions.Timeout:
            logger.warning("⚠️ 检查更新超时")
            return None
        except Exception as e:
            logger.error(f"❌ 检查更新失败: {str(e)}")
            return None
    
    def open_download_page(self):
        """打开下载页面"""
        if self.latest_info and self.latest_info.get("url"):
            webbrowser.open(self.latest_info["url"])
        else:
            webbrowser.open(GITHUB_RELEASES)
    
    def get_update_message(self) -> str:
        """获取更新提示消息"""
        if not self.latest_info:
            return "当前已是最新版本"
        
        info = self.latest_info
        message = f"""发现新版本！

当前版本: v{info['current']}
最新版本: v{info['version']}

更新内容:
{info['notes'][:200]}...

是否前往下载？"""
        
        return message
    
    def download_update(self, save_path: Optional[str] = None, progress_callback: Optional[Callable] = None) -> Optional[str]:
        """
        下载更新文件
        
        Args:
            save_path: 保存路径，如果为None则保存到临时目录
            progress_callback: 进度回调函数 (downloaded, total)
            
        Returns:
            下载文件的完整路径，失败返回None
        """
        if not self.latest_info or not self.latest_info.get("download"):
            logger.error("❌ 没有可下载的更新文件")
            return None
        
        try:
            download_url = self.latest_info["download"]
            filename = download_url.split("/")[-1]
            
            if save_path is None:
                temp_dir = tempfile.gettempdir()
                save_path = os.path.join(temp_dir, filename)
            
            logger.info(f"📥 开始下载更新: {filename}")
            
            # 下载文件
            response = requests.get(download_url, stream=True, timeout=60)
            total_size = int(response.headers.get('content-length', 0))
            
            with open(save_path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # 进度回调
                        if progress_callback:
                            progress_callback(downloaded, total_size)
            
            logger.info(f"✅ 下载完成: {save_path}")
            return save_path
            
        except Exception as e:
            logger.error(f"❌ 下载失败: {str(e)}")
            return None
    
    def install_update(self, zip_path: str) -> bool:
        """
        安装更新（自动解压、替换、重启）
        
        Args:
            zip_path: 下载的zip文件路径
            
        Returns:
            是否成功启动更新流程
        """
        try:
            # 获取当前exe路径
            if getattr(sys, 'frozen', False):
                current_exe = sys.executable
                current_dir = os.path.dirname(current_exe)
            else:
                # 开发模式
                current_dir = os.getcwd()
                current_exe = os.path.join(current_dir, "JieDimension-Toolkit.exe")
            
            # 创建临时解压目录
            temp_dir = os.path.join(tempfile.gettempdir(), UPDATE_TEMP_DIR)
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)
            
            logger.info(f"📦 解压更新包到: {temp_dir}")
            
            # 解压zip文件
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # 创建更新脚本
            script_path = os.path.join(temp_dir, UPDATE_SCRIPT_NAME)
            self._create_update_script(script_path, temp_dir, current_dir, current_exe)
            
            logger.info(f"🚀 启动更新程序...")
            
            # 启动更新脚本
            subprocess.Popen(
                [script_path],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                shell=True
            )
            
            # 给脚本时间启动
            import time
            time.sleep(0.5)
            
            logger.info("✅ 更新程序已启动，主程序即将退出...")
            return True
            
        except Exception as e:
            logger.error(f"❌ 安装更新失败: {str(e)}")
            return False
    
    def _create_update_script(self, script_path: str, temp_dir: str, target_dir: str, exe_path: str):
        """
        创建Windows批处理更新脚本
        
        Args:
            script_path: 脚本保存路径
            temp_dir: 临时文件目录
            target_dir: 目标安装目录
            exe_path: 主程序exe路径
        """
        # 批处理脚本内容
        script_content = f'''@echo off
chcp 65001 > nul
title JieDimension Toolkit - 自动更新程序

echo ========================================
echo    JieDimension Toolkit 更新程序
echo ========================================
echo.
echo 正在准备更新...
echo.

REM 等待主程序退出（最多30秒）
set /a count=0
:wait_loop
tasklist | find /i "JieDimension-Toolkit.exe" > nul
if not errorlevel 1 (
    if %count% GEQ 30 (
        echo 警告：主程序未能正常退出，继续更新...
        goto start_update
    )
    timeout /t 1 /nobreak > nul
    set /a count+=1
    goto wait_loop
)

:start_update
echo [OK] 主程序已退出
echo.
echo 正在备份旧版本...

REM 备份旧版本（含用户数据，回滚时才能完整还原）
if exist "{target_dir}\\backup" rmdir /s /q "{target_dir}\\backup"
mkdir "{target_dir}\\backup" 2>nul
if exist "{exe_path}" (
    copy "{exe_path}" "{target_dir}\\backup\\" > nul 2>&1
    echo [OK] 旧版本程序已备份
) else (
    echo [!] 未找到旧版本exe文件
)
if exist "{target_dir}\\data" (
    xcopy /E /Y /I "{target_dir}\\data" "{target_dir}\\backup\\data\\" > nul 2>&1
    echo [OK] 数据目录已备份
)
if exist "{target_dir}\\config" (
    xcopy /E /Y /I "{target_dir}\\config" "{target_dir}\\backup\\config\\" > nul 2>&1
    echo [OK] 配置目录已备份
)
echo.

echo 正在复制新文件...
REM 复制新文件（根据解压后的目录结构）
xcopy /E /Y /I "{temp_dir}\\*" "{target_dir}\\" > nul 2>&1
if errorlevel 1 (
    echo [X] 复制文件失败！
    echo.
    echo 正在恢复备份...
    if exist "{target_dir}\\backup\\JieDimension-Toolkit.exe" (
        copy "{target_dir}\\backup\\JieDimension-Toolkit.exe" "{target_dir}\\" > nul
        echo [OK] 程序已回滚
    )
    if exist "{target_dir}\\backup\\data" (
        xcopy /E /Y /I "{target_dir}\\backup\\data" "{target_dir}\\data\\" > nul 2>&1
        echo [OK] 数据已回滚
    )
    if exist "{target_dir}\\backup\\config" (
        xcopy /E /Y /I "{target_dir}\\backup\\config" "{target_dir}\\config\\" > nul 2>&1
        echo [OK] 配置已回滚
    )
    goto error_end
)
echo [OK] 新文件复制完成
echo.

echo 正在清理临时文件...
REM 清理临时文件
rmdir /s /q "{temp_dir}" > nul 2>&1
echo [OK] 清理完成
echo.

echo ========================================
echo    更新完成！即将重启应用...
echo ========================================
echo.
timeout /t 2 /nobreak > nul

REM 重启应用
start "" "{exe_path}"
echo [OK] 应用已重启
echo.

REM 3秒后自动关闭
timeout /t 3 /nobreak > nul
exit

:error_end
echo.
echo 按任意键退出...
pause > nul
exit
'''
        
        # bat 由 cmd.exe 以本地代码页(中文系统为 GBK)执行，所以必须按 GBK 落盘。
        # errors='replace' 是保险：万一以后模板里混进 GBK 表示不了的字符（比如 emoji），
        # 也只是那几个字符变成 '?'，而不是整个更新流程崩掉。
        with open(script_path, 'w', encoding='gbk', errors='replace') as f:
            f.write(script_content)
    
    def auto_update(self, progress_callback: Optional[Callable] = None) -> bool:
        """
        一键自动更新（检查→下载→安装→重启）
        
        Args:
            progress_callback: 进度回调函数
            
        Returns:
            是否成功启动更新
        """
        try:
            # 1. 检查更新
            logger.info("🔍 检查更新...")
            if not self.latest_info:
                self.check_for_updates()
            
            if not self.latest_info:
                logger.info("✅ 当前已是最新版本")
                return False
            
            # 2. 下载更新
            logger.info(f"📥 下载新版本 v{self.latest_info['version']}...")
            zip_path = self.download_update(progress_callback=progress_callback)
            
            if not zip_path:
                logger.error("❌ 下载失败")
                return False
            
            # 3. 安装更新
            logger.info("🔧 安装更新...")
            success = self.install_update(zip_path)
            
            return success
            
        except Exception as e:
            logger.error(f"❌ 自动更新失败: {str(e)}")
            return False


def check_updates_on_startup(silent: bool = False) -> Optional[Dict]:
    """
    启动时检查更新（便捷函数）
    
    Args:
        silent: 是否静默检查（不输出日志）
        
    Returns:
        版本信息或None
    """
    checker = UpdateChecker()
    
    try:
        return checker.check_for_updates(timeout=3)
    except:
        if not silent:
            logger.debug("启动时检查更新失败")
        return None


# 测试代码
if __name__ == "__main__":
    print("="*60)
    print("🔍 JieDimension Toolkit 更新检查器测试")
    print("="*60)
    print()
    
    checker = UpdateChecker()
    
    print(f"📌 当前版本: v{checker.current_version}")
    print(f"🌐 仓库地址: {GITHUB_REPO}")
    print()
    
    print("⏳ 正在检查更新...")
    update_info = checker.check_for_updates()
    
    if update_info:
        print()
        print("✨ " + "="*58)
        print(f"   发现新版本: v{update_info['version']}")
        print("="*60)
        print()
        print(f"📝 版本名称: {update_info['name']}")
        print(f"📅 发布日期: {update_info['date']}")
        print()
        print("📋 更新内容:")
        print("-"*60)
        print(update_info['notes'][:500])
        print()
        print(f"🔗 下载地址: {update_info['url']}")
        if update_info['download']:
            print(f"📦 直接下载: {update_info['download']}")
    else:
        print()
        print("✅ 当前已是最新版本！")
    
    print()
    print("="*60)

