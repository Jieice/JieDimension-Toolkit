"""
JieDimension Toolkit - Emoji智能优化器
为小红书内容智能插入合适的emoji表情
Version: 1.0.0
"""

import re
from typing import List, Dict, Optional


class EmojiOptimizer:
    """Emoji智能优化器"""
    
    # 分类emoji库
    EMOJI_MAP = {
        "美妆": {
            "核心": ["💄", "✨", "💅", "💋"],
            "辅助": ["🌟", "💫", "🎀", "💖", "🌺"],
            "强调": ["‼️", "❗", "💯", "🔥"],
        },
        "美食": {
            "核心": ["🍰", "🍜", "🥗", "☕", "🍵"],
            "辅助": ["😋", "🤤", "👍", "💕"],
            "强调": ["🔥", "💯", "✨", "❗"],
        },
        "穿搭": {
            "核心": ["👗", "👠", "💃", "🛍️"],
            "辅助": ["✨", "💫", "🎀", "💖"],
            "强调": ["🔥", "💯", "‼️", "👌"],
        },
        "好物": {
            "核心": ["✨", "🌟", "💯", "🔥"],
            "辅助": ["👍", "💕", "💖", "🎁"],
            "强调": ["❗", "‼️", "💪", "👏"],
        },
        "教程": {
            "核心": ["📝", "✅", "💡", "🎯"],
            "辅助": ["📌", "💪", "👍", "🔧"],
            "强调": ["‼️", "❗", "💯", "🔥"],
        },
        "旅行": {
            "核心": ["✈️", "🏖️", "🗺️", "📷"],
            "辅助": ["🌈", "☀️", "🌸", "💕"],
            "强调": ["✨", "💫", "🔥", "💯"],
        },
        "健身": {
            "核心": ["💪", "🏃", "🧘", "🏋️"],
            "辅助": ["🔥", "💯", "✨", "💦"],
            "强调": ["❗", "‼️", "👏", "🎯"],
        },
        "学习": {
            "核心": ["📚", "✏️", "📝", "💡"],
            "辅助": ["💪", "✨", "🎯", "📌"],
            "强调": ["‼️", "❗", "💯", "🔥"],
        },
    }
    
    # 情感emoji
    EMOTION_EMOJI = {
        "开心": ["😊", "😄", "🥰", "😍", "🤩"],
        "惊讶": ["😲", "😱", "🤯", "😳", "😮"],
        "爱心": ["❤️", "💕", "💖", "💗", "💓"],
        "赞叹": ["👍", "👏", "💯", "🔥", "✨"],
        "疑问": ["❓", "🤔", "💭", "❔", "⁉️"],
        "警告": ["⚠️", "❌", "⛔", "🚫", "💢"],
    }
    
    # 动作emoji
    ACTION_EMOJI = {
        "推荐": "👉",
        "收藏": "📌",
        "分享": "📢",
        "关注": "⭐",
        "点赞": "👍",
        "查看": "👀",
        "购买": "🛒",
        "使用": "✋",
    }
    
    # 位置emoji（用于不同位置的emoji选择）
    POSITION_EMOJI = {
        "开头": ["✨", "💕", "🌟", "💖"],  # 吸引注意
        "结尾": ["💕", "✨", "💖", "🥰"],  # 增强情感
        "强调": ["‼️", "❗", "💯", "🔥"],  # 重点强调
    }
    
    def __init__(self):
        """初始化优化器"""
        pass
    
    def optimize_emoji(
        self,
        text: str,
        category: str,
        intensity: str = "medium"
    ) -> str:
        """
        为文本智能插入emoji
        
        Args:
            text: 原始文本
            category: 内容分类（美妆/美食/穿搭等）
            intensity: emoji强度（low/medium/high）
            
        Returns:
            优化后的文本
        """
        # 获取分类对应的emoji
        emoji_set = self.EMOJI_MAP.get(category, self.EMOJI_MAP["好物"])
        
        # 根据强度选择emoji数量
        emoji_count = {
            "low": {"核心": 1, "辅助": 1, "强调": 0},
            "medium": {"核心": 1, "辅助": 2, "强调": 1},
            "high": {"核心": 2, "辅助": 3, "强调": 2},
        }
        
        counts = emoji_count.get(intensity, emoji_count["medium"])
        
        # 在关键位置插入emoji
        optimized = self._insert_strategic_emoji(
            text, 
            emoji_set, 
            counts
        )
        
        return optimized
    
    def _insert_strategic_emoji(
        self,
        text: str,
        emoji_set: Dict[str, List[str]],
        counts: Dict[str, int]
    ) -> str:
        """
        在关键位置插入emoji
        
        Args:
            text: 原文本
            emoji_set: emoji集合
            counts: 各类emoji数量
            
        Returns:
            插入emoji后的文本
        """
        # 分句
        sentences = text.split('！')
        if len(sentences) == 1:
            sentences = text.split('。')
        
        result = []
        import random
        
        for i, sentence in enumerate(sentences):
            if not sentence.strip():
                continue
            
            # 清理已有的emoji（避免重复）
            sentence = self._remove_existing_emoji(sentence)
            
            # 在句子开头（第一句）
            if i == 0:
                emoji = random.choice(self.POSITION_EMOJI["开头"])
                sentence = emoji + " " + sentence.strip()
            
            # 在句子结尾
            if random.random() > 0.5 and counts["辅助"] > 0:
                emoji = random.choice(emoji_set["辅助"])
                sentence = sentence.strip() + " " + emoji
                counts["辅助"] -= 1
            
            # 添加强调emoji
            if ("真的" in sentence or "超级" in sentence or "太" in sentence) and counts["强调"] > 0:
                emoji = random.choice(emoji_set["强调"])
                # 在强调词后面插入
                for keyword in ["真的", "超级", "太"]:
                    if keyword in sentence:
                        sentence = sentence.replace(keyword, keyword + emoji, 1)
                        counts["强调"] -= 1
                        break
            
            result.append(sentence)
        
        # 重新组合
        optimized = '！'.join(result) if '！' in text else '。'.join(result)
        
        # 确保结尾有emoji
        if not self._has_emoji_at_end(optimized):
            emoji = random.choice(self.POSITION_EMOJI["结尾"])
            optimized += " " + emoji
        
        return optimized
    
    def add_emotion_emoji(
        self,
        text: str,
        emotion: str
    ) -> str:
        """
        添加情感emoji
        
        Args:
            text: 文本
            emotion: 情感类型（开心/惊讶/爱心等）
            
        Returns:
            添加情感emoji后的文本
        """
        emojis = self.EMOTION_EMOJI.get(emotion, self.EMOTION_EMOJI["开心"])
        
        import random
        emoji = random.choice(emojis)
        
        # 在文本末尾添加
        return text.strip() + " " + emoji
    
    def add_action_emoji(
        self,
        text: str,
        action: str
    ) -> str:
        """
        添加动作emoji
        
        Args:
            text: 文本
            action: 动作类型（推荐/收藏/分享等）
            
        Returns:
            添加动作emoji后的文本
        """
        emoji = self.ACTION_EMOJI.get(action, "👉")
        
        # 在动作词前面添加
        if action in text:
            return text.replace(action, emoji + " " + action, 1)
        else:
            return emoji + " " + text
    
    def _has_emoji_at_end(self, text: str) -> bool:
        """检查文本末尾是否有emoji"""
        # 简单检查最后几个字符
        emoji_pattern = re.compile(
            "[\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE
        )
        
        # 检查最后5个字符
        return bool(emoji_pattern.search(text[-5:] if len(text) > 5 else text))
    
    def _remove_existing_emoji(self, text: str) -> str:
        """移除文本中已有的emoji"""
        emoji_pattern = re.compile(
            "[\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE
        )
        
        return emoji_pattern.sub('', text).strip()
    
    def optimize_title_emoji(self, title: str, category: str) -> str:
        """
        优化标题的emoji使用
        
        Args:
            title: 标题文本
            category: 内容分类
            
        Returns:
            优化后的标题
        """
        # 移除原有emoji
        clean_title = self._remove_existing_emoji(title)
        
        # 获取合适的emoji
        emoji_set = self.EMOJI_MAP.get(category, self.EMOJI_MAP["好物"])
        
        import random
        
        # 选择1-2个emoji
        selected_emojis = []
        selected_emojis.append(random.choice(emoji_set["核心"]))
        
        if len(clean_title) > 15:  # 较长标题可以多一个emoji
            selected_emojis.append(random.choice(emoji_set["辅助"]))
        
        # 组合标题（emoji放在结尾）
        optimized = clean_title + " " + " ".join(selected_emojis)
        
        return optimized


