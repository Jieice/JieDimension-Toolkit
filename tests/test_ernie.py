"""
JieDimension Toolkit - 文心一言 API 集成测试
测试百度文心一言API的连接和功能
Author: JieDimension Studio
Date: 2025-10-09 (Day 7)
"""

import asyncio
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ai_engine import AIEngine, AIConfig, TaskComplexity


async def test_ernie():
    """测试文心一言API"""
    
    print("=" * 60)
    print("🧪 文心一言 API 集成测试")
    print("=" * 60)
    
    # 从环境变量获取API密钥
    ernie_api_key = os.getenv('ERNIE_API_KEY')
    ernie_secret_key = os.getenv('ERNIE_SECRET_KEY')
    
    if not ernie_api_key or not ernie_secret_key:
        print("\n⚠️ 警告：ERNIE_API_KEY 或 ERNIE_SECRET_KEY 环境变量未设置")
        print("跳过文心一言测试")
        print("\n获取API密钥：")
        print("1. 访问 https://cloud.baidu.com/product/wenxinworkshop")
        print("2. 注册并创建应用")
        print("3. 获取 API Key 和 Secret Key")
        return
    
    # 创建配置
    config = AIConfig(
        ernie_api_key=ernie_api_key,
        ernie_secret_key=ernie_secret_key,
        ernie_model="ernie-4.0-8k"
    )
    
    # 创建引擎
    engine = AIEngine(config)
    
    # 测试0：获取access_token
    print("\n" + "-" * 60)
    print("测试0: 获取文心一言access_token")
    print("-" * 60)
    
    access_token = await engine._get_ernie_access_token()
    
    if access_token:
        print(f"✅ access_token获取成功")
        print(f"Token前10位: {access_token[:10]}...")
    else:
        print(f"❌ access_token获取失败")
        return
    
    # 测试1：简单文本生成
    print("\n" + "-" * 60)
    print("测试1: 文心一言简单文本生成")
    print("-" * 60)
    
    response = await engine._call_ernie(
        prompt="用一句话介绍文心一言",
        temperature=0.7
    )
    
    if response.success:
        print(f"✅ 测试通过")
        print(f"响应内容: {response.content}")
        print(f"耗时: {response.latency:.2f}秒")
        print(f"Tokens: {response.tokens}")
    else:
        print(f"❌ 测试失败: {response.error}")
    
    # 测试2：闲鱼标题优化（中文优势）
    print("\n" + "-" * 60)
    print("测试2: 文心一言闲鱼标题优化（中文任务）")
    print("-" * 60)
    
    response = await engine._call_ernie(
        prompt="优化这个闲鱼标题，让它更有吸引力：九成新小米13 Pro 256G 黑色",
        system_prompt="你是专业的中文电商标题优化专家，擅长闲鱼平台标题优化",
        temperature=0.8
    )
    
    if response.success:
        print(f"✅ 测试通过")
        print(f"优化后标题: {response.content}")
        print(f"耗时: {response.latency:.2f}秒")
    else:
        print(f"❌ 测试失败: {response.error}")
    
    # 测试3：中文长文本生成
    print("\n" + "-" * 60)
    print("测试3: 文心一言长文本生成 - 小红书风格笔记")
    print("-" * 60)
    
    response = await engine._call_ernie(
        prompt="""
生成一篇小红书风格的种草笔记：

主题：居家好物推荐 - 智能扫地机器人
要点：
- 解放双手
- 清扫效果好
- 智能路径规划
- 性价比高

要求：
1. 口语化、亲切
2. 使用适当emoji
3. 150-200字
4. 引发共鸣
        """,
        system_prompt="你是小红书爆款笔记写手，擅长种草内容创作",
        temperature=0.9
    )
    
    if response.success:
        print(f"✅ 测试通过")
        print(f"生成的笔记:\n{response.content}")
        print(f"耗时: {response.latency:.2f}秒")
    else:
        print(f"❌ 测试失败: {response.error}")
    
    # 测试4：智能调度 - 中文MEDIUM任务
    print("\n" + "-" * 60)
    print("测试4: 智能调度测试 - 中文MEDIUM任务")
    print("-" * 60)
    
    response = await engine.generate(
        prompt="写一句欢迎语，用于闲鱼店铺介绍",
        complexity=TaskComplexity.MEDIUM,
        system_prompt="你是友好的客服"
    )
    
    if response.success:
        print(f"✅ 测试通过")
        print(f"使用的提供商: {response.provider}")
        print(f"生成内容: {response.content}")
        print(f"耗时: {response.latency:.2f}秒")
    else:
        print(f"❌ 测试失败: {response.error}")
    
    # 测试5：对比测试 - 同一任务用不同提供商
    print("\n" + "-" * 60)
    print("测试5: 多提供商对比 - 相同任务质量对比")
    print("-" * 60)
    
    prompt = "用20字描述：什么是人工智能？"
    
    # 文心一言
    response_ernie = await engine._call_ernie(prompt=prompt)
    print(f"文心一言: {response_ernie.content if response_ernie.success else '失败'}")
    
    # 如果有Gemini
    if engine.gemini_model:
        response_gemini = await engine._call_gemini(prompt=prompt)
        print(f"Gemini: {response_gemini.content if response_gemini.success else '失败'}")
    
    # 输出统计
    print("\n" + "=" * 60)
    print("📊 测试统计")
    print("=" * 60)
    engine.print_stats()
    
    print("\n✨ 文心一言测试完成！")


if __name__ == "__main__":
    asyncio.run(test_ernie())

