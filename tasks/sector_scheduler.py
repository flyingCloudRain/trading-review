#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
板块数据定时任务调度器
"""
import logging
from datetime import datetime, time, date, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.db import SessionLocal
from services.sector_history_service import SectorHistoryService
from services.zt_pool_history_service import ZtPoolHistoryService
from services.zbgc_pool_history_service import ZbgcPoolHistoryService
from services.dtgc_pool_history_service import DtgcPoolHistoryService
from services.index_history_service import IndexHistoryService
from utils.excel_export import append_sectors_to_excel
from utils.time_utils import UTC8, get_utc8_date
import akshare as ak

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SectorScheduler:
    """板块数据定时任务调度器"""
    
    def __init__(self):
        # 使用UTC+8时区（北京时间）
        self.scheduler = BackgroundScheduler(timezone=UTC8)
        # 使用进程锁，防止多个实例同时运行
        self.scheduler.add_jobstore('memory', alias='default')
        self._setup_jobs()
    
    def _setup_jobs(self):
        """设置定时任务"""
        # 每日15:10执行（北京时间）- 保存所有数据（收盘后最终数据）
        self.scheduler.add_job(
            func=self.save_daily_data,
            trigger=CronTrigger(hour=15, minute=10, timezone=UTC8),
            id='save_daily_data',
            name='每日15:10保存板块和股票池数据',
            replace_existing=True
        )
        
        # 每日15:10执行获取即时资金流数据（概念板块）
        self.scheduler.add_job(
            func=self.save_realtime_fund_flow,
            trigger=CronTrigger(hour=15, minute=10, timezone=UTC8),
            id='save_realtime_fund_flow_1510',
            name='每日15:10获取即时资金流数据',
            replace_existing=True
        )
        
        logger.info("定时任务已设置：")
        logger.info("  - 每日15:10（北京时间）执行数据保存（板块、涨停、炸板、跌停、指数）")
        logger.info("  - 每日15:10（北京时间）获取即时资金流数据（概念板块）")
    
    def _is_trading_day(self, target_date: date) -> bool:
        """检查是否为交易日"""
        try:
            # 使用 akshare 获取交易日历
            trade_dates = ak.tool_trade_date_hist_sina()
            if trade_dates is not None and not trade_dates.empty:
                # 将目标日期转换为字符串格式 YYYYMMDD
                date_str = target_date.strftime('%Y%m%d')
                
                # 交易日历返回的日期格式可能是 'YYYY-MM-DD' 字符串
                # 需要先转换为日期对象，再格式化为 YYYYMMDD 进行比较
                import pandas as pd
                trade_dates['date_str'] = pd.to_datetime(trade_dates['trade_date']).dt.strftime('%Y%m%d')
                trade_date_list = trade_dates['date_str'].tolist()
                
                is_trading = date_str in trade_date_list
                logger.debug(f"检查日期 {target_date} ({date_str}) 是否为交易日: {is_trading}")
                return is_trading
            else:
                logger.warning("无法获取交易日历数据，默认认为是交易日")
                return True  # 如果无法获取交易日历，默认认为是交易日
        except Exception as e:
            logger.warning(f"无法判断交易日，默认执行: {str(e)}")
            return True  # 如果出错，默认执行
    
    def save_daily_data(self):
        """保存每日数据（板块、涨停、炸板、跌停、指数）"""
        try:
            logger.info("开始执行每日数据保存任务...")
            
            # 检查是否为交易日
            today = get_utc8_date()
            if not self._is_trading_day(today):
                logger.info(f"今日 ({today}) 不是交易日，跳过数据保存")
                return
            
            # 获取数据库会话
            db = SessionLocal()
            try:
                # 1. 保存行业板块数据（明确使用今天的日期）
                try:
                    saved_count = SectorHistoryService.save_today_sectors(db, sector_type='industry', target_date=today)
                    logger.info(f"✅ 成功保存 {saved_count} 条行业板块数据到数据库 ({today})")
                    
                    # 追加到Excel文件
                    excel_file = append_sectors_to_excel()
                    logger.info(f"✅ 成功追加行业板块数据到Excel文件: {excel_file}")
                except Exception as e:
                    logger.error(f"❌ 保存行业板块数据失败: {str(e)}", exc_info=True)
                
                # 1.1 保存概念板块数据（明确使用今天的日期）
                try:
                    concept_count = SectorHistoryService.save_today_sectors(db, sector_type='concept', target_date=today)
                    logger.info(f"✅ 成功保存 {concept_count} 条概念板块数据到数据库 ({today})")
                except Exception as e:
                    logger.error(f"❌ 保存概念板块数据失败: {str(e)}", exc_info=True)
                
                # 2. 保存涨停股票池数据（明确使用今天的日期）
                try:
                    zt_count = ZtPoolHistoryService.save_today_zt_pool(db, target_date=today)
                    logger.info(f"✅ 成功保存 {zt_count} 条涨停股票数据到数据库 ({today})")
                except Exception as e:
                    logger.error(f"❌ 保存涨停股票数据失败: {str(e)}", exc_info=True)
                
                # 3. 保存炸板股票池数据（明确使用今天的日期）
                try:
                    zbgc_count = ZbgcPoolHistoryService.save_today_zbgc_pool(db, target_date=today)
                    logger.info(f"✅ 成功保存 {zbgc_count} 条炸板股票数据到数据库 ({today})")
                except Exception as e:
                    logger.error(f"❌ 保存炸板股票数据失败: {str(e)}", exc_info=True)
                
                # 4. 保存跌停股票池数据（明确使用今天的日期）
                try:
                    dtgc_count = DtgcPoolHistoryService.save_today_dtgc_pool(db, target_date=today)
                    logger.info(f"✅ 成功保存 {dtgc_count} 条跌停股票数据到数据库 ({today})")
                except Exception as e:
                    logger.error(f"❌ 保存跌停股票数据失败: {str(e)}", exc_info=True)
                
                # 5. 保存指数数据（明确使用今天的日期）
                try:
                    index_count = IndexHistoryService.save_today_indices(db, target_date=today)
                    logger.info(f"✅ 成功保存 {index_count} 条指数数据到数据库 ({today})")
                except Exception as e:
                    logger.error(f"❌ 保存指数数据失败: {str(e)}", exc_info=True)
                
                logger.info(f"每日数据保存任务完成 ({today})")
                
            except Exception as e:
                logger.error(f"数据库操作失败: {str(e)}", exc_info=True)
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"定时任务执行失败: {str(e)}", exc_info=True)
    
    def save_realtime_fund_flow(self):
        """保存即时资金流数据（概念板块）- 每日15:10执行"""
        try:
            logger.info("开始执行即时资金流数据保存任务...")
            
            # 检查是否为交易日
            today = get_utc8_date()
            if not self._is_trading_day(today):
                logger.info(f"今日 ({today}) 不是交易日，跳过即时资金流数据保存")
                return
            
            # 获取数据库会话
            db = SessionLocal()
            try:
                # 保存概念板块即时资金流数据（明确使用今天的日期）
                try:
                    concept_count = SectorHistoryService.save_today_sectors(db, sector_type='concept', target_date=today)
                    logger.info(f"✅ 成功保存 {concept_count} 条概念板块即时资金流数据到数据库 ({today})")
                except Exception as e:
                    logger.error(f"❌ 保存概念板块即时资金流数据失败: {str(e)}", exc_info=True)
                
                logger.info("即时资金流数据保存任务完成")
                
            except Exception as e:
                logger.error(f"数据库操作失败: {str(e)}", exc_info=True)
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"即时资金流定时任务执行失败: {str(e)}", exc_info=True)
    
    def start(self):
        """启动调度器"""
        self.scheduler.start()
        logger.info("板块数据定时任务调度器已启动")
    
    def shutdown(self):
        """关闭调度器"""
        self.scheduler.shutdown()
        logger.info("板块数据定时任务调度器已关闭")

# 全局调度器实例
_scheduler = None

def get_scheduler():
    """获取调度器实例（单例模式）"""
    global _scheduler
    if _scheduler is None:
        _scheduler = SectorScheduler()
    return _scheduler

