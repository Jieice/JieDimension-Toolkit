"""
测试 Gemini API 集成
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.ai_engine import AIEngine, TaskComplexity, AIConfig
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


async def test_gemini_simple():
    """测试Gemini简单任务"""
    print("=" * 60)
    print("测试 1: Gemini简单文本生成")
    print("=" * 60)
    
    # 创建AI引擎（会自动从环境变量加载GEMINI_API_KEY）
    engine = AIEngine()
    
    if not engine.gemini_model:
        print("⚠️ Gemini未配置，跳过测试")
        print("请在.env文件中配置GEMINI_API_KEY")
        return False
    
    prompt = "用一句话介绍人工智能。"
    
    response = await engine._call_gemini(
        prompt=prompt,
        temperature=0.7
    )
    
    if response.success:
        print(f"✅ 测试通过")
        print(f"   - 提供商: {response.provider}")
        print(f"   - 模型: {response.model}")
        print(f"   - 耗时: {response.latency:.2f}s")
        print(f"   - 响应: {response.content[:100]}...")
        return True
    else:
        print(f"❌ 测试失败: {response.error}")
        return False


async def test_smart_scheduling():
    """测试智能调度"""
    print("\n" + "=" * 60)
    print("测试 2: 智能调度算法")
    print("=" * 60)
    
    engine = AIEngine()
    
    # 测试不同复杂度的任务
    test_cases = [
        (TaskComplexity.SIMPLE, "优化这个标题：iPhone 15"),
        (TaskComplexity.MEDIUM, "为一款智能手表写一段产品描述"),
        (TaskComplexity.COMPLEX, "写一篇关于AI发展趋势的分析文章"),
    ]
    
    results = []
    
    for complexity, prompt in test_cases:
        print(f"\n🎯 测试 {complexity.name} 任务")
        print(f"   提示词: {prompt}")
        
        response = await engine.generate(
            prompt=prompt,
            complexity=complexity,
            temperature=0.7
        )
        
        if response.success:
            print(f"✅ 成功 - 使用: {response.provider}")
            print(f"   耗时: {response.latency:.2f}s")
            print(f"   响应: {response.content[:80]}...")
            results.append(True)
        else:
            print(f"❌ 失败: {response.error}")
            results.append(False)
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n📊 测试结果: {sum(results)}/{len(results)} 通过 ({success_rate:.0f}%)")
    
    return all(results)


async def test_fallback():
    """测试降级策略"""
    print("\n" + "=" * 60)
    print("测试 3: 降级策略")
    print("=" * 60)
    
    # 测试当Ollama失败时，是否会降级到Gemini
    config = AIConfig(
        ollama_url="http://localhost:99999",  # 错误的地址，会失败
        fallback_enabled=True
    )
    
    engine = AIEngine(config)
    
    if not engine.gemini_model:
        print("⚠️ Gemini未配置，无法测试降级")
        return False
    
    prompt = "说一句Hello"
    
    response = await engine.generate(
        prompt=prompt,
        complexity=TaskComplexity.MEDIUM,
        temperature=0.7
    )
    
    if response.success and response.provider == "gemini":
        print(f"✅ 降级成功 - 从Ollama降级到Gemini")
        print(f"   响应: {response.content}")
        return True
    else:
        print(f"❌ 降级失败")
        return False


async def test_statistics():
    """测试统计功能"""
    print("\n" + "=" * 60)
    print("测试 4: 统计功能")
    print("=" * 60)
    
    engine = AIEngine()
    
    # 进行几次调用
    prompts = [
        "Hello",
        "你好",
        "Bonjour"
    ]
    
    for prompt in prompts:
        await engine.generate(prompt, complexity=TaskComplexity.SIMPLE)
    
    # 获取统计
    stats = engine.get_statistics()
    
    print(f"\n📊 统计信息:")
    for provider, data in stats.items():
        if data['total_calls'] > 0:
            print(f"\n{provider.upper()}:")
            print(f"  - 总调用: {data['total_calls']}")
            print(f"  - 成功: {data['success_calls']}")
            print(f"  - 失败: {data['failed_calls']}")
            print(f"  - 平均延迟: {data['avg_latency']:.2f}s")
    
    return True


async def main():
    """运行所有测试"""
    print("🚀 开始测试 Gemini API 集成")
    print()
    
    tests = [
        test_gemini_simple,
        test_smart_scheduling,
        test_fallback,
        test_statistics,
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            results.append(False)
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    
    total = len(results)
    passed = sum(1 for r in results if r)
    
    print(f"总测试数: {total}")
    print(f"通过: {passed}")
    print(f"失败: {total - passed}")
    print(f"通过率: {passed/total*100:.0f}%")
    
    if passed == total:
        print("\n✅ 所有测试通过！")
    else:
        print("\n⚠️ 部分测试失败")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

