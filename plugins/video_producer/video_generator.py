"""
视频生成模块
使用moviepy生成图文视频
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class VideoGenerator:
    """视频生成器"""
    
    def __init__(self):
        """初始化视频生成器"""
        self.output_dir = Path("data/videos")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 视频配置
        self.fps = 30
        self.resolution = (1080, 1920)  # 竖屏9:16
        self.duration_per_slide = 5  # 每屏5秒
    
    async def generate_text_video(
        self,
        script_segments: List[str],
        title: str = "",
        bgm_path: Optional[str] = None,
        output_name: str = "output.mp4"
    ) -> str:
        """
        生成图文视频
        
        Args:
            script_segments: 脚本片段列表
            title: 视频标题
            bgm_path: 背景音乐路径
            output_name: 输出文件名
            
        Returns:
            生成的视频路径
        """
        try:
            # 检查moviepy是否安装
            try:
                # moviepy 2.x 简化导入
                from moviepy import TextClip, ImageClip, CompositeVideoClip, AudioFileClip, concatenate_videoclips
            except ImportError as e:
                logger.error(f"moviepy导入失败：{e}")
                logger.error("请确保已安装：pip install moviepy")
                raise
            
            logger.info(f"开始生成视频：{len(script_segments)}个片段")
            
            clips = []
            
            # 生成每个文字片段的视频
            for i, text in enumerate(script_segments):
                # 创建文字图层
                txt_clip = TextClip(
                    text,
                    fontsize=60,
                    color='white',
                    font='SimHei',  # 黑体
                    size=self.resolution,
                    method='caption',
                    align='center'
                )
                
                # 创建背景（纯色或图片）
                bg_clip = ImageClip(
                    self._create_background(self.resolution),
                    duration=self.duration_per_slide
                )
                
                # 合成
                video_clip = CompositeVideoClip([
                    bg_clip,
                    txt_clip.set_position('center')
                ]).set_duration(self.duration_per_slide)
                
                clips.append(video_clip)
            
            # 合并所有片段
            final_video = concatenate_videoclips(clips, method="compose")
            
            # 添加背景音乐
            if bgm_path and os.path.exists(bgm_path):
                audio = AudioFileClip(bgm_path)
                # 循环或裁剪音频以匹配视频长度
                if audio.duration < final_video.duration:
                    audio = audio.audio_loop(duration=final_video.duration)
                else:
                    audio = audio.subclip(0, final_video.duration)
                
                final_video = final_video.set_audio(audio)
            
            # 输出视频
            output_path = self.output_dir / output_name
            final_video.write_videofile(
                str(output_path),
                fps=self.fps,
                codec='libx264',
                audio_codec='aac'
            )
            
            logger.info(f"✅ 视频生成成功：{output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"生成视频失败：{e}")
            raise
    
    def _create_background(self, size: tuple) -> str:
        """创建背景图片"""
        try:
            from PIL import Image, ImageDraw
            
            # 创建渐变背景
            img = Image.new('RGB', size, color=(30, 30, 50))
            draw = ImageDraw.Draw(img)
            
            # 简单渐变效果
            for i in range(size[1]):
                ratio = i / size[1]
                color = (
                    int(30 + ratio * 20),
                    int(30 + ratio * 40),
                    int(50 + ratio * 80)
                )
                draw.line([(0, i), (size[0], i)], fill=color)
            
            # 保存临时背景
            bg_path = self.output_dir / "temp_bg.png"
            img.save(bg_path)
            
            return str(bg_path)
            
        except Exception as e:
            logger.error(f"创建背景失败：{e}")
            # 返回纯色背景
            return None
    
    async def add_subtitle(
        self,
        video_path: str,
        subtitle_text: str,
        output_path: str
    ) -> str:
        """
        为视频添加字幕
        
        Args:
            video_path: 原视频路径
            subtitle_text: 字幕文本
            output_path: 输出路径
            
        Returns:
            添加字幕后的视频路径
        """
        try:
            from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
            
            # 加载视频
            video = VideoFileClip(video_path)
            
            # 创建字幕
            subtitle = TextClip(
                subtitle_text,
                fontsize=40,
                color='white',
                bg_color='black',
                font='SimHei'
            ).set_position(('center', 'bottom')).set_duration(video.duration)
            
            # 合成
            result = CompositeVideoClip([video, subtitle])
            result.write_videofile(output_path, codec='libx264')
            
            logger.info(f"✅ 字幕添加成功：{output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"添加字幕失败：{e}")
            return video_path
    
    def get_free_bgm(self) -> List[str]:
        """
        获取免费背景音乐列表
        
        Returns:
            音乐文件路径列表
        """
        # TODO: 集成免费音乐库API或使用本地素材
        bgm_dir = Path("data/bgm")
        
        if bgm_dir.exists():
            return [str(f) for f in bgm_dir.glob("*.mp3")]
        
        return []

