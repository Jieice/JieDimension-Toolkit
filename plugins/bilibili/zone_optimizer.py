"""
B站分区优化器

功能：
- 分区特点分析
- 内容风格适配
- 分区规则建议
"""

from typing import Dict, List, Any, Optional


class BilibiliZoneOptimizer:
    """B站分区优化器"""
    
    # B站主要分区配置
    ZONES = {
        "游戏": {
            "description": "游戏视频、游戏解说、游戏攻略",
            "keywords": ["游戏", "攻略", "教程", "实况", "解说", "通关", "测评"],
            "title_style": "激情型",
            "content_features": [
                "强调游戏体验和感受",
                "技巧分享和教学",
                "激情解说风格",
                "高能片段剪辑"
            ],
            "emoji": ["🎮", "🎯", "🔥", "⚡", "💪"],
            "length_suggest": {
                "title": "30-60字，悬念感强",
                "intro": "简短有力，1-2句话",
                "video": "10-30分钟最佳"
            },
            "hot_topics": ["原神", "王者荣耀", "英雄联盟", "和平精英", "我的世界"],
        },
        "科技": {
            "description": "数码评测、科技资讯、教程分享",
            "keywords": ["科技", "数码", "评测", "开箱", "教程", "对比", "测试"],
            "title_style": "专业型",
            "content_features": [
                "客观评测和数据展示",
                "详细参数对比",
                "专业术语使用",
                "理性分析"
            ],
            "emoji": ["💻", "📱", "🔧", "⚙️", "📊"],
            "length_suggest": {
                "title": "25-50字，突出产品名",
                "intro": "说明测试环境和方法",
                "video": "8-25分钟"
            },
            "hot_topics": ["手机", "电脑", "AI", "数码", "黑科技"],
        },
        "知识": {
            "description": "科普知识、教程分享、技能学习",
            "keywords": ["知识", "科普", "教程", "学习", "干货", "技巧", "原理"],
            "title_style": "教学型",
            "content_features": [
                "逻辑清晰，结构分明",
                "知识点详细讲解",
                "配合图表演示",
                "实用性强"
            ],
            "emoji": ["📚", "🎓", "💡", "✍️", "🧠"],
            "length_suggest": {
                "title": "20-45字，问题导向",
                "intro": "明确学习目标和收获",
                "video": "15-45分钟"
            },
            "hot_topics": ["编程", "设计", "英语", "数学", "物理"],
        },
        "生活": {
            "description": "日常生活、美食、旅行、Vlog",
            "keywords": ["生活", "日常", "vlog", "美食", "旅行", "分享", "记录"],
            "title_style": "亲切型",
            "content_features": [
                "真实自然的记录",
                "个人风格突出",
                "情感共鸣",
                "轻松愉快"
            ],
            "emoji": ["🏠", "☕", "📷", "🌸", "💝"],
            "length_suggest": {
                "title": "15-40字，生活化表达",
                "intro": "轻松开场，引发共鸣",
                "video": "5-20分钟"
            },
            "hot_topics": ["美食", "穿搭", "好物", "探店", "日常"],
        },
        "娱乐": {
            "description": "搞笑、影视、音乐、娱乐内容",
            "keywords": ["娱乐", "搞笑", "影视", "音乐", "沙雕", "整活", "鬼畜"],
            "title_style": "趣味型",
            "content_features": [
                "轻松搞笑风格",
                "创意剪辑",
                "梗和流行元素",
                "娱乐性优先"
            ],
            "emoji": ["😂", "🎬", "🎵", "🎪", "🎉"],
            "length_suggest": {
                "title": "20-45字，吸引眼球",
                "intro": "快速进入主题",
                "video": "3-15分钟"
            },
            "hot_topics": ["电影", "综艺", "明星", "音乐", "搞笑"],
        },
    }
    
    def get_zone_info(self, zone: str) -> Dict[str, Any]:
        """
        获取分区详细信息
        
        Args:
            zone: 分区名称
            
        Returns:
            分区配置信息
        """
        return self.ZONES.get(zone, self.ZONES["生活"])
    
    def suggest_zone(
        self,
        title: str,
        content: str
    ) -> List[Dict[str, Any]]:
        """
        根据内容推荐合适的分区
        
        Args:
            title: 标题
            content: 内容描述
            
        Returns:
            推荐分区列表，包含匹配度
        """
        
        text = f"{title} {content}".lower()
        suggestions = []
        
        for zone_name, zone_info in self.ZONES.items():
            # 计算关键词匹配度
            keywords = zone_info["keywords"]
            match_count = sum(1 for kw in keywords if kw in text)
            match_score = (match_count / len(keywords)) * 100
            
            if match_score > 0:
                suggestions.append({
                    "zone": zone_name,
                    "score": round(match_score, 1),
                    "description": zone_info["description"],
                    "matched_keywords": [kw for kw in keywords if kw in text]
                })
        
        # 按匹配度排序
        suggestions.sort(key=lambda x: x["score"], reverse=True)
        return suggestions
    
    def get_style_suggestions(self, zone: str) -> Dict[str, Any]:
        """
        获取分区风格建议
        
        Args:
            zone: 分区名称
            
        Returns:
            风格建议（标题、内容、长度等）
        """
        
        zone_info = self.get_zone_info(zone)
        
        return {
            "zone": zone,
            "title_style": zone_info["title_style"],
            "content_features": zone_info["content_features"],
            "emoji_suggestions": zone_info["emoji"],
            "length_suggest": zone_info["length_suggest"],
            "hot_topics": zone_info["hot_topics"][:5],
        }
    
    def optimize_for_zone(
        self,
        content: Dict[str, str],
        zone: str
    ) -> Dict[str, Any]:
        """
        针对特定分区优化内容
        
        Args:
            content: 内容数据
                - title: 标题
                - description: 描述
                - tags: 标签列表
            zone: 目标分区
            
        Returns:
            优化建议
        """
        
        zone_info = self.get_zone_info(zone)
        suggestions = []
        
        # 1. 检查标题长度
        title = content.get("title", "")
        title_len = len(title)
        length_suggest = zone_info["length_suggest"]["title"]
        
        if "30-60" in length_suggest and (title_len < 30 or title_len > 60):
            suggestions.append({
                "type": "标题长度",
                "issue": f"当前{title_len}字，建议{length_suggest}",
                "priority": "中"
            })
        
        # 2. 检查关键词使用
        text = f"{title} {content.get('description', '')}".lower()
        zone_keywords = zone_info["keywords"]
        matched = [kw for kw in zone_keywords if kw in text]
        
        if len(matched) < 2:
            suggestions.append({
                "type": "关键词优化",
                "issue": f"建议包含更多分区关键词，如：{', '.join(zone_keywords[:3])}",
                "priority": "高"
            })
        
        # 3. Emoji建议
        has_emoji = any(emoji in title for emoji in zone_info["emoji"])
        if not has_emoji and zone in ["游戏", "生活", "娱乐"]:
            suggestions.append({
                "type": "Emoji使用",
                "issue": f"建议添加emoji增强表现力，推荐：{' '.join(zone_info['emoji'][:3])}",
                "priority": "低"
            })
        
        return {
            "zone": zone,
            "suggestions": suggestions,
            "score": self._calculate_zone_fit_score(content, zone_info),
            "style_guide": zone_info["content_features"]
        }
    
    def _calculate_zone_fit_score(
        self,
        content: Dict[str, str],
        zone_info: Dict[str, Any]
    ) -> float:
        """计算内容与分区的匹配度（0-100分）"""
        
        score = 0.0
        text = f"{content.get('title', '')} {content.get('description', '')}".lower()
        
        # 关键词匹配（50分）
        keywords = zone_info["keywords"]
        match_count = sum(1 for kw in keywords if kw in text)
        score += (match_count / len(keywords)) * 50
        
        # 标题长度合适性（20分）
        title_len = len(content.get("title", ""))
        if 20 <= title_len <= 60:
            score += 20
        elif 10 <= title_len < 20 or 60 < title_len <= 80:
            score += 10
        
        # 热门话题（30分）
        hot_topics = zone_info["hot_topics"]
        topic_match = sum(1 for topic in hot_topics if topic in text)
        score += (topic_match / len(hot_topics)) * 30
        
        return round(score, 1)
    
    def get_all_zones(self) -> List[str]:
        """获取所有分区列表"""
        return list(self.ZONES.keys())