# 测试函数
def test_emoji_optimizer():
    """测试Emoji优化器"""
    print("="*60)
    print("🧪 测试Emoji优化器")
    print("="*60)
    
    optimizer = EmojiOptimizer()
    
    # 测试1：美妆内容
    print("\n📝 测试1：美妆内容优化")
    print("-"*60)
    
    text1 = "这款口红真的太好用了！颜色超级显白，而且不沾杯。质地很滋润，持久度也很棒。强烈推荐给大家。"
    
    print(f"原文：{text1}")
    print()
    
    optimized1 = optimizer.optimize_emoji(text1, "美妆", "medium")
    print(f"优化后：{optimized1}")
    
    # 测试2：美食内容
    print("\n📝 测试2：美食内容优化")
    print("-"*60)
    
    text2 = "周末在家做了蛋糕！第一次尝试就成功了。味道很不错，家人都说好吃。"
    
    print(f"原文：{text2}")
    print()
    
    optimized2 = optimizer.optimize_emoji(text2, "美食", "high")
    print(f"优化后：{optimized2}")
    
    # 测试3：标题优化
    print("\n📝 测试3：标题Emoji优化")
    print("-"*60)
    
    title = "学生党平价护肤品分享｜超好用不踩雷"
    
    print(f"原标题：{title}")
    print()
    
    optimized_title = optimizer.optimize_title_emoji(title, "好物")
    print(f"优化后：{optimized_title}")
    
    # 测试4：情感emoji
    print("\n📝 测试4：添加情感Emoji")
    print("-"*60)
    
    text3 = "收到礼物的那一刻"
    
    print(f"原文：{text3}")
    optimized3 = optimizer.add_emotion_emoji(text3, "开心")
    print(f"添加开心：{optimized3}")
    
    optimized4 = optimizer.add_emotion_emoji(text3, "惊讶")
    print(f"添加惊讶：{optimized4}")
    
    print("\n" + "="*60)
    print("✅ 测试完成")
    print("="*60)


if __name__ == "__main__":
    test_emoji_optimizer()

