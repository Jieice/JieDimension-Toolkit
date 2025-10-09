"""
测试智能调度功能（不需要Gemini API密钥）
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.ai_engine import AIEngine, TaskComplexity, AIConfig


async def test_provider_selection():
    """测试提供商选择逻辑"""
    print("=" * 60)
    print("测试: 智能调度 - 提供商选择逻辑")
    print("=" * 60)
    
    engine = AIEngine()
    
    # 测试不同复杂度的提供商选择
    complexities = [
        TaskComplexity.SIMPLE,
        TaskComplexity.MEDIUM,
        TaskComplexity.COMPLEX,
        TaskComplexity.ADVANCED
    ]
    
    for complexity in complexities:
        providers = engine._select_providers(complexity)
        print(f"\n{complexity.name}:")
        print(f"  提供商顺序: {[p.value for p in providers]}")
        
        if complexity == TaskComplexity.SIMPLE:
            assert len(providers) == 1 and providers[0].value == "ollama", "SIMPLE应该只用Ollama"
            print("  ✅ 策略正确: 仅使用本地Ollama（最快）")
        
        elif complexity == TaskComplexity.MEDIUM:
            assert providers[0].value == "ollama", "MEDIUM应该优先Ollama"
            print("  ✅ 策略正确: Ollama优先，Gemini降级")
        
        elif complexity == TaskComplexity.COMPLEX:
            # 如果Gemini可用，应该优先；否则用Ollama
            if engine.gemini_model:
                assert providers[0].value == "gemini", "COMPLEX应该优先Gemini"
                print("  ✅ 策略正确: Gemini优先（高质量）")
            else:
                assert providers[0].value == "ollama", "Gemini不可用时用Ollama"
                print("  ⚠️ Gemini未配置，使用Ollama降级")
    
    print("\n" + "=" * 60)
    print("✅ 提供商选择逻辑测试通过！")
    return True


async def test_actual_calls():
    """测试实际调用（使用Ollama）"""
    print("\n" + "=" * 60)
    print("测试: 不同复杂度的实际AI调用")
    print("=" * 60)
    
    engine = AIEngine()
    
    test_cases = [
        (TaskComplexity.SIMPLE, "优化标题：iPhone 15"),
        (TaskComplexity.MEDIUM, "为智能手表写一段产品描述"),
    ]
    
    for complexity, prompt in test_cases:
        print(f"\n🎯 {complexity.name} 任务")
        print(f"   提示词: {prompt}")
        
        response = await engine.generate(
            prompt=prompt,
            complexity=complexity,
            temperature=0.7
        )
        
        if response.success:
            print(f"   ✅ 成功 - 使用: {response.provider}")
            print(f"   耗时: {response.latency:.2f}s")
            content_preview = response.content[:60].replace('\n', ' ')
            print(f"   响应: {content_preview}...")
        else:
            print(f"   ❌ 失败: {response.error}")
            return False
    
    print("\n" + "=" * 60)
    print("✅ 实际调用测试通过！")
    return True


async def test_statistics():
    """测试统计功能"""
    print("\n" + "=" * 60)
    print("测试: 统计功能")
    print("=" * 60)
    
    engine = AIEngine()
    
    # 进行几次调用
    for i in range(3):
        await engine.generate(
            prompt=f"测试 {i+1}",
            complexity=TaskComplexity.SIMPLE
        )
    
    # 获取统计
    stats = engine.get_statistics()
    
    print("\n📊 统计信息:")
    for provider, data in stats.items():
        if data['total_calls'] > 0:
            print(f"\n{provider.upper()}:")
            print(f"  总调用: {data['total_calls']}")
            print(f"  成功: {data['success_calls']}")
            print(f"  失败: {data['failed_calls']}")
            print(f"  成功率: {data['success_calls']/data['total_calls']*100:.1f}%")
            print(f"  平均延迟: {data['avg_latency']:.2f}s")
    
    print("\n" + "=" * 60)
    print("✅ 统计功能测试通过！")
    return True


async def main():
    """运行所有测试"""
    print("\n🚀 智能调度功能测试")
    print("=" * 60)
    print("说明: 本测试仅使用Ollama，不需要Gemini API密钥")
    print("=" * 60)
    print()
    
    tests = [
        ("提供商选择逻辑", test_provider_selection),
        ("实际AI调用", test_actual_calls),
        ("统计功能", test_statistics),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            print(f"\n▶️ 运行: {name}")
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            results.append((name, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\n通过率: {passed}/{total} ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 所有测试通过！智能调度功能正常！")
    else:
        print("\n⚠️ 部分测试失败")


if __name__ == "__main__":
    asyncio.run(main())

