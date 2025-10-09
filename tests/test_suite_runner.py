"""
测试套件运行器
运行所有测试并生成报告
"""

import sys
import os
import time
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_test_file(test_file: str) -> tuple:
    """运行单个测试文件"""
    
    print(f"\n▶️  运行: {test_file}")
    print("-" * 60)
    
    start_time = time.time()
    
    try:
        # 导入并运行测试
        module_name = test_file.replace(".py", "").replace("/", ".").replace("\\", ".")
        module = __import__(module_name, fromlist=[""])
        
        if hasattr(module, "run_all_tests"):
            result = module.run_all_tests()
        else:
            print("  ⚠️  未找到 run_all_tests() 函数")
            result = None
        
        elapsed = time.time() - start_time
        
        if result == 0 or result is None:
            print(f"✅ 通过 ({elapsed:.2f}秒)")
            return True, elapsed
        else:
            print(f"❌ 失败 ({elapsed:.2f}秒)")
            return False, elapsed
    
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ 错误: {e}")
        return False, elapsed


def generate_report(results: dict, output_file: str):
    """生成测试报告"""
    
    total = len(results)
    passed = sum(1 for r in results.values() if r["passed"])
    failed = total - passed
    total_time = sum(r["time"] for r in results.values())
    
    report = f"""
# JieDimension Toolkit - 测试报告

**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**版本**: v1.14.0

---

## 📊 测试结果总览

| 指标 | 数值 |
|------|------|
| 总测试文件 | {total} |
| 通过 | {passed} ✅ |
| 失败 | {failed} ❌ |
| 成功率 | {(passed/total*100):.1f}% |
| 总耗时 | {total_time:.2f}秒 |

---

## 📋 详细结果

"""
    
    for test_file, result in results.items():
        status = "✅ 通过" if result["passed"] else "❌ 失败"
        report += f"### {test_file}\n"
        report += f"- 状态: {status}\n"
        report += f"- 耗时: {result['time']:.2f}秒\n"
        report += "\n"
    
    report += """
---

## 🎯 总结

"""
    
    if failed == 0:
        report += "✅ **所有测试通过！** 代码质量良好，可以发布。\n"
    else:
        report += f"⚠️ **有 {failed} 个测试失败**，请检查并修复相关问题。\n"
    
    report += f"\n**测试完成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    # 保存报告
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\n📄 测试报告已生成: {output_file}")


def main():
    """主函数"""
    
    print("="*70)
    print("🧪 JieDimension Toolkit - 完整测试套件")
    print("="*70)
    
    # 测试文件列表
    test_files = [
        "tests/test_ollama.py",
        "tests/test_gemini.py",
        "tests/test_database.py",
        "tests/test_xianyu_plugin.py",
        "tests/test_charts.py",
        "tests/test_xiaohongshu.py",
        "tests/test_zhihu.py",
        "tests/test_bilibili.py",
        "tests/test_batch_publisher.py",
        "tests/test_api_integration.py",
        "tests/test_day18_features.py",
    ]
    
    # 检查文件是否存在
    existing_tests = []
    for test_file in test_files:
        if os.path.exists(test_file):
            existing_tests.append(test_file)
        else:
            print(f"⚠️  跳过不存在的测试: {test_file}")
    
    print(f"\n找到 {len(existing_tests)} 个测试文件")
    
    # 运行测试
    results = {}
    
    for test_file in existing_tests:
        passed, elapsed = run_test_file(test_file)
        results[test_file] = {
            "passed": passed,
            "time": elapsed
        }
    
    # 生成报告
    print("\n" + "="*70)
    print("📊 生成测试报告...")
    
    report_file = f"tests/测试报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    generate_report(results, report_file)
    
    # 显示总结
    total = len(results)
    passed = sum(1 for r in results.values() if r["passed"])
    failed = total - passed
    
    print("\n" + "="*70)
    print("📊 测试总结")
    print("="*70)
    print(f"总测试文件: {total}")
    print(f"通过: {passed} ✅")
    print(f"失败: {failed} ❌")
    print(f"成功率: {(passed/total*100):.1f}%")
    print("="*70)
    
    if failed == 0:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  有 {failed} 个测试失败")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

