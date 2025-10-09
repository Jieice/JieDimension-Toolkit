"""
闲鱼插件功能测试
测试Excel导入、标题优化、批量处理等功能
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from plugins.xianyu.data_importer import DataImporter
from core.ai_engine import AIEngine, TaskComplexity
from core.database import Database


async def test_excel_import():
    """测试Excel导入功能"""
    print("\n" + "=" * 60)
    print("🧪 测试1: Excel文件导入")
    print("=" * 60)
    
    importer = DataImporter()
    db = Database()
    await db.connect()
    
    # 测试文件路径
    test_file = "data/test_products.xlsx"
    
    try:
        # 导入数据
        print(f"📂 导入文件: {test_file}")
        products = importer.import_from_excel(test_file)
        
        print(f"✅ 成功导入 {len(products)} 个商品")
        
        # 显示前2个商品
        for i, product in enumerate(products[:2], 1):
            print(f"\n📦 商品 {i}:")
            print(f"   标题: {product.get('title', 'N/A')}")
            print(f"   价格: ¥{product.get('price', 0)}")
            print(f"   分类: {product.get('category', 'N/A')}")
        
        await db.close()
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        await db.close()
        return False


async def test_title_optimization():
    """测试标题优化功能"""
    print("\n" + "=" * 60)
    print("🧪 测试2: 闲鱼标题优化")
    print("=" * 60)
    
    engine = AIEngine()
    
    test_titles = [
        "iPhone 13 128G",
        "MacBook Pro 2020"
    ]
    
    print(f"📝 待优化标题: {len(test_titles)} 个\n")
    
    success_count = 0
    
    for i, title in enumerate(test_titles, 1):
        print(f"[{i}/{len(test_titles)}] 原标题: {title}")
        
        try:
            # 优化标题
            response = await engine.generate(
                prompt=f"优化这个闲鱼标题：{title}",
                system_prompt="你是闲鱼标题优化助手，要求：1) 控制在30字以内 2) 突出卖点 3) 吸引眼球 4) 只返回优化后的标题，不要其他内容",
                complexity=TaskComplexity.SIMPLE
            )
            
            if response.success:
                # 清理输出，只保留标题部分
                optimized = response.content.strip()
                # 移除<think>标签内容
                if '<think>' in optimized:
                    optimized = optimized.split('</think>')[-1].strip()
                
                print(f"   优化后: {optimized[:50]}...")
                print(f"   耗时: {response.latency:.2f}s")
                print(f"   提供商: {response.provider}\n")
                success_count += 1
            else:
                print(f"   ❌ 优化失败: {response.error}\n")
                
        except Exception as e:
            print(f"   ❌ 错误: {e}\n")
    
    print(f"✅ 成功优化 {success_count}/{len(test_titles)} 个标题")
    return success_count == len(test_titles)


async def test_batch_import_and_optimize():
    """测试批量导入并优化"""
    print("\n" + "=" * 60)
    print("🧪 测试3: 批量导入+优化（完整流程）")
    print("=" * 60)
    
    importer = DataImporter()
    engine = AIEngine()
    db = Database()
    await db.connect()
    
    try:
        # 1. 导入Excel
        print("📂 步骤1: 导入Excel数据")
        products = importer.import_from_excel("data/test_products.xlsx")
        print(f"   ✅ 导入 {len(products)} 个商品")
        
        # 2. 优化第一个商品的标题
        if products:
            print(f"\n🎯 步骤2: 优化第一个商品")
            product = products[0]
            original_title = product.get('title', '')
            print(f"   原标题: {original_title}")
            
            response = await engine.generate(
                prompt=f"优化闲鱼标题：{original_title}",
                system_prompt="你是闲鱼标题优化助手，控制在30字以内，只返回优化后的标题",
                complexity=TaskComplexity.SIMPLE
            )
            
            if response.success:
                optimized = response.content.strip()
                if '<think>' in optimized:
                    optimized = optimized.split('</think>')[-1].strip()
                
                print(f"   优化后: {optimized[:50]}...")
                print(f"   耗时: {response.latency:.2f}s")
        
        # 3. 保存到数据库
        print(f"\n💾 步骤3: 保存到数据库")
        saved_count = await db.insert_products(products[:2])  # 只保存前2个作为测试
        print(f"   ✅ 已保存 {saved_count} 个商品到数据库")
        
        # 4. 验证统计
        print(f"\n📊 步骤4: 验证数据统计")
        total_products = await db.count_products()
        xianyu_products = await db.count_products(platform='xianyu')
        print(f"   总商品数: {total_products}")
        print(f"   闲鱼商品: {xianyu_products}")
        
        await db.close()
        print(f"\n✅ 完整流程测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        await db.close()
        return False


async def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("🚀 闲鱼插件测试套件")
    print("=" * 60)
    print("📅 测试Excel导入、标题优化、批量处理")
    print("=" * 60)
    
    results = []
    
    # 测试1: Excel导入
    try:
        result = await test_excel_import()
        results.append(("Excel导入", result))
    except Exception as e:
        print(f"❌ Excel导入测试失败: {e}")
        results.append(("Excel导入", False))
    
    # 测试2: 标题优化
    try:
        result = await test_title_optimization()
        results.append(("标题优化", result))
    except Exception as e:
        print(f"❌ 标题优化测试失败: {e}")
        results.append(("标题优化", False))
    
    # 测试3: 完整流程
    try:
        result = await test_batch_import_and_optimize()
        results.append(("完整流程", result))
    except Exception as e:
        print(f"❌ 完整流程测试失败: {e}")
        results.append(("完整流程", False))
    
    # 打印总结
    print("\n" + "=" * 60)
    print("📋 测试报告")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {test_name}")
    
    print("-" * 60)
    print(f"通过率: {passed}/{total} ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 所有测试通过！闲鱼插件功能正常！")
    else:
        print(f"\n⚠️ 有 {total - passed} 个测试失败")
    
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

