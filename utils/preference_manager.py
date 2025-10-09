"""
JieDimension Toolkit - 用户偏好管理器
保存和加载用户的输入历史和偏好设置
Version: 1.0.0
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PreferenceManager:
    """用户偏好管理器"""
    
    def __init__(self, config_file: str = "config/user_preferences.json"):
        """
        初始化偏好管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.preferences = self._load_preferences()
    
    def _load_preferences(self) -> Dict[str, Any]:
        """加载偏好设置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.warning(f"加载偏好设置失败: {e}")
            return {}
    
    def _save_preferences(self):
        """保存偏好设置"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, ensure_ascii=False, indent=2)
            
            logger.info("偏好设置已保存")
        except Exception as e:
            logger.error(f"保存偏好设置失败: {e}")
    
    def save_last_input(self, tab_name: str, data: Dict[str, Any]):
        """
        保存用户最后输入
        
        Args:
            tab_name: Tab标识（如'xiaohongshu', 'zhihu'等）
            data: 输入数据字典
        """
        if tab_name not in self.preferences:
            self.preferences[tab_name] = {}
        
        self.preferences[tab_name]["last_input"] = data
        self._save_preferences()
    
    def load_last_input(self, tab_name: str) -> Optional[Dict[str, Any]]:
        """
        加载用户最后输入
        
        Args:
            tab_name: Tab标识
            
        Returns:
            输入数据字典，如果不存在返回None
        """
        return self.preferences.get(tab_name, {}).get("last_input")
    
    def save_preference(self, tab_name: str, key: str, value: Any):
        """
        保存单个偏好设置
        
        Args:
            tab_name: Tab标识
            key: 设置键
            value: 设置值
        """
        if tab_name not in self.preferences:
            self.preferences[tab_name] = {}
        
        self.preferences[tab_name][key] = value
        self._save_preferences()
    
    def get_preference(self, tab_name: str, key: str, default: Any = None) -> Any:
        """
        获取单个偏好设置
        
        Args:
            tab_name: Tab标识
            key: 设置键
            default: 默认值
            
        Returns:
            设置值，如果不存在返回默认值
        """
        return self.preferences.get(tab_name, {}).get(key, default)
    
    def add_to_history(self, tab_name: str, history_key: str, value: str, max_items: int = 10):
        """
        添加到历史记录
        
        Args:
            tab_name: Tab标识
            history_key: 历史记录键（如'topics', 'keywords'）
            value: 要添加的值
            max_items: 最大保留数量
        """
        if tab_name not in self.preferences:
            self.preferences[tab_name] = {}
        
        if history_key not in self.preferences[tab_name]:
            self.preferences[tab_name][history_key] = []
        
        history = self.preferences[tab_name][history_key]
        
        # 如果已存在，先删除
        if value in history:
            history.remove(value)
        
        # 添加到最前面
        history.insert(0, value)
        
        # 限制数量
        self.preferences[tab_name][history_key] = history[:max_items]
        
        self._save_preferences()
    
    def get_history(self, tab_name: str, history_key: str) -> list:
        """
        获取历史记录
        
        Args:
            tab_name: Tab标识
            history_key: 历史记录键
            
        Returns:
            历史记录列表
        """
        return self.preferences.get(tab_name, {}).get(history_key, [])
    
    def clear_history(self, tab_name: str, history_key: Optional[str] = None):
        """
        清除历史记录
        
        Args:
            tab_name: Tab标识
            history_key: 历史记录键，如果为None则清除该Tab所有历史
        """
        if tab_name in self.preferences:
            if history_key:
                if history_key in self.preferences[tab_name]:
                    del self.preferences[tab_name][history_key]
            else:
                del self.preferences[tab_name]
            
            self._save_preferences()


# 全局单例
_preference_manager = None

def get_preference_manager() -> PreferenceManager:
    """获取全局偏好管理器单例"""
    global _preference_manager
    if _preference_manager is None:
        _preference_manager = PreferenceManager()
    return _preference_manager

