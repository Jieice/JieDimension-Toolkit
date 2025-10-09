"""
JieDimension Toolkit - Claude API 集成测试
测试Claude API的连接和功能
Author: JieDimension Studio
Date: 2025-10-09 (Day 7)
"""

import asyncio
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ai_engine import AIEngine, AIConfig, TaskComplexity


async def test_claude():
    """测试Claude API"""
    
    print("=" * 60)
    print("🧪 Claude API 集成测试")
    print("=" * 60)
    
    # 从环境变量获取API密钥
    claude_api_key = os.getenv('CLAUDE_API_KEY')
    
    if not claude_api_key:
        print("\n⚠️ 警告：CLAUDE_API_KEY 环境变量未设置")
        print("跳过Claude测试")
        return
    
    # 创建配置
    config = AIConfig(
        claude_api_key=claude_api_key,
        claude_model="claude-3-5-sonnet-20241022"
    )
    
    # 创建引擎
    engine = AIEngine(config)
    
    # 测试1：简单文本生成
    print("\n" + "-" * 60)
    print("测试1: Claude简单文本生成")
    print("-" * 60)
    
    response = await engine._call_claude(
        prompt="用一句话介绍Claude AI",
        temperature=0.7
    )
    
    if response.success:
        print(f"✅ 测试通过")
        print(f"响应内容: {response.content[:100]}...")
        print(f"耗时: {response.latency:.2f}秒")
        print(f"Tokens: {response.tokens}")
    else:
        print(f"❌ 测试失败: {response.error}")
    
    # 测试2：闲鱼标题优化
    print("\n" + "-" * 60)
    print("测试2: Claude闲鱼标题优化")
    print("-" * 60)
    
    response = await engine._call_claude(
        prompt="优化这个闲鱼标题：二手iPhone 13 128G",
        system_prompt="你是专业的电商标题优化助手",
        temperature=0.7
    )
    
    if response.success:
        print(f"✅ 测试通过")
        print(f"优化后标题: {response.content}")
        print(f"耗时: {response.latency:.2f}秒")
    else:
        print(f"❌ 测试失败: {response.error}")
    
    # 测试3：复杂任务（长文本生成）
    print("\n" + "-" * 60)
    print("测试3: Claude复杂任务 - 商品描述生成")
    print("-" * 60)
    
    response = await engine._call_claude(
        prompt="""
为以下商品生成一个专业且吸引人的闲鱼描述：

商品：MacBook Pro 14寸 2021款
配置：M1 Pro芯片，16GB内存，512GB存储
价格：¥9999
状态：9成新，无划痕，保护完好

要求：
1. 突出性能优势
2. 强调性价比
3. 描述使用体验
4. 200字左右
        """,
        system_prompt="你是专业的电商文案专家",
        temperature=0.8
    )
    
    if response.success:
        print(f"✅ 测试通过")
        print(f"生成的描述:\n{response.content}")
        print(f"耗时: {response.latency:.2f}秒")
    else:
        print(f"❌ 测试失败: {response.error}")
    
    # 测试4：智能调度 - COMPLEX任务应该优先使用Claude
    print("\n" + "-" * 60)
    print("测试4: 智能调度测试 - COMPLEX任务")
    print("-" * 60)
    
    response = await engine.generate(
        prompt="生成一篇关于AI发展的100字短文",
        complexity=TaskComplexity.COMPLEX
    )
    
    if response.success:
        print(f"✅ 测试通过")
        print(f"使用的提供商: {response.provider}")
        print(f"生成内容: {response.content[:100]}...")
        print(f"耗时: {response.latency:.2f}秒")
        
        if response.provider == "claude":
            print("✅ 正确：COMPLEX任务优先使用了Claude")
        else:
            print(f"⚠️ 注意：使用了 {response.provider}（可能是Claude不可用）")
    else:
        print(f"❌ 测试失败: {response.error}")
    
    # 输出统计
    print("\n" + "=" * 60)
    print("📊 测试统计")
    print("=" * 60)
    engine.print_stats()
    
    print("\n✨ Claude测试完成！")


if __name__ == "__main__":
    asyncio.run(test_claude())

