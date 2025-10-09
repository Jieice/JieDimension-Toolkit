# tests/test_api_config_ui.py

"""
测试API配置界面
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_api_config_import():
    """测试API配置面板导入"""
    
    print("="*60)
    print("🧪 测试1：API配置面板导入")
    print("="*60)
    
    try:
        from ui.api_config_panel import APIConfigPanel
        print("✅ APIConfigPanel 导入成功")
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False


def test_auth_manager_integration():
    """测试认证管理器集成"""
    
    print("\n" + "="*60)
    print("🧪 测试2：认证管理器集成")
    print("="*60)
    
    try:
        from core.auth_manager import AuthManager
        import asyncio
        
        async def test():
            auth = AuthManager()
            await auth.load_credentials()
            platforms = await auth.list_platforms()
            print(f"✅ 认证管理器工作正常，已配置 {len(platforms)} 个平台")
            return True
        
        return asyncio.run(test())
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_browser_automation_import():
    """测试浏览器自动化导入"""
    
    print("\n" + "="*60)
    print("🧪 测试3：浏览器自动化导入")
    print("="*60)
    
    try:
        from core.browser_automation import BrowserAutomation, XianyuAutomation
        print("✅ BrowserAutomation 导入成功")
        print("✅ XianyuAutomation 导入成功")
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False


def test_bilibili_api_client():
    """测试B站API客户端"""
    
    print("\n" + "="*60)
    print("🧪 测试4：B站API客户端")
    print("="*60)
    
    try:
        from plugins.bilibili.api_client import BilibiliAPIClient
        print("✅ BilibiliAPIClient 导入成功")
        
        # 创建客户端实例
        client = BilibiliAPIClient(
            access_key="test_key",
            secret_key="test_secret"
        )
        print("✅ 客户端实例化成功")
        return True
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_main_window_integration():
    """测试主窗口集成"""
    
    print("\n" + "="*60)
    print("🧪 测试5：主窗口集成检查")
    print("="*60)
    
    try:
        from ui.main_window import MainWindow
        
        # 检查是否有show_api_config方法
        if hasattr(MainWindow, 'show_api_config'):
            print("✅ show_api_config 方法存在")
            return True
        else:
            print("❌ show_api_config 方法不存在")
            return False
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    
    print("\n" + "🚀"*30)
    print("JieDimension Toolkit - API配置界面测试套件")
    print("Day 13: GUI API配置功能测试")
    print("🚀"*30 + "\n")
    
    tests = [
        ("API配置面板导入", test_api_config_import),
        ("认证管理器集成", test_auth_manager_integration),
        ("浏览器自动化导入", test_browser_automation_import),
        ("B站API客户端", test_bilibili_api_client),
        ("主窗口集成", test_main_window_integration),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {name} 执行异常: {e}")
            results.append(False)
    
    # 总结
    passed = sum(results)
    total = len(results)
    
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    print(f"✅ 通过: {passed}/{total}")
    print(f"❌ 失败: {total-passed}/{total}")
    print(f"📈 通过率: {passed/total*100:.0f}%")
    
    if passed == total:
        print("\n🎉 所有测试通过！API配置界面已就绪！")
    else:
        print(f"\n⚠️  有 {total-passed} 个测试失败，请检查")
    
    print("="*60)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
