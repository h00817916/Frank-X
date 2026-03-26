"""文件存储模块"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import logging
from config.settings import DATA_DIR, FileConfig

logger = logging.getLogger(__name__)


class DataStorage:
    """数据存储"""
    
    def __init__(self):
        """初始化存储"""
        self.base_dir = DATA_DIR
        self.encoding = FileConfig.FILE_ENCODING
    
    def save_summary(self, summary: str) -> Path:
        """保存总结文件"""
        try:
            # 创建每日文件夹
            today = datetime.now().strftime('%Y%m%d')
            folder = self.base_dir / f"huawei_news_{today}"
            folder.mkdir(parents=True, exist_ok=True)
            
            # 保存总结
            filename = folder / f"{FileConfig.SUMMARY_PREFIX}_{today}.txt"
            
            with open(filename, 'w', encoding=self.encoding) as f:
                f.write(summary)
            
            logger.info(f"总结已保存到: {filename}")
            return filename
            
        except IOError as e:
            logger.error(f"保存总结文件失败: {e}")
            raise
    
    def save_raw_data(self, news_list: List[Dict]) -> Path:
        """保存原始数据"""
        try:
            today = datetime.now().strftime('%Y%m%d')
            folder = self.base_dir / f"huawei_news_{today}"
            folder.mkdir(parents=True, exist_ok=True)
            
            filename = folder / f"{FileConfig.RAW_DATA_PREFIX}_{today}.json"
            
            with open(filename, 'w', encoding=self.encoding) as f:
                json.dump(news_list, f, ensure_ascii=False, indent=2)
            
            logger.info(f"原始数据已保存到: {filename}")
            return filename
            
        except IOError as e:
            logger.error(f"保存原始数据失败: {e}")
            raise
    
    def load_historical_data(self, date: str) -> List[Dict]:
        """加载历史数据"""
        try:
            folder = self.base_dir / f"huawei_news_{date}"
            filename = folder / f"{FileConfig.RAW_DATA_PREFIX}_{date}.json"
            
            if not filename.exists():
                logger.warning(f"历史数据不存在: {filename}")
                return []
            
            with open(filename, 'r', encoding=self.encoding) as f:
                data = json.load(f)
            
            logger.info(f"成功加载历史数据: {filename}")
            return data
            
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"加载历史数据失败: {e}")
            return []