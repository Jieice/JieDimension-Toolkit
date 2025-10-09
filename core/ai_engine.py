"""
JieDimension Toolkit - AI Engine
智能AI调度引擎，支持本地Ollama + 多云端API轮替
Version: 1.5.0 - Day 16: 添加AI输出清理功能
Author: JieDimension Studio
"""

import asyncio
import time
import json
import logging
import os
import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import httpx

# Gemini API支持
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger_temp = logging.getLogger(__name__)
    logger_temp.warning("⚠️ google-generativeai未安装，Gemini功能不可用")

# Claude API支持（使用httpx直接调用）
CLAUDE_AVAILABLE = True  # Claude使用REST API，无需额外库

# 文心一言API支持（使用httpx直接调用）
ERNIE_AVAILABLE = True  # 文心一言使用REST API，无需额外库

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def clean_ai_output(text: str) -> str:
    """
    清理AI输出内容
    - 去除deepseek-r1模型的<think>...</think>思考过程标签
    - 去除多余的空白
    - 保留实际输出内容
    
    Args:
        text: 原始AI输出
        
    Returns:
        清理后的文本
    """
    if not text:
        return text
    
    # 去除<think>...</think>标签及其内容
    # 使用re.DOTALL让.匹配换行符
    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # 去除多余的空白
    cleaned = cleaned.strip()
    
    # 去除多个连续换行，最多保留两个换行
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    
    return cleaned


class TaskComplexity(Enum):
    """任务复杂度枚举"""
    SIMPLE = 1      # 简单任务（标题优化）-> 本地模型
    MEDIUM = 2      # 中等任务（描述生成）-> 本地模型 or 免费API
    COMPLEX = 3     # 复杂任务（多轮对话）-> 免费API优先
    ADVANCED = 4    # 高级任务（长文本生成）-> 高级API


class AIProvider(Enum):
    """AI提供商枚举"""
    OLLAMA = "ollama"
    GEMINI = "gemini"
    CLAUDE = "claude"      # Day 7新增
    ERNIE = "ernie"        # Day 7新增 - 文心一言
    COHERE = "cohere"      # 预留
    DOUBAO = "doubao"      # 预留


@dataclass
class AIConfig:
    """AI配置"""
    # Ollama配置
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "deepseek-r1:1.5b"
    
    # Gemini配置
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-1.5-flash"  # 免费版
    
    # Claude配置（Day 7新增）
    claude_api_key: Optional[str] = None
    claude_model: str = "claude-3-5-sonnet-20241022"  # 最新Sonnet模型
    claude_base_url: str = "https://api.anthropic.com/v1/messages"
    
    # 文心一言配置（Day 7新增）
    ernie_api_key: Optional[str] = None
    ernie_secret_key: Optional[str] = None
    ernie_model: str = "ernie-4.0-8k"  # ERNIE 4.0
    ernie_base_url: str = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat"
    
    # API配置
    max_retries: int = 3
    timeout: int = 30
    
    # 调度策略
    prefer_local: bool = True  # 优先使用本地模型（简单任务）
    fallback_enabled: bool = True  # 启用降级策略
    use_cloud_for_complex: bool = True  # 复杂任务使用云端


@dataclass
class AIResponse:
    """AI响应"""
    success: bool
    content: str
    provider: str
    model: str
    latency: float
    tokens: Optional[int] = None
    error: Optional[str] = None


