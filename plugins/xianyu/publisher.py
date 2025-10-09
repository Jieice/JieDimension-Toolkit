"""
JieDimension Toolkit - 闲鱼发布器
支持批量优化商品标题、描述，并发布到闲鱼
Version: 1.0.0
"""

import asyncio
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import logging

# 导入AI引擎
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.ai_engine import AIEngine, TaskComplexity
from plugins.xianyu.retry_handler import RetryHandler, ErrorClassifier

logger = logging.getLogger(__name__)


class XianyuPublisher:
    """闲鱼发布器"""
    
    def __init__(self, max_retries: int = 3):
        """
        初始化发布器
        
        Args:
            max_retries: 最大重试次数
        """
        self.ai_engine = AIEngine()
        self.retry_handler = RetryHandler(max_retries=max_retries)
    
    async def optimize_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        AI优化单个商品
        
        Args:
            product: 商品数据
            
        Returns:
            优化后的商品数据
        """
        logger.info(f"🤖 优化商品: {product['title']}")
        
        optimized = product.copy()
        
        # 1. 优化标题
        optimized_title = await self._optimize_title(
            product['title'],
            product['category'],
            product['price']
        )
        
        optimized["title_original"] = product["title"]
        optimized["title"] = optimized_title
        
        # 2. 生成或优化描述
        if not product.get("description") or len(product.get("description", "").strip()) == 0:
            # 没有描述，AI生成
            logger.info("  - 生成商品描述...")
            description = await self._generate_description(
                optimized["title"],
                product["category"],
                product["price"]
            )
            optimized["description"] = description
        else:
            # 已有描述，优化
            logger.info("  - 优化商品描述...")
            description = await self._optimize_description(
                product["description"]
            )
            optimized["description"] = description
        
        logger.info(f"✅ 优化完成")
        logger.info(f"   原标题: {product['title']}")
        logger.info(f"   新标题: {optimized['title']}")
        
        return optimized
    
    async def _optimize_title(
        self,
        title: str,
        category: str,
        price: float
    ) -> str:
        """
        优化商品标题
        
        Args:
            title: 原始标题
            category: 分类
            price: 价格
            
        Returns:
            优化后的标题
        """
        system_prompt = """你是一个专业的闲鱼商品标题优化专家。
优化要求：
1. 保留核心关键信息（品牌、型号、容量等）
2. 添加吸引眼球的词汇
3. 控制在30字以内
4. 只返回优化后的标题，不要解释
5. 不要加引号"""
        
        prompt = f"""请优化这个闲鱼商品标题：

原标题：{title}
分类：{category}
价格：¥{price}

优化后的标题："""
        
        response = await self.ai_engine.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            complexity=TaskComplexity.SIMPLE,
            temperature=0.8
        )
        
        if response.success:
            # 清理输出
            optimized = response.content.strip()
            optimized = optimized.strip('"').strip("'").strip('【】')
            
            # 确保长度不超过50字
            if len(optimized) > 50:
                optimized = optimized[:50]
            
            return optimized
        else:
            logger.warning(f"⚠️ 标题优化失败，使用原标题: {response.error}")
            return title
    
    async def _generate_description(
        self,
        title: str,
        category: str,
        price: float
    ) -> str:
        """
        生成商品描述
        
        Args:
            title: 标题
            category: 分类
            price: 价格
            
        Returns:
            商品描述
        """
        system_prompt = """你是一个专业的闲鱼商品描述撰写专家。
要求：
1. 描述商品特点和优势
2. 突出性价比
3. 语气亲切自然，口语化
4. 150-200字左右
5. 不要过度夸张
6. 只返回描述内容，不要解释"""
        
        prompt = f"""为这个闲鱼商品生成描述：

标题：{title}
分类：{category}
价格：¥{price}

商品描述："""
        
        response = await self.ai_engine.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            complexity=TaskComplexity.MEDIUM,
            temperature=0.7
        )
        
        if response.success:
            return response.content.strip()
        else:
            logger.warning(f"⚠️ 描述生成失败: {response.error}")
            return f"【{category}】{title}，价格实惠，质量保证！"
    
    async def _optimize_description(self, description: str) -> str:
        """
        优化已有描述
        
        Args:
            description: 原始描述
            
        Returns:
            优化后的描述
        """
        system_prompt = """你是一个专业的闲鱼商品描述优化专家。
优化要求：
1. 保留原有信息
2. 使语言更生动、更吸引人
3. 控制在200字左右
4. 只返回优化后的描述，不要解释"""
        
        prompt = f"""优化这个闲鱼商品描述：

原描述：{description}

