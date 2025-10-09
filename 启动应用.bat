@echo off
chcp 65001 > nul
title JieDimension Toolkit v1.16.0
echo.
echo ========================================
echo   JieDimension Toolkit v1.16.0
echo   AI驱动的多平台内容发布工具
echo ========================================
echo.
echo 正在启动...
echo.

REM 启动程序
JieDimension-Toolkit.exe

REM 如果程序崩溃，暂停以查看错误
if errorlevel 1 (
    echo.
    echo ========================================
    echo   程序异常退出
    echo ========================================
    echo.
    echo 错误代码: %errorlevel%
    echo 请查看 data/logs/crash_*.txt 获取详细信息
    echo.
    pause
)
