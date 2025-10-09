@echo off
echo ========================================
echo   JieDimension Toolkit - Git 初始化
echo ========================================
echo.
echo 请先在GitHub创建仓库：JieDimension-Toolkit
echo 然后将下面的 YOUR_USERNAME 替换为你的GitHub用户名
echo.
pause
echo.
echo 正在初始化Git...
git init
git add .
git commit -m \"Initial release: JieDimension Toolkit v1.17.1 Beta\"
git branch -M main
echo.
echo 请输入你的GitHub用户名并回车（例如：JieDimension）:
set /p username=
git remote add origin https://github.com/%username%/JieDimension-Toolkit.git
echo.
echo 正在推送到GitHub...
git push -u origin main
echo.
echo ========================================
echo   Git推送完成！
echo   下一步：访问GitHub创建Release
echo ========================================
pause
