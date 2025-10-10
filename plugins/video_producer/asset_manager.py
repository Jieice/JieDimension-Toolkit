"""
素材管理器
管理表情包、背景图、音乐等素材
"""

import os
from pathlib import Path
from typing import List, Dict
import shutil
import logging

logger = logging.getLogger(__name__)


class AssetManager:
    """素材管理器"""
    
    def __init__(self):
        """初始化素材管理器"""
        # 素材目录
        self.base_dir = Path("data/assets")
        self.emoji_dir = self.base_dir / "emojis"
        self.bg_dir = self.base_dir / "backgrounds"
        self.music_dir = self.base_dir / "music"
        
        # 创建目录
        for dir_path in [self.emoji_dir, self.bg_dir, self.music_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def get_emojis(self) -> List[str]:
        """获取所有表情包"""
        return [str(f) for f in self.emoji_dir.glob("*.png")] + \
               [str(f) for f in self.emoji_dir.glob("*.jpg")]
    
    def get_backgrounds(self) -> List[str]:
        """获取所有背景图"""
        return [str(f) for f in self.bg_dir.glob("*.png")] + \
               [str(f) for f in self.bg_dir.glob("*.jpg")]
    
    def get_music(self) -> List[str]:
        """获取所有音乐"""
        return [str(f) for f in self.music_dir.glob("*.mp3")] + \
               [str(f) for f in self.music_dir.glob("*.wav")]
    
    def add_emoji(self, file_path: str) -> bool:
        """添加表情包"""
        try:
            dest = self.emoji_dir / Path(file_path).name
            shutil.copy(file_path, dest)
            logger.info(f"✅ 表情包已添加: {dest.name}")
            return True
        except Exception as e:
            logger.error(f"添加表情包失败: {e}")
            return False
    
    def add_background(self, file_path: str) -> bool:
        """添加背景图"""
        try:
            dest = self.bg_dir / Path(file_path).name
            shutil.copy(file_path, dest)
            logger.info(f"✅ 背景图已添加: {dest.name}")
            return True
        except Exception as e:
            logger.error(f"添加背景图失败: {e}")
            return False
    
    def add_music(self, file_path: str) -> bool:
        """添加音乐"""
        try:
            dest = self.music_dir / Path(file_path).name
            shutil.copy(file_path, dest)
            logger.info(f"✅ 音乐已添加: {dest.name}")
            return True
        except Exception as e:
            logger.error(f"添加音乐失败: {e}")
            return False
    
    def delete_asset(self, asset_path: str) -> bool:
        """删除素材"""
        try:
            Path(asset_path).unlink()
            logger.info(f"✅ 素材已删除")
            return True
        except Exception as e:
            logger.error(f"删除素材失败: {e}")
            return False
    
    def get_asset_info(self) -> Dict:
        """获取素材统计信息"""
        return {
            "emojis": len(self.get_emojis()),
            "backgrounds": len(self.get_backgrounds()),
            "music": len(self.get_music())
        }

