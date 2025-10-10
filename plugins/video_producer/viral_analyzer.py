"""
爆款分析模块
分析为什么某个内容能火：标题、内容、数据
"""

import re
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ViralAnalyzer:
    """爆款分析器 - 类似SEO分析"""
    
    def __init__(self, ai_engine=None):
        """
        初始化爆款分析器
        
        Args:
            ai_engine: AI引擎实例
        """
        self.ai_engine = ai_engine
    
    async def analyze_title(self, title: str, metadata: Dict = None) -> Dict[str, Any]:
        """
        分析标题为什么吸引人
        
        Args:
            title: 标题文本
            metadata: 元数据（播放量、点赞等）
            
        Returns:
            分析结果
        """
        logger.info(f"分析标题：{title}")
        
        analysis = {
            'title': title,
            'length': len(title),
            'keywords': [],
            'hooks': [],  # 吸引点
            'structure': '',
            'score': 0,
            'suggestions': []
        }
        
        # 1. 关键词提取
        analysis['keywords'] = self._extract_keywords(title)
        
        # 2. 识别吸引元素
        analysis['hooks'] = self._identify_hooks(title)
        
        # 3. 分析结构
        analysis['structure'] = self._analyze_structure(title)
        
        # 4. AI深度分析
        if self.ai_engine:
            ai_analysis = await self._ai_analyze_title(title, metadata)
            analysis['ai_insights'] = ai_analysis
        
        # 5. 综合评分
        analysis['score'] = self._calculate_title_score(analysis)
        
        # 6. 优化建议
        analysis['suggestions'] = self._generate_suggestions(analysis)
        
        return analysis
    
    def _extract_keywords(self, title: str) -> List[str]:
        """提取关键词"""
        # 数字
        numbers = re.findall(r'\d+', title)
        
        # 疑问词
        questions = ['如何', '怎么', '为什么', '什么']
        found_questions = [q for q in questions if q in title]
        
        # 情绪词
        emotions = ['震惊', '惊呆', '绝了', '太牛', '必看', '火了']
        found_emotions = [e for e in emotions if e in title]
        
        return numbers + found_questions + found_emotions
    
    def _identify_hooks(self, title: str) -> List[str]:
        """识别吸引点（Hook）"""
        hooks = []
        
        # 数字Hook（具体数据）
        if re.search(r'\d+', title):
            hooks.append('数字Hook（具体可信）')
        
        # 疑问Hook（引发好奇）
        if any(q in title for q in ['如何', '怎么', '为什么', '什么']):
            hooks.append('疑问Hook（引发好奇）')
        
        # 情绪Hook（激发情感）
        if any(e in title for e in ['震惊', '绝了', '必看', '火了']):
            hooks.append('情绪Hook（激发点击）')
        
        # 悬念Hook（制造悬念）
        if any(s in title for s in ['竟然', '居然', '没想到', '原来']):
            hooks.append('悬念Hook（制造悬念）')
        
        # 对比Hook（冲突感）
        if any(c in title for c in ['vs', 'VS', '对比', '比较']):
            hooks.append('对比Hook（制造冲突）')
        
        return hooks
    
    def _analyze_structure(self, title: str) -> str:
        """分析标题结构"""
        if '：' in title or ':' in title:
            return '主副标题结构'
        elif ',' in title or '，' in title:
            return '并列结构'
        elif '!' in title or '！' in title:
            return '感叹结构'
        elif '?' in title or '？' in title:
            return '疑问结构'
        else:
            return '简单结构'
    
    async def _ai_analyze_title(self, title: str, metadata: Dict = None) -> str:
        """AI深度分析标题"""
        if not self.ai_engine:
            return "AI未配置"
        
        try:
            meta_info = ""
            if metadata:
                meta_info = f"\n播放量：{metadata.get('play', 0)}\n点赞：{metadata.get('like', 0)}"
            
            prompt = f"""分析这个视频/文章标题为什么吸引人：

标题：{title}{meta_info}

请分析：
1. 核心吸引点是什么？
2. 使用了什么心理技巧？
3. 目标受众是谁？
4. 如果要优化，应该怎么改？

简洁回答，每点1-2句话。"""
            
            result = await self.ai_engine.generate(
                prompt=prompt,
                complexity="SIMPLE"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"AI分析标题失败：{e}")
            return "AI分析失败"
    
    def _calculate_title_score(self, analysis: Dict) -> int:
        """计算标题吸引力评分（0-100）"""
        score = 50  # 基础分
        
        # 有数字 +10
        if any(k.isdigit() for k in analysis['keywords']):
            score += 10
        
        # 每个Hook +8
        score += len(analysis['hooks']) * 8
        
        # 长度适中（10-30字）+10
        if 10 <= analysis['length'] <= 30:
            score += 10
        
        # 限制在0-100
        return min(100, max(0, score))
    
    def _generate_suggestions(self, analysis: Dict) -> List[str]:
        """生成优化建议"""
        suggestions = []
        
        if analysis['length'] < 10:
            suggestions.append('标题太短，建议增加到15-25字')
        elif analysis['length'] > 30:
            suggestions.append('标题太长，建议精简到25字内')
        
        if not analysis['hooks']:
            suggestions.append('缺少吸引点，建议添加数字、疑问或情绪词')
        
        if analysis['score'] < 60:
            suggestions.append('整体吸引力不足，参考热门标题结构')
        
        return suggestions or ['标题质量良好']
    
    async def analyze_content(
        self, 
        content: str, 
        content_type: str = 'article'
    ) -> Dict[str, Any]:
        """
        分析内容为什么能火
        
        Args:
            content: 内容文本
            content_type: 类型（article/video_desc）
            
        Returns:
            分析结果
        """
        logger.info(f"分析内容，类型：{content_type}")
        
        if not self.ai_engine:
            return {"error": "AI引擎未配置"}
        
        try:
            prompt = f"""分析这个{content_type}内容为什么能火：

内容：
{content[:500]}...

请分析：
1. 核心卖点是什么？
2. 使用了什么内容技巧？（悬念/反转/共鸣等）
3. 情绪调动如何？
4. 节奏把控如何？
5. 如果模仿，应该注意什么？

每点1-2句话，给出具体可操作的建议。"""
            
            result = await self.ai_engine.generate(
                prompt=prompt,
                complexity="MEDIUM"
            )
            
            return {
                'content_type': content_type,
                'analysis': result,
                'length': len(content),
                'insights': self._extract_insights(result)
            }
            
        except Exception as e:
            logger.error(f"内容分析失败：{e}")
            return {"error": str(e)}
    
    def _extract_insights(self, ai_result: str) -> List[str]:
        """从AI分析中提取关键洞察"""
        # 简单实现：按行分割
        lines = [l.strip() for l in ai_result.split('\n') if l.strip()]
        return lines[:10]  # 最多10条
    
    async def analyze_data(
        self, 
        views: int, 
        likes: int, 
        comments: int,
        avg_data: Dict = None
    ) -> Dict[str, Any]:
        """
        数据分析：为什么这个数据好
        
        Args:
            views: 播放量
            likes: 点赞数
            comments: 评论数
            avg_data: 平均数据对比
            
        Returns:
            数据分析结果
        """
        analysis = {
            'views': views,
            'likes': likes,
            'comments': comments,
            'like_rate': likes / views * 100 if views > 0 else 0,
            'comment_rate': comments / views * 100 if views > 0 else 0,
            'insights': []
        }
        
        # 与平均值对比
        if avg_data:
            if views > avg_data.get('avg_views', 0) * 2:
                analysis['insights'].append(f"播放量超平均{views/avg_data.get('avg_views', 1):.1f}倍")
            
            if analysis['like_rate'] > avg_data.get('avg_like_rate', 5):
                analysis['insights'].append(f"点赞率{analysis['like_rate']:.2f}%超高")
        
        # AI分析数据
        if self.ai_engine:
            prompt = f"""分析这个视频数据为什么好：

播放量：{views:,}
点赞数：{likes:,}
评论数：{comments:,}
点赞率：{analysis['like_rate']:.2f}%

请分析可能的原因（内容质量、推荐算法、用户粘性等），给出3-5点具体原因。"""
            
            ai_result = await self.ai_engine.generate(prompt, complexity="SIMPLE")
            analysis['ai_analysis'] = ai_result
        
        return analysis
    
    async def generate_viral_formula(
        self, 
        successful_cases: List[Dict]
    ) -> Dict[str, Any]:
        """
        从成功案例中总结爆款公式
        
        Args:
            successful_cases: 成功案例列表
            
        Returns:
            爆款公式和建议
        """
        if not successful_cases:
            return {"error": "没有成功案例"}
        
        if not self.ai_engine:
            return {"error": "AI引擎未配置"}
        
        try:
            # 汇总所有案例
            cases_text = "\n\n".join([
                f"案例{i+1}：\n标题：{case.get('title')}\n播放量：{case.get('views', 0):,}"
                for i, case in enumerate(successful_cases[:10])
            ])
            
            prompt = f"""分析这些爆款视频的共同规律：

{cases_text}

请总结：
1. 标题的共同特征
2. 内容的共同模式
3. 数据表现的共性
4. 可复制的爆款公式
5. 具体的创作建议

给出可执行的爆款制作指南。"""
            
            formula = await self.ai_engine.generate(
                prompt=prompt,
                complexity="COMPLEX"
            )
            
            return {
                'formula': formula,
                'case_count': len(successful_cases),
                'summary': self._summarize_formula(formula)
            }
            
        except Exception as e:
            logger.error(f"生成爆款公式失败：{e}")
            return {"error": str(e)}
    
    def _summarize_formula(self, formula: str) -> List[str]:
        """总结爆款公式为要点列表"""
        # 简单实现：按编号分割
        points = re.findall(r'\d+[\.、]\s*([^\n]+)', formula)
        return points[:10]

