"""
测试 Ollama 连接和 AI 引擎
Day 1 测试脚本
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.ai_engine import AIEngine, AIConfig, TaskComplexity


async def test_connection():
    """测试1: Ollama连接测试"""
    print("\n" + "="*60)
    print("🧪 测试1: Ollama连接测试")
    print("="*60)
    
    config = AIConfig(
        ollama_url="http://localhost:11434",
        ollama_model="deepseek-r1:1.5b"
    )
    
    engine = AIEngine(config)
    success = await engine.test_ollama_connection()
    
    if success:
        print("\n✅ 连接测试通过！")
        return True
    else:
        print("\n❌ 连接测试失败！")
        print("\n请检查：")
        print("  1. Ollama 是否已启动？（运行 'ollama serve'）")
        print("  2. 模型是否已下载？（运行 'ollama pull deepseek-r1:1.5b'）")
        return False


async def test_simple_generation():
    """测试2: 简单文本生成"""
    print("\n" + "="*60)
    print("🧪 测试2: 简单文本生成")
    print("="*60)
    
    engine = AIEngine()
    
    prompt = "用一句话介绍什么是人工智能。"
    
    print(f"\n📝 提示词: {prompt}")
    print("⏳ 生成中...")
    
    response = await engine.generate(
        prompt=prompt,
        complexity=TaskComplexity.SIMPLE,
        temperature=0.7
    )
    
    if response.success:
        print(f"\n✅ 生成成功！")
        print(f"⏱️  耗时: {response.latency:.2f}秒")
        print(f"📊 Tokens: {response.tokens}")
        print(f"\n💬 回复:\n{response.content}")
        return True
    else:
        print(f"\n❌ 生成失败: {response.error}")
        return False


async def test_title_optimization():
    """测试3: 闲鱼标题优化（实际应用场景）"""
    print("\n" + "="*60)
    print("🧪 测试3: 闲鱼标题优化")
    print("="*60)
    
    engine = AIEngine()
    
    original_title = "九成新iPhone 13 128G"
    
    system_prompt = """你是一个专业的电商标题优化助手。
优化要求：
1. 保留关键信息（品牌、型号、容量、成色）
2. 添加吸引人的形容词
3. 控制在30字以内
4. 只返回优化后的标题，不要解释"""
    
    prompt = f"请优化这个闲鱼标题：{original_title}"
    
    print(f"\n📝 原标题: {original_title}")
    print("⏳ 优化中...")
    
    response = await engine.generate(
        prompt=prompt,
        system_prompt=system_prompt,
        complexity=TaskComplexity.SIMPLE,
        temperature=0.8
    )
    
    if response.success:
        print(f"\n✅ 优化成功！")
        print(f"⏱️  耗时: {response.latency:.2f}秒")
        print(f"\n✨ 优化后标题:\n{response.content}")
        return True
    else:
        print(f"\n❌ 优化失败: {response.error}")
        return False


async def test_batch_processing():
    """测试4: 批量处理测试"""
    print("\n" + "="*60)
    print("🧪 测试4: 批量处理测试")
    print("="*60)
    
    engine = AIEngine()
    
    titles = [
        "MacBook Pro 2020款",
        "小米手环7",
        "索尼降噪耳机"
    ]
    
    system_prompt = """你是电商标题优化助手。要求：
1. 添加吸引眼球的词汇
2. 保持简洁
3. 只返回标题"""
    
    print(f"\n📋 待优化标题数量: {len(titles)}")
    
    results = []
    for i, title in enumerate(titles, 1):
        print(f"\n[{i}/{len(titles)}] 处理: {title}")
        
        response = await engine.generate(
            prompt=f"优化标题：{title}",
            system_prompt=system_prompt,
            complexity=TaskComplexity.SIMPLE
        )
        
        if response.success:
            print(f"  ✓ 成功 ({response.latency:.2f}s)")
            results.append({
                'original': title,
                'optimized': response.content.strip(),
                'latency': response.latency
            })
        else:
            print(f"  ✗ 失败: {response.error}")
    
    # 显示结果
    print("\n" + "-"*60)
    print("📊 批量处理结果:")
    print("-"*60)
    for i, result in enumerate(results, 1):
        print(f"\n{i}. 原标题: {result['original']}")
        print(f"   优化后: {result['optimized']}")
        print(f"   耗时: {result['latency']:.2f}s")
    
    # 统计
    if results:
        avg_latency = sum(r['latency'] for r in results) / len(results)
        print(f"\n✅ 成功: {len(results)}/{len(titles)}")
        print(f"⏱️  平均耗时: {avg_latency:.2f}秒")
        return True
    else:
        print("\n❌ 全部失败")
        return False


async def test_stats():
    """测试5: 统计信息显示"""
    print("\n" + "="*60)
    print("🧪 测试5: 查看引擎统计")
    print("="*60)
    
    engine = AIEngine()
    
    # 进行几次调用
    for i in range(3):
        await engine.generate(
            prompt=f"测试消息 {i+1}",
            complexity=TaskComplexity.SIMPLE
        )
    
    # 显示统计
    engine.print_stats()
    return True


async def run_all_tests():
    """运行所有测试"""
    print("\n")
    print("="*60)
    print("🚀 JieDimension Toolkit - AI引擎测试套件")
    print("="*60)
    print("📅 Day 1: Ollama连接与基础功能测试")
    print(f"🤖 模型: deepseek-r1:1.5b")
    print("="*60)
    
    tests = [
        ("连接测试", test_connection),
        ("简单生成", test_simple_generation),
        ("标题优化", test_title_optimization),
        ("批量处理", test_batch_processing),
        ("统计信息", test_stats),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ 测试异常: {e}")
            results.append((test_name, False))
        
        # 测试间隔
        await asyncio.sleep(0.5)
    
    # 最终报告
    print("\n" + "="*60)
    print("📋 测试报告")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} - {test_name}")
    
    print("-"*60)
    print(f"总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！AI引擎工作正常！")
    else:
        print(f"\n⚠️ 有 {total - passed} 个测试失败，请检查")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    # 运行所有测试
    asyncio.run(run_all_tests())

