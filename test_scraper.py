"""快速测试内容抓取"""
import asyncio
from plugins.video_producer.content_scraper import ContentScraper

async def main():
    scraper = ContentScraper()
    
    print("🎬 测试B站热门抓取...")
    videos = await scraper.scrape_bilibili_hot(5)
    
    print(f"\n✅ 成功抓取{len(videos)}个视频:\n")
    for i, v in enumerate(videos, 1):
        print(f"{i}. {v.get('title')}")
        print(f"   播放: {v.get('play'):,} | 点赞: {v.get('like'):,}")
        print(f"   作者: {v.get('author')}")
        print()

if __name__ == "__main__":
    asyncio.run(main())

