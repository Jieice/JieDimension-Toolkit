"""
B站标签推荐器

功能：
- 智能推荐10个相关标签
- 热门标签库
- 长尾标签生成
- 标签热度评估
"""

import asyncio
from typing import List, Dict, Any, Optional
from core.ai_engine import AIEngine, TaskComplexity


class BilibiliTagRecommender:
    """B站标签推荐器"""
    
    # 各分区热门标签库
    HOT_TAGS = {
        "游戏": {
            "通用": ["游戏", "单机游戏", "手机游戏", "主机游戏", "电子竞技"],
            "热门": ["原神", "王者荣耀", "和平精英", "英雄联盟", "我的世界"],
            "类型": ["RPG", "FPS", "MOBA", "沙盒游戏", "卡牌游戏"],
            "内容": ["游戏解说", "游戏攻略", "游戏实况", "游戏测评", "游戏剪辑"],
        },
        "科技": {
            "通用": ["科技", "数码", "评测", "开箱", "DIY"],
            "设备": ["手机", "电脑", "笔记本", "平板", "耳机"],
            "品牌": ["苹果", "华为", "小米", "OPPO", "vivo"],
            "技术": ["AI", "人工智能", "编程", "黑科技", "科技分享"],
        },
        "知识": {
            "通用": ["知识", "科普", "教程", "学习", "干货"],
            "学科": ["数学", "物理", "化学", "历史", "地理"],
            "技能": ["编程教程", "设计教程", "外语学习", "职场技能"],
            "内容": ["知识分享", "硬核知识", "冷知识", "涨知识"],
        },
        "生活": {
            "通用": ["生活", "日常", "vlog", "分享", "记录"],
            "美食": ["美食", "吃播", "探店", "美食教程", "家常菜"],
            "穿搭": ["穿搭", "时尚", "搭配", "好物分享"],
            "旅行": ["旅行", "旅游", "风景", "打卡", "旅游攻略"],
        },
        "娱乐": {
            "通用": ["娱乐", "搞笑", "沙雕", "整活", "鬼畜"],
            "影视": ["影视", "电影", "电视剧", "动漫", "综艺"],
            "音乐": ["音乐", "翻唱", "原创音乐", "MV", "音乐分享"],
        },
    }
    
    def __init__(self, ai_engine: Optional[AIEngine] = None):
        """
        初始化标签推荐器
        
        Args:
            ai_engine: AI引擎实例
        """
        self.ai_engine = ai_engine or AIEngine()
    
    async def recommend_tags(
        self,
        title: str,
        content: str,
        zone: str = "生活",
        count: int = 10,
        use_ai: bool = True
    ) -> List[Dict[str, Any]]:
        """
        推荐标签
        
        Args:
            title: 视频标题
            content: 视频描述/内容
            zone: 分区
            count: 推荐数量（最多10个）
            use_ai: 是否使用AI增强
            
        Returns:
            标签列表，每个包含 tag、热度、相关度
        """
        
        tags = []
        
        # 1. 从热门标签库中提取
        hot_tags = self._get_hot_tags(zone, title, content)
        tags.extend(hot_tags)
        
        # 2. 使用AI生成长尾标签
        if use_ai:
            ai_tags = await self._generate_tags_with_ai(
                title, content, zone
            )
            tags.extend(ai_tags)
        
        # 3. 去重和评分
        unique_tags = {}
        for tag_info in tags:
            tag = tag_info["tag"]
            if tag not in unique_tags:
                unique_tags[tag] = tag_info
            else:
                # 保留更高分的
                if tag_info.get("score", 0) > unique_tags[tag].get("score", 0):
                    unique_tags[tag] = tag_info
        
        # 4. 排序并返回
        result = list(unique_tags.values())
        result.sort(key=lambda x: (x.get("hot_score", 0), x.get("score", 0)), reverse=True)
        
        return result[:count]
    
    def _get_hot_tags(
        self,
        zone: str,
        title: str,
        content: str
    ) -> List[Dict[str, Any]]:
        """从热门标签库中提取相关标签"""
        
        tags = []
        zone_tags = self.HOT_TAGS.get(zone, self.HOT_TAGS["生活"])
        
        # 合并所有标签
        all_tags = []
        for category, tag_list in zone_tags.items():
            all_tags.extend(tag_list)
        
        # 检查标签相关性
        text = f"{title} {content}".lower()
        
        for tag in all_tags:
            # 简单的相关性检查
            tag_lower = tag.lower()
            if tag_lower in text or any(word in text for word in tag_lower.split()):
                tags.append({
                    "tag": tag,
                    "hot_score": 80,  # 热门标签热度高
                    "score": 70,
                    "source": "热门库"
                })
        
        return tags
    
    async def _generate_tags_with_ai(
        self,
        title: str,
        content: str,
        zone: str
    ) -> List[Dict[str, Any]]:
        """使用AI生成长尾标签"""
        
        prompt = f"""
为以下B站视频推荐5-8个相关标签。

视频标题：{title}
视频内容：{content}
分区：{zone}

标签要求：
1. 与视频内容高度相关
2. 包含长尾关键词（如：具体技术名称、细分领域）
3. 避免过于宽泛的标签
4. 每个标签3-8个字
5. 不要包含特殊符号
6. 考虑用户搜索习惯

请直接输出标签，每行一个，不要编号和解释：
"""
        
        try:
            response = await self.ai_engine.generate(
                prompt=prompt,
                system_prompt="你是B站内容运营专家，擅长标签优化和SEO。",
                complexity=TaskComplexity.SIMPLE,
                max_length=200
            )
            
            if response.success:
                lines = response.content.strip().split('\n')
                tags = []
                
                for line in lines:
                    tag = line.strip()
                    # 清理格式
                    import re
                    tag = re.sub(r'^\d+[\.、\s]+', '', tag)
                    tag = re.sub(r'[#\s]+', '', tag)
                    
                    if tag and 2 <= len(tag) <= 10:
                        tags.append({
                            "tag": tag,
                            "hot_score": 50,  # AI生成的标签热度中等
                            "score": 80,      # 但相关性高
                            "source": "AI生成"
                        })
                
                return tags
        
        except Exception as e:
            print(f"⚠️ AI生成标签失败: {e}")
        
        return []
    
    def get_tag_suggestions_by_keyword(
        self,
        keyword: str,
        zone: str = "生活"
    ) -> List[str]:
        """
        根据关键词获取标签建议
        
        Args:
            keyword: 关键词
            zone: 分区
            
        Returns:
            相关标签列表
        """
        
        suggestions = []
        zone_tags = self.HOT_TAGS.get(zone, self.HOT_TAGS["生活"])
        
        keyword_lower = keyword.lower()
        
        for category, tag_list in zone_tags.items():
            for tag in tag_list:
                if keyword_lower in tag.lower() or tag.lower() in keyword_lower:
                    suggestions.append(tag)
        
        return suggestions[:10]


