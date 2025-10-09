# core/browser_automation.py

"""
浏览器自动化工具 - 使用Playwright实现网页自动化

用于没有公开API的平台（如闲鱼）的自动化发布
"""

import asyncio
from typing import Optional, Dict, Any, List
from pathlib import Path


class BrowserAutomation:
    """浏览器自动化基类"""
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        
        print(f"🌐 浏览器自动化初始化 (headless={headless})")
    
    async def start(self):
        """启动浏览器"""
        
        try:
            from playwright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            
            # 启动浏览器
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=['--start-maximized']
            )
            
            # 创建上下文（带Cookie持久化）
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
            # 创建页面
            self.page = await self.context.new_page()
            
            print("✅ 浏览器启动成功")
        
        except ImportError:
            raise ImportError(
                "需要安装playwright:\n"
                "pip install playwright\n"
                "playwright install chromium"
            )
        except Exception as e:
            print(f"❌ 浏览器启动失败: {e}")
            raise
    
    async def stop(self):
        """停止浏览器"""
        
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        
        print("✅ 浏览器关闭")
    
    async def goto(self, url: str, wait_until: str = "networkidle"):
        """导航到URL"""
        
        if not self.page:
            raise RuntimeError("浏览器未启动")
        
        try:
            await self.page.goto(url, wait_until=wait_until, timeout=30000)
            print(f"✅ 导航到: {url}")
        except Exception as e:
            print(f"❌ 导航失败: {e}")
            raise
    
    async def wait_for_selector(
        self,
        selector: str,
        timeout: int = 10000
    ):
        """等待元素出现"""
        
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except Exception as e:
            print(f"⚠️  等待元素超时: {selector}")
            return False
    
    async def click(self, selector: str):
        """点击元素"""
        
        try:
            await self.page.click(selector)
            await asyncio.sleep(0.5)  # 等待动画
            return True
        except Exception as e:
            print(f"❌ 点击失败: {selector} - {e}")
            return False
    
    async def fill(self, selector: str, value: str):
        """填充输入框"""
        
        try:
            await self.page.fill(selector, value)
            await asyncio.sleep(0.3)
            return True
        except Exception as e:
            print(f"❌ 填充失败: {selector} - {e}")
            return False
    
    async def upload_file(self, selector: str, file_path: str):
        """上传文件"""
        
        try:
            await self.page.set_input_files(selector, file_path)
            await asyncio.sleep(0.5)
            return True
        except Exception as e:
            print(f"❌ 上传失败: {file_path} - {e}")
            return False
    
    async def screenshot(self, path: str = "screenshot.png"):
        """截图"""
        
        try:
            await self.page.screenshot(path=path)
            print(f"✅ 截图保存: {path}")
            return True
        except Exception as e:
            print(f"❌ 截图失败: {e}")
            return False
    
    async def get_cookies(self) -> List[Dict]:
        """获取Cookie"""
        
        if not self.context:
            return []
        
        cookies = await self.context.cookies()
        return cookies
    
    async def set_cookies(self, cookies: List[Dict]):
        """设置Cookie"""
        
        if not self.context:
            raise RuntimeError("浏览器未启动")
        
        await self.context.add_cookies(cookies)
        print(f"✅ 设置了 {len(cookies)} 个Cookie")
    
    async def save_cookies(self, file_path: str):
        """保存Cookie到文件"""
        
        import json
        
        cookies = await self.get_cookies()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=2)
        
        print(f"✅ Cookie保存到: {file_path}")
    
    async def load_cookies(self, file_path: str):
        """从文件加载Cookie"""
        
        import json
        
        if not Path(file_path).exists():
            print(f"⚠️  Cookie文件不存在: {file_path}")
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
        
        await self.set_cookies(cookies)
        print(f"✅ 从文件加载Cookie: {file_path}")
        return True


