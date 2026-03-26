"""摘要生成器模块"""
from typing import List, Dict
from datetime import datetime
import logging
from src.analyzer import TextAnalyzer

logger = logging.getLogger(__name__)


class NewsSummarizer:
    """新闻摘要生成器"""
    
    def __init__(self):
        """初始化摘要生成器"""
        self.analyzer = TextAnalyzer()
    
    def generate_summary(self, news_list: List[Dict]) -> str:
        """生成新闻总结"""
        if not news_list:
            return self._generate_empty_summary()
        
        try:
            # 计算统计信息
            stats = self.analyzer.calculate_statistics(news_list)
            
            # 生成总结
            summary_parts = []
            
            # 头部
            summary_parts.append(self._generate_header())
            
            # 总体概况
            summary_parts.append(self._generate_overview(stats))
            
            # 热点关键词
            summary_parts.append(self._generate_keywords(stats.get('keywords', [])))
            
            # 情感分析
            summary_parts.append(self._generate_sentiment_analysis(stats.get('sentiment', {})))
            
            # 重要新闻
            summary_parts.append(self._generate_important_news(news_list[:10]))
            
            # 简讯速览
            short_news = self._get_short_news(news_list)
            if short_news:
                summary_parts.append(self._generate_short_news(short_news[:5]))
            
            # 今日总结
            summary_parts.append(self._generate_conclusion(stats))
            
            return '\n'.join(summary_parts)
            
        except Exception as e:
            logger.error(f"生成摘要失败: {e}")
            return f"生成摘要时出错: {e}"
    
    def _generate_header(self) -> str:
        """生成头部"""
        today = datetime.now().strftime('%Y年%m月%d日')
        return f"""
{'='*70}
华为新闻日报 - {today}
{'='*70}
"""
    
    def _generate_overview(self, stats: Dict) -> str:
        """生成总体概况"""
        total = stats.get('total', 0)
        sources = stats.get('sources', {})
        
        sources_text = ', '.join([f"{k}: {v}" for k, v in sources.items()]) if sources else '无数据'
        
        return f"""
【总体概况】
今日共收集到 {total} 条华为相关新闻
新闻来源分布: {sources_text}
"""
    
    def _generate_keywords(self, keywords: List[str]) -> str:
        """生成热点关键词"""
        if not keywords:
            return "\n【热点关键词】\n暂无关键词数据"
        
        return f"""
【热点关键词】
{', '.join(keywords[:10])}
"""
    
    def _generate_sentiment_analysis(self, sentiment: Dict) -> str:
        """生成情感分析"""
        positive = sentiment.get('正面', 0)
        negative = sentiment.get('负面', 0)
        neutral = sentiment.get('中性', 0)
        
        return f"""
【情感分析】
正面新闻: {positive} 条
负面新闻: {negative} 条
中性新闻: {neutral} 条
"""
    
    def _generate_important_news(self, news_list: List[Dict]) -> str:
        """生成重要新闻"""
        if not news_list:
            return "\n【重要新闻摘要】\n暂无重要新闻"
        
        result = "\n【重要新闻摘要】"
        
        for i, news in enumerate(news_list, 1):
            sentiment, score = self.analyzer.analyze_sentiment(news['title'])
            sentiment_emoji = {'正面': '📈', '负面': '📉', '中性': '📊'}.get(sentiment, '📰')
            
            result += f"\n\n{i}. {sentiment_emoji} 【{sentiment}】 {news['title']}"
            
            if news.get('abstract'):
                abstract = news['abstract'][:120]
                result += f"\n   摘要: {abstract}..."
            
            if news.get('source'):
                result += f"\n   来源: {news['source']}"
            
            if news.get('comment_count', 0) > 0:
                result += f" | 评论: {news['comment_count']}条"
        
        return result
    
    def _get_short_news(self, news_list: List[Dict]) -> List[Dict]:
        """获取简短新闻"""
        return [news for news in news_list if len(news['title']) < 20]
    
    def _generate_short_news(self, short_news: List[Dict]) -> str:
        """生成简讯速览"""
        result = "\n\n【简讯速览】"
        
        for news in short_news:
            sentiment, _ = self.analyzer.analyze_sentiment(news['title'])
            emoji = {'正面': '✓', '负面': '⚠', '中性': '○'}.get(sentiment, '•')
            result += f"\n{emoji} {news['title']}"
        
        return result
    
    def _generate_conclusion(self, stats: Dict) -> str:
        """生成今日总结"""
        sentiment = stats.get('sentiment', {})
        positive = sentiment.get('正面', 0)
        negative = sentiment.get('负面', 0)
        
        result = f"""
{'='*70}
【今日总结】
"""
        
        if positive > negative:
            result += "今日华为相关新闻整体偏向正面，显示出积极的发展态势。"
        elif negative > positive:
            result += "今日华为相关新闻中负面信息较多，需关注相关挑战。"
        else:
            result += "今日华为相关新闻保持中性，各方面情况相对平稳。"
        
        keywords = stats.get('keywords', [])
        if keywords:
            result += f"\n重点关注: {'、'.join(keywords[:3])} 等关键词相关的新闻报道。"
        
        result += f"\n\n报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return result
    
    def _generate_empty_summary(self) -> str:
        """生成空总结"""
        return f"""
{'='*70}
华为新闻日报 - {datetime.now().strftime('%Y年%m月%d日')}
{'='*70}

【总体概况】
今日未收集到华为相关新闻

可能原因：
1. 网络连接问题
2. 新闻源暂时无数据
3. 反爬虫机制限制

建议：
- 检查网络连接
- 稍后重试
- 检查日志文件获取详细信息

报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""