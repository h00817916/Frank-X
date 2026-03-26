"""配置文件"""
import os
from pathlib import Path

# 基础路径
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# 创建必要的目录
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# 新闻源配置
class NewsSourceConfig:
    """新闻源配置"""
    # 今日头条配置
    TOUTIAO_URL = "https://www.toutiao.com/search/"
    TOUTIAO_KEYWORD = "华为"
    TOUTIAO_PARAMS = {
        'offset': 0,
        'format': 'json',
        'autoload': 'true',
        'count': 20,
        'cur_tab': 1,
        'from': 'search_tab'
    }
    
    # 百度新闻配置
    BAIDU_URL = "https://news.baidu.com/ns"
    BAIDU_PARAMS = {
        'word': '华为',
        'cl': 1,
        'tn': 'news',
        'rn': 20
    }
    
    # 请求配置
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive'
    }
    
    TIMEOUT = 10
    RETRY_TIMES = 3
    RETRY_DELAY = 1

# 情感分析配置
class SentimentConfig:
    """情感分析配置"""
    # 正面词库
    POSITIVE_WORDS = [
        '突破', '领先', '创新', '成功', '增长', '优秀', '第一', '超越', 
        '获奖', '好评', '卓越', '辉煌', '强大', '崛起', '新高度', '里程碑',
        '里程碑式', '重大突破', '关键技术', '自主研发'
    ]
    
    # 负面词库
    NEGATIVE_WORDS = [
        '问题', '困难', '挑战', '下滑', '亏损', '竞争', '压力', '限制', 
        '制裁', '危机', '困境', '受阻', '受阻', '质疑', '担忧', '挑战'
    ]
    
    # 权重配置
    POSITIVE_WEIGHT = 1.0
    NEGATIVE_WEIGHT = 1.2  # 负面词权重更高

# 调度配置
class SchedulerConfig:
    """调度配置"""
    DAILY_HOUR = 9
    DAILY_MINUTE = 0
    RETRY_INTERVAL = 3600  # 重试间隔（秒）

# 文件配置
class FileConfig:
    """文件配置"""
    SUMMARY_PREFIX = "summary"
    RAW_DATA_PREFIX = "raw_data"
    FILE_ENCODING = "utf-8"