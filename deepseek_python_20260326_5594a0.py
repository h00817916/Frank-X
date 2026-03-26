"""文本分析器模块"""
import re
from typing import List, Tuple, Dict
from collections import Counter
import logging
import jieba
import jieba.analyse
from config.settings import SentimentConfig

logger = logging.getLogger(__name__)


class TextAnalyzer:
    """文本分析器"""
    
    def __init__(self):
        """初始化分析器"""
        self.config = SentimentConfig()
        self._init_jieba()
        
    def _init_jieba(self):
        """初始化jieba分词器"""
        # 添加自定义词典
        custom_words = ['华为', '麒麟', '鸿蒙', '5G', '芯片', '手机']
        for word in custom_words:
            jieba.add_word(word)
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """提取关键词"""
        if not text:
            return []
        
        try:
            # 使用TF-IDF提取关键词
            keywords = jieba.analyse.extract_tags(
                text, 
                topK=top_k, 
                withWeight=False,
                allowPOS=('n', 'nr', 'ns', 'nt', 'nz', 'v', 'vn')
            )
            return keywords
            
        except Exception as e:
            logger.error(f"关键词提取失败: {e}")
            return text[:50].split()[:top_k]
    
    def analyze_sentiment(self, text: str) -> Tuple[str, float]:
        """情感分析，返回情感标签和得分"""
        if not text:
            return '中性', 0.0
        
        try:
            # 分词
            words = jieba.lcut(text)
            
            positive_score = 0.0
            negative_score = 0.0
            
            # 计算情感得分
            for word in words:
                if word in self.config.POSITIVE_WORDS:
                    positive_score += self.config.POSITIVE_WEIGHT
                elif word in self.config.NEGATIVE_WORDS:
                    negative_score += self.config.NEGATIVE_WEIGHT
            
            # 计算综合得分
            total_score = positive_score - negative_score
            
            # 判断情感倾向
            if total_score > 1:
                sentiment = '正面'
            elif total_score < -0.5:
                sentiment = '负面'
            else:
                sentiment = '中性'
            
            return sentiment, total_score
            
        except Exception as e:
            logger.error(f"情感分析失败: {e}")
            return '中性', 0.0
    
    def calculate_statistics(self, news_list: List[Dict]) -> Dict:
        """计算新闻统计信息"""
        if not news_list:
            return {}
        
        try:
            # 来源统计
            source_counter = Counter(news.get('source', '未知') for news in news_list)
            
            # 情感统计
            sentiments = []
            for news in news_list:
                sentiment, _ = self.analyze_sentiment(news['title'])
                sentiments.append(sentiment)
            sentiment_counter = Counter(sentiments)
            
            # 关键词统计
            all_text = ' '.join(news['title'] for news in news_list)
            keywords = self.extract_keywords(all_text, 15)
            
            # 时间统计
            times = [news.get('time', '') for news in news_list if news.get('time')]
            
            return {
                'total': len(news_list),
                'sources': dict(source_counter.most_common(5)),
                'sentiment': dict(sentiment_counter),
                'keywords': keywords,
                'has_time': len(times),
                'avg_comment': sum(news.get('comment_count', 0) for news in news_list) / len(news_list)
            }
            
        except Exception as e:
            logger.error(f"统计计算失败: {e}")
            return {'total': len(news_list)}