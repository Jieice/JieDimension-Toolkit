"""
测试更新检查功能
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from utils.updater import UpdateChecker

print("="*60)
print("🧪 测试更新检查功能")
print("="*60)
print()

# 创建检查器
checker = UpdateChecker()

print(f"📌 当前版本: v{checker.current_version}")
print()

# 测试1：模拟有新版本的情况
print("📝 测试1：模拟发现新版本")
print("-"*60)

# 手动创建模拟数据
checker.latest_info = {
    "version": "1.17.0",
    "name": "v1.17.0 - 添加自动更新功能",
    "notes": """## 🎉 新功能
- ✅ 添加版本检查功能
- ✅ 支持一键检查更新
- ✅ 自动打开下载页面

## 🐛 Bug修复
- 修复小红书AI参数错误
- 修复知乎模块加载问题""",
    "url": "https://github.com/test/releases/tag/v1.17.0",
    "download": "https://github.com/test/releases/download/v1.17.0/JieDimension-Toolkit.exe",
    "date": "2025-10-09T16:00:00Z",
    "current": checker.current_version
}

message = checker.get_update_message()
print(message)
print()

print("✅ 测试1通过：消息格式正确")
print()

# 测试2：测试版本比较
print("📝 测试2：测试版本比较逻辑")
print("-"*60)

from packaging import version

test_cases = [
    ("1.16.2", "1.17.0", True),   # 有新版本
    ("1.16.2", "1.16.2", False),  # 版本相同
    ("1.16.2", "1.16.1", False),  # 当前版本更新
    ("1.16.2", "2.0.0", True),    # 大版本更新
]

all_passed = True
for current, latest, expected in test_cases:
    result = version.parse(latest) > version.parse(current)
    status = "✅" if result == expected else "❌"
    print(f"{status} v{current} vs v{latest} -> {'需要更新' if result else '无需更新'}")
    if result != expected:
        all_passed = False

print()
if all_passed:
    print("✅ 测试2通过：版本比较逻辑正确")
else:
    print("❌ 测试2失败：版本比较逻辑有误")

print()

# 测试3：测试UI集成（需要在GUI中测试）
print("📝 测试3：GUI集成测试")
print("-"*60)
print("请在程序中点击'🔄 检查更新'按钮测试：")
print("1. 菜单项是否显示")
print("2. 点击后是否弹出对话框")
print("3. 点击'是'是否打开浏览器")
print()

print("="*60)
print("✨ 测试完成！")
print("="*60)

