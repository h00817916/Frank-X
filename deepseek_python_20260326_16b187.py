"""任务调度器模块"""
import time
import signal
import sys
from datetime import datetime, timedelta
from typing import Callable
import logging
from config.settings import SchedulerConfig

logger = logging.getLogger(__name__)


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self, task_func: Callable):
        """初始化调度器"""
        self.task_func = task_func
        self.config = SchedulerConfig()
        self.running = True
        
        # 注册信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        logger.info("收到终止信号，正在停止调度器...")
        self.running = False
    
    def run_once(self):
        """立即执行一次任务"""
        logger.info("开始执行任务...")
        try:
            self.task_func()
            logger.info("任务执行完成")
        except Exception as e:
            logger.error(f"任务执行失败: {e}", exc_info=True)
    
    def run_daily(self):
        """每天定时执行任务"""
        logger.info("启动每日定时任务调度器")
        
        while self.running:
            try:
                # 计算下次执行时间
                now = datetime.now()
                next_run = now.replace(
                    hour=self.config.DAILY_HOUR,
                    minute=self.config.DAILY_MINUTE,
                    second=0,
                    microsecond=0
                )
                
                if now >= next_run:
                    next_run += timedelta(days=1)
                
                # 计算等待时间
                wait_seconds = (next_run - now).total_seconds()
                
                logger.info(f"下次执行时间: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"等待 {wait_seconds/3600:.1f} 小时")
                
                # 等待到下次执行时间，但可以响应中断
                while self.running and wait_seconds > 0:
                    sleep_time = min(wait_seconds, 60)  # 每分钟检查一次
                    time.sleep(sleep_time)
                    wait_seconds -= sleep_time
                
                if not self.running:
                    break
                
                # 执行任务
                self.run_once()
                
            except Exception as e:
                logger.error(f"调度器运行错误: {e}", exc_info=True)
                logger.info(f"等待 {self.config.RETRY_INTERVAL} 秒后重试...")
                time.sleep(self.config.RETRY_INTERVAL)
        
        logger.info("调度器已停止")