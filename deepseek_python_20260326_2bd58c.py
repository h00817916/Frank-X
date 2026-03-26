"""新闻收集器模块"""
import json
import time
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

from config.settings import NewsSourceConfig

logger = logging.getLogger(__name__)


class NewsCollector:
    """新闻收集器"""
    
    def __init__(self):
        """初始化收集器"""
        self.session = self._create_session()
        self.config = NewsSourceConfig()
        
    def _create_session(self) -> requests.Session:
        """创建带重试机制的会话"""
        session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=self.config.RETRY_TIMES,
            backoff_factor=self.config.RETRY_DELAY,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def collect_from_toutiao(self) -> List[Dict]:
        """从今日头条抓取新闻"""
        try:
            params = {
                'keyword': self.config.TOUTIAO_KEYWORD,
                **self.config.TOUTIAO_PARAMS
            }
            
            response = self.session.get(
                self.config.TOUTIAO_URL,
                headers=self.config.HEADERS,
                params=params,
                timeout=self.config.TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            news_items = self._parse_toutiao_response(data)
            
            if news_items:
                logger.info(f"从今日头条成功抓取 {len(news_items)} 条新闻")
                return news_items
            
            logger.warning("今日头条未抓取到新闻，尝试备用方案")
            return []
            
        except requests.exceptions.RequestException as e:
            logger.error(f"今日头条抓取失败: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            return []
    
    def _parse_toutiao_response(self, data: Dict) -> List[Dict]:
        """解析今日头条响应数据"""
        news_items = []
        
        if 'data' not in data or not isinstance(data['data'], list):
            logger.warning("今日头条响应数据格式异常")
            return news_items
        
        for item in data['data']:
            if not isinstance(item, dict):
                continue
                
            title = item.get('title', '')
            if not title or self.config.TOUTIAO_KEYWORD not in title:
                continue
            
            news = {
                'title': title.strip(),
                'source': item.get('source', '今日头条'),
                'time': item.get('datetime', ''),
                'url': item.get('article_url', ''),
                'abstract': item.get('abstract', '').strip(),
                'comment_count': item.get('comment_count', 0),
                'source_type': 'toutiao'
            }
            news_items.append(news)
        
        return news_items
    
    def collect_from_baidu(self) -> List[Dict]:
        """从百度新闻抓取（备用方案）"""
        try:
            response = self.session.get(
                self.config.BAIDU_URL,
                headers=self.config.HEADERS,
                params=self.config.BAIDU_PARAMS,
                timeout=self.config.TIMEOUT
            )
            response.encoding = 'utf-8'
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = self._parse_baidu_response(soup)
            
            logger.info(f"从百度新闻成功抓取 {len(news_items)} 条新闻")
            return news_items
            
        except requests.exceptions.RequestException as e:
            logger.error(f"百度新闻抓取失败: {e}")
            return []
        except Exception as e:
            logger.error(f"百度新闻解析失败: {e}")
            return []
    
    def _parse_baidu_response(self, soup: BeautifulSoup) -> List[Dict]:
        """解析百度新闻响应"""
        news_items = []
        results = soup.find_all('div', class_='result')
        
        for result in results:
            try:
                title_tag = result.find('h3')
                if not title_tag:
                    continue
                
                title = title_tag.get_text(strip=True)
                if self.config.TOUTIAO_KEYWORD not in title:
                    continue
                
                # 获取链接
                link_tag = title_tag.find('a')
                url = link_tag.get('href', '') if link_tag else ''
                
                # 获取来源和时间
                author_tag = result.find('div', class_='c-author')
                author_text = author_tag.get_text(strip=True) if author_tag else ''
                
                # 获取摘要
                summary_tag = result.find('div', class_='c-summary')
                abstract = summary_tag.get_text(strip=True) if summary_tag else ''
                
                news = {
                    'title': title,
                    'source': author_text.split()[0] if author_text else '百度新闻',
                    'time': author_text.split()[-1] if len(author_text.split()) > 1 else '',
                    'url': url,
                    'abstract': abstract,
                    'comment_count': 0,
                    'source_type': 'baidu'
                }
                news_items.append(news)
                
            except Exception as e:
                logger.error(f"解析单个新闻条目失败: {e}")
                continue
        
        return news_items
    
    def collect_all(self) -> List[Dict]:
        """收集所有来源的新闻"""
        all_news = []
        
        # 主来源
        toutiao_news = self.collect_from_toutiao()
        all_news.extend(toutiao_news)
        
        # 如果没有主来源数据，使用备用方案
        if not toutiao_news:
            logger.info("主来源无数据，使用备用方案")
            baidu_news = self.collect_from_baidu()
            all_news.extend(baidu_news)
        
        # 去重（基于标题）
        unique_news = self._deduplicate(all_news)
        logger.info(f"去重后共 {len(unique_news)} 条新闻")
        
        return unique_news
    
    def _deduplicate(self, news_list: List[Dict]) -> List[Dict]:
        """新闻去重"""
        seen_titles = set()
        unique_news = []
        
        for news in news_list:
            title = news['title']
            if title not in seen_titles:
                seen_titles.add(title)
                unique_news.append(news)
        
        return unique_news