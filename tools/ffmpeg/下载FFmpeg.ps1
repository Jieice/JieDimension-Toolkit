# 自动下载FFmpeg便携版

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  FFmpeg 自动下载脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$downloadUrl = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
$zipFile = "ffmpeg.zip"
$extractPath = "."

Write-Host "📥 开始下载FFmpeg..." -ForegroundColor Yellow
Write-Host "URL: $downloadUrl" -ForegroundColor Gray
Write-Host "大小: 约100MB，请耐心等待..." -ForegroundColor Gray
Write-Host ""

try {
    # 下载
    Invoke-WebRequest -Uri $downloadUrl -OutFile $zipFile -UseBasicParsing
    
    Write-Host "✅ 下载完成！" -ForegroundColor Green
    Write-Host ""
    Write-Host "📦 解压中..." -ForegroundColor Yellow
    
    # 解压
    Expand-Archive -Path $zipFile -DestinationPath $extractPath -Force
    
    # 查找ffmpeg.exe
    $ffmpegExe = Get-ChildItem -Path $extractPath -Filter "ffmpeg.exe" -Recurse | Select-Object -First 1
    
    if ($ffmpegExe) {
        Write-Host "✅ FFmpeg安装成功！" -ForegroundColor Green
        Write-Host "位置: $($ffmpegExe.FullName)" -ForegroundColor Gray
        
        # 测试
        & $ffmpegExe.FullName -version | Select-Object -First 1
        
        # 清理zip
        Remove-Item $zipFile
        
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  安装完成！可以生成视频了！" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
    } else {
        Write-Host "❌ 未找到ffmpeg.exe" -ForegroundColor Red
    }
    
} catch {
    Write-Host ""
    Write-Host "❌ 下载失败：$($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "请手动下载:" -ForegroundColor Yellow
    Write-Host "1. 访问: https://www.gyan.dev/ffmpeg/builds/" -ForegroundColor Gray
    Write-Host "2. 下载: ffmpeg-release-essentials.zip" -ForegroundColor Gray
    Write-Host "3. 解压到此目录" -ForegroundColor Gray
}

Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

