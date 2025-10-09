"""
JieDimension Toolkit - 话题标签推荐器
为小红书内容推荐合适的话题标签
Version: 1.0.0
"""

import sys
import os
from typing import List, Dict, Optional, Set

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.ai_engine import AIEngine, TaskComplexity


class TopicTagRecommender:
    """话题标签推荐器"""
    
    # 热门话题库（按分类）
    HOT_TOPICS = {
        "美妆": [
            "#美妆分享", "#化妆教程", "#护肤心得", "#好物推荐",
            "#学生党必备", "#平价好物", "#口红推荐", "#底妆",
            "#眼妆教程", "#日常妆容", "#约会妆", "#妆容分享"
        ],
        "美食": [
            "#美食分享", "#家常菜", "#烘焙日记", "#甜品制作",
            "#减肥餐", "#健康饮食", "#快手菜", "#下午茶",
            "#美食教程", "#探店", "#网红美食", "#料理"
        ],
        "穿搭": [
            "#穿搭分享", "#日常穿搭", "#通勤穿搭", "#约会穿搭",
            "#学生党穿搭", "#平价穿搭", "#搭配技巧", "#衣橱整理",
            "#服饰", "#时尚", "#OOTD", "#穿搭灵感"
        ],
        "旅行": [
            "#旅行", "#旅游攻略", "#打卡", "#旅行日记",
            "#周末游", "#自驾游", "#美景", "#旅行vlog",
            "#风景", "#探店", "#出游", "#度假"
        ],
        "健身": [
            "#健身", "#减肥", "#运动", "#瘦身",
            "#健康生活", "#居家健身", "#健身打卡", "#运动日常",
            "#减脂", "#塑形", "#健身房", "#健身教程"
        ],
        "学习": [
            "#学习", "#自律", "#学习方法", "#考研",
            "#备考", "#英语学习", "#笔记", "#效率",
            "#读书", "#考证", "#学习打卡", "#提升自己"
        ],
        "生活": [
            "#生活", "#日常", "#vlog", "#记录生活",
            "#生活分享", "#好物推荐", "#居家好物", "#生活方式",
            "#幸福感", "#精致生活", "#慢生活", "#治愈"
        ],
        "好物": [
            "#好物推荐", "#好物分享", "#种草", "#拔草",
            "#平价好物", "#学生党", "#性价比", "#实用好物",
            "#必买清单", "#宝藏好物", "#好物合集", "#剁手"
        ]
    }
    
    # 季节性话题
    SEASONAL_TOPICS = {
        "春季": ["#春天", "#春游", "#踏青", "#春装", "#春日穿搭"],
        "夏季": ["#夏天", "#防晒", "#夏日", "#清凉", "#夏日穿搭", "#避暑"],
        "秋季": ["#秋天", "#秋游", "#秋装", "#秋日", "#秋日穿搭"],
        "冬季": ["#冬天", "#保暖", "#冬装", "#冬日", "#冬日穿搭", "#御寒"],
    }
    
    # 节日话题
    FESTIVAL_TOPICS = {
        "新年": ["#新年", "#跨年", "#元旦", "#新年愿望"],
        "春节": ["#春节", "#过年", "#新春", "#拜年"],
        "情人节": ["#情人节", "#520", "#七夕", "#约会"],
        "女神节": ["#女神节", "#38节", "#女王节", "#犒劳自己"],
        "母亲节": ["#母亲节", "#感恩妈妈", "#母爱"],
        "儿童节": ["#儿童节", "#童心", "#六一"],
        "毕业季": ["#毕业季", "#毕业", "#青春"],
        "中秋": ["#中秋节", "#中秋", "#团圆"],
        "国庆": ["#国庆", "#十一", "#假期"],
        "双十一": ["#双十一", "#购物", "#剁手"],
        "圣诞": ["#圣诞节", "#圣诞", "#平安夜"],
    }
    
    def __init__(self, ai_engine: Optional[AIEngine] = None):
        """
        初始化推荐器
        
        Args:
            ai_engine: AI引擎实例
        """
        self.ai_engine = ai_engine or AIEngine()
    
    async def recommend_tags(
        self,
        content: str,
        category: Optional[str] = None,
        max_tags: int = 5,
        use_ai: bool = True
    ) -> List[str]:
        """
        推荐话题标签
        
        Args:
            content: 笔记内容
            category: 内容分类（如果不提供，会自动检测）
            max_tags: 最多推荐数量
            use_ai: 是否使用AI辅助推荐
            
        Returns:
            标签列表
        """
        tags = set()
        
        # 1. 如果没有指定分类，先检测分类
        if not category:
            category = self._detect_category(content)
        
        # 2. 从热门话题库中匹配
        hot_tags = self._match_hot_topics(content, category)
        tags.update(hot_tags[:max_tags])
        
        # 3. 如果使用AI，获取AI推荐
        if use_ai and len(tags) < max_tags:
            ai_tags = await self._recommend_with_ai(content, max_tags - len(tags))
            tags.update(ai_tags)
        
        # 4. 添加季节性和节日话题
        if len(tags) < max_tags:
            seasonal_tags = self._get_seasonal_topics()
            tags.update(seasonal_tags[:max_tags - len(tags)])
        
        # 转换为列表并返回
        return list(tags)[:max_tags]
    
    def _detect_category(self, content: str) -> str:
        """
        自动检测内容分类
        
        Args:
            content: 内容文本
            
        Returns:
            分类名称
        """
        # 关键词映射
        keywords_map = {
            "美妆": ["化妆", "口红", "粉底", "眼影", "护肤", "面膜", "精华"],
            "美食": ["美食", "做饭", "烹饪", "食谱", "烘焙", "蛋糕", "菜"],
            "穿搭": ["穿搭", "衣服", "裙子", "外套", "鞋", "搭配", "服装"],
            "旅行": ["旅游", "旅行", "景点", "游玩", "打卡", "攻略", "出游"],
            "健身": ["健身", "运动", "减肥", "瘦身", "锻炼", "塑形", "跑步"],
            "学习": ["学习", "考试", "备考", "笔记", "读书", "自律", "效率"],
        }
        
        # 计算每个分类的匹配度
        scores = {}
        for category, keywords in keywords_map.items():
            score = sum(1 for keyword in keywords if keyword in content)
            scores[category] = score
        
        # 返回得分最高的分类
        if scores:
            best_category = max(scores, key=scores.get)
            if scores[best_category] > 0:
                return best_category
        
        return "生活"  # 默认分类
    
    def _match_hot_topics(
        self,
        content: str,
        category: str
    ) -> List[str]:
        """
        从热门话题库中匹配
        
        Args:
            content: 内容文本
            category: 分类
            
        Returns:
            匹配的话题列表
        """
        # 获取分类的热门话题
        topics = self.HOT_TOPICS.get(category, self.HOT_TOPICS["生活"])
        
        # 简单的关键词匹配
        matched = []
        for topic in topics:
            # 移除#符号进行匹配
            keyword = topic.replace("#", "")
            if keyword in content:
                matched.append(topic)
        
        # 如果匹配数不足，补充该分类的高频话题
        if len(matched) < 3:
            for topic in topics[:3]:
                if topic not in matched:
                    matched.append(topic)
        
        return matched
    
    async def _recommend_with_ai(
        self,
        content: str,
        count: int
    ) -> List[str]:
        """
        使用AI推荐话题标签
        
        Args:
            content: 内容文本
            count: 需要的数量
            
        Returns:
            AI推荐的标签列表
        """
        prompt = f"""
分析以下小红书笔记内容，推荐{count}个最合适的话题标签：

内容：{content[:200]}...

要求：
1. 标签要热门且相关
2. 格式必须是 #标签
3. 每个标签2-4个字
4. 优先推荐热门话题
5. 只输出标签，用空格分隔
6. 不要任何解释

推荐标签：
"""
        
        try:
            response = await self.ai_engine.generate(
                prompt=prompt,
                system_prompt="你是小红书话题标签专家",
                complexity=TaskComplexity.SIMPLE
            )
            
            if response.success:
                # 解析标签
                tags = self._parse_tags(response.content)
                return tags[:count]
        except Exception as e:
            print(f"AI推荐失败: {e}")
        
        return []
    
    def _parse_tags(self, text: str) -> List[str]:
        """
        解析标签文本
        
        Args:
            text: AI返回的文本
            
        Returns:
            标签列表
        """
        import re
        
        # 提取所有#开头的标签
        tags = re.findall(r'#[\u4e00-\u9fa5a-zA-Z0-9]+', text)
        
        # 去重
        return list(set(tags))
    
    def _get_seasonal_topics(self) -> List[str]:
        """
        获取当前季节的话题
        
        Returns:
            季节话题列表
        """
        from datetime import datetime
        
        month = datetime.now().month
        
        # 判断季节
        if 3 <= month <= 5:
            season = "春季"
        elif 6 <= month <= 8:
            season = "夏季"
        elif 9 <= month <= 11:
            season = "秋季"
        else:
            season = "冬季"
        
        return self.SEASONAL_TOPICS.get(season, [])
    
    def get_festival_topics(self, festival: str) -> List[str]:
        """
        获取节日相关话题
        
        Args:
            festival: 节日名称
            
        Returns:
            节日话题列表
        """
        return self.FESTIVAL_TOPICS.get(festival, [])
    
    def combine_tags(
        self,
        content_tags: List[str],
        hot_tags: List[str],
        max_tags: int = 5
    ) -> List[str]:
        """
        组合内容标签和热门标签
        
        Args:
            content_tags: 内容相关标签
            hot_tags: 热门标签
            max_tags: 最大标签数
            
        Returns:
            组合后的标签列表
        """
        # 优先内容标签，补充热门标签
        combined = []
        
        # 先加入内容标签
        for tag in content_tags:
            if len(combined) < max_tags:
                combined.append(tag)
        
        # 补充热门标签
        for tag in hot_tags:
            if len(combined) >= max_tags:
                break
            if tag not in combined:
                combined.append(tag)
        
        return combined[:max_tags]


