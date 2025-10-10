"""
AI内容分析模块
使用AI分析文章/视频内容，提取要点，生成视频脚本
"""

from typing import List, Dict, Any
import logging
from core.ai_engine import TaskComplexity

logger = logging.getLogger(__name__)


class AIContentAnalyzer:
    """AI内容分析器"""
    
    def __init__(self, ai_engine):
        """
        初始化AI分析器
        
        Args:
            ai_engine: JieDimension的AIEngine实例
        """
        self.ai_engine = ai_engine
    
    async def extract_key_points(
        self, 
        content: str, 
        num_points: int = 5
    ) -> List[str]:
        """
        从文章/视频中提取核心要点
        
        Args:
            content: 文章内容或视频描述
            num_points: 提取要点数量
            
        Returns:
            要点列表
        """
        try:
            prompt = f"""从以下内容中提取{num_points}个核心要点：

内容：
{content[:2000]}

要求：
1. 每个要点15-30字
2. 简洁有力，适合做视频文案
3. 按重要性排序
4. 只输出要点，不要编号

格式：每行一个要点"""
            
            result = await self.ai_engine.generate(
                prompt=prompt,
                complexity=TaskComplexity.MEDIUM
            )
            
            # 解析结果（AIResponse对象）
            content = result.content if hasattr(result, 'content') else str(result)
            points = [line.strip() for line in content.split('\n') if line.strip()]
            points = points[:num_points]
            
            logger.info(f"✅ 提取{len(points)}个要点")
            return points
            
        except Exception as e:
            logger.error(f"提取要点失败：{e}")
            return []
    
    async def generate_video_script(
        self, 
        key_points: List[str],
        style: str = "解说"
    ) -> Dict[str, Any]:
        """
        根据要点生成视频脚本
        
        Args:
            key_points: 核心要点
            style: 视频风格（解说/吐槽/严肃/幽默）
            
        Returns:
            视频脚本
        """
        try:
            points_text = "\n".join([f"{i+1}. {p}" for i, p in enumerate(key_points)])
            
            prompt = f"""根据以下要点，生成一个60秒短视频脚本：

要点：
{points_text}

要求：
1. 风格：{style}
2. 时长：60秒左右（约180字）
3. 开头要吸引人（3秒抓住注意力）
4. 中间有节奏（每15秒一个要点）
5. 结尾有互动（引导点赞关注）

直接输出脚本文本，不要多余说明。"""
            
            script_result = await self.ai_engine.generate(
                prompt=prompt,
                complexity=TaskComplexity.MEDIUM
            )
            
            # 获取脚本文本
            script = script_result.content if hasattr(script_result, 'content') else str(script_result)
            
            # 分割成片段（每15秒一段）
            segments = self._split_script(script, num_segments=4)
            
            return {
                'full_script': script,
                'segments': segments,
                'estimated_duration': len(script) / 3,  # 约3字/秒
                'style': style
            }
            
        except Exception as e:
            logger.error(f"生成脚本失败：{e}")
            return {}
    
    def _split_script(self, script: str, num_segments: int = 4) -> List[str]:
        """将脚本分割成片段"""
        # 按句号分割
        sentences = [s.strip() + '。' for s in script.split('。') if s.strip()]
        
        # 平均分配
        segment_size = len(sentences) // num_segments
        segments = []
        
        for i in range(num_segments):
            start = i * segment_size
            end = start + segment_size if i < num_segments - 1 else len(sentences)
            segment = ''.join(sentences[start:end])
            if segment:
                segments.append(segment)
        
        return segments
    
    async def generate_title(
        self, 
        content_summary: str,
        platform: str = "douyin"
    ) -> List[str]:
        """
        生成吸引人的标题
        
        Args:
            content_summary: 内容摘要
            platform: 平台（douyin/bilibili）
            
        Returns:
            标题列表（3-5个）
        """
        try:
            platform_guide = {
                'douyin': '抖音标题要短（20字内）、有悬念、带emoji',
                'bilibili': 'B站标题可长（40字内）、信息量大、专业'
            }
            
            guide = platform_guide.get(platform, platform_guide['douyin'])
            
            prompt = f"""根据内容生成5个吸引人的{platform}标题：

内容摘要：
{content_summary}

要求：
{guide}
必须包含Hook（数字/疑问/情绪/悬念之一）

直接输出标题，每行一个，不要编号。"""
            
            result = await self.ai_engine.generate(
                prompt=prompt,
                complexity=TaskComplexity.SIMPLE
            )
            
            # 获取文本内容
            content = result.content if hasattr(result, 'content') else str(result)
            titles = [line.strip() for line in content.split('\n') if line.strip()]
            
            logger.info(f"✅ 生成{len(titles)}个标题")
            return titles[:5]
            
        except Exception as e:
            logger.error(f"生成标题失败：{e}")
            return []
    
    async def analyze_video_transcript(
        self, 
        transcript: str
    ) -> Dict[str, Any]:
        """
        分析视频文案/字幕
        
        Args:
            transcript: 视频文案或字幕
            
        Returns:
            分析结果
        """
        try:
            prompt = f"""分析这个视频文案的优缺点：

文案：
{transcript[:1000]}

分析：
1. 开头是否吸引人？
2. 节奏把控如何？
3. 情绪调动如何？
4. 结尾是否有互动？
5. 整体评分（0-100分）

简洁回答。"""
            
            analysis_result = await self.ai_engine.generate(
                prompt=prompt,
                complexity=TaskComplexity.SIMPLE
            )
            
            # 获取分析文本
            analysis = analysis_result.content if hasattr(analysis_result, 'content') else str(analysis_result)
            
            return {
                'transcript': transcript,
                'analysis': analysis,
                'length': len(transcript)
            }
            
        except Exception as e:
            logger.error(f"分析视频文案失败：{e}")
            return {}

