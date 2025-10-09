"""
JieDimension Toolkit - 数据可视化图表模块
提供AI使用趋势图、发布统计图等可视化功能
Version: 1.0.0
"""

import matplotlib
matplotlib.use('TkAgg')  # 使用TkAgg后端支持CustomTkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.database import Database

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


class ChartGenerator:
    """图表生成器（带缓存优化）"""
    
    def __init__(self, db: Database, cache_duration: int = 300):
        """
        初始化图表生成器
        
        Args:
            db: 数据库实例
            cache_duration: 缓存有效期（秒），默认5分钟
        """
        self.db = db
        self.cache_duration = cache_duration
        
        # 缓存存储：{cache_key: (data, timestamp)}
        self._cache = {}
        self._cache_timestamps = {}
    
    def _get_cache_key(self, chart_type: str, **kwargs) -> str:
        """
        生成缓存键
        
        Args:
            chart_type: 图表类型
            **kwargs: 其他参数
            
        Returns:
            缓存键字符串
        """
        # 将kwargs转换为有序字符串
        params = '_'.join(f"{k}_{v}" for k, v in sorted(kwargs.items()))
        return f"{chart_type}_{params}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """
        检查缓存是否有效
        
        Args:
            cache_key: 缓存键
            
        Returns:
            True表示缓存有效，False表示已过期
        """
        if cache_key not in self._cache:
            return False
        
        timestamp = self._cache_timestamps.get(cache_key, 0)
        current_time = datetime.now().timestamp()
        
        return (current_time - timestamp) < self.cache_duration
    
    def _update_cache(self, cache_key: str, data: Any):
        """
        更新缓存
        
        Args:
            cache_key: 缓存键
            data: 要缓存的数据
        """
        self._cache[cache_key] = data
        self._cache_timestamps[cache_key] = datetime.now().timestamp()
    
    def clear_cache(self, chart_type: str = None):
        """
        清除缓存
        
        Args:
            chart_type: 图表类型，None表示清除所有缓存
        """
        if chart_type is None:
            self._cache.clear()
            self._cache_timestamps.clear()
        else:
            # 清除特定类型的缓存
            keys_to_remove = [k for k in self._cache.keys() if k.startswith(chart_type)]
            for key in keys_to_remove:
                self._cache.pop(key, None)
                self._cache_timestamps.pop(key, None)
    
    def _get_cache_remaining_time(self, cache_key: str) -> float:
        """
        获取缓存剩余时间
        
        Args:
            cache_key: 缓存键
            
        Returns:
            剩余秒数
        """
        if cache_key not in self._cache_timestamps:
            return 0
        
        timestamp = self._cache_timestamps[cache_key]
        current_time = datetime.now().timestamp()
        elapsed = current_time - timestamp
        
        return max(0, self.cache_duration - elapsed)
    
    async def create_ai_usage_trend_chart(
        self, 
        days: int = 7,
        figsize: Tuple[int, int] = (8, 4),
        force_refresh: bool = False
    ) -> Figure:
        """
        创建AI使用趋势图（带缓存）
        
        Args:
            days: 显示最近几天的数据
            figsize: 图表尺寸
            force_refresh: 强制刷新缓存
            
        Returns:
            matplotlib Figure对象
        """
        # 生成缓存键
        cache_key = self._get_cache_key('ai_usage_trend', days=days, figsize=figsize)
        
        # 检查缓存
        if not force_refresh and self._is_cache_valid(cache_key):
            print(f"✅ 使用缓存: AI使用趋势图 (剩余时间: {self._get_cache_remaining_time(cache_key):.0f}秒)")
            return self._cache[cache_key]
        
        # 创建图表
        fig = Figure(figsize=figsize, dpi=100, facecolor='#2b2b2b')
        ax = fig.add_subplot(111)
        
        # 设置背景色
        ax.set_facecolor('#1e1e1e')
        
        try:
            # 获取日期范围
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days-1)
            
            # 获取AI调用记录
            ai_calls = await self.db.get_ai_calls(
                start_date.isoformat(),
                end_date.isoformat()
            )
            
            if not ai_calls:
                # 无数据时显示提示
                ax.text(
                    0.5, 0.5, 
                    '暂无AI调用数据',
                    ha='center', va='center',
                    fontsize=16, color='gray',
                    transform=ax.transAxes
                )
                ax.set_xticks([])
                ax.set_yticks([])
                return fig
            
            # 按日期和提供商分组统计
            daily_stats = {}
            for call in ai_calls:
                call_date = datetime.fromisoformat(call['created_at']).date()
                provider = call['provider']
                
                if call_date not in daily_stats:
                    daily_stats[call_date] = {
                        'ollama': {'total': 0, 'success': 0},
                        'gemini': {'total': 0, 'success': 0}
                    }
                
                daily_stats[call_date][provider]['total'] += 1
                if call['success']:
                    daily_stats[call_date][provider]['success'] += 1
            
            # 生成完整日期序列（填充没有数据的日期）
            dates = []
            current_date = start_date.date()
            while current_date <= end_date.date():
                dates.append(current_date)
                if current_date not in daily_stats:
                    daily_stats[current_date] = {
                        'ollama': {'total': 0, 'success': 0},
                        'gemini': {'total': 0, 'success': 0}
                    }
                current_date += timedelta(days=1)
            
            # 提取数据
            ollama_counts = [daily_stats[d]['ollama']['total'] for d in dates]
            gemini_counts = [daily_stats[d]['gemini']['total'] for d in dates]
            
            # 绘制折线图
            ax.plot(dates, ollama_counts, marker='o', linewidth=2, 
                   color='#3498db', label='Ollama (本地)', markersize=6)
            ax.plot(dates, gemini_counts, marker='s', linewidth=2, 
                   color='#e74c3c', label='Gemini (云端)', markersize=6)
            
            # 设置标题和标签
            ax.set_title('AI调用趋势（最近{}天）'.format(days), 
                        fontsize=14, color='white', pad=15)
            ax.set_xlabel('日期', fontsize=11, color='gray')
            ax.set_ylabel('调用次数', fontsize=11, color='gray')
            
            # 设置网格
            ax.grid(True, alpha=0.2, linestyle='--', color='gray')
            
            # 设置坐标轴颜色
            ax.spines['bottom'].set_color('gray')
            ax.spines['left'].set_color('gray')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.tick_params(colors='gray')
            
            # 设置x轴日期格式
            if days <= 7:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
                ax.xaxis.set_major_locator(mdates.DayLocator())
            else:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, days // 7)))
            
            # 旋转x轴标签
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            # 添加图例
            legend = ax.legend(loc='upper left', framealpha=0.8, 
                             facecolor='#2b2b2b', edgecolor='gray')
            plt.setp(legend.get_texts(), color='white')
            
            # 调整布局
            fig.tight_layout()
            
        except Exception as e:
            print(f"生成AI使用趋势图失败: {e}")
            ax.text(
                0.5, 0.5, 
                f'图表生成失败\n{str(e)}',
                ha='center', va='center',
                fontsize=12, color='red',
                transform=ax.transAxes
            )
        
        # 更新缓存
        self._update_cache(cache_key, fig)
        print(f"📊 生成新图表: AI使用趋势图 (缓存{self.cache_duration}秒)")
        
        return fig
    
    async def create_publish_stats_chart(
        self,
        days: int = 30,
        figsize: Tuple[int, int] = (8, 4),
        force_refresh: bool = False
    ) -> Figure:
        """
        创建发布统计图（柱状图，带缓存）
        
        Args:
            days: 统计最近几天的数据
            figsize: 图表尺寸
            force_refresh: 强制刷新缓存
            
        Returns:
            matplotlib Figure对象
        """
        # 生成缓存键
        cache_key = self._get_cache_key('publish_stats', days=days, figsize=figsize)
        
        # 检查缓存
        if not force_refresh and self._is_cache_valid(cache_key):
            print(f"✅ 使用缓存: 发布统计图 (剩余时间: {self._get_cache_remaining_time(cache_key):.0f}秒)")
            return self._cache[cache_key]
        
        # 创建图表
        fig = Figure(figsize=figsize, dpi=100, facecolor='#2b2b2b')
        ax = fig.add_subplot(111)
        
        # 设置背景色
        ax.set_facecolor('#1e1e1e')
        
        try:
            # 获取日期范围
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days-1)
            
            # 获取任务数据
            tasks = await self.db.get_tasks_by_date_range(
                start_date.isoformat(),
                end_date.isoformat()
            )
            
            if not tasks:
                # 无数据时显示提示
                ax.text(
                    0.5, 0.5, 
                    '暂无发布数据',
                    ha='center', va='center',
                    fontsize=16, color='gray',
                    transform=ax.transAxes
                )
                ax.set_xticks([])
                ax.set_yticks([])
                return fig
            
            # 按平台统计
            platform_stats = {}
            for task in tasks:
                platform = task['platform']
                status = task['status']
                
                if platform not in platform_stats:
                    platform_stats[platform] = {
                        'total': 0,
                        'completed': 0,
                        'failed': 0,
                        'pending': 0
                    }
                
                platform_stats[platform]['total'] += 1
                if status in platform_stats[platform]:
                    platform_stats[platform][status] += 1
            
            # 提取数据
            platforms = list(platform_stats.keys())
            completed_counts = [platform_stats[p]['completed'] for p in platforms]
            failed_counts = [platform_stats[p]['failed'] for p in platforms]
            pending_counts = [platform_stats[p]['pending'] for p in platforms]
            
            # 设置柱状图位置
            x = range(len(platforms))
            width = 0.25
            
            # 绘制堆叠柱状图
            ax.bar(x, completed_counts, width, label='成功', color='#2ecc71')
            ax.bar(x, failed_counts, width, bottom=completed_counts, 
                  label='失败', color='#e74c3c')
            
            bottom = [completed_counts[i] + failed_counts[i] for i in range(len(platforms))]
            ax.bar(x, pending_counts, width, bottom=bottom,
                  label='待处理', color='#f39c12')
            
            # 设置标题和标签
            ax.set_title(f'发布统计（最近{days}天）', 
                        fontsize=14, color='white', pad=15)
            ax.set_xlabel('平台', fontsize=11, color='gray')
            ax.set_ylabel('任务数量', fontsize=11, color='gray')
            
            # 设置x轴标签
            platform_names = {
                'xianyu': '🐟 闲鱼',
                'xiaohongshu': '📝 小红书',
                'zhihu': '📖 知乎',
                'bilibili': '🎬 B站'
            }
            ax.set_xticks(x)
            ax.set_xticklabels([platform_names.get(p, p.upper()) for p in platforms])
            
            # 设置网格
            ax.grid(True, alpha=0.2, linestyle='--', color='gray', axis='y')
            
            # 设置坐标轴颜色
            ax.spines['bottom'].set_color('gray')
            ax.spines['left'].set_color('gray')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.tick_params(colors='gray')
            
            # 添加图例
            legend = ax.legend(loc='upper right', framealpha=0.8,
                             facecolor='#2b2b2b', edgecolor='gray')
            plt.setp(legend.get_texts(), color='white')
            
            # 调整布局
            fig.tight_layout()
            
        except Exception as e:
            print(f"生成发布统计图失败: {e}")
            ax.text(
                0.5, 0.5, 
                f'图表生成失败\n{str(e)}',
                ha='center', va='center',
                fontsize=12, color='red',
                transform=ax.transAxes
            )
        
        # 更新缓存
        self._update_cache(cache_key, fig)
        print(f"📊 生成新图表: 发布统计图 (缓存{self.cache_duration}秒)")
        
        return fig
    
    async def create_success_rate_chart(
        self,
        days: int = 7,
        figsize: Tuple[int, int] = (8, 4),
        force_refresh: bool = False
    ) -> Figure:
        """
        创建成功率趋势图（带缓存）
        
        Args:
            days: 显示最近几天的数据
            figsize: 图表尺寸
            force_refresh: 强制刷新缓存
            
        Returns:
            matplotlib Figure对象
        """
        # 生成缓存键
        cache_key = self._get_cache_key('success_rate', days=days, figsize=figsize)
        
        # 检查缓存
        if not force_refresh and self._is_cache_valid(cache_key):
            print(f"✅ 使用缓存: 成功率趋势图 (剩余时间: {self._get_cache_remaining_time(cache_key):.0f}秒)")
            return self._cache[cache_key]
        
        # 创建图表
        fig = Figure(figsize=figsize, dpi=100, facecolor='#2b2b2b')
        ax = fig.add_subplot(111)
        
        # 设置背景色
        ax.set_facecolor('#1e1e1e')
        
        try:
            # 获取日期范围
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days-1)
            
            # 获取AI调用记录
            ai_calls = await self.db.get_ai_calls(
                start_date.isoformat(),
                end_date.isoformat()
            )
            
            if not ai_calls:
                # 无数据时显示提示
                ax.text(
                    0.5, 0.5, 
                    '暂无数据',
                    ha='center', va='center',
                    fontsize=16, color='gray',
                    transform=ax.transAxes
                )
                ax.set_xticks([])
                ax.set_yticks([])
                return fig
            
            # 按日期和提供商分组统计
            daily_stats = {}
            for call in ai_calls:
                call_date = datetime.fromisoformat(call['created_at']).date()
                provider = call['provider']
                
                if call_date not in daily_stats:
                    daily_stats[call_date] = {
                        'ollama': {'total': 0, 'success': 0},
                        'gemini': {'total': 0, 'success': 0}
                    }
                
                daily_stats[call_date][provider]['total'] += 1
                if call['success']:
                    daily_stats[call_date][provider]['success'] += 1
            
            # 生成完整日期序列
            dates = []
            current_date = start_date.date()
            while current_date <= end_date.date():
                dates.append(current_date)
                if current_date not in daily_stats:
                    daily_stats[current_date] = {
                        'ollama': {'total': 0, 'success': 0},
                        'gemini': {'total': 0, 'success': 0}
                    }
                current_date += timedelta(days=1)
            
            # 计算成功率
            ollama_rates = []
            gemini_rates = []
            for d in dates:
                ollama_total = daily_stats[d]['ollama']['total']
                ollama_success = daily_stats[d]['ollama']['success']
                ollama_rate = (ollama_success / ollama_total * 100) if ollama_total > 0 else 0
                ollama_rates.append(ollama_rate)
                
                gemini_total = daily_stats[d]['gemini']['total']
                gemini_success = daily_stats[d]['gemini']['success']
                gemini_rate = (gemini_success / gemini_total * 100) if gemini_total > 0 else 0
                gemini_rates.append(gemini_rate)
            
            # 绘制折线图
            ax.plot(dates, ollama_rates, marker='o', linewidth=2,
                   color='#3498db', label='Ollama', markersize=6)
            ax.plot(dates, gemini_rates, marker='s', linewidth=2,
                   color='#e74c3c', label='Gemini', markersize=6)
            
            # 设置标题和标签
            ax.set_title(f'AI成功率趋势（最近{days}天）',
                        fontsize=14, color='white', pad=15)
            ax.set_xlabel('日期', fontsize=11, color='gray')
            ax.set_ylabel('成功率 (%)', fontsize=11, color='gray')
            
            # 设置y轴范围
            ax.set_ylim(0, 105)
            
            # 设置网格
            ax.grid(True, alpha=0.2, linestyle='--', color='gray')
            
            # 设置坐标轴颜色
            ax.spines['bottom'].set_color('gray')
            ax.spines['left'].set_color('gray')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.tick_params(colors='gray')
            
            # 设置x轴日期格式
            if days <= 7:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
                ax.xaxis.set_major_locator(mdates.DayLocator())
            else:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, days // 7)))
            
            # 旋转x轴标签
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            # 添加图例
            legend = ax.legend(loc='lower right', framealpha=0.8,
                             facecolor='#2b2b2b', edgecolor='gray')
            plt.setp(legend.get_texts(), color='white')
            
            # 调整布局
            fig.tight_layout()
            
        except Exception as e:
            print(f"生成成功率趋势图失败: {e}")
            ax.text(
                0.5, 0.5,
                f'图表生成失败\n{str(e)}',
                ha='center', va='center',
                fontsize=12, color='red',
                transform=ax.transAxes
            )
        
        # 更新缓存
        self._update_cache(cache_key, fig)
        print(f"📊 生成新图表: 成功率趋势图 (缓存{self.cache_duration}秒)")
        
        return fig


def embed_chart_in_frame(parent, figure: Figure) -> FigureCanvasTkAgg:
    """
    将matplotlib图表嵌入到CustomTkinter框架中
    
    Args:
        parent: 父容器
        figure: matplotlib Figure对象
        
    Returns:
        FigureCanvasTkAgg对象
    """
    canvas = FigureCanvasTkAgg(figure, master=parent)
    canvas.draw()
    return canvas


# ===== 测试代码 =====

async def test_charts():
    """测试图表生成"""
    import asyncio
    
    # 创建数据库连接
    db = Database()
    await db.connect()
    
    # 创建图表生成器
    generator = ChartGenerator(db)
    
    # 测试AI使用趋势图
    print("生成AI使用趋势图...")
    fig1 = await generator.create_ai_usage_trend_chart(days=7)
    fig1.savefig('test_ai_usage.png', facecolor='#2b2b2b')
    print("✅ AI使用趋势图已保存到 test_ai_usage.png")
    
    # 测试发布统计图
    print("生成发布统计图...")
    fig2 = await generator.create_publish_stats_chart(days=30)
    fig2.savefig('test_publish_stats.png', facecolor='#2b2b2b')
    print("✅ 发布统计图已保存到 test_publish_stats.png")
    
    # 测试成功率趋势图
    print("生成成功率趋势图...")
    fig3 = await generator.create_success_rate_chart(days=7)
    fig3.savefig('test_success_rate.png', facecolor='#2b2b2b')
    print("✅ 成功率趋势图已保存到 test_success_rate.png")
    
    await db.close()
    print("\n🎉 所有图表测试完成！")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_charts())

