"""测试分析器"""
import unittest
from src.analyzer import TextAnalyzer


class TestTextAnalyzer(unittest.TestCase):
    """测试文本分析器"""
    
    def setUp(self):
        self.analyzer = TextAnalyzer()
    
    def test_extract_keywords(self):
        """测试关键词提取"""
        text = "华为发布新款手机，搭载麒麟芯片，支持5G网络"
        keywords = self.analyzer.extract_keywords(text, 3)
        self.assertIsInstance(keywords, list)
        self.assertGreater(len(keywords), 0)
    
    def test_sentiment_analysis_positive(self):
        """测试正面情感分析"""
        text = "华为技术突破，创新引领行业发展"
        sentiment, score = self.analyzer.analyze_sentiment(text)
        self.assertEqual(sentiment, '正面')
        self.assertGreater(score, 0)
    
    def test_sentiment_analysis_negative(self):
        """测试负面情感分析"""
        text = "华为面临制裁压力，市场竞争加剧"
        sentiment, score = self.analyzer.analyze_sentiment(text)
        self.assertEqual(sentiment, '负面')
        self.assertLess(score, 0)
    
    def test_empty_text(self):
        """测试空文本"""
        keywords = self.analyzer.extract_keywords("")
        self.assertEqual(keywords, [])
        
        sentiment, score = self.analyzer.analyze_sentiment("")
        self.assertEqual(sentiment, '中性')
        self.assertEqual(score, 0.0)


if __name__ == '__main__':
    unittest.main()