"""
B站标题生成器

特点：
- 关键词前置（SEO优势）
- 悬念感强（结局意想不到）
- 数字化表达（10分钟学会XXX）
- 时效性（2025最新）
- 分区特色（游戏/科技/生活风格）
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from core.ai_engine import AIEngine, TaskComplexity


class BilibiliTitleGenerator:
    """B站标题生成器"""
    
    # B站标题模板 - 3种主流风格
    TITLE_PATTERNS = {
        "悬念型": [
            "{keyword}居然能这样{action}？看完惊了！",
            "不会吧？{keyword}竟然{result}！",
            "{keyword}的真相，99%的人都不知道",
            "万万没想到！{keyword}最后会{result}",
            "{keyword}到底{how}？结局太意外了！",
            "震惊！{keyword}居然{result}！",
        ],
        "教程型": [
            "{time}教你{skill}！{keyword}从入门到精通",
            "{keyword}完整教程！{number}个步骤搞定",
            "史上最全{keyword}教程！建议收藏",
            "{keyword}新手指南：{number}分钟速成",
            "保姆级{keyword}教程！跟着做就能学会",
            "{year}年最新{keyword}教程 | 零基础到精通",
        ],
        "测评型": [
            "{keyword}真实测评！{price}值不值？",
            "对比{number}款{keyword}，最终我选择了...",
            "{keyword}深度测评：优缺点全分析",
            "{keyword}使用{time}后的真实感受",
            "{price}{keyword}体验报告 | 这钱花得值吗？",
            "{keyword}评测 | {number}个理由告诉你买不买",
        ],
    }
    
    def __init__(self, ai_engine: Optional[AIEngine] = None):
        """
        初始化B站标题生成器
        
        Args:
            ai_engine: AI引擎实例
        """
        self.ai_engine = ai_engine or AIEngine()
        
    async def generate_titles(
        self,
        topic: str,
        keywords: List[str],
        style: str = "悬念型",
        zone: str = "生活",
        count: int = 5,
        use_ai: bool = True
    ) -> List[Dict[str, Any]]:
        """
        生成多个B站标题
        
        Args:
            topic: 视频主题
            keywords: 关键词列表
            style: 标题风格（悬念型/教程型/测评型）
            zone: 分区（游戏/科技/生活等）
            count: 生成数量
            use_ai: 是否使用AI增强
            
        Returns:
            标题列表，每个包含 title 和 score
        """
        titles = []
        
        # 1. 基于模板生成
        template_titles = self._generate_from_templates(
            topic, keywords, style, zone, count
        )
        titles.extend(template_titles)
        
        # 2. AI增强生成
        if use_ai:
            ai_titles = await self._generate_with_ai(
                topic, keywords, style, zone, count
            )
            titles.extend(ai_titles)
        
        # 3. 评分排序
        scored_titles = []
        for title in titles:
            score = self._score_title(title, keywords, zone)
            scored_titles.append({
                "title": title,
                "score": score,
                "length": len(title),
                "style": style
            })
        
        # 排序并返回top N
        scored_titles.sort(key=lambda x: x["score"], reverse=True)
        return scored_titles[:count]
    
    def _generate_from_templates(
        self,
        topic: str,
        keywords: List[str],
        style: str,
        zone: str,
        count: int
    ) -> List[str]:
        """基于模板生成标题"""
        
        templates = self.TITLE_PATTERNS.get(style, self.TITLE_PATTERNS["悬念型"])
        titles = []
        
        # 提取主关键词
        main_keyword = keywords[0] if keywords else topic
        
        # 填充变量
        variables = {
            "keyword": main_keyword,
            "action": self._get_action_word(zone),
            "result": self._get_result_word(zone),
            "time": self._get_time_word(),
            "skill": self._get_skill_word(zone),
            "number": self._get_number(),
            "how": self._get_how_word(),
            "year": datetime.now().year,
            "price": self._get_price(),
        }
        
        # 生成标题
        import random
        selected_templates = random.sample(templates, min(count, len(templates)))
        
        for template in selected_templates:
            try:
                title = template.format(**variables)
                # 确保长度不超过80字
                if len(title) > 80:
                    title = title[:77] + "..."
                titles.append(title)
            except KeyError:
                continue
        
        return titles
    
    async def _generate_with_ai(
        self,
        topic: str,
        keywords: List[str],
        style: str,
        zone: str,
        count: int
    ) -> List[str]:
        """使用AI生成标题"""
        
        # 构建提示词
        keyword_str = "、".join(keywords[:3])
        
        prompt = f"""
你是一个B站爆款视频标题生成专家。请为以下视频生成{count}个吸引人的标题。

视频信息：
- 主题：{topic}
- 关键词：{keyword_str}
- 风格：{style}
- 分区：{zone}

B站标题要求：
1. 长度：20-80字之间
2. 风格特点：
   - 悬念型：制造悬念、结局反转、引发好奇（如：万万没想到、结局太意外）
   - 教程型：时间量化、步骤清晰、新手友好（如：10分钟学会、保姆级教程）
   - 测评型：真实体验、对比分析、价格敏感（如：值不值、深度测评）
3. 关键词前置：重要关键词放在标题前半部分
4. 数字化表达：使用具体数字（如：5个、10分钟、2025年）
5. 时效性：突出最新、今年、当下
6. 情绪词：震惊、万万没想到、建议收藏
7. 符号使用：适当使用！？｜等符号增强表现力

