"""主程序入口"""
import logging
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.collector import NewsCollector
from src.analyzer import TextAnalyzer
from src.summarizer import NewsSummarizer
from src.storage import DataStorage
from src.scheduler import TaskScheduler
from config.settings import LOGS_DIR

def setup_logging():
    """配置日志系统"""
    log_file = LOGS_DIR / f"huawei_news_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def daily_task():
    """每日任务"""
    logger = logging.getLogger(__name__)
    logger.info("="*50)
    logger.info("开始执行每日华为新闻抓取任务")
    
    try:
        # 初始化组件
        collector = NewsCollector()
        summarizer = NewsSummarizer()
        storage = DataStorage()
        
        # 抓取新闻
        logger.info("正在抓取华为相关新闻...")
        news_list = collector.collect_all()
        logger.info(f"成功抓取 {len(news_list)} 条新闻")
        
        if news_list:
            # 保存原始数据
            storage.save_raw_data(news_list)
            
            # 生成总结
            logger.info("正在生成新闻总结...")
            summary = summarizer.generate_summary(news_list)
            
            # 保存总结
            filename = storage.save_summary(summary)
            
            # 打印总结到控制台
            print("\n" + summary)
            logger.info(f"任务完成，总结已保存到: {filename}")
        else:
            logger.warning("未抓取到任何新闻，请检查网络或新闻源")
            
    except Exception as e:
        logger.error(f"任务执行失败: {e}", exc_info=True)
        raise

def main():
    """主函数"""
    # 配置日志
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("="*60)
    print("华为新闻自动抓取与总结系统 v2.0")
    print("="*60)
    
    # 选择运行模式
    print("\n请选择运行模式:")
    print("1. 立即执行一次")
    print("2. 每天定时执行（默认上午9点）")
    
    choice = input("\n请输入选择 (1/2): ").strip()
    
    # 创建调度器
    scheduler = TaskScheduler(daily_task)
    
    if choice == "1":
        logger.info("选择立即执行模式")
        scheduler.run_once()
    else:
        logger.info("选择定时执行模式")
        try:
            scheduler.run_daily()
        except KeyboardInterrupt:
            logger.info("\n程序已停止")

if __name__ == "__main__":
    main()