# ===== 测试代码 =====

def test_bilibili_zone_optimizer():
    """测试B站分区优化器"""
    
    print("="*60)
    print("🎯 测试B站分区优化器")
    print("="*60)
    
    optimizer = BilibiliZoneOptimizer()
    
    # 测试1：获取分区信息
    print("\n【测试1：获取游戏区信息】")
    zone_info = optimizer.get_zone_info("游戏")
    print(f"分区：{zone_info['description']}")
    print(f"风格：{zone_info['title_style']}")
    print(f"关键词：{', '.join(zone_info['keywords'][:5])}")
    print(f"建议emoji：{' '.join(zone_info['emoji'])}")
    
    # 测试2：推荐分区
    print("\n【测试2：内容分区推荐】")
    suggestions = optimizer.suggest_zone(
        title="iPhone 16 Pro深度评测",
        content="详细测试了拍照、性能、续航等方面，并与上一代对比"
    )
    print("推荐分区：")
    for sug in suggestions[:3]:
        print(f"  • {sug['zone']}: {sug['score']}分 "
              f"(匹配词: {', '.join(sug['matched_keywords'][:3])})")
    
    # 测试3：分区优化建议
    print("\n【测试3：分区优化建议】")
    result = optimizer.optimize_for_zone(
        content={
            "title": "游戏",
            "description": "好玩",
            "tags": ["游戏"]
        },
        zone="游戏"
    )
    print(f"匹配度：{result['score']}分")
    print("优化建议：")
    for sug in result['suggestions']:
        print(f"  [{sug['priority']}] {sug['type']}: {sug['issue']}")
    
    # 测试4：风格建议
    print("\n【测试4：知识区风格建议】")
    style = optimizer.get_style_suggestions("知识")
    print(f"标题风格：{style['title_style']}")
    print("内容特点：")
    for feature in style['content_features'][:3]:
        print(f"  • {feature}")
    
    print("\n" + "="*60)
    print("✅ 测试完成！")
    print("="*60)


if __name__ == "__main__":
    test_bilibili_zone_optimizer()

