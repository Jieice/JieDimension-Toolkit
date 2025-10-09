# plugins/bilibili/api_client.py

"""
B站官方API客户端

支持功能：
- 视频投稿
- 动态发布
- 专栏发布
- 账号信息查询
"""

import asyncio
import aiohttp
import hashlib
import time
from typing import Dict, Any, Optional, List
from datetime import datetime


class BilibiliAPIClient:
    """B站API客户端"""
    
    # API地址
    API_BASE = "https://api.bilibili.com"
    MEMBER_API = "https://member.bilibili.com/x"
    
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        sessdata: Optional[str] = None
    ):
        """
        初始化B站API客户端
        
        Args:
            access_key: API访问密钥
            secret_key: API密钥
            sessdata: 会话Cookie（可选，用于部分操作）
        """
        self.access_key = access_key
        self.secret_key = secret_key
        self.sessdata = sessdata
        
        self.session: Optional[aiohttp.ClientSession] = None
        
        print("📺 B站API客户端初始化完成")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取HTTP会话"""
        
        if not self.session:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            # 添加Cookie
            if self.sessdata:
                headers["Cookie"] = f"SESSDATA={self.sessdata}"
            
            self.session = aiohttp.ClientSession(headers=headers)
        
        return self.session
    
    async def close(self):
        """关闭会话"""
        
        if self.session:
            await self.session.close()
            self.session = None
    
    def _generate_sign(self, params: Dict[str, Any]) -> str:
        """
        生成API签名
        
        B站API需要对参数进行签名验证
        """
        
        # 排序参数
        sorted_params = sorted(params.items())
        
        # 拼接参数字符串
        param_str = "&".join([f"{k}={v}" for k, v in sorted_params])
        
        # 添加密钥
        sign_str = param_str + self.secret_key
        
        # MD5签名
        sign = hashlib.md5(sign_str.encode()).hexdigest()
        
        return sign
    
    async def _request(
        self,
        method: str,
        url: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """发送API请求"""
        
        session = await self._get_session()
        
        try:
            # 添加通用参数
            if params is None:
                params = {}
            
            params.update({
                "appkey": self.access_key,
                "ts": int(time.time())
            })
            
            # 生成签名
            params["sign"] = self._generate_sign(params)
            
            # 发送请求
            async with session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json_data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                result = await resp.json()
                return result
        
        except Exception as e:
            print(f"❌ API请求失败: {e}")
            raise
    
    async def get_user_info(self) -> Dict[str, Any]:
        """获取用户信息"""
        
        try:
            result = await self._request(
                method="GET",
                url=f"{self.API_BASE}/x/space/myinfo"
            )
            
            if result.get("code") == 0:
                print("✅ 获取用户信息成功")
                return result.get("data", {})
            else:
                print(f"❌ 获取用户信息失败: {result.get('message')}")
                return {}
        
        except Exception as e:
            print(f"❌ 获取用户信息异常: {e}")
            return {}
    
    async def upload_video(
        self,
        video_path: str,
        title: str,
        desc: str,
        tid: int = 17,  # 分区ID，17=单机游戏
        tags: Optional[List[str]] = None,
        cover: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        上传视频
        
        Args:
            video_path: 视频文件路径
            title: 标题
            desc: 描述
            tid: 分区ID
            tags: 标签列表
            cover: 封面图片路径
        
        Returns:
            上传结果
        """
        
        print(f"📤 开始上传视频: {title}")
        
        try:
            # 注意：实际的视频上传流程较复杂，包括：
            # 1. 获取上传地址
            # 2. 分片上传视频文件
            # 3. 提交投稿信息
            # 
            # 这里提供简化的模拟实现
            
            # 1. 获取上传授权
            print("   1️⃣ 获取上传授权...")
            upload_auth = await self._get_upload_auth()
            
            if not upload_auth:
                return {
                    "success": False,
                    "message": "获取上传授权失败"
                }
            
            # 2. 上传视频文件
            print("   2️⃣ 上传视频文件...")
            video_url = await self._upload_video_file(video_path, upload_auth)
            
            if not video_url:
                return {
                    "success": False,
                    "message": "视频上传失败"
                }
            
            # 3. 上传封面（如果有）
            cover_url = None
            if cover:
                print("   3️⃣ 上传封面...")
                cover_url = await self._upload_cover(cover)
            
            # 4. 提交投稿
            print("   4️⃣ 提交投稿...")
            result = await self._submit_video(
                title=title,
                desc=desc,
                tid=tid,
                tags=tags or [],
                video_url=video_url,
                cover_url=cover_url
            )
            
            if result.get("code") == 0:
                print("✅ 视频上传成功")
                return {
                    "success": True,
                    "bvid": result.get("data", {}).get("bvid"),
                    "aid": result.get("data", {}).get("aid")
                }
            else:
                print(f"❌ 投稿失败: {result.get('message')}")
                return {
                    "success": False,
                    "message": result.get("message")
                }
        
        except Exception as e:
            print(f"❌ 上传视频异常: {e}")
            return {
                "success": False,
                "message": str(e)
            }
    
    async def _get_upload_auth(self) -> Optional[Dict]:
        """获取上传授权"""
        
        # 模拟实现
        # 实际需要调用：POST /x/vu/web/add
        print("      ℹ️  (模拟) 获取上传授权")
        return {"upload_id": "mock_upload_id"}
    
    async def _upload_video_file(
        self,
        video_path: str,
        upload_auth: Dict
    ) -> Optional[str]:
        """上传视频文件"""
        
        # 模拟实现
        # 实际需要：
        # 1. 分片上传到B站存储服务器
        # 2. 等待转码完成
        print(f"      ℹ️  (模拟) 上传视频文件: {video_path}")
        return "mock_video_url"
    
    async def _upload_cover(self, cover_path: str) -> Optional[str]:
        """上传封面"""
        
        # 模拟实现
        print(f"      ℹ️  (模拟) 上传封面: {cover_path}")
        return "mock_cover_url"
    
    async def _submit_video(
        self,
        title: str,
        desc: str,
        tid: int,
        tags: List[str],
        video_url: str,
        cover_url: Optional[str]
    ) -> Dict[str, Any]:
        """提交投稿"""
        
        # 模拟实现
        # 实际需要调用：POST /x/vu/web/add
        print("      ℹ️  (模拟) 提交投稿")
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "bvid": "BV1xx411c7mD",
                "aid": 123456789
            }
        }
    
    async def publish_dynamic(
        self,
        content: str,
        images: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        发布动态
        
        Args:
            content: 动态内容（最多233字）
            images: 图片路径列表（最多9张）
        
        Returns:
            发布结果
        """
        
        print(f"📤 发布动态: {content[:30]}...")
        
        try:
            # 检查长度
            if len(content) > 233:
                print("⚠️  动态内容超过233字，将自动截断")
                content = content[:233]
            
            # 上传图片（如果有）
            image_urls = []
            if images:
                print(f"   📸 上传 {len(images)} 张图片...")
                for img in images[:9]:  # 最多9张
                    url = await self._upload_dynamic_image(img)
                    if url:
                        image_urls.append(url)
            
            # 发布动态
            data = {
                "dynamic_id": 0,
                "type": 4,  # 纯文字动态
                "rid": 0,
                "content": content,
                "extension": {
                    "emoji_type": 1
                }
            }
            
            if image_urls:
                data["type"] = 2  # 带图片动态
                data["pictures"] = [
                    {"img_src": url} for url in image_urls
                ]
            
            result = await self._request(
                method="POST",
                url=f"{self.API_BASE}/x/dynamic/feed/create",
                json_data=data
            )
            
            if result.get("code") == 0:
                print("✅ 动态发布成功")
                return {
                    "success": True,
                    "dynamic_id": result.get("data", {}).get("dynamic_id")
                }
            else:
                print(f"❌ 动态发布失败: {result.get('message')}")
                return {
                    "success": False,
                    "message": result.get("message")
                }
        
        except Exception as e:
            print(f"❌ 发布动态异常: {e}")
            return {
                "success": False,
                "message": str(e)
            }
    
    async def _upload_dynamic_image(self, image_path: str) -> Optional[str]:
        """上传动态图片"""
        
        # 模拟实现
        print(f"      ℹ️  (模拟) 上传图片: {image_path}")
        return "mock_image_url"


# 测试代码
async def test_bilibili_api():
    """测试B站API客户端"""
    
    print("="*60)
    print("🧪 测试B站API客户端")
    print("="*60)
    
    # 创建客户端（使用测试密钥）
    client = BilibiliAPIClient(
        access_key="test_access_key",
        secret_key="test_secret_key",
        sessdata="test_sessdata"
    )
    
    try:
        # 测试1：获取用户信息
        print("\n1️⃣ 测试获取用户信息...")
        # user_info = await client.get_user_info()
        print("   ℹ️  (跳过，需要真实API密钥)")
        
        # 测试2：发布动态
        print("\n2️⃣ 测试发布动态...")
        result = await client.publish_dynamic(
            content="这是一条测试动态 #测试 #B站"
        )
        print(f"   结果: {result}")
        
        # 测试3：上传视频（模拟）
        print("\n3️⃣ 测试上传视频...")
        result = await client.upload_video(
            video_path="test_video.mp4",
            title="测试视频标题",
            desc="这是测试视频的描述",
            tags=["测试", "演示"]
        )
        print(f"   结果: {result}")
    
    finally:
        await client.close()
    
    print("\n" + "="*60)
    print("✅ 测试完成！")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_bilibili_api())

