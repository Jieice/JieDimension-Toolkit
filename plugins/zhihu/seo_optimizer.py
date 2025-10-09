"""
SEO优化器
针对知乎平台的搜索引擎优化
"""

import re
from typing import List, Dict, Any, Optional
from collections import Counter
import jieba  # 中文分词


class SEOOptimizer:
    """SEO优化器"""
    
    # 停用词列表（常见的无意义词）
    STOP_WORDS = {
        "的", "了", "在", "是", "我", "有", "和", "就", 
        "不", "人", "都", "一", "一个", "上", "也", "很",
        "到", "说", "要", "去", "你", "会", "着", "没有",
        "看", "好", "自己", "这"
    }
    
    def __init__(self):
        """初始化SEO优化器"""
        pass
    
    def extract_keywords(
        self,
        text: str,
        top_k: int = 10,
        min_length: int = 2
    ) -> List[Dict[str, Any]]:
        """
        从文本中提取关键词
        
        Args:
            text: 文本内容
            top_k: 返回前K个关键词
            min_length: 最小词长
            
        Returns:
            关键词列表，每个包含词和权重
        """
        # 中文分词
        words = jieba.cut(text)
        
        # 过滤
        filtered_words = [
            word for word in words
            if len(word) >= min_length and word not in self.STOP_WORDS
        ]
        
        # 统计词频
        word_counts = Counter(filtered_words)
        
        # 计算权重（TF）
        total = sum(word_counts.values())
        keywords = [
            {
                "word": word,
                "count": count,
                "weight": round(count / total, 4)
            }
            for word, count in word_counts.most_common(top_k)
        ]
        
        return keywords
    
    def optimize_keywords_layout(
        self,
        title: str,
        keywords: List[str],
        max_length: int = 50
    ) -> str:
        """
        优化标题中的关键词布局
        
        Args:
            title: 原标题
            keywords: 关键词列表
            max_length: 最大长度
            
        Returns:
            优化后的标题
        """
        # 1. 确保主关键词在前20个字内
        if keywords:
            main_keyword = keywords[0]
            
            # 如果主关键词不在前面，尝试前置
            if main_keyword in title and title.find(main_keyword) > 20:
                title = title.replace(main_keyword, "", 1)
                title = f"{main_keyword}{title}"
        
        # 2. 确保包含尽可能多的关键词
        for keyword in keywords[1:]:
            if keyword not in title:
                # 尝试在合适位置插入
                if len(title) + len(keyword) + 1 <= max_length:
                    # 简单策略：在中间插入
                    mid = len(title) // 2
                    title = title[:mid] + keyword + title[mid:]
        
        # 3. 控制长度
        if len(title) > max_length:
            title = title[:max_length - 3] + "..."
        
        return title
    
    def generate_long_tail_keywords(
        self,
        main_keyword: str,
        related_keywords: List[str]
    ) -> List[str]:
        """
        生成长尾关键词
        
        Args:
            main_keyword: 主关键词
            related_keywords: 相关关键词
            
        Returns:
            长尾关键词列表
        """
        long_tail = []
        
        # 组合策略
        patterns = [
            "{main} {related}",
            "如何 {main}",
            "{main} 教程",
            "{main} 方法",
            "{main} 技巧",
            "{main} 指南",
            "最好的 {main}",
            "{main} 推荐",
        ]
        
        for related in related_keywords:
            for pattern in patterns:
                keyword = pattern.format(main=main_keyword, related=related)
                long_tail.append(keyword)
        
        return long_tail[:10]  # 返回前10个
    
    def generate_meta_description(
        self,
        content: str,
        keywords: Optional[List[str]] = None,
        max_length: int = 160
    ) -> str:
        """
        生成SEO元描述
        
        Args:
            content: 文章内容
            keywords: 关键词列表
            max_length: 最大长度
            
        Returns:
            元描述
        """
        # 1. 提取文章开头（通常是摘要）
        sentences = re.split(r'[。！？\n]', content)
        description = sentences[0] if sentences else content[:max_length]
        
        # 2. 确保包含关键词
        if keywords:
            for keyword in keywords[:3]:  # 前3个关键词
                if keyword not in description:
                    # 尝试在合适位置插入
                    if len(description) + len(keyword) + 1 <= max_length:
                        description = f"{keyword}：{description}"
                        break
        
        # 3. 控制长度
        if len(description) > max_length:
            description = description[:max_length - 3] + "..."
        
        return description
    
    def analyze_keyword_density(
        self,
        text: str,
        keywords: List[str]
    ) -> Dict[str, Any]:
        """
        分析关键词密度
        
        Args:
            text: 文本
            keywords: 关键词列表
            
        Returns:
            密度分析结果
        """
        # 总字数
        total_chars = len(text)
        
        # 分析每个关键词
        density_data = {}
        for keyword in keywords:
            count = text.count(keyword)
            density = round((len(keyword) * count) / total_chars * 100, 2)
            
            # 判断密度是否合理（2-8%为最佳）
            status = "最佳" if 2 <= density <= 8 else "过低" if density < 2 else "过高"
            
            density_data[keyword] = {
                "count": count,
                "density": density,
                "status": status
            }
        
        return density_data
    
    def suggest_internal_links(
        self,
        content: str,
        available_articles: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        建议内部链接
        
        Args:
            content: 当前文章内容
            available_articles: 可用文章列表 [{"title": "...", "url": "..."}]
            
        Returns:
            推荐链接列表
        """
        suggestions = []
        
        # 提取当前文章关键词
        current_keywords = self.extract_keywords(content, top_k=20)
        current_words = {kw["word"] for kw in current_keywords}
        
        # 匹配相关文章
        for article in available_articles:
            article_title = article.get("title", "")
            article_keywords = self.extract_keywords(article_title, top_k=10)
            article_words = {kw["word"] for kw in article_keywords}
            
            # 计算相关度（共同关键词数量）
            common_words = current_words & article_words
            relevance = len(common_words)
            
            if relevance > 0:
                suggestions.append({
                    "title": article_title,
                    "url": article.get("url", ""),
                    "relevance": relevance,
                    "common_keywords": list(common_words)
                })
        
        # 按相关度排序
        suggestions.sort(key=lambda x: x["relevance"], reverse=True)
        
        return suggestions[:5]  # 返回前5个
    
    def check_readability(self, text: str) -> Dict[str, Any]:
        """
        检查可读性
        
        Args:
            text: 文本
            
        Returns:
            可读性分析
        """
        # 统计
        total_chars = len(text)
        sentences = len(re.split(r'[。！？]', text))
        paragraphs = len(re.split(r'\n\n+', text.strip()))
        
        # 计算指标
        avg_sentence_length = total_chars / sentences if sentences > 0 else 0
        avg_paragraph_length = total_chars / paragraphs if paragraphs > 0 else 0
        
        # 评分
        score = 100
        issues = []
        
        # 1. 句子长度（建议20-50字）
        if avg_sentence_length > 60:
            score -= 20
            issues.append("句子过长，建议分段")
        elif avg_sentence_length < 15:
            score -= 10
            issues.append("句子过短，可适当增加描述")
        
        # 2. 段落长度（建议100-300字）
        if avg_paragraph_length > 400:
            score -= 20
            issues.append("段落过长，建议增加分段")
        
        # 3. 总长度
        if total_chars < 500:
            score -= 15
            issues.append("内容过短，建议增加到800字以上")
        
        return {
            "score": max(0, score),
            "level": "优秀" if score >= 80 else "良好" if score >= 60 else "需改进",
            "total_chars": total_chars,
            "sentences": sentences,
            "paragraphs": paragraphs,
            "avg_sentence_length": round(avg_sentence_length, 1),
            "avg_paragraph_length": round(avg_paragraph_length, 1),
            "issues": issues
        }


# 测试代码
def test_seo_optimizer():
    """测试SEO优化器"""
    print("="*60)
    print("🧪 测试SEO优化器")
    print("="*60)
    
    optimizer = SEOOptimizer()
    
    # 测试文本
    test_content = """
    Python是一门非常强大的编程语言，它在数据科学、人工智能、Web开发等领域都有广泛应用。
    学习Python需要掌握基础语法、数据结构、面向对象编程等核心概念。
    本文将介绍Python学习的完整路径，帮助初学者快速入门。
    我们会从环境搭建开始，逐步深入到实战项目开发。
    """
    
    # 测试1：提取关键词
    print("\n1️⃣ 测试关键词提取")
    keywords = optimizer.extract_keywords(test_content, top_k=5)
    for kw in keywords:
        print(f"   - {kw['word']}: 权重 {kw['weight']}, 出现 {kw['count']} 次")
    
    # 测试2：优化关键词布局
    print("\n2️⃣ 测试关键词布局优化")
    title = "编程语言学习指南"
    optimized_title = optimizer.optimize_keywords_layout(
        title, 
        ["Python", "入门", "实战"]
    )
    print(f"   原标题: {title}")
    print(f"   优化后: {optimized_title}")
    
    # 测试3：生成长尾关键词
    print("\n3️⃣ 测试长尾关键词生成")
    long_tail = optimizer.generate_long_tail_keywords(
        "Python",
        ["入门", "教程"]
    )
    print("   长尾关键词:")
    for i, kw in enumerate(long_tail[:5], 1):
        print(f"   {i}. {kw}")
    
    # 测试4：生成元描述
    print("\n4️⃣ 测试元描述生成")
    meta_desc = optimizer.generate_meta_description(
        test_content,
        keywords=["Python", "学习", "入门"]
    )
    print(f"   元描述: {meta_desc}")
    
    # 测试5：关键词密度分析
    print("\n5️⃣ 测试关键词密度分析")
    density = optimizer.analyze_keyword_density(
        test_content,
        ["Python", "学习", "编程"]
    )
    for word, data in density.items():
        print(f"   - {word}: {data['density']}% ({data['status']}), 出现{data['count']}次")
    
    # 测试6：可读性检查
    print("\n6️⃣ 测试可读性检查")
    readability = optimizer.check_readability(test_content)
    print(f"   评分: {readability['score']}/100 ({readability['level']})")
    print(f"   总字数: {readability['total_chars']}")
    print(f"   平均句长: {readability['avg_sentence_length']}字")
    if readability['issues']:
        print(f"   建议: {', '.join(readability['issues'])}")
    
    print("\n" + "="*60)
    print("✅ 测试完成！")
    print("="*60)


if __name__ == "__main__":
    test_seo_optimizer()