请生成{count}个标题，每行一个，不要编号：
"""
        
        try:
            # 使用SIMPLE复杂度（标题生成较简单）
            response = await self.ai_engine.generate(
                prompt=prompt,
                system_prompt="你是B站内容创作专家，擅长生成高播放量标题。",
                complexity=TaskComplexity.SIMPLE
            )
            
            if response.success:
                # 解析AI返回的标题
                lines = response.content.strip().split('\n')
                titles = []
                for line in lines:
                    # 清理格式
                    title = line.strip()
                    # 移除编号
                    if title and len(title) > 0:
                        # 移除可能的编号前缀
                        import re
                        title = re.sub(r'^\d+[\.、\s]+', '', title)
                        if len(title) > 0 and len(title) <= 80:
                            titles.append(title)
                
                return titles[:count]
            
        except Exception as e:
            print(f"⚠️ AI生成标题失败: {e}")
        
        return []
    
    def _score_title(self, title: str, keywords: List[str], zone: str) -> float:
        """
        评估标题质量
        
        评分维度：
        - 长度合理性 (20分)
        - 关键词包含 (30分)
        - 悬念感/吸引力 (20分)
        - 数字化表达 (15分)
        - 时效性 (15分)
        
        Returns:
            0-100分
        """
        score = 0.0
        
        # 1. 长度评分（20分）
        title_len = len(title)
        if 30 <= title_len <= 60:
            score += 20
        elif 20 <= title_len < 30 or 60 < title_len <= 80:
            score += 15
        else:
            score += 10
        
        # 2. 关键词评分（30分）
        keyword_count = sum(1 for kw in keywords if kw in title)
        keyword_ratio = keyword_count / len(keywords) if keywords else 0
        score += keyword_ratio * 30
        
        # 3. 悬念词评分（20分）
        suspense_words = ["万万没想到", "震惊", "不会吧", "居然", "竟然", "结局", "真相", "意外"]
        suspense_count = sum(1 for word in suspense_words if word in title)
        score += min(suspense_count * 10, 20)
        
        # 4. 数字化评分（15分）
        import re
        numbers = re.findall(r'\d+', title)
        if numbers:
            score += 15
        elif any(word in title for word in ["一", "二", "三", "五", "十"]):
            score += 10
        
        # 5. 时效性评分（15分）
        current_year = str(datetime.now().year)
        time_words = [current_year, "最新", "今年", "最近", "当下"]
        if any(word in title for word in time_words):
            score += 15
        
        return round(score, 1)
    
    # ===== 辅助方法 =====
    
    def _get_action_word(self, zone: str) -> str:
        """获取动作词"""
        actions = {
            "游戏": ["玩", "通关", "上分", "操作"],
            "科技": ["使用", "设置", "优化", "体验"],
            "生活": ["做", "搞定", "实现", "完成"],
            "知识": ["学习", "掌握", "理解", "应用"],
        }
        import random
        return random.choice(actions.get(zone, actions["生活"]))
    
    def _get_result_word(self, zone: str) -> str:
        """获取结果词"""
        results = {
            "游戏": ["无敌了", "起飞了", "翻盘了", "躺赢"],
            "科技": ["神器", "好用", "完美", "香"],
            "生活": ["太绝了", "惊了", "爱了", "服了"],
            "知识": ["涨知识", "学到了", "懂了", "会了"],
        }
        import random
        return random.choice(results.get(zone, results["生活"]))
    
    def _get_time_word(self) -> str:
        """获取时间词"""
        import random
        return random.choice(["3分钟", "5分钟", "10分钟", "一键", "快速"])
    
    def _get_skill_word(self, zone: str) -> str:
        """获取技能词"""
        skills = {
            "游戏": "上分",
            "科技": "玩转",
            "生活": "掌握",
            "知识": "学会",
        }
        return skills.get(zone, "学会")
    
    def _get_number(self) -> str:
        """获取数字"""
        import random
        return str(random.choice([3, 5, 7, 10]))
    
    def _get_how_word(self) -> str:
        """获取疑问词"""
        import random
        return random.choice(["怎么样", "如何", "怎么办", "是什么"])
    
    def _get_price(self) -> str:
        """获取价格词"""
        import random
        prices = ["99元", "199元", "999元", "千元", "百元"]
        return random.choice(prices)


# ===== 测试代码 =====

async def test_bilibili_title_generator():
    """测试B站标题生成器"""
    
    print("="*60)
    print("🎬 测试B站标题生成器")
    print("="*60)
    
    generator = BilibiliTitleGenerator()
    
    # 测试场景1：游戏区悬念型
    print("\n【测试1：游戏区 - 悬念型】")
    titles = await generator.generate_titles(
        topic="原神新角色实战",
        keywords=["原神", "新角色", "实战"],
        style="悬念型",
        zone="游戏",
        count=5,
        use_ai=True
    )
    
    for i, item in enumerate(titles, 1):
        print(f"{i}. {item['title']}")
        print(f"   评分: {item['score']}分 | 长度: {item['length']}字")
    
    # 测试场景2：科技区教程型
    print("\n【测试2：科技区 - 教程型】")
    titles = await generator.generate_titles(
        topic="Python数据分析教程",
        keywords=["Python", "数据分析", "教程"],
        style="教程型",
        zone="科技",
        count=5,
        use_ai=False  # 只用模板
    )
    
    for i, item in enumerate(titles, 1):
        print(f"{i}. {item['title']}")
        print(f"   评分: {item['score']}分")
    
    # 测试场景3：生活区测评型
    print("\n【测试3：生活区 - 测评型】")
    titles = await generator.generate_titles(
        topic="蓝牙耳机对比测评",
        keywords=["蓝牙耳机", "降噪", "测评"],
        style="测评型",
        zone="生活",
        count=3,
        use_ai=True
    )
    
    for i, item in enumerate(titles, 1):
        print(f"{i}. {item['title']}")
        print(f"   评分: {item['score']}分")
    
    print("\n" + "="*60)
    print("✅ 测试完成！")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_bilibili_title_generator())