class AIEngine:
    """
    AI智能调度引擎
    
    功能：
    1. 本地Ollama优先调用（无限制，最快）
    2. 免费API轮替（Gemini, Cohere, 豆包）
    3. 任务复杂度智能分级
    4. 失败自动重试与降级
    """
    
    def __init__(self, config: Optional[AIConfig] = None):
        """初始化AI引擎"""
        self.config = config or AIConfig()
        
        # 从环境变量加载API密钥（如果未在config中设置）
        if not self.config.gemini_api_key:
            self.config.gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not self.config.claude_api_key:
            self.config.claude_api_key = os.getenv('CLAUDE_API_KEY')
        if not self.config.ernie_api_key:
            self.config.ernie_api_key = os.getenv('ERNIE_API_KEY')
        if not self.config.ernie_secret_key:
            self.config.ernie_secret_key = os.getenv('ERNIE_SECRET_KEY')
        
        # 初始化Gemini
        self.gemini_model = None
        if GEMINI_AVAILABLE and self.config.gemini_api_key:
            try:
                genai.configure(api_key=self.config.gemini_api_key)
                self.gemini_model = genai.GenerativeModel(self.config.gemini_model)
                logger.info(f"✅ Gemini已配置: {self.config.gemini_model}")
            except Exception as e:
                logger.warning(f"⚠️ Gemini配置失败: {e}")
        
        # 初始化Claude（REST API，无需特殊配置）
        self.claude_available = CLAUDE_AVAILABLE and bool(self.config.claude_api_key)
        if self.claude_available:
            logger.info(f"✅ Claude已配置: {self.config.claude_model}")
        
        # 初始化文心一言（需要获取access_token）
        self.ernie_access_token = None
        self.ernie_available = False
        if ERNIE_AVAILABLE and self.config.ernie_api_key and self.config.ernie_secret_key:
            logger.info("📝 文心一言配置完成，将在首次调用时获取access_token")
            self.ernie_available = True
        
        self.api_providers = []
        self.provider_stats = {}
        
        # 初始化统计
        for provider in AIProvider:
            self.provider_stats[provider.value] = {
                'total_calls': 0,
                'success_calls': 0,
                'failed_calls': 0,
                'total_latency': 0.0,
                'avg_latency': 0.0,
                'enabled': True
            }
        
        logger.info("🚀 AI引擎初始化完成")
        logger.info(f"   - Ollama模型: {self.config.ollama_model}")
        logger.info(f"   - Ollama地址: {self.config.ollama_url}")
        logger.info(f"   - Gemini状态: {'可用' if self.gemini_model else '未配置'}")
        logger.info(f"   - Claude状态: {'可用' if self.claude_available else '未配置'}")
        logger.info(f"   - 文心一言状态: {'可用' if self.ernie_available else '未配置'}")
    
    async def test_ollama_connection(self) -> bool:
        """
        测试Ollama连接
        
        Returns:
            bool: 连接是否成功
        """
        try:
            logger.info("🔍 测试Ollama连接...")
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 测试Ollama服务是否运行
                response = await client.get(f"{self.config.ollama_url}/api/tags")
                
                if response.status_code == 200:
                    models = response.json().get('models', [])
                    model_names = [m['name'] for m in models]
                    
                    logger.info(f"✅ Ollama连接成功！")
                    logger.info(f"   - 可用模型: {', '.join(model_names)}")
                    
                    # 检查目标模型是否存在
                    if self.config.ollama_model in model_names:
                        logger.info(f"   - ✓ 找到模型: {self.config.ollama_model}")
                        return True
                    else:
                        logger.warning(f"   - ⚠️ 未找到模型: {self.config.ollama_model}")
                        logger.warning(f"   - 请运行: ollama pull {self.config.ollama_model}")
                        return False
                else:
                    logger.error(f"❌ Ollama服务响应异常: {response.status_code}")
                    return False
                    
        except httpx.ConnectError:
            logger.error("❌ 无法连接到Ollama服务")
            logger.error("   - 请确认Ollama已启动")
            logger.error("   - 启动命令: ollama serve")
            return False
        except Exception as e:
            logger.error(f"❌ Ollama连接测试失败: {e}")
            return False
    
    async def _call_ollama(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> AIResponse:
        """
        调用Ollama本地模型
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数
            
        Returns:
            AIResponse: AI响应
        """
        start_time = time.time()
        provider = AIProvider.OLLAMA.value
        
        try:
            logger.info(f"📤 调用Ollama: {self.config.ollama_model}")
            
            # 构建请求
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.config.ollama_model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature
                }
            }
            
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.post(
                    f"{self.config.ollama_url}/api/chat",
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    raw_content = result.get('message', {}).get('content', '')
                    
                    # 清理AI输出（去除<think>标签等）
                    content = clean_ai_output(raw_content)
                    
                    latency = time.time() - start_time
                    
                    # 更新统计
                    self._update_stats(provider, True, latency)
                    
                    logger.info(f"✅ Ollama响应成功 (耗时: {latency:.2f}s)")
                    
                    return AIResponse(
                        success=True,
                        content=content,
                        provider=provider,
                        model=self.config.ollama_model,
                        latency=latency,
                        tokens=result.get('eval_count')
                    )
                else:
                    raise Exception(f"HTTP {response.status_code}: {response.text}")
                    
        except Exception as e:
            latency = time.time() - start_time
            self._update_stats(provider, False, latency)
            
            logger.error(f"❌ Ollama调用失败: {e}")
            
            return AIResponse(
                success=False,
                content="",
                provider=provider,
                model=self.config.ollama_model,
                latency=latency,
                error=str(e)
            )
    
    async def _call_gemini(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> AIResponse:
        """
        调用Gemini API
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数
            
        Returns:
            AIResponse: AI响应
        """
        start_time = time.time()
        provider = AIProvider.GEMINI.value
        
        try:
            if not self.gemini_model:
                raise Exception("Gemini未配置或不可用")
            
            logger.info(f"📤 调用Gemini: {self.config.gemini_model}")
            
            # 构建完整提示词
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # 配置生成参数
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=2048,
            )
            
            # 调用Gemini API
            response = await asyncio.to_thread(
                self.gemini_model.generate_content,
                full_prompt,
                generation_config=generation_config
            )
            
            raw_content = response.text
            # 清理AI输出（去除<think>标签等）
            content = clean_ai_output(raw_content)
            
            latency = time.time() - start_time
            
            # 更新统计
            self._update_stats(provider, True, latency)
            
            logger.info(f"✅ Gemini响应成功 (耗时: {latency:.2f}s)")
            
            return AIResponse(
                success=True,
                content=content,
                provider=provider,
                model=self.config.gemini_model,
                latency=latency,
                tokens=len(content.split())  # 粗略估计
            )
                    
        except Exception as e:
            latency = time.time() - start_time
            self._update_stats(provider, False, latency)
            
            logger.error(f"❌ Gemini调用失败: {e}")
            
            return AIResponse(
                success=False,
                content="",
                provider=provider,
                model=self.config.gemini_model,
                latency=latency,
                error=str(e)
            )
    
    async def _call_claude(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> AIResponse:
        """
        调用Claude API
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数
            
        Returns:
            AIResponse: AI响应
        """
        start_time = time.time()
        provider = AIProvider.CLAUDE.value
        
        try:
            if not self.claude_available:
                raise Exception("Claude未配置或不可用")
            
            logger.info(f"📤 调用Claude: {self.config.claude_model}")
            
            # 构建消息
            messages = [{"role": "user", "content": prompt}]
            
            # 构建请求体
            payload = {
                "model": self.config.claude_model,
                "max_tokens": 2048,
                "temperature": temperature,
                "messages": messages
            }
            
            # 如果有系统提示词，添加到请求中
            if system_prompt:
                payload["system"] = system_prompt
            
            # 调用Claude API
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.post(
                    self.config.claude_base_url,
                    headers={
                        "x-api-key": self.config.claude_api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    },
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    raw_content = result.get('content', [{}])[0].get('text', '')
                    
                    # 清理AI输出（去除<think>标签等）
                    content = clean_ai_output(raw_content)
                    
                    latency = time.time() - start_time
                    
                    # 更新统计
                    self._update_stats(provider, True, latency)
                    
                    logger.info(f"✅ Claude响应成功 (耗时: {latency:.2f}s)")
                    
                    return AIResponse(
                        success=True,
                        content=content,
                        provider=provider,
                        model=self.config.claude_model,
                        latency=latency,
                        tokens=result.get('usage', {}).get('output_tokens', 0)
                    )
                else:
                    raise Exception(f"HTTP {response.status_code}: {response.text}")
                    
        except Exception as e:
            latency = time.time() - start_time
            self._update_stats(provider, False, latency)
            
            logger.error(f"❌ Claude调用失败: {e}")
            
            return AIResponse(
                success=False,
                content="",
                provider=provider,
                model=self.config.claude_model,
                latency=latency,
                error=str(e)
            )
    
    async def _get_ernie_access_token(self) -> Optional[str]:
        """
        获取文心一言的access_token
        
        Returns:
            Optional[str]: access_token或None
        """
        try:
            token_url = "https://aip.baidubce.com/oauth/2.0/token"
            params = {
                "grant_type": "client_credentials",
                "client_id": self.config.ernie_api_key,
                "client_secret": self.config.ernie_secret_key
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(token_url, params=params)
                
                if response.status_code == 200:
                    result = response.json()
                    access_token = result.get('access_token')
                    logger.info("✅ 文心一言access_token获取成功")
                    return access_token
                else:
                    logger.error(f"❌ 获取文心一言token失败: {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ 获取文心一言token异常: {e}")
            return None
    
    async def _call_ernie(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> AIResponse:
        """
        调用文心一言API
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数
            
        Returns:
            AIResponse: AI响应
        """
        start_time = time.time()
        provider = AIProvider.ERNIE.value
        
        try:
            if not self.ernie_available:
                raise Exception("文心一言未配置或不可用")
            
            # 获取access_token（如果还没有）
            if not self.ernie_access_token:
                self.ernie_access_token = await self._get_ernie_access_token()
                if not self.ernie_access_token:
                    raise Exception("无法获取文心一言access_token")
            
            logger.info(f"📤 调用文心一言: {self.config.ernie_model}")
            
            # 构建消息
            messages = []
            if system_prompt:
                messages.append({"role": "user", "content": system_prompt})
                messages.append({"role": "assistant", "content": "好的，我明白了。"})
            messages.append({"role": "user", "content": prompt})
            
            # 构建请求体
            payload = {
                "messages": messages,
                "temperature": temperature,
                "top_p": 0.8,
                "penalty_score": 1.0,
                "disable_search": False,
                "enable_citation": False
            }
            
            # API URL（根据模型类型）
            api_url = f"{self.config.ernie_base_url}/{self.config.ernie_model}?access_token={self.ernie_access_token}"
            
            # 调用文心一言API
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.post(
                    api_url,
                    headers={"Content-Type": "application/json"},
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # 检查是否有错误
                    if 'error_code' in result:
                        raise Exception(f"API错误: {result.get('error_msg', '未知错误')}")
                    
                    raw_content = result.get('result', '')
                    
                    # 清理AI输出（去除<think>标签等）
                    content = clean_ai_output(raw_content)
                    
                    latency = time.time() - start_time
                    
                    # 更新统计
                    self._update_stats(provider, True, latency)
                    
                    logger.info(f"✅ 文心一言响应成功 (耗时: {latency:.2f}s)")
                    
                    return AIResponse(
                        success=True,
                        content=content,
                        provider=provider,
                        model=self.config.ernie_model,
                        latency=latency,
                        tokens=result.get('usage', {}).get('total_tokens', 0)
                    )
                else:
                    raise Exception(f"HTTP {response.status_code}: {response.text}")
                    
        except Exception as e:
            latency = time.time() - start_time
            self._update_stats(provider, False, latency)
            
            logger.error(f"❌ 文心一言调用失败: {e}")
            
            # 如果是token失效，清除缓存的token
            if "token" in str(e).lower() or "invalid" in str(e).lower():
                self.ernie_access_token = None
            
            return AIResponse(
                success=False,
                content="",
                provider=provider,
                model=self.config.ernie_model,
                latency=latency,
                error=str(e)
            )
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        complexity: TaskComplexity = TaskComplexity.SIMPLE,
        temperature: float = 0.7
    ) -> AIResponse:
        """
        智能生成文本（核心方法）
        
        调度策略：
        1. SIMPLE/MEDIUM任务 -> 优先本地Ollama
        2. COMPLEX/ADVANCED任务 -> 优先免费API（如果配置）
        3. 失败自动重试，最多3次
        4. 本地失败可降级到免费API
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            complexity: 任务复杂度（可以是TaskComplexity枚举或整数1-4）
            temperature: 温度参数
            
        Returns:
            AIResponse: AI响应
        """
        # 如果传入的是整数，转换为TaskComplexity枚举
        if isinstance(complexity, int):
            complexity = TaskComplexity(complexity)
        
        logger.info(f"🎯 开始AI生成任务 (复杂度: {complexity.name})")
        
        # 根据复杂度选择提供商
        providers = self._select_providers(complexity)
        
        # 依次尝试各个提供商
        for attempt in range(self.config.max_retries):
            for provider in providers:
                if provider == AIProvider.OLLAMA:
                    response = await self._call_ollama(
                        prompt=prompt,
                        system_prompt=system_prompt,
                        temperature=temperature
                    )
                    
                    if response.success:
                        return response
                    
                    logger.warning(f"⚠️ {provider.value} 调用失败，尝试下一个提供商...")
                
                elif provider == AIProvider.GEMINI:
                    response = await self._call_gemini(
                        prompt=prompt,
                        system_prompt=system_prompt,
                        temperature=temperature
                    )
                    
                    if response.success:
                        return response
                    
                    logger.warning(f"⚠️ {provider.value} 调用失败，尝试下一个提供商...")
                
                elif provider == AIProvider.CLAUDE:
                    response = await self._call_claude(
                        prompt=prompt,
                        system_prompt=system_prompt,
                        temperature=temperature
                    )
                    
                    if response.success:
                        return response
                    
                    logger.warning(f"⚠️ {provider.value} 调用失败，尝试下一个提供商...")
                
                elif provider == AIProvider.ERNIE:
                    response = await self._call_ernie(
                        prompt=prompt,
                        system_prompt=system_prompt,
                        temperature=temperature
                    )
                    
                    if response.success:
                        return response
                    
                    logger.warning(f"⚠️ {provider.value} 调用失败，尝试下一个提供商...")
                
            if attempt < self.config.max_retries - 1:
                logger.warning(f"🔄 第 {attempt + 1} 次尝试失败，重试中...")
                await asyncio.sleep(1)  # 等待1秒后重试
        
        # 所有尝试都失败
        logger.error("❌ 所有AI提供商调用均失败")
        return AIResponse(
            success=False,
            content="",
            provider="none",
            model="none",
            latency=0.0,
            error="所有AI提供商均不可用"
        )
    
    def _select_providers(self, complexity: TaskComplexity) -> List[AIProvider]:
        """
        根据任务复杂度智能选择AI提供商顺序（Day 7更新）
        
        调度策略：
        - SIMPLE: 本地Ollama（快速、免费、适合简单任务）
        - MEDIUM: 本地Ollama优先，云端API降级（Gemini/Claude/文心一言）
        - COMPLEX: 高级云端API优先（Claude/Gemini），中文任务优先文心一言
        - ADVANCED: 仅高级云端API（Claude优先，Gemini次之）
        
        优先级（质量）：
        1. Claude-3.5-Sonnet（最强）
        2. Gemini-1.5-Flash（快速且免费）
        3. 文心一言4.0（中文任务）
        4. Ollama（本地快速）
        
        Args:
            complexity: 任务复杂度
            
        Returns:
            List[AIProvider]: 提供商列表（按优先级排序）
        """
        providers = []
        
        if complexity == TaskComplexity.SIMPLE:
            # 简单任务：仅本地（最快、最省钱）
            providers = [AIProvider.OLLAMA]
            
        elif complexity == TaskComplexity.MEDIUM:
            # 中等任务：本地优先，云端降级
            if self.config.prefer_local:
                providers = [AIProvider.OLLAMA]
                # 添加可用的云端API作为降级
                if self.config.fallback_enabled:
                    if self.gemini_model:
                        providers.append(AIProvider.GEMINI)
                    if self.ernie_available:
                        providers.append(AIProvider.ERNIE)
                    if self.claude_available:
                        providers.append(AIProvider.CLAUDE)
            else:
                # 云端优先
                if self.gemini_model:
                    providers.append(AIProvider.GEMINI)
                if self.ernie_available:
                    providers.append(AIProvider.ERNIE)
                providers.append(AIProvider.OLLAMA)
                
        elif complexity == TaskComplexity.COMPLEX:
            # 复杂任务：高级云端优先（质量更重要）
            if self.config.use_cloud_for_complex:
                # 按质量排序：Claude > Gemini > 文心一言
                if self.claude_available:
                    providers.append(AIProvider.CLAUDE)
                if self.gemini_model:
                    providers.append(AIProvider.GEMINI)
                if self.ernie_available:
                    providers.append(AIProvider.ERNIE)
                    
                # 降级到本地
                if self.config.fallback_enabled:
                    providers.append(AIProvider.OLLAMA)
            else:
                providers = [AIProvider.OLLAMA]
                
        else:  # ADVANCED
            # 高级任务：仅高级云端API
            if self.claude_available:
                providers = [AIProvider.CLAUDE]
            elif self.gemini_model:
                providers = [AIProvider.GEMINI]
            elif self.ernie_available:
                providers = [AIProvider.ERNIE]
            else:
                # 所有云端API都不可用，降级到Ollama并警告
                logger.warning("⚠️ 高级任务需要云端API，但均未配置，将使用Ollama（质量可能不足）")
                providers = [AIProvider.OLLAMA]
        
        logger.info(f"📋 任务 {complexity.name} - 提供商顺序: {[p.value for p in providers]}")
        return providers
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取所有提供商的统计信息
        
        Returns:
            Dict[str, Any]: 统计信息字典
        """
        return self.provider_stats.copy()
    
    def _update_stats(self, provider: str, success: bool, latency: float):
        """更新提供商统计信息"""
        stats = self.provider_stats[provider]
        stats['total_calls'] += 1
        
        if success:
            stats['success_calls'] += 1
        else:
            stats['failed_calls'] += 1
        
        stats['total_latency'] += latency
        stats['avg_latency'] = stats['total_latency'] / stats['total_calls']
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.provider_stats
    
    def print_stats(self):
        """打印统计信息"""
        logger.info("\n" + "="*60)
        logger.info("📊 AI引擎统计信息")
        logger.info("="*60)
        
        for provider, stats in self.provider_stats.items():
            if stats['total_calls'] > 0:
                success_rate = (stats['success_calls'] / stats['total_calls']) * 100
                
                logger.info(f"\n{provider.upper()}:")
                logger.info(f"  - 总调用: {stats['total_calls']}")
                logger.info(f"  - 成功: {stats['success_calls']}")
                logger.info(f"  - 失败: {stats['failed_calls']}")
                logger.info(f"  - 成功率: {success_rate:.1f}%")
                logger.info(f"  - 平均延迟: {stats['avg_latency']:.2f}s")
        
        logger.info("="*60 + "\n")


# ===== 辅助函数 =====

async def create_ai_engine() -> AIEngine:
    """创建AI引擎实例"""
    config = AIConfig()
    engine = AIEngine(config)
    return engine


async def quick_generate(prompt: str, system_prompt: Optional[str] = None) -> str:
    """
    快速生成文本（便捷方法）
    
    Args:
        prompt: 用户提示词
        system_prompt: 系统提示词
        
    Returns:
        str: 生成的文本
    """
    engine = await create_ai_engine()
    response = await engine.generate(prompt, system_prompt)
    
    if response.success:
        return response.content
    else:
        raise Exception(f"AI生成失败: {response.error}")


# ===== 示例用法 =====

async def example_usage():
    """使用示例"""
    
    # 1. 创建AI引擎
    engine = await create_ai_engine()
    
    # 2. 测试连接
    connected = await engine.test_ollama_connection()
    if not connected:
        logger.error("Ollama连接失败，请检查配置")
        return
    
    # 3. 简单生成
    response = await engine.generate(
        prompt="帮我优化这个闲鱼标题：九成新iPhone 13 128G",
        system_prompt="你是一个专业的电商标题优化助手，擅长优化闲鱼商品标题。",
        complexity=TaskComplexity.SIMPLE
    )
    
    if response.success:
        logger.info(f"\n✨ 生成结果:\n{response.content}")
    else:
        logger.error(f"生成失败: {response.error}")
    
    # 4. 查看统计
    engine.print_stats()


if __name__ == "__main__":
    # 运行示例
    asyncio.run(example_usage())

