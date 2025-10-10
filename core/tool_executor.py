"""
工具执行器 - AI助手的工具调用系统
类似MCP的function calling
"""

from typing import Dict, Any, List, Callable
import logging
import asyncio

logger = logging.getLogger(__name__)


class Tool:
    """工具定义"""
    
    def __init__(
        self,
        name: str,
        description: str,
        function: Callable,
        parameters: Dict[str, Any]
    ):
        self.name = name
        self.description = description
        self.function = function
        self.parameters = parameters


class ToolExecutor:
    """工具执行器 - AI可以调用的工具集合"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self._register_builtin_tools()
    
    def _register_builtin_tools(self):
        """注册内置工具"""
        
        # 视频工具
        self.register_tool(
            name="analyze_viral_title",
            description="分析视频标题为什么吸引人",
            function=self._analyze_title,
            parameters={"title": "str", "metadata": "dict"}
        )
        
        self.register_tool(
            name="generate_video_script",
            description="生成视频脚本",
            function=self._generate_script,
            parameters={"topic": "str", "duration": "int"}
        )
        
        self.register_tool(
            name="scrape_bilibili_hot",
            description="抓取B站热门视频",
            function=self._scrape_bilibili,
            parameters={"limit": "int"}
        )
        
        # 内容生成工具
        self.register_tool(
            name="generate_xiaohongshu_title",
            description="生成小红书标题",
            function=self._gen_xhs_title,
            parameters={"topic": "str", "style": "str"}
        )
        
        self.register_tool(
            name="generate_zhihu_article",
            description="生成知乎文章",
            function=self._gen_zhihu_article,
            parameters={"topic": "str", "length": "int"}
        )
        
        # 数据分析工具
        self.register_tool(
            name="get_statistics",
            description="获取使用统计数据",
            function=self._get_stats,
            parameters={}
        )
        
        # 剪映工具（未来）
        self.register_tool(
            name="capcut_auto_edit",
            description="使用剪映自动剪辑视频",
            function=self._capcut_edit,
            parameters={"video_path": "str", "style": "str"}
        )
    
    def register_tool(
        self,
        name: str,
        description: str,
        function: Callable,
        parameters: Dict[str, Any]
    ):
        """注册新工具"""
        tool = Tool(name, description, function, parameters)
        self.tools[name] = tool
        logger.info(f"注册工具：{name}")
    
    def get_tools_description(self) -> str:
        """获取所有工具的描述（给AI看）"""
        desc = "可用工具列表：\n\n"
        for name, tool in self.tools.items():
            desc += f"{name}:\n"
            desc += f"  功能：{tool.description}\n"
            desc += f"  参数：{tool.parameters}\n\n"
        return desc
    
    async def execute_tool(
        self,
        tool_name: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行工具"""
        if tool_name not in self.tools:
            return {"error": f"工具不存在：{tool_name}"}
        
        try:
            tool = self.tools[tool_name]
            logger.info(f"执行工具：{tool_name}")
            
            # 调用工具函数
            if asyncio.iscoroutinefunction(tool.function):
                result = await tool.function(**params)
            else:
                result = tool.function(**params)
            
            return {"success": True, "result": result}
            
        except Exception as e:
            logger.error(f"工具执行失败：{e}")
            return {"error": str(e)}
    
    # ===== 工具实现 =====
    
    async def _analyze_title(self, title: str, metadata: Dict = None):
        """分析标题"""
        from plugins.video_producer.viral_analyzer import ViralAnalyzer
        from core.ai_engine import AIEngine
        
        analyzer = ViralAnalyzer(AIEngine())
        result = await analyzer.analyze_title(title, metadata)
        return result
    
    async def _generate_script(self, topic: str, duration: int = 60):
        """生成视频脚本"""
        from plugins.video_producer.ai_analyzer import AIContentAnalyzer
        from core.ai_engine import AIEngine
        
        analyzer = AIContentAnalyzer(AIEngine())
        
        # 先生成要点
        num_points = duration // 15  # 每15秒一个要点
        points = await analyzer.extract_key_points(topic, num_points)
        
        # 生成脚本
        script = await analyzer.generate_video_script(points)
        return script
    
    async def _scrape_bilibili(self, limit: int = 10):
        """抓取B站"""
        from plugins.video_producer.content_scraper import ContentScraper
        
        scraper = ContentScraper()
        videos = await scraper.scrape_bilibili_hot(limit)
        return videos
    
    async def _gen_xhs_title(self, topic: str, style: str = "种草"):
        """生成小红书标题"""
        from plugins.xiaohongshu.title_generator import XiaohongshuTitleGenerator, TitleStyle
        from core.ai_engine import AIEngine
        
        generator = XiaohongshuTitleGenerator(AIEngine())
        
        style_map = {
            "种草": TitleStyle.ZHONGCAO,
            "教程": TitleStyle.JIAOCHENG,
            "分享": TitleStyle.FENXIANG
        }
        
        titles = await generator.generate_multiple_titles(
            topic=topic,
            keywords=[topic],
            count=3,
            style=style_map.get(style, TitleStyle.ZHONGCAO)
        )
        
        return titles
    
    async def _gen_zhihu_article(self, topic: str, length: int = 1000):
        """生成知乎文章"""
        from plugins.zhihu.content_generator import ZhihuContentGenerator
        from core.ai_engine import AIEngine
        
        generator = ZhihuContentGenerator(AIEngine())
        article = await generator.generate_article(topic, min_length=length)
        return article
    
    def _get_stats(self):
        """获取统计"""
        # TODO: 从数据库获取
        return {
            "total_generated": 100,
            "success_rate": 95,
            "today": 10
        }
    
    async def _capcut_edit(self, video_path: str, style: str = "auto"):
        """剪映剪辑"""
        from plugins.video_producer.capcut_integration import CapCutAPI
        
        capcut = CapCutAPI()
        result = await capcut.auto_edit_video(video_path, style=style)
        return result


# 全局单例
_tool_executor = None

def get_tool_executor() -> ToolExecutor:
    """获取工具执行器单例"""
    global _tool_executor
    if _tool_executor is None:
        _tool_executor = ToolExecutor()
    return _tool_executor

