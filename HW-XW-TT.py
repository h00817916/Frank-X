import requests
from bs4 import BeautifulSoup
import re
import json
import time
from datetime import datetime, timedelta
import os
from collections import Counter
import jieba
import jieba.analyse

class HuaweiNewsCollector:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.news_list = []
        
    def get_toutiao_news(self):
        """从今日头条抓取华为相关新闻"""
        try:
            # 今日头条搜索API
            url = "https://www.toutiao.com/search/?"
            params = {
                'keyword': '华为',
                'offset': 0,
                'format': 'json',
                'autoload': 'true',
                'count': 20,
                'cur_tab': 1,
                'from': 'search_tab'
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            data = response.json()
            
            news_items = []
            if 'data' in data:
                for item in data['data']:
                    if 'title' in item and '华为' in item['title']:
                        news = {
                            'title': item['title'],
                            'source': item.get('source', '今日头条'),
                            'time': item.get('datetime', ''),
                            'url': item.get('article_url', ''),
                            'abstract': item.get('abstract', ''),
                            'comment_count': item.get('comment_count', 0)
                        }
                        news_items.append(news)
            
            # 如果API失败，使用备用爬虫方法
            if not news_items:
                news_items = self._backup_crawler()
                
            return news_items
            
        except Exception as e:
            print(f"抓取今日头条新闻失败: {e}")
            return self._backup_crawler()
    
    def _backup_crawler(self):
        """备用爬虫方法"""
        try:
            # 百度新闻作为备用
            url = "https://news.baidu.com/ns"
            params = {
                'word': '华为',
                'cl': 1,
                'tn': 'news',
                'rn': 20
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            news_items = []
            for item in soup.find_all('div', class_='result'):
                title_tag = item.find('h3')
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    if '华为' in title:
                        news = {
                            'title': title,
                            'source': item.find('div', class_='c-author').get_text(strip=True) if item.find('div', class_='c-author') else '百度新闻',
                            'time': '',
                            'url': title_tag.find('a')['href'] if title_tag.find('a') else '',
                            'abstract': item.find('div', class_='c-summary').get_text(strip=True) if item.find('div', class_='c-summary') else '',
                            'comment_count': 0
                        }
                        news_items.append(news)
            
            return news_items
            
        except Exception as e:
            print(f"备用爬虫失败: {e}")
            return []
    
    def extract_keywords(self, text):
        """提取关键词"""
        try:
            keywords = jieba.analyse.extract_tags(text, topK=10, withWeight=False)
            return keywords
        except:
            return text[:20].split()
    
    def analyze_news_sentiment(self, text):
        """简单的情感分析"""
        positive_words = ['突破', '领先', '创新', '成功', '增长', '优秀', '第一', '超越', '获奖', '好评']
        negative_words = ['问题', '困难', '挑战', '下滑', '亏损', '竞争', '压力', '限制', '制裁']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            return '正面'
        elif negative_count > positive_count:
            return '负面'
        else:
            return '中性'
    
    def generate_summary(self, news_items):
        """生成新闻总结"""
        if not news_items:
            return "今日暂无华为相关新闻"
        
        # 统计信息
        total_news = len(news_items)
        titles = [item['title'] for item in news_items]
        sources = [item['source'] for item in news_items if item['source']]
        
        # 关键词提取
        all_text = ' '.join(titles)
        keywords = self.extract_keywords(all_text)
        
        # 情感分析
        sentiments = [self.analyze_news_sentiment(item['title']) for item in news_items]
        sentiment_counts = Counter(sentiments)
        
        # 按标题长度分类
        short_news = [t for t in titles if len(t) < 20]
        long_news = [t for t in titles if len(t) >= 20]
        
        # 生成总结
        summary = f"""
{'='*60}
华为新闻日报 - {datetime.now().strftime('%Y年%m月%d日')}
{'='*60}

【总体概况】
今日共收集到 {total_news} 条华为相关新闻
新闻来源分布: {dict(Counter(sources[:3]))}

【热点关键词】
{', '.join(keywords[:8])}

【情感分析】
正面新闻: {sentiment_counts.get('正面', 0)} 条
负面新闻: {sentiment_counts.get('负面', 0)} 条
中性新闻: {sentiment_counts.get('中性', 0)} 条

【重要新闻摘要】
"""
        
        # 添加重要新闻
        for i, item in enumerate(news_items[:10], 1):
            sentiment = self.analyze_news_sentiment(item['title'])
            summary += f"\n{i}. 【{sentiment}】 {item['title']}"
            if item['abstract']:
                summary += f"\n   摘要: {item['abstract'][:100]}..."
            summary += f"\n   来源: {item['source']}"
        
        # 添加简短新闻列表
        if short_news:
            summary += f"\n\n【简讯速览】"
            for news in short_news[:5]:
                summary += f"\n• {news}"
        
        # 添加总结评语
        summary += f"""
\n{'='*60}
【今日总结】
"""
        
        if sentiment_counts.get('正面', 0) > sentiment_counts.get('负面', 0):
            summary += "今日华为相关新闻整体偏向正面，显示出积极的发展态势。"
        elif sentiment_counts.get('负面', 0) > sentiment_counts.get('正面', 0):
            summary += "今日华为相关新闻中负面信息较多，需关注相关挑战。"
        else:
            summary += "今日华为相关新闻保持中性，各方面情况相对平稳。"
        
        summary += f"\n重点关注: {'、'.join(keywords[:3])} 等关键词相关的新闻报道。"
        summary += f"\n\n报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return summary
    
    def save_summary(self, summary):
        """保存总结到文件"""
        # 创建每日文件夹
        today = datetime.now().strftime('%Y%m%d')
        folder = f"huawei_news_{today}"
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        # 保存到文件
        filename = f"{folder}/summary_{today}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        # 同时保存原始新闻数据
        data_file = f"{folder}/raw_data_{today}.json"
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(self.news_list, f, ensure_ascii=False, indent=2)
        
        return filename
    
    def run_daily_task(self):
        """执行每日任务"""
        print(f"开始执行每日华为新闻抓取任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 抓取新闻
        print("正在抓取华为相关新闻...")
        self.news_list = self.get_toutiao_news()
        print(f"成功抓取 {len(self.news_list)} 条新闻")
        
        # 生成总结
        print("正在生成新闻总结...")
        summary = self.generate_summary(self.news_list)
        
        # 保存总结
        filename = self.save_summary(summary)
        print(f"总结已保存到: {filename}")
        
        # 打印到控制台
        print("\n" + summary)
        
        return summary

def schedule_daily_task():
    """定时执行每日任务"""
    collector = HuaweiNewsCollector()
    
    # 获取当前时间
    now = datetime.now()
    
    # 计算下一次执行时间（每天上午9点）
    next_run = now.replace(hour=9, minute=0, second=0, microsecond=0)
    if now >= next_run:
        next_run += timedelta(days=1)
    
    print(f"任务已启动，下一次执行时间: {next_run}")
    
    while True:
        try:
            # 立即执行一次
            collector.run_daily_task()
            
            # 计算到第二天9点的等待时间
            now = datetime.now()
            next_run = now.replace(hour=9, minute=0, second=0, microsecond=0)
            if now >= next_run:
                next_run += timedelta(days=1)
            
            wait_seconds = (next_run - now).total_seconds()
            print(f"等待 {wait_seconds/3600:.1f} 小时后执行下一次任务")
            time.sleep(wait_seconds)
            
        except KeyboardInterrupt:
            print("\n任务被用户中断")
            break
        except Exception as e:
            print(f"任务执行出错: {e}")
            print("等待1小时后重试...")
            time.sleep(3600)

if __name__ == "__main__":
    # 安装依赖库
    # pip install requests beautifulsoup4 jieba
    
    print("华为新闻自动抓取与总结系统")
    print("="*50)
    
    # 选择运行模式
    print("请选择运行模式:")
    print("1. 立即执行一次")
    print("2. 每天定时执行")
    
    choice = input("请输入选择 (1/2): ").strip()
    
    collector = HuaweiNewsCollector()
    
    if choice == "1":
        # 立即执行一次
        collector.run_daily_task()
    else:
        # 定时执行
        try:
            schedule_daily_task()
        except KeyboardInterrupt:
            print("\n程序已停止")