# 测试函数
async def test_topic_recommender():
    """测试话题推荐器"""
    print("="*60)
    print("🧪 测试话题标签推荐器")
    print("="*60)
    
    recommender = TopicTagRecommender()
    
    # 测试1：美妆内容
    print("\n📝 测试1：美妆内容推荐")
    print("-"*60)
    
    content1 = """
    今天分享一下我最近在用的口红！这款口红真的超级好用，
    颜色很显白，而且持久度也很棒。学生党平价好物，
    强烈推荐给大家！适合日常妆容和约会妆。
    """
    
    print(f"内容：{content1.strip()}")
    print()
    
    tags1 = await recommender.recommend_tags(
        content=content1,
        category="美妆",
        max_tags=5
    )
    
    print("推荐标签：")
    for tag in tags1:
        print(f"  {tag}")
    
    # 测试2：美食内容
    print("\n📝 测试2：美食内容推荐")
    print("-"*60)
    
    content2 = """
    周末在家做了蛋糕，第一次尝试烘焙就成功了！
    分享一下详细的制作步骤，超级简单，新手也能做。
    味道很不错，家人都说好吃。
    """
    
    print(f"内容：{content2.strip()}")
    print()
    
    tags2 = await recommender.recommend_tags(
        content=content2,
        max_tags=5
    )
    
    print("推荐标签：")
    for tag in tags2:
        print(f"  {tag}")
    
    # 测试3：分类检测
    print("\n📝 测试3：自动分类检测")
    print("-"*60)
    
    content3 = "最近开始健身了，每天坚持运动打卡，感觉身体状态好了很多。"
    
    category = recommender._detect_category(content3)
    print(f"内容：{content3}")
    print(f"检测分类：{category}")
    
    tags3 = await recommender.recommend_tags(
        content=content3,
        max_tags=5
    )
    
    print("推荐标签：")
    for tag in tags3:
        print(f"  {tag}")
    
    print("\n" + "="*60)
    print("✅ 测试完成")
    print("="*60)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_topic_recommender())

