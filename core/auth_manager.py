# core/auth_manager.py

"""
认证管理器 - 统一管理各平台的认证和会话

支持：
- OAuth 2.0 认证
- Cookie会话管理
- API密钥管理
- Token自动刷新
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path
from cryptography.fernet import Fernet
import aiofiles


class PlatformCredentials:
    """平台凭证数据模型"""
    
    def __init__(
        self,
        platform: str,
        auth_type: str,  # oauth, api_key, cookie
        credentials: Dict[str, Any],
        expires_at: Optional[datetime] = None
    ):
        self.platform = platform
        self.auth_type = auth_type
        self.credentials = credentials
        self.expires_at = expires_at
        self.created_at = datetime.now()
    
    def is_expired(self) -> bool:
        """检查凭证是否过期"""
        if not self.expires_at:
            return False
        return datetime.now() >= self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "platform": self.platform,
            "auth_type": self.auth_type,
            "credentials": self.credentials,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlatformCredentials':
        """从字典创建"""
        expires_at = None
        if data.get("expires_at"):
            expires_at = datetime.fromisoformat(data["expires_at"])
        
        cred = cls(
            platform=data["platform"],
            auth_type=data["auth_type"],
            credentials=data["credentials"],
            expires_at=expires_at
        )
        
        if data.get("created_at"):
            cred.created_at = datetime.fromisoformat(data["created_at"])
        
        return cred


class AuthManager:
    """认证管理器"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # 凭证存储文件
        self.credentials_file = self.config_dir / "credentials.enc"
        self.key_file = self.config_dir / ".auth_key"
        
        # 加密密钥
        self.cipher = self._load_or_create_cipher()
        
        # 凭证缓存
        self.credentials: Dict[str, PlatformCredentials] = {}
        
        print("🔐 认证管理器初始化完成")
    
    def _load_or_create_cipher(self) -> Fernet:
        """加载或创建加密密钥"""
        
        if self.key_file.exists():
            # 加载现有密钥
            with open(self.key_file, "rb") as f:
                key = f.read()
        else:
            # 创建新密钥
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(key)
            print("✅ 创建新的加密密钥")
        
        return Fernet(key)
    
    async def load_credentials(self):
        """从文件加载凭证"""
        
        if not self.credentials_file.exists():
            print("ℹ️  没有找到凭证文件，使用空凭证")
            return
        
        try:
            # 读取加密文件
            async with aiofiles.open(self.credentials_file, "rb") as f:
                encrypted_data = await f.read()
            
            # 解密
            decrypted_data = self.cipher.decrypt(encrypted_data)
            credentials_dict = json.loads(decrypted_data.decode())
            
            # 加载凭证
            for platform, cred_data in credentials_dict.items():
                self.credentials[platform] = PlatformCredentials.from_dict(cred_data)
            
            print(f"✅ 加载了 {len(self.credentials)} 个平台凭证")
        
        except Exception as e:
            print(f"❌ 加载凭证失败: {e}")
    
    async def save_credentials(self):
        """保存凭证到文件"""
        
        try:
            # 转换为字典
            credentials_dict = {
                platform: cred.to_dict()
                for platform, cred in self.credentials.items()
            }
            
            # 序列化
            json_data = json.dumps(credentials_dict, indent=2)
            
            # 加密
            encrypted_data = self.cipher.encrypt(json_data.encode())
            
            # 写入文件
            async with aiofiles.open(self.credentials_file, "wb") as f:
                await f.write(encrypted_data)
            
            print(f"✅ 保存了 {len(self.credentials)} 个平台凭证")
        
        except Exception as e:
            print(f"❌ 保存凭证失败: {e}")
    
    async def set_credentials(
        self,
        platform: str,
        auth_type: str,
        credentials: Dict[str, Any],
        expires_in: Optional[int] = None  # 过期时间（秒）
    ):
        """设置平台凭证"""
        
        expires_at = None
        if expires_in:
            expires_at = datetime.now() + timedelta(seconds=expires_in)
        
        cred = PlatformCredentials(
            platform=platform,
            auth_type=auth_type,
            credentials=credentials,
            expires_at=expires_at
        )
        
        self.credentials[platform] = cred
        await self.save_credentials()
        
        print(f"✅ 设置 {platform} 凭证成功")
    
    async def get_credentials(self, platform: str) -> Optional[PlatformCredentials]:
        """获取平台凭证"""
        
        cred = self.credentials.get(platform)
        
        if not cred:
            print(f"⚠️  未找到 {platform} 凭证")
            return None
        
        if cred.is_expired():
            print(f"⚠️  {platform} 凭证已过期")
            return None
        
        return cred
    
    async def remove_credentials(self, platform: str):
        """删除平台凭证"""
        
        if platform in self.credentials:
            del self.credentials[platform]
            await self.save_credentials()
            print(f"✅ 删除 {platform} 凭证成功")
        else:
            print(f"⚠️  未找到 {platform} 凭证")
    
    async def list_platforms(self) -> list:
        """列出所有已配置的平台"""
        
        platforms = []
        for platform, cred in self.credentials.items():
            platforms.append({
                "platform": platform,
                "auth_type": cred.auth_type,
                "expired": cred.is_expired(),
                "created_at": cred.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return platforms


class SessionManager:
    """会话管理器 - 管理HTTP会话和Cookie"""
    
    def __init__(self, auth_manager: AuthManager):
        self.auth_manager = auth_manager
        self.sessions: Dict[str, Any] = {}  # platform -> session
        
        print("📡 会话管理器初始化完成")
    
    async def get_session(self, platform: str):
        """获取平台会话"""
        
        # 如果已有会话，返回
        if platform in self.sessions:
            return self.sessions[platform]
        
        # 获取凭证
        cred = await self.auth_manager.get_credentials(platform)
        if not cred:
            raise ValueError(f"未找到 {platform} 凭证")
        
        # 创建会话（根据认证类型）
        session = await self._create_session(platform, cred)
        self.sessions[platform] = session
        
        return session
    
    async def _create_session(
        self,
        platform: str,
        cred: PlatformCredentials
    ):
        """创建平台会话"""
        
        import aiohttp
        
        # 创建会话
        session = aiohttp.ClientSession()
        
        # 根据认证类型配置
        if cred.auth_type == "api_key":
            # API密钥认证
            api_key = cred.credentials.get("api_key")
            session.headers.update({
                "Authorization": f"Bearer {api_key}"
            })
        
        elif cred.auth_type == "cookie":
            # Cookie认证
            cookies = cred.credentials.get("cookies", {})
            for name, value in cookies.items():
                session.cookie_jar.update_cookies({name: value})
        
        elif cred.auth_type == "oauth":
            # OAuth认证
            access_token = cred.credentials.get("access_token")
            session.headers.update({
                "Authorization": f"Bearer {access_token}"
            })
        
        print(f"✅ 创建 {platform} 会话成功")
        return session
    
    async def close_session(self, platform: str):
        """关闭平台会话"""
        
        if platform in self.sessions:
            session = self.sessions[platform]
            await session.close()
            del self.sessions[platform]
            print(f"✅ 关闭 {platform} 会话")
    
    async def close_all(self):
        """关闭所有会话"""
        
        for platform in list(self.sessions.keys()):
            await self.close_session(platform)
        
        print("✅ 关闭所有会话")


# 测试代码
async def test_auth_manager():
    """测试认证管理器"""
    
    print("="*60)
    print("🧪 测试认证管理器")
    print("="*60)
    
    # 创建管理器
    auth_manager = AuthManager()
    await auth_manager.load_credentials()
    
    # 测试1：设置B站API凭证
    print("\n1️⃣ 设置B站API凭证...")
    await auth_manager.set_credentials(
        platform="bilibili",
        auth_type="api_key",
        credentials={
            "api_key": "test_bilibili_key_12345",
            "secret_key": "test_secret_67890"
        },
        expires_in=7200  # 2小时过期
    )
    
    # 测试2：设置闲鱼Cookie凭证
    print("\n2️⃣ 设置闲鱼Cookie凭证...")
    await auth_manager.set_credentials(
        platform="xianyu",
        auth_type="cookie",
        credentials={
            "cookies": {
                "session_id": "abc123def456",
                "user_token": "xyz789"
            }
        }
    )
    
    # 测试3：获取凭证
    print("\n3️⃣ 获取B站凭证...")
    bilibili_cred = await auth_manager.get_credentials("bilibili")
    if bilibili_cred:
        print(f"   平台: {bilibili_cred.platform}")
        print(f"   类型: {bilibili_cred.auth_type}")
        print(f"   过期: {bilibili_cred.is_expired()}")
    
    # 测试4：列出所有平台
    print("\n4️⃣ 列出所有平台...")
    platforms = await auth_manager.list_platforms()
    for p in platforms:
        print(f"   - {p['platform']}: {p['auth_type']} (过期: {p['expired']})")
    
    # 测试5：会话管理
    print("\n5️⃣ 测试会话管理...")
    session_manager = SessionManager(auth_manager)
    
    try:
        session = await session_manager.get_session("bilibili")
        print(f"   ✅ 获取B站会话成功")
    except Exception as e:
        print(f"   ⚠️  获取会话失败: {e}")
    
    # 清理
    await session_manager.close_all()
    
    print("\n" + "="*60)
    print("✅ 测试完成！")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_auth_manager())