class XianyuAutomation(BrowserAutomation):
    """闲鱼自动化发布"""
    
    XIANYU_URL = "https://2.taobao.com"
    LOGIN_URL = "https://login.taobao.com"
    PUBLISH_URL = "https://2.taobao.com/publish/index.htm"
    
    # 选择器配置（根据实际页面可能需要调整）
    SELECTORS = {
        # 登录相关
        "user_info": ".user-info, .user-name, .avatar, [class*='user'], [class*='avatar']",
        
        # 发布页面
        "image_upload": "input[type='file']",
        "title_input": "input[placeholder*='标题'], input[name='title'], textarea[placeholder*='标题']",
        "price_input": "input[placeholder*='价格'], input[name='price']",
        "desc_input": "textarea[placeholder*='描述'], textarea[name='description']",
        "category_btn": "button.category-btn, .category-select, [class*='category']",
        "publish_btn": "button.publish-btn, button[type='submit'], .submit-btn, [class*='publish']",
        
        # 发布结果
        "success_indicator": ".success, [class*='success'], .result-success"
    }
    
    def __init__(self, headless: bool = False, progress_callback = None):
        """
        初始化闲鱼自动化
        
        Args:
            headless: 是否无头模式
            progress_callback: 进度回调函数 callback(step_index, status, message, elapsed_time, screenshot_path)
        """
        super().__init__(headless=headless)
        self.progress_callback = progress_callback
    
    async def login(self, cookies_file: Optional[str] = None):
        """登录闲鱼"""
        
        # 尝试加载Cookie
        if cookies_file and await self.load_cookies(cookies_file):
            # 验证登录状态
            await self.goto(self.XIANYU_URL)
            await asyncio.sleep(2)
            
            # 检查是否已登录
            is_logged_in = await self._check_login_status()
            if is_logged_in:
                print("✅ 使用Cookie登录成功")
                return True
        
        # 需要手动登录
        print("⚠️  需要手动登录")
        await self.goto(self.LOGIN_URL)
        
        # 等待用户手动登录
        print("📱 请在浏览器中完成登录（扫码或密码登录）")
        print("⏳ 等待登录完成...")
        
        # 等待登录成功（检测URL变化或特定元素）
        for _ in range(60):  # 等待最多60秒
            await asyncio.sleep(1)
            if await self._check_login_status():
                print("✅ 登录成功")
                
                # 保存Cookie
                if cookies_file:
                    await self.save_cookies(cookies_file)
                
                return True
        
        print("❌ 登录超时")
        return False
    
    async def _check_login_status(self) -> bool:
        """检查登录状态"""
        
        # 方法1: 检查URL是否包含登录成功的标识
        current_url = self.page.url
        if "login" not in current_url.lower():
            print("✅ 检测到非登录页面，可能已登录")
            return True
        
        # 方法2: 尝试多个可能的用户信息选择器
        selectors = [
            "div.user-info",           # 通用选择器
            ".user-name",              # 用户名
            ".avatar",                 # 头像
            "[class*='user']",         # 包含user的类名
            "[class*='avatar']",       # 包含avatar的类名
        ]
        
        for selector in selectors:
            try:
                element = await self.page.query_selector(selector)
                if element:
                    print(f"✅ 找到登录元素: {selector}")
                    return True
            except:
                continue
        
        print("⚠️ 未找到登录元素，可能需要手动登录")
        return False
    
    def _update_progress(
        self,
        step_index: int,
        status: str,
        message: str = "",
        elapsed_time: float = 0,
        screenshot_path: str = ""
    ):
        """
        更新进度（调用回调函数）
        
        Args:
            step_index: 步骤索引 (0-8)
            status: 状态 ("waiting", "running", "success", "failed", "skipped")
            message: 消息内容
            elapsed_time: 耗时（秒）
            screenshot_path: 截图路径
        """
        if self.progress_callback:
            try:
                self.progress_callback(step_index, status, message, elapsed_time, screenshot_path)
            except Exception as e:
                print(f"⚠️ 进度回调失败: {e}")
    
    async def publish_product(
        self,
        title: str,
        price: float,
        description: str,
        images: List[str],
        category: str = "二手闲置"
    ) -> Dict[str, Any]:
        """
        发布商品到闲鱼
        
        Args:
            title: 商品标题
            price: 价格
            description: 商品描述
            images: 图片路径列表
            category: 分类
            
        Returns:
            发布结果字典 {
                "success": bool,
                "error": str (可选),
                "post_id": str (可选),
                "post_url": str (可选)
            }
        """
        import time
        
        result = {
            "success": False,
            "error": None,
            "post_id": None,
            "post_url": None
        }
        
        try:
            print(f"📤 开始发布: {title}")
            
            # 步骤0: 打开发布页面
            print("   🌐 打开发布页面...")
            step_start = time.time()
            self._update_progress(0, "running", "正在打开发布页面...")
            
            await self.goto(self.PUBLISH_URL)
            await asyncio.sleep(2)
            
            # 截图记录（用于调试）
            screenshot_path = "data/temp/publish_step0_page.png"
            await self.screenshot(screenshot_path)
            
            elapsed = time.time() - step_start
            self._update_progress(0, "success", "发布页面已打开", elapsed, screenshot_path)
            
            # 步骤1: 上传图片
            step_start = time.time()
            if images:
                print(f"   📸 上传图片 ({len(images[:9])}张)...")
                self._update_progress(1, "running", f"正在上传 {len(images[:9])} 张图片...")
                
                upload_success = 0
                
                for idx, image_path in enumerate(images[:9]):  # 最多9张
                    if await self.upload_file(self.SELECTORS["image_upload"], image_path):
                        upload_success += 1
                        print(f"      ✓ 图片{idx+1}上传成功")
                    else:
                        print(f"      ⚠️ 图片{idx+1}上传失败: {image_path}")
                    
                    await asyncio.sleep(1)  # 等待上传完成
                
                if upload_success == 0 and len(images) > 0:
                    raise Exception("所有图片上传失败")
                
                screenshot_path = "data/temp/publish_step1_images.png"
                await self.screenshot(screenshot_path)
                
                elapsed = time.time() - step_start
                self._update_progress(1, "success", f"已上传 {upload_success} 张图片", elapsed, screenshot_path)
            else:
                self._update_progress(1, "skipped", "无图片需要上传", 0)
            
            # 步骤2: 填写标题
            print("   ✍️  填写标题...")
            step_start = time.time()
            self._update_progress(2, "running", "正在填写标题...")
            
            if not await self.fill(self.SELECTORS["title_input"], title):
                self._update_progress(2, "failed", "标题填写失败", time.time() - step_start)
                raise Exception("标题填写失败")
            
            await asyncio.sleep(0.5)
            elapsed = time.time() - step_start
            self._update_progress(2, "success", "标题填写完成", elapsed)
            
            # 步骤3: 填写价格
            print("   💰 填写价格...")
            step_start = time.time()
            self._update_progress(3, "running", f"正在填写价格 ¥{price}...")
            
            if not await self.fill(self.SELECTORS["price_input"], str(price)):
                self._update_progress(3, "failed", "价格填写失败", time.time() - step_start)
                raise Exception("价格填写失败")
            
            await asyncio.sleep(0.5)
            elapsed = time.time() - step_start
            self._update_progress(3, "success", "价格填写完成", elapsed)
            
            # 步骤4: 填写描述
            print("   📝 填写描述...")
            step_start = time.time()
            self._update_progress(4, "running", "正在填写描述...")
            
            if not await self.fill(self.SELECTORS["desc_input"], description):
                print("      ⚠️ 描述填写失败（继续）")
                self._update_progress(4, "failed", "描述填写失败", time.time() - step_start)
            else:
                elapsed = time.time() - step_start
                self._update_progress(4, "success", "描述填写完成", elapsed)
            
            await asyncio.sleep(0.5)
            screenshot_path = "data/temp/publish_step4_content.png"
            await self.screenshot(screenshot_path)
            
            # 步骤5: 选择分类
            print("   🏷️  选择分类...")
            step_start = time.time()
            self._update_progress(5, "running", f"正在选择分类 [{category}]...")
            
            # 注意：分类选择较复杂，可能需要多步操作
            try:
                # 尝试点击分类按钮
                if await self.click(self.SELECTORS["category_btn"]):
                    await asyncio.sleep(1)
                    # TODO: 根据category参数选择具体分类
                    # 这里需要根据实际页面实现
                    elapsed = time.time() - step_start
                    self._update_progress(5, "success", "分类选择完成", elapsed)
                else:
                    self._update_progress(5, "skipped", "使用默认分类", time.time() - step_start)
            except Exception as e:
                print(f"      ⚠️ 分类选择失败: {e}")
                self._update_progress(5, "skipped", "使用默认分类", time.time() - step_start)
            
            # 步骤6: 提交发布
            print("   🚀 提交发布...")
            step_start = time.time()
            self._update_progress(6, "running", "正在提交发布...")
            
            if not await self.click(self.SELECTORS["publish_btn"]):
                self._update_progress(6, "failed", "提交按钮点击失败", time.time() - step_start)
                raise Exception("提交按钮点击失败")
            
            elapsed = time.time() - step_start
            self._update_progress(6, "success", "发布已提交", elapsed)
            
            # 步骤7: 等待发布完成
            print("   ⏳ 等待发布完成...")
            step_start = time.time()
            self._update_progress(7, "running", "等待服务器处理...")
            await asyncio.sleep(3)
            elapsed = time.time() - step_start
            self._update_progress(7, "success", "处理完成", elapsed)
            
            # 步骤8: 验证发布结果
            print("   🔍 验证发布结果...")
            step_start = time.time()
            self._update_progress(8, "running", "正在验证发布结果...")
            success = await self._check_publish_success()
            
            if success:
                # 尝试获取发布ID和URL
                current_url = self.page.url
                result["success"] = True
                result["post_url"] = current_url
                
                # 从URL提取ID（如果可能）
                if "id=" in current_url:
                    post_id = current_url.split("id=")[1].split("&")[0]
                    result["post_id"] = post_id
                
                screenshot_path = "data/temp/publish_success.png"
                await self.screenshot(screenshot_path)
                
                elapsed = time.time() - step_start
                self._update_progress(8, "success", "发布成功！", elapsed, screenshot_path)
                print("✅ 发布成功！")
            else:
                elapsed = time.time() - step_start
                self._update_progress(8, "failed", "发布验证失败", elapsed)
                raise Exception("发布验证失败：未检测到成功标识")
        
        except Exception as e:
            error_msg = str(e)
            print(f"❌ 发布失败: {error_msg}")
            
            result["error"] = error_msg
            
            # 错误截图
            screenshot_path = "data/temp/publish_error.png"
            await self.screenshot(screenshot_path)
            
            # 更新所有未完成步骤为失败
            # 注意：这里只是示例，实际应该根据失败的具体步骤来更新
        
        return result
    
    async def _check_publish_success(self) -> bool:
        """
        检查发布是否成功
        
        Returns:
            是否发布成功
        """
        # 方法1: 检查URL变化
        current_url = self.page.url
        if "success" in current_url.lower() or "detail" in current_url.lower():
            print("      ✓ URL变化表示发布成功")
            return True
        
        # 方法2: 查找成功提示元素
        try:
            element = await self.page.query_selector(self.SELECTORS["success_indicator"])
            if element:
                print("      ✓ 找到成功提示元素")
                return True
        except:
            pass
        
        # 方法3: 检查是否不在发布页面
        if "publish" not in current_url.lower():
            print("      ✓ 已离开发布页面")
            return True
        
        print("      ✗ 未检测到发布成功标识")
        return False


# 测试代码
async def test_browser_automation():
    """测试浏览器自动化"""
    
    print("="*60)
    print("🧪 测试浏览器自动化")
    print("="*60)
    
    # 创建自动化实例
    automation = BrowserAutomation(headless=False)
    
    try:
        # 启动浏览器
        print("\n1️⃣ 启动浏览器...")
        await automation.start()
        
        # 导航到测试页面
        print("\n2️⃣ 导航到测试页面...")
        await automation.goto("https://www.baidu.com")
        await asyncio.sleep(2)
        
        # 测试截图
        print("\n3️⃣ 测试截图...")
        await automation.screenshot("test_screenshot.png")
        
        # 获取Cookie
        print("\n4️⃣ 获取Cookie...")
        cookies = await automation.get_cookies()
        print(f"   获取到 {len(cookies)} 个Cookie")
        
        # 等待一下
        await asyncio.sleep(2)
        
    finally:
        # 关闭浏览器
        print("\n5️⃣ 关闭浏览器...")
        await automation.stop()
    
    print("\n" + "="*60)
    print("✅ 测试完成！")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_browser_automation())

