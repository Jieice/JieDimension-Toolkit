"""
闲鱼发布重试处理器

提供发布失败后的自动重试机制
"""

import asyncio
import logging
from typing import Dict, Any, Callable, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class RetryHandler:
    """发布重试处理器"""
    
    def __init__(
        self, 
        max_retries: int = 3,
        retry_delay: float = 5.0,
        backoff_multiplier: float = 2.0
    ):
        """
        初始化重试处理器
        
        Args:
            max_retries: 最大重试次数
            retry_delay: 初始重试延迟（秒）
            backoff_multiplier: 延迟增长倍数
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.backoff_multiplier = backoff_multiplier
    
    async def retry_with_backoff(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """
        带指数退避的重试机制
        
        Args:
            func: 要重试的异步函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            函数执行结果
        """
        last_error = None
        delay = self.retry_delay
        
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"  🔄 尝试 {attempt + 1}/{self.max_retries + 1}...")
                
                # 执行函数
                result = await func(*args, **kwargs)
                
                # 检查结果
                if isinstance(result, dict) and result.get("success"):
                    if attempt > 0:
                        logger.info(f"  ✅ 重试成功！")
                    return result
                else:
                    # 发布失败但没有抛异常
                    error_msg = result.get("error", "未知错误") if isinstance(result, dict) else "发布失败"
                    logger.warning(f"  ⚠️  尝试 {attempt + 1} 失败: {error_msg}")
                    
                    if attempt < self.max_retries:
                        logger.info(f"  ⏳ 等待 {delay:.1f}秒 后重试...")
                        await asyncio.sleep(delay)
                        delay *= self.backoff_multiplier
                    else:
                        logger.error(f"  ❌ 已达最大重试次数")
                        return result
            
            except Exception as e:
                last_error = e
                logger.error(f"  ❌ 尝试 {attempt + 1} 异常: {str(e)}")
                
                if attempt < self.max_retries:
                    logger.info(f"  ⏳ 等待 {delay:.1f}秒 后重试...")
                    await asyncio.sleep(delay)
                    delay *= self.backoff_multiplier
                else:
                    logger.error(f"  ❌ 已达最大重试次数")
                    return {
                        "success": False,
                        "error": f"重试失败: {str(last_error)}",
                        "post_id": None,
                        "post_url": None
                    }
        
        # 如果所有重试都失败
        return {
            "success": False,
            "error": f"所有 {self.max_retries + 1} 次尝试均失败: {str(last_error)}",
            "post_id": None,
            "post_url": None
        }


class ErrorClassifier:
    """错误分类器 - 判断错误是否可重试"""
    
    # 不可重试的错误类型
    NON_RETRYABLE_ERRORS = [
        "登录失败",
        "缺少playwright依赖",
        "Cookie已过期",
        "账号被封禁",
        "标题填写失败",
        "价格填写失败",
    ]
    
    @classmethod
    def is_retryable(cls, error: str) -> bool:
        """
        判断错误是否可重试
        
        Args:
            error: 错误信息
            
        Returns:
            是否可重试
        """
        if not error:
            return True
        
        error_lower = error.lower()
        
        # 检查是否包含不可重试的错误
        for non_retryable in cls.NON_RETRYABLE_ERRORS:
            if non_retryable.lower() in error_lower:
                logger.info(f"  ℹ️  检测到不可重试错误: {non_retryable}")
                return False
        
        return True
    
    @classmethod
    def get_error_category(cls, error: str) -> str:
        """
        获取错误类别
        
        Args:
            error: 错误信息
            
        Returns:
            错误类别
        """
        if not error:
            return "未知错误"
        
        error_lower = error.lower()
        
        if "登录" in error_lower or "cookie" in error_lower:
            return "认证问题"
        elif "网络" in error_lower or "timeout" in error_lower:
            return "网络问题"
        elif "playwright" in error_lower or "依赖" in error_lower:
            return "环境问题"
        elif "选择器" in error_lower or "元素" in error_lower:
            return "页面结构变化"
        else:
            return "其他错误"


# 使用示例
async def test_retry_handler():
    """测试重试处理器"""
    
    print("="*60)
    print("🧪 测试重试处理器")
    print("="*60)
    
    # 创建重试处理器
    retry_handler = RetryHandler(max_retries=3, retry_delay=2.0)
    
    # 模拟一个会失败的函数
    attempt_count = [0]
    
    async def mock_publish():
        attempt_count[0] += 1
        print(f"\n模拟发布 - 尝试 {attempt_count[0]}")
        
        # 前2次失败，第3次成功
        if attempt_count[0] < 3:
            return {
                "success": False,
                "error": f"模拟失败 #{attempt_count[0]}"
            }
        else:
            return {
                "success": True,
                "post_id": "test_123",
                "post_url": "https://example.com/item/123"
            }
    
    # 测试重试
    result = await retry_handler.retry_with_backoff(mock_publish)
    
    print("\n最终结果:")
    print(f"  成功: {result['success']}")
    print(f"  尝试次数: {attempt_count[0]}")
    
    # 测试错误分类
    print("\n\n🔍 测试错误分类:")
    
    test_errors = [
        "登录失败",
        "网络超时",
        "缺少playwright依赖",
        "元素未找到",
        "未知错误"
    ]
    
    for error in test_errors:
        retryable = ErrorClassifier.is_retryable(error)
        category = ErrorClassifier.get_error_category(error)
        print(f"  {error:30s} - 可重试: {retryable:5s} - 类别: {category}")
    
    print("\n" + "="*60)
    print("✅ 测试完成")
    print("="*60)


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    asyncio.run(test_retry_handler())
