# JieDimension Toolkit - 自动更新GitHub Release
# 使用GitHub CLI (gh) 自动上传新版本

param(
    [string]$Version = "v1.17.1",
    [string]$ZipFile = "release\JieDimension-Toolkit-v1.17.1-Final-Windows.zip"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GitHub Release 自动更新工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查GitHub CLI是否安装
Write-Host "🔍 检查GitHub CLI..." -ForegroundColor Yellow
$ghInstalled = Get-Command gh -ErrorAction SilentlyContinue

if (-not $ghInstalled) {
    Write-Host "❌ 未安装GitHub CLI" -ForegroundColor Red
    Write-Host ""
    Write-Host "请安装GitHub CLI:" -ForegroundColor Yellow
    Write-Host "  1. 访问: https://cli.github.com/" -ForegroundColor Gray
    Write-Host "  2. 下载并安装" -ForegroundColor Gray
    Write-Host "  3. 运行: gh auth login" -ForegroundColor Gray
    Write-Host ""
    Write-Host "或者手动更新:" -ForegroundColor Yellow
    Write-Host "  1. 访问: https://github.com/Jieice/JieDimension-Toolkit/releases/tag/$Version" -ForegroundColor Gray
    Write-Host "  2. 点击 Edit release" -ForegroundColor Gray
    Write-Host "  3. 删除旧zip，上传新zip: $ZipFile" -ForegroundColor Gray
    exit 1
}

Write-Host "✅ GitHub CLI已安装" -ForegroundColor Green
Write-Host ""

# 检查zip文件是否存在
Write-Host "📦 检查发布包..." -ForegroundColor Yellow
if (-not (Test-Path $ZipFile)) {
    Write-Host "❌ 找不到文件: $ZipFile" -ForegroundColor Red
    exit 1
}

$fileSize = [math]::Round((Get-Item $ZipFile).Length / 1MB, 2)
Write-Host "✅ 发布包: $ZipFile ($fileSize MB)" -ForegroundColor Green
Write-Host ""

# 确认操作
Write-Host "⚠️  即将更新GitHub Release:" -ForegroundColor Yellow
Write-Host "   仓库: Jieice/JieDimension-Toolkit" -ForegroundColor Gray
Write-Host "   版本: $Version" -ForegroundColor Gray
Write-Host "   文件: $ZipFile" -ForegroundColor Gray
Write-Host ""
$confirm = Read-Host "是否继续? (y/n)"

if ($confirm -ne 'y' -and $confirm -ne 'Y') {
    Write-Host "❌ 已取消" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "🚀 开始更新..." -ForegroundColor Cyan
Write-Host ""

# 删除Release中的旧asset
Write-Host "🗑️  删除旧文件..." -ForegroundColor Yellow
gh release delete-asset $Version "JieDimension-Toolkit-v1.17.1-Beta-Windows.zip" -R Jieice/JieDimension-Toolkit --yes 2>$null
Write-Host "✅ 旧文件已删除（如果存在）" -ForegroundColor Green
Write-Host ""

# 上传新asset
Write-Host "📤 上传新文件..." -ForegroundColor Yellow
gh release upload $Version $ZipFile -R Jieice/JieDimension-Toolkit --clobber

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✅ Release更新成功！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "🔗 查看Release:" -ForegroundColor Cyan
    Write-Host "   https://github.com/Jieice/JieDimension-Toolkit/releases/tag/$Version" -ForegroundColor Gray
    Write-Host ""
}
else {
    Write-Host ""
    Write-Host "❌ 上传失败！" -ForegroundColor Red
    Write-Host "请手动更新或检查网络连接" -ForegroundColor Yellow
}

Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

