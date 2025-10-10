"""
视频生成模块
使用moviepy生成图文视频
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from PIL import Image

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
        
        # 配置FFmpeg路径（优先使用项目内的）
        self._setup_ffmpeg()
    
    async def generate_text_video(
        self,
        script_segments: List[str],
        title: str = "",
        bgm_path: Optional[str] = None,
        output_name: str = "output.mp4",
        font_name: str = "微软雅黑",
        font_size: int = 70,
        use_emoji: bool = True,
        bg_style: str = "渐变"
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
            
            # 简化实现：使用Pillow生成图片，然后合成视频
            from PIL import Image, ImageDraw, ImageFont
            
            image_clips = []
            
            # 为每个文字生成图片
            for i, text in enumerate(script_segments):
                # 创建渐变背景
                img = self._create_gradient_background(self.resolution, i)
                draw = ImageDraw.Draw(img)
                
                # 加载字体（使用参数）
                font = self._load_font(font_size, font_name)
                
                # 计算文字位置（居中）
                # 处理多行文字
                lines = self._wrap_text(text, font, self.resolution[0] - 200)
                
                # 计算总高度
                total_height = len(lines) * 100  # 每行约100px
                start_y = (self.resolution[1] - total_height) // 2
                
                # 绘制每一行
                for line_idx, line in enumerate(lines):
                    bbox = draw.textbbox((0, 0), line, font=font)
                    text_width = bbox[2] - bbox[0]
                    x = (self.resolution[0] - text_width) // 2
                    y = start_y + line_idx * 100
                    
                    # 绘制文字阴影（增加立体感）
                    shadow_offset = 3
                    draw.text((x + shadow_offset, y + shadow_offset), line, font=font, fill=(0, 0, 0, 180))
                    
                    # 绘制描边（增加清晰度）
                    for adj_x, adj_y in [(-2,0), (2,0), (0,-2), (0,2)]:
                        draw.text((x + adj_x, y + adj_y), line, font=font, fill=(0, 0, 0))
                    
                    # 绘制主文字
                    draw.text((x, y), line, font=font, fill='white')
                
                # 添加序号标记（左上角）
                draw.text((40, 40), f"{i+1}/{len(script_segments)}", font=self._load_font(30, font_name), fill=(255, 255, 255, 200))
                
                # 添加表情包装饰（如果开启）
                if use_emoji:
                    emoji = self._get_emoji_for_text(text)
                    if emoji:
                        try:
                            emoji_img = Image.open(emoji).convert("RGBA")
                            # 调整大小
                            emoji_img = emoji_img.resize((200, 200), Image.Resampling.LANCZOS)
                            # 粘贴到顶部中央（透明背景）
                            emoji_x = (self.resolution[0] - 200) // 2
                            emoji_y = 150
                            # 转换RGBA到RGB背景
                            if emoji_img.mode == 'RGBA':
                                # 创建白色背景
                                bg = Image.new('RGB', emoji_img.size, (255, 255, 255))
                                bg.paste(emoji_img, mask=emoji_img.split()[3])  # 使用alpha通道
                                img.paste(bg, (emoji_x, emoji_y))
                            else:
                                img.paste(emoji_img, (emoji_x, emoji_y))
                        except Exception as e:
                            logger.warning(f"添加表情失败: {e}")
                
                # 保存临时图片
                temp_img_path = self.output_dir / f"temp_{i}.png"
                img.save(temp_img_path)
                
                # 创建图片片段
                img_clip = ImageClip(str(temp_img_path), duration=self.duration_per_slide)
                image_clips.append(img_clip)
            
            # 合并所有片段
            final_video = concatenate_videoclips(image_clips, method="compose")
            
            # 输出视频
            output_path = self.output_dir / output_name
            final_video.write_videofile(
                str(output_path),
                fps=self.fps,
                codec='libx264',
                preset='ultrafast',  # 加快速度
                logger=None  # 减少日志输出
            )
            
            # 清理临时图片
            for i in range(len(script_segments)):
                temp_img = self.output_dir / f"temp_{i}.png"
                if temp_img.exists():
                    temp_img.unlink()
            
            logger.info(f"✅ 视频生成成功：{output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"生成视频失败：{e}")
            raise
    
    def _create_gradient_background(self, size: tuple, index: int) -> Image:
        """创建渐变背景（不同片段不同颜色）"""
        from PIL import Image, ImageDraw
        
        # 多种配色方案，根据index循环使用
        color_schemes = [
            # 蓝紫渐变
            [(60, 80, 150), (120, 80, 200)],
            # 橙红渐变
            [(200, 80, 60), (240, 120, 80)],
            # 绿蓝渐变
            [(40, 150, 120), (80, 180, 200)],
            # 紫粉渐变
            [(150, 60, 150), (200, 100, 180)],
            # 深蓝渐变
            [(30, 60, 100), (60, 100, 150)]
        ]
        
        scheme = color_schemes[index % len(color_schemes)]
        start_color, end_color = scheme
        
        # 创建渐变
        img = Image.new('RGB', size)
        draw = ImageDraw.Draw(img)
        
        for i in range(size[1]):
            ratio = i / size[1]
            color = tuple(
                int(start_color[j] + (end_color[j] - start_color[j]) * ratio)
                for j in range(3)
            )
            draw.line([(0, i), (size[0], i)], fill=color)
        
        return img
    
    def _load_font(self, size: int, font_name: str = "微软雅黑"):
        """加载字体（多种尝试）"""
        from PIL import ImageFont
        
        # 字体映射
        font_map = {
            "微软雅黑": ["msyh.ttc", "msyh.ttf"],
            "黑体": ["simhei.ttf", "SimHei.ttf"],
            "宋体": ["simsun.ttc", "simsun.ttf"],
            "楷体": ["simkai.ttf", "kaiti.ttf"]
        }
        
        # 尝试指定字体
        for font_file in font_map.get(font_name, []):
            try:
                return ImageFont.truetype(font_file, size)
            except:
                continue
        
        # 尝试所有字体
        for font_list in font_map.values():
            for font_file in font_list:
                try:
                    return ImageFont.truetype(font_file, size)
                except:
                    continue
        
        # 都失败了用默认字体
        return ImageFont.load_default()
    
    def _get_emoji_for_text(self, text: str) -> Optional[str]:
        """根据文本内容选择合适的表情"""
        from plugins.video_producer.asset_manager import AssetManager
        
        asset_mgr = AssetManager()
        emojis = asset_mgr.get_emojis()
        
        if not emojis:
            return None
        
        # 简单匹配（TODO: AI智能匹配）
        keywords_emoji_map = {
            "好": ["👍", "😊", "🎉"],
            "技巧": ["💡", "🔧", "⚡"],
            "方法": ["📝", "✨", "🎯"],
            "第一": ["1️⃣", "🥇"],
            "第二": ["2️⃣", "🥈"],
            "简单": ["😄", "👌"],
            "记得": ["📌", "⭐"]
        }
        
        # 尝试匹配关键词
        for keyword, emoji_list in keywords_emoji_map.items():
            if keyword in text:
                # TODO: 返回实际的表情包文件
                # 现在先返回None，需要先有表情包素材
                return None
        
        return None
    
    def _wrap_text(self, text: str, font, max_width: int) -> list:
        """文字自动换行"""
        from PIL import ImageDraw
        
        # 临时draw用于测量
        temp_img = Image.new('RGB', (1, 1))
        draw = ImageDraw.Draw(temp_img)
        
        words = list(text)  # 中文按字符分
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # 限制最多5行
        return lines[:5] if lines else [text]
    
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
    
    def _setup_ffmpeg(self):
        """配置FFmpeg路径"""
        # 检查项目内的FFmpeg
        project_ffmpeg = Path("tools/ffmpeg/bin/ffmpeg.exe")
        
        if project_ffmpeg.exists():
            # 使用项目内的FFmpeg
            os.environ["IMAGEIO_FFMPEG_EXE"] = str(project_ffmpeg.absolute())
            logger.info(f"✅ 使用项目FFmpeg: {project_ffmpeg}")
        else:
            # 使用系统FFmpeg（如果有）
            logger.warning("⚠️ 项目FFmpeg未找到，使用系统FFmpeg")
            logger.warning(f"请运行: tools\\ffmpeg\\下载FFmpeg.ps1")
    
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