优化后的描述："""
        
        response = await self.ai_engine.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            complexity=TaskComplexity.SIMPLE,
            temperature=0.7
        )
        
        if response.success:
            return response.content.strip()
        else:
            logger.warning(f"⚠️ 描述优化失败，使用原描述")
            return description
    
    async def batch_optimize(
        self,
        products: List[Dict[str, Any]],
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> List[Dict[str, Any]]:
        """
        批量优化商品
        
        Args:
            products: 商品列表
            progress_callback: 进度回调函数 (progress, current_title)
            
        Returns:
            优化后的商品列表
        """
        logger.info(f"📦 开始批量优化 {len(products)} 个商品")
        
        optimized_products = []
        total = len(products)
        
        for idx, product in enumerate(products):
            try:
                # 优化商品
                optimized = await self.optimize_product(product)
                optimized_products.append(optimized)
                
                # 更新进度
                progress = (idx + 1) / total * 100
                if progress_callback:
                    progress_callback(progress, product["title"])
                
                # 延迟（避免过快调用AI）
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"❌ 优化失败: {product['title']} - {e}")
                # 优化失败，使用原始数据
                optimized_products.append(product)
        
        logger.info(f"✅ 批量优化完成！成功 {len(optimized_products)}/{total}")
        return optimized_products
    
    async def publish_product(
        self, 
        product: Dict[str, Any],
        use_browser: bool = True,
        cookies_file: str = "data/xianyu_cookies.json",
        enable_retry: bool = True,
        progress_callback = None
    ) -> Dict[str, Any]:
        """
        发布单个商品到闲鱼（支持真实发布和自动重试）
        
        Args:
            product: 商品数据
            use_browser: 是否使用浏览器自动化（True=真实发布，False=模拟）
            cookies_file: Cookie文件路径
            enable_retry: 是否启用重试机制
            progress_callback: 进度回调函数 callback(step_index, status, message, elapsed_time, screenshot_path)
            
        Returns:
            发布结果字典 {
                "success": bool,
                "error": str,
                "post_id": str,
                "post_url": str
            }
        """
        logger.info(f"📤 发布商品: {product['title']}")
        
        # 如果启用重试，使用重试处理器
        if enable_retry and use_browser:
            return await self.retry_handler.retry_with_backoff(
                self._publish_product_impl,
                product,
                use_browser,
                cookies_file,
                progress_callback
            )
        else:
            return await self._publish_product_impl(product, use_browser, cookies_file, progress_callback)
    
    async def _publish_product_impl(
        self, 
        product: Dict[str, Any],
        use_browser: bool,
        cookies_file: str,
        progress_callback = None
    ) -> Dict[str, Any]:
        """
        发布商品的实际实现（不含重试逻辑）
        
        Args:
            product: 商品数据
            use_browser: 是否使用浏览器自动化
            cookies_file: Cookie文件路径
            progress_callback: 进度回调函数
            
        Returns:
            发布结果
        """
        
        if not use_browser:
            # 模拟发布（用于测试）
            logger.info("   ⚠️ 使用模拟发布模式")
            await asyncio.sleep(1)
            return {
                "success": True,
                "error": None,
                "post_id": f"mock_{int(asyncio.get_event_loop().time())}",
                "post_url": "https://2.taobao.com/item.htm?id=mock"
            }
        
        # 真实发布
        try:
            # 导入浏览器自动化
            from core.browser_automation import XianyuAutomation
            
            # 创建浏览器实例（传递进度回调）
            automation = XianyuAutomation(headless=False, progress_callback=progress_callback)
            
            try:
                # 启动浏览器
                logger.info("   🌐 启动浏览器...")
                await automation.start()
                
                # 登录
                logger.info("   🔐 检查登录状态...")
                login_success = await automation.login(cookies_file)
                
                if not login_success:
                    raise Exception("登录失败")
                
                # 发布商品
                result = await automation.publish_product(
                    title=product.get("title", ""),
                    price=product.get("price", 0),
                    description=product.get("description", ""),
                    images=product.get("images", []),
                    category=product.get("category", "二手闲置")
                )
                
                if result["success"]:
                    logger.info(f"✅ 发布成功！")
                    logger.info(f"   商品ID: {result.get('post_id', '未知')}")
                    logger.info(f"   商品URL: {result.get('post_url', '未知')}")
                else:
                    logger.error(f"❌ 发布失败: {result.get('error', '未知错误')}")
                
                return result
            
            finally:
                # 关闭浏览器
                logger.info("   🔒 关闭浏览器...")
                await automation.stop()
        
        except ImportError as e:
            error_msg = "缺少playwright依赖，请安装: pip install playwright && playwright install chromium"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "post_id": None,
                "post_url": None
            }
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ 发布失败: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "post_id": None,
                "post_url": None
            }
    
    async def batch_publish(
        self,
        products: List[Dict[str, Any]],
        optimize: bool = True,
        use_browser: bool = True,
        cookies_file: str = "data/xianyu_cookies.json",
        progress_callback: Optional[Callable[[float, str, str], None]] = None
    ) -> Dict[str, Any]:
        """
        批量发布商品
        
        Args:
            products: 商品列表
            optimize: 是否先进行AI优化
            use_browser: 是否使用真实浏览器发布
            cookies_file: Cookie文件路径
            progress_callback: 进度回调 (progress, status, current_title)
            
        Returns:
            发布结果统计 {
                "total": int,
                "success": int,
                "failed": int,
                "errors": list,
                "published_items": list  # 成功发布的商品信息
            }
        """
        logger.info(f"🚀 开始批量发布 {len(products)} 个商品")
        logger.info(f"   模式: {'真实发布' if use_browser else '模拟发布'}")
        
        results = {
            "total": len(products),
            "success": 0,
            "failed": 0,
            "errors": [],
            "published_items": []
        }
        
        # 1. AI优化（如果需要）
        if optimize:
            logger.info("📝 第一步：AI优化商品信息...")
            
            def opt_progress(prog, title):
                if progress_callback:
                    progress_callback(prog * 0.5, "优化中", title)
            
            products = await self.batch_optimize(products, opt_progress)
        
        # 2. 发布商品
        logger.info("📤 第二步：发布商品到闲鱼...")
        
        total = len(products)
        for idx, product in enumerate(products):
            try:
                # 发布商品
                result = await self.publish_product(
                    product, 
                    use_browser=use_browser,
                    cookies_file=cookies_file
                )
                
                if result["success"]:
                    results["success"] += 1
                    results["published_items"].append({
                        "title": product["title"],
                        "post_id": result.get("post_id"),
                        "post_url": result.get("post_url")
                    })
                else:
                    results["failed"] += 1
                    error_msg = f"{product.get('title', '未知')}: {result.get('error', '未知错误')}"
                    results["errors"].append(error_msg)
                
                # 更新进度
                if optimize:
                    progress = 50 + (idx + 1) / total * 50
                else:
                    progress = (idx + 1) / total * 100
                
                if progress_callback:
                    status = "发布中" if result["success"] else "发布失败"
                    progress_callback(progress, status, product["title"])
                
                # 延迟（遵守闲鱼发布间隔，真实发布时需要更长间隔）
                delay = 5 if use_browser else 2
                await asyncio.sleep(delay)
                
            except Exception as e:
                results["failed"] += 1
                error_msg = f"{product.get('title', '未知')}: {str(e)}"
                results["errors"].append(error_msg)
                logger.error(f"❌ 发布失败: {error_msg}")
        
        logger.info(f"✅ 批量发布完成！成功 {results['success']}/{results['total']}")
        
        if results['errors']:
            logger.info(f"⚠️  失败详情:")
            for error in results['errors'][:5]:  # 只显示前5个错误
                logger.info(f"   - {error}")
        
        return results


# ===== 测试函数 =====

async def test_publisher():
    """测试发布器"""
    
    print("\n" + "="*60)
    print("🧪 测试闲鱼发布器")
    print("="*60)
    
    # 创建发布器
    publisher = XianyuPublisher()
    
    # 测试商品
    test_product = {
        "title": "二手iPhone 13 128G",
        "price": 3999,
        "category": "数码产品",
        "description": ""  # 空描述，测试AI生成
    }
    
    try:
        # 1. 测试单个商品优化
        print("\n1️⃣ 测试单个商品优化...")
        print(f"原标题: {test_product['title']}")
        
        optimized = await publisher.optimize_product(test_product)
        
        print(f"\n优化结果:")
        print(f"  标题: {optimized['title']}")
        print(f"  描述: {optimized['description'][:100]}...")
        
        # 2. 测试批量优化
        print("\n2️⃣ 测试批量优化...")
        
        test_products = [
            {
                "title": "小米手环7",
                "price": 199,
                "category": "数码配件",
                "description": ""
            },
            {
                "title": "索尼降噪耳机",
                "price": 1999,
                "category": "数码配件",
                "description": "降噪效果很好"
            }
        ]
        
        def progress_cb(progress, title):
            print(f"  进度: {progress:.1f}% - {title}")
        
        optimized_list = await publisher.batch_optimize(
            test_products,
            progress_callback=progress_cb
        )
        
        print(f"\n批量优化结果:")
        for i, p in enumerate(optimized_list, 1):
            print(f"\n商品 {i}:")
            print(f"  标题: {p['title']}")
            print(f"  描述: {p['description'][:80]}...")
        
        print("\n" + "="*60)
        print("✅ 测试完成！")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 运行测试
    asyncio.run(test_publisher())