# ===== 测试代码 =====

async def test_bilibili_tag_recommender():
    """测试B站标签推荐器"""
    
    print("="*60)
    print("🏷️  测试B站标签推荐器")
    print("="*60)
    
    recommender = BilibiliTagRecommender()
    
    # 测试1：游戏区视频
    print("\n【测试1：游戏区视频标签】")
    tags = await recommender.recommend_tags(
        title="原神5.0版本新角色强度分析",
        content="本期视频详细分析5.0新角色的技能机制、伤害测试和配队推荐",
        zone="游戏",
        count=10,
        use_ai=True
    )
    
    print(f"推荐{len(tags)}个标签：")
    for i, tag_info in enumerate(tags, 1):
        print(f"{i}. {tag_info['tag']} "
              f"(热度:{tag_info['hot_score']}, "
              f"相关度:{tag_info['score']}, "
              f"来源:{tag_info['source']})")
    
    # 测试2：科技区视频
    print("\n【测试2：科技区视频标签】")
    tags = await recommender.recommend_tags(
        title="iPhone 16 Pro深度评测",
        content="最新iPhone 16 Pro使用两周的真实体验，包括拍照、续航、性能等全方位测试",
        zone="科技",
        count=8,
        use_ai=True
    )
    
    print(f"推荐{len(tags)}个标签：")
    for tag_info in tags:
        print(f"• {tag_info['tag']}")
    
    # 测试3：关键词建议
    print("\n【测试3：关键词标签建议】")
    suggestions = recommender.get_tag_suggestions_by_keyword(
        keyword="编程",
        zone="知识"
    )
    print(f"'编程'相关标签: {', '.join(suggestions)}")
    
    print("\n" + "="*60)
    print("✅ 测试完成！")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_bilibili_tag_recommender())

