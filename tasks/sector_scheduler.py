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
from services.scheduler_execution_service import SchedulerExecutionService
from utils.excel_export import append_sectors_to_excel
from utils.time_utils import UTC8, get_utc8_date, get_utc8_now, get_data_date
import akshare as ak
import traceback

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
        
        # 每日15:10执行获取所有股票的资金流数据（从 stock_fund_flow_individual 接口）
        self.scheduler.add_job(
            func=self.save_all_stocks_fund_flow,
            trigger=CronTrigger(hour=15, minute=10, timezone=UTC8),
            id='save_all_stocks_fund_flow_1510',
            name='每日15:10获取所有股票资金流数据',
            replace_existing=True
        )
        
        logger.info("定时任务已设置：")
        logger.info("  - 每日15:10（北京时间）执行数据保存（板块、涨停、炸板、跌停、指数）")
        logger.info("  - 每日15:10（北京时间）获取即时资金流数据（概念板块）")
        logger.info("  - 每日15:10（北京时间）获取所有股票资金流数据（stock_fund_flow_individual接口）")
    
    def _is_trading_day(self, target_date: date) -> bool:
        """
        检查是否为交易日（基于北京时间UTC+8）
        
        注意：target_date 应该是基于北京时间的日期对象
        所有交易日判断均基于北京时间（UTC+8），确保交易日判断的准确性
        
        :param target_date: 要检查的日期（基于北京时间）
        :return: True表示是交易日，False表示不是交易日
        """
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
                logger.debug(f"检查日期 {target_date} ({date_str}) 是否为交易日（基于北京时间）: {is_trading}")
                return is_trading
            else:
                logger.warning("无法获取交易日历数据，默认认为是交易日")
                return True  # 如果无法获取交易日历，默认认为是交易日
        except Exception as e:
            logger.warning(f"无法判断交易日，默认执行: {str(e)}")
            return True  # 如果出错，默认执行
    
    def save_daily_data(self):
        """
        保存每日数据到 Supabase 数据库（板块、涨停、炸板、跌停、指数）
        
        逻辑说明：
        1. 获取实时数据（AKShare API 只能获取实时数据）
        2. 保存日期使用当日交易日（如果今天是交易日用今天，否则用上一个交易日）
        3. 如果今天不是交易日，跳过保存
        """
        job_id = 'save_daily_data'
        job_name = '每日15:10保存板块和股票池数据'
        execution_start_time = get_utc8_now()
        today = get_utc8_date()  # 当前日期
        is_trading = self._is_trading_day(today)
        
        # 获取应该保存的日期（当日交易日）
        # 如果今天是交易日，使用今天；如果今天不是交易日，使用上一个交易日
        data_date = get_data_date()  # 当日交易日
        
        # 初始化统计数据
        stats = {
            'industry_sectors_count': 0,
            'concept_sectors_count': 0,
            'zt_pool_count': 0,
            'zbgc_pool_count': 0,
            'dtgc_pool_count': 0,
            'index_count': 0,
        }
        
        error_message = None
        error_traceback = None
        status = 'success'
        
        try:
            logger.info("=" * 60)
            logger.info("开始执行每日数据保存任务（保存到 Supabase 数据库）...")
            
            # 检查是否为交易日（基于北京时间判断）
            if not is_trading:
                logger.info(f"今日 ({today}，北京时间) 不是交易日，跳过数据保存")
                logger.info(f"上一个交易日（北京时间）: {data_date}")
                status = 'skipped'
                # 记录跳过执行
                db = SessionLocal()
                try:
                    SchedulerExecutionService.create_execution(
                        db=db,
                        job_id=job_id,
                        job_name=job_name,
                        execution_date=today,
                        execution_time=execution_start_time,
                        status=status,
                        duration_seconds=(get_utc8_now() - execution_start_time).total_seconds(),
                        is_trading_day=is_trading,
                        notes=f"非交易日，跳过执行。上一个交易日: {data_date}"
                    )
                finally:
                    db.close()
                return
            
            # 记录保存的日期信息（所有日期均基于北京时间UTC+8）
            logger.info(f"📅 当前日期（北京时间）: {today}, 保存日期（当日交易日，北京时间）: {data_date}")
            if today != data_date:
                logger.warning(f"⚠️  注意: 当前日期 ({today}) 与保存日期 ({data_date}) 不同，这是正常的（非交易日情况）")
            
            # 验证数据库连接（确保使用 Supabase）
            try:
                from database.db_supabase import engine
                from sqlalchemy import text
                # 测试数据库连接
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                logger.info("✅ Supabase 数据库连接正常")
            except Exception as e:
                logger.error(f"❌ Supabase 数据库连接失败: {str(e)}")
                raise
            
            # 获取数据库会话（使用 Supabase）
            db = SessionLocal()
            try:
                logger.info(f"📊 开始保存 {data_date}（当日交易日，北京时间）的数据到 Supabase 数据库...")
                logger.info(f"💡 说明: 获取的是实时数据，保存日期为当日交易日 ({data_date}，北京时间)")
                
                # 1. 保存行业板块数据到 Supabase（使用当日交易日）
                try:
                    saved_count = SectorHistoryService.save_today_sectors(db, sector_type='industry', target_date=data_date)
                    stats['industry_sectors_count'] = saved_count
                    logger.info(f"✅ 成功保存 {saved_count} 条行业板块数据到 Supabase 数据库 (日期: {data_date})")
                    
                    # 追加到Excel文件
                    excel_file = append_sectors_to_excel()
                    logger.info(f"✅ 成功追加行业板块数据到Excel文件: {excel_file}")
                except Exception as e:
                    logger.error(f"❌ 保存行业板块数据到 Supabase 失败: {str(e)}", exc_info=True)
                    if status == 'success':
                        status = 'failed'
                        error_message = f"保存行业板块数据失败: {str(e)}"
                
                # 1.1 保存概念板块数据到 Supabase（使用当日交易日）
                try:
                    concept_count = SectorHistoryService.save_today_sectors(db, sector_type='concept', target_date=data_date)
                    stats['concept_sectors_count'] = concept_count
                    logger.info(f"✅ 成功保存 {concept_count} 条概念板块数据到 Supabase 数据库 (日期: {data_date})")
                except Exception as e:
                    logger.error(f"❌ 保存概念板块数据到 Supabase 失败: {str(e)}", exc_info=True)
                    if status == 'success':
                        status = 'failed'
                        error_message = f"保存概念板块数据失败: {str(e)}"
                
                # 2. 保存涨停股票池数据到 Supabase（使用当日交易日）
                try:
                    zt_count = ZtPoolHistoryService.save_today_zt_pool(db, target_date=data_date)
                    stats['zt_pool_count'] = zt_count
                    logger.info(f"✅ 成功保存 {zt_count} 条涨停股票数据到 Supabase 数据库 (日期: {data_date})")
                except Exception as e:
                    logger.error(f"❌ 保存涨停股票数据到 Supabase 失败: {str(e)}", exc_info=True)
                    if status == 'success':
                        status = 'failed'
                        error_message = f"保存涨停股票数据失败: {str(e)}"
                
                # 3. 保存炸板股票池数据到 Supabase（使用当日交易日）
                try:
                    zbgc_count = ZbgcPoolHistoryService.save_today_zbgc_pool(db, target_date=data_date)
                    stats['zbgc_pool_count'] = zbgc_count
                    logger.info(f"✅ 成功保存 {zbgc_count} 条炸板股票数据到 Supabase 数据库 (日期: {data_date})")
                except Exception as e:
                    logger.error(f"❌ 保存炸板股票数据到 Supabase 失败: {str(e)}", exc_info=True)
                    if status == 'success':
                        status = 'failed'
                        error_message = f"保存炸板股票数据失败: {str(e)}"
                
                # 4. 保存跌停股票池数据到 Supabase（使用当日交易日）
                try:
                    dtgc_count = DtgcPoolHistoryService.save_today_dtgc_pool(db, target_date=data_date)
                    stats['dtgc_pool_count'] = dtgc_count
                    logger.info(f"✅ 成功保存 {dtgc_count} 条跌停股票数据到 Supabase 数据库 (日期: {data_date})")
                except Exception as e:
                    logger.error(f"❌ 保存跌停股票数据到 Supabase 失败: {str(e)}", exc_info=True)
                    if status == 'success':
                        status = 'failed'
                        error_message = f"保存跌停股票数据失败: {str(e)}"
                
                # 5. 保存指数数据到 Supabase（使用当日交易日）
                try:
                    index_count = IndexHistoryService.save_today_indices(db, target_date=data_date)
                    stats['index_count'] = index_count
                    logger.info(f"✅ 成功保存 {index_count} 条指数数据到 Supabase 数据库 (日期: {data_date})")
                except Exception as e:
                    logger.error(f"❌ 保存指数数据到 Supabase 失败: {str(e)}", exc_info=True)
                    if status == 'success':
                        status = 'failed'
                        error_message = f"保存指数数据失败: {str(e)}"
                
                logger.info("=" * 60)
                logger.info(f"✅ 每日数据保存任务完成，所有数据已保存到 Supabase 数据库")
                logger.info(f"📅 保存日期（当日交易日，北京时间）: {data_date}")
                logger.info(f"📅 执行日期（北京时间）: {today}")
                logger.info("=" * 60)
                
            except Exception as e:
                logger.error(f"数据库操作失败: {str(e)}", exc_info=True)
                status = 'failed'
                error_message = str(e)
                error_traceback = traceback.format_exc()
            finally:
                # 记录执行情况
                execution_end_time = get_utc8_now()
                duration = (execution_end_time - execution_start_time).total_seconds()
                
                try:
                    SchedulerExecutionService.create_execution(
                        db=db,
                        job_id=job_id,
                        job_name=job_name,
                        execution_date=today,
                        execution_time=execution_start_time,
                        status=status,
                        duration_seconds=duration,
                        industry_sectors_count=stats['industry_sectors_count'],
                        concept_sectors_count=stats['concept_sectors_count'],
                        zt_pool_count=stats['zt_pool_count'],
                        zbgc_pool_count=stats['zbgc_pool_count'],
                        dtgc_pool_count=stats['dtgc_pool_count'],
                        index_count=stats['index_count'],
                        error_message=error_message,
                        error_traceback=error_traceback,
                        is_trading_day=is_trading,
                        notes=f"总耗时: {duration:.2f}秒 | 保存日期（当日交易日，北京时间）: {data_date} | 执行日期（北京时间）: {today}"
                    )
                    logger.info(f"✅ 执行记录已保存到数据库")
                except Exception as e:
                    logger.error(f"❌ 保存执行记录失败: {str(e)}", exc_info=True)
                finally:
                    db.close()
                
        except Exception as e:
            logger.error(f"定时任务执行失败: {str(e)}", exc_info=True)
            # 记录失败执行
            execution_end_time = get_utc8_now()
            duration = (execution_end_time - execution_start_time).total_seconds()
            db = SessionLocal()
            try:
                SchedulerExecutionService.create_execution(
                    db=db,
                    job_id=job_id,
                    job_name=job_name,
                    execution_date=today,
                    execution_time=execution_start_time,
                    status='failed',
                    duration_seconds=duration,
                    error_message=str(e),
                    error_traceback=traceback.format_exc(),
                    is_trading_day=is_trading,
                    notes="任务执行异常"
                )
            finally:
                db.close()
    
    def save_realtime_fund_flow(self):
        """
        保存即时资金流数据到 Supabase 数据库（概念板块）- 每日15:10执行
        
        逻辑说明：
        1. 获取实时数据（AKShare API 只能获取实时数据）
        2. 保存日期使用当日交易日（如果今天是交易日用今天，否则用上一个交易日）
        3. 如果今天不是交易日，跳过保存
        """
        job_id = 'save_realtime_fund_flow_1510'
        job_name = '每日15:10获取即时资金流数据'
        execution_start_time = get_utc8_now()
        today = get_utc8_date()  # 当前日期（北京时间UTC+8）
        is_trading = self._is_trading_day(today)  # 判断今天是否为交易日（基于北京时间）
        
        # 获取应该保存的日期（当日交易日，基于北京时间）
        # 如果今天是交易日（按北京时间判断），使用今天；如果今天不是交易日，使用上一个交易日
        data_date = get_data_date()  # 当日交易日（基于北京时间）
        
        # 初始化统计数据
        concept_count = 0
        error_message = None
        error_traceback = None
        status = 'success'
        
        try:
            logger.info("=" * 60)
            logger.info("开始执行即时资金流数据保存任务（保存到 Supabase 数据库）...")
            
            # 检查是否为交易日（基于北京时间判断）
            if not is_trading:
                logger.info(f"今日 ({today}，北京时间) 不是交易日，跳过即时资金流数据保存")
                logger.info(f"上一个交易日（北京时间）: {data_date}")
                status = 'skipped'
                # 记录跳过执行
                db = SessionLocal()
                try:
                    SchedulerExecutionService.create_execution(
                        db=db,
                        job_id=job_id,
                        job_name=job_name,
                        execution_date=today,
                        execution_time=execution_start_time,
                        status=status,
                        duration_seconds=(get_utc8_now() - execution_start_time).total_seconds(),
                        is_trading_day=is_trading,
                        notes=f"非交易日，跳过执行。上一个交易日（北京时间）: {data_date}"
                    )
                finally:
                    db.close()
                return
            
            # 记录保存的日期信息（所有日期均基于北京时间UTC+8）
            logger.info(f"📅 当前日期（北京时间）: {today}, 保存日期（当日交易日，北京时间）: {data_date}")
            if today != data_date:
                logger.warning(f"⚠️  注意: 当前日期 ({today}) 与保存日期 ({data_date}) 不同，这是正常的（非交易日情况）")
            
            # 验证数据库连接（确保使用 Supabase）
            try:
                from database.db_supabase import engine
                from sqlalchemy import text
                # 测试数据库连接
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                logger.info("✅ Supabase 数据库连接正常")
            except Exception as e:
                logger.error(f"❌ Supabase 数据库连接失败: {str(e)}")
                raise
            
            # 获取数据库会话（使用 Supabase）
            db = SessionLocal()
            try:
                logger.info(f"📊 开始保存 {data_date}（当日交易日，北京时间）的概念板块即时资金流数据到 Supabase 数据库...")
                logger.info(f"💡 说明: 获取的是实时数据，保存日期为当日交易日 ({data_date}，北京时间)")
                
                # 保存概念板块即时资金流数据到 Supabase（使用当日交易日）
                try:
                    concept_count = SectorHistoryService.save_today_sectors(db, sector_type='concept', target_date=data_date)
                    logger.info(f"✅ 成功保存 {concept_count} 条概念板块即时资金流数据到 Supabase 数据库 (日期: {data_date})")
                except Exception as e:
                    logger.error(f"❌ 保存概念板块即时资金流数据到 Supabase 失败: {str(e)}", exc_info=True)
                
                logger.info("=" * 60)
                logger.info("✅ 即时资金流数据保存任务完成，数据已保存到 Supabase 数据库")
                logger.info(f"📅 保存日期（当日交易日，北京时间）: {data_date}")
                logger.info(f"📅 执行日期（北京时间）: {today}")
                logger.info("=" * 60)
                
            except Exception as e:
                logger.error(f"数据库操作失败: {str(e)}", exc_info=True)
                status = 'failed'
                error_message = str(e)
                error_traceback = traceback.format_exc()
            finally:
                # 记录执行情况
                execution_end_time = get_utc8_now()
                duration = (execution_end_time - execution_start_time).total_seconds()
                
                try:
                    SchedulerExecutionService.create_execution(
                        db=db,
                        job_id=job_id,
                        job_name=job_name,
                        execution_date=today,
                        execution_time=execution_start_time,
                        status=status,
                        duration_seconds=duration,
                        concept_sectors_count=concept_count,
                        error_message=error_message,
                        error_traceback=error_traceback,
                        is_trading_day=is_trading,
                        notes=f"总耗时: {duration:.2f}秒 | 保存日期（当日交易日，北京时间）: {data_date} | 执行日期（北京时间）: {today}"
                    )
                    logger.info(f"✅ 执行记录已保存到数据库")
                except Exception as e:
                    logger.error(f"❌ 保存执行记录失败: {str(e)}", exc_info=True)
                finally:
                    db.close()
                
        except Exception as e:
            logger.error(f"即时资金流定时任务执行失败: {str(e)}", exc_info=True)
            # 记录失败执行
            execution_end_time = get_utc8_now()
            duration = (execution_end_time - execution_start_time).total_seconds()
            db = SessionLocal()
            try:
                SchedulerExecutionService.create_execution(
                    db=db,
                    job_id=job_id,
                    job_name=job_name,
                    execution_date=today,
                    execution_time=execution_start_time,
                    status='failed',
                    duration_seconds=duration,
                    error_message=str(e),
                    error_traceback=traceback.format_exc(),
                    is_trading_day=is_trading,
                    notes="任务执行异常"
                )
            finally:
                db.close()
    
    def save_stock_fund_flow(self):
        """
        保存个股资金流数据（即时数据）- 每日15:10执行
        使用 stock_fund_flow_individual 接口
        
        逻辑说明：
        1. 获取关注股票列表（从配置文件或交易日志）
        2. 对每个股票调用 stock_fund_flow_individual 接口获取即时资金流数据
        3. 保存日期使用当日交易日
        4. 如果今天不是交易日，跳过保存
        """
        job_id = 'save_stock_fund_flow_1510'
        job_name = '每日15:10获取个股资金流数据'
        execution_start_time = get_utc8_now()
        today = get_utc8_date()
        is_trading = self._is_trading_day(today)
        data_date = get_data_date()
        
        # 初始化统计数据
        success_count = 0
        failed_count = 0
        error_message = None
        error_traceback = None
        status = 'success'
        
        try:
            logger.info("=" * 60)
            logger.info("开始执行个股资金流数据保存任务...")
            
            # 检查是否为交易日
            if not is_trading:
                logger.info(f"今日 ({today}，北京时间) 不是交易日，跳过个股资金流数据保存")
                status = 'skipped'
                db = SessionLocal()
                try:
                    SchedulerExecutionService.create_execution(
                        db=db,
                        job_id=job_id,
                        job_name=job_name,
                        execution_date=today,
                        execution_time=execution_start_time,
                        status=status,
                        duration_seconds=(get_utc8_now() - execution_start_time).total_seconds(),
                        is_trading_day=is_trading,
                        notes=f"非交易日，跳过执行"
                    )
                finally:
                    db.close()
                return
            
            # 获取要查询的股票列表
            from utils.focused_stocks import get_focused_stocks
            from services.trading_review_service import TradingReviewService
            
            # 1. 从关注股票列表获取
            focused_stocks = get_focused_stocks()
            
            # 2. 从交易日志中获取用户交易过的股票代码（去重）
            db = SessionLocal()
            try:
                all_reviews = TradingReviewService.get_all_reviews(db)
                traded_stocks = list(set([r.stock_code for r in all_reviews if r.stock_code]))
                
                # 合并关注股票和交易过的股票（去重）
                stock_codes = list(set(focused_stocks + traded_stocks))
                
                if not stock_codes:
                    logger.info("没有需要查询的股票，跳过个股资金流数据保存")
                    status = 'skipped'
                    SchedulerExecutionService.create_execution(
                        db=db,
                        job_id=job_id,
                        job_name=job_name,
                        execution_date=today,
                        execution_time=execution_start_time,
                        status=status,
                        duration_seconds=(get_utc8_now() - execution_start_time).total_seconds(),
                        is_trading_day=is_trading,
                        notes="没有需要查询的股票"
                    )
                    return
                
                logger.info(f"📊 开始保存 {len(stock_codes)} 只股票的资金流数据到 Supabase 数据库...")
                logger.info(f"📅 保存日期（当日交易日，北京时间）: {data_date}")
                
                # 导入个股资金流服务
                from services.stock_fund_flow_history_service import StockFundFlowHistoryService
                
                # 批量保存股票资金流数据
                results = StockFundFlowHistoryService.save_multiple_stocks_fund_flow(
                    db=db,
                    stock_codes=stock_codes,
                    target_date=data_date
                )
                
                # 统计结果
                success_count = sum(1 for success in results.values() if success)
                failed_count = len(results) - success_count
                
                logger.info(f"✅ 成功保存 {success_count} 只股票的资金流数据")
                if failed_count > 0:
                    logger.warning(f"⚠️  {failed_count} 只股票的资金流数据保存失败")
                    status = 'partial_success'
                
                logger.info("=" * 60)
                logger.info("✅ 个股资金流数据保存任务完成")
                logger.info(f"📅 保存日期（当日交易日，北京时间）: {data_date}")
                logger.info(f"📅 执行日期（北京时间）: {today}")
                logger.info("=" * 60)
                
            except Exception as e:
                logger.error(f"数据库操作失败: {str(e)}", exc_info=True)
                status = 'failed'
                error_message = str(e)
                error_traceback = traceback.format_exc()
            finally:
                # 记录执行情况
                execution_end_time = get_utc8_now()
                duration = (execution_end_time - execution_start_time).total_seconds()
                
                try:
                    SchedulerExecutionService.create_execution(
                        db=db,
                        job_id=job_id,
                        job_name=job_name,
                        execution_date=today,
                        execution_time=execution_start_time,
                        status=status,
                        duration_seconds=duration,
                        error_message=error_message,
                        error_traceback=error_traceback,
                        is_trading_day=is_trading,
                        notes=f"总耗时: {duration:.2f}秒 | 成功: {success_count} | 失败: {failed_count} | 保存日期（当日交易日，北京时间）: {data_date} | 执行日期（北京时间）: {today}"
                    )
                    logger.info(f"✅ 执行记录已保存到数据库")
                except Exception as e:
                    logger.error(f"❌ 保存执行记录失败: {str(e)}", exc_info=True)
                finally:
                    db.close()
                    
        except Exception as e:
            logger.error(f"个股资金流定时任务执行失败: {str(e)}", exc_info=True)
            execution_end_time = get_utc8_now()
            duration = (execution_end_time - execution_start_time).total_seconds()
            db = SessionLocal()
            try:
                SchedulerExecutionService.create_execution(
                    db=db,
                    job_id=job_id,
                    job_name=job_name,
                    execution_date=today,
                    execution_time=execution_start_time,
                    status='failed',
                    duration_seconds=duration,
                    error_message=str(e),
                    error_traceback=traceback.format_exc(),
                    is_trading_day=is_trading,
                    notes="任务执行异常"
                )
            finally:
                db.close()
    
    def save_all_stocks_fund_flow(self):
        """
        保存所有股票的资金流数据（从 stock_fund_flow_individual 接口）- 每日15:10执行
        
        逻辑说明：
        1. 调用 stock_fund_flow_individual(symbol="即时") 接口获取所有股票的即时资金流数据
        2. 批量保存所有股票数据到数据库
        3. 保存日期使用当日交易日
        4. 如果今天不是交易日，跳过保存
        """
        job_id = 'save_all_stocks_fund_flow_1510'
        job_name = '每日15:10获取所有股票资金流数据'
        execution_start_time = get_utc8_now()
        today = get_utc8_date()
        is_trading = self._is_trading_day(today)
        data_date = get_data_date()
        
        # 初始化统计数据
        success_count = 0
        failed_count = 0
        total_count = 0
        error_message = None
        error_traceback = None
        status = 'success'
        
        try:
            logger.info("=" * 60)
            logger.info("开始执行所有股票资金流数据保存任务...")
            
            # 检查是否为交易日
            if not is_trading:
                logger.info(f"今日 ({today}，北京时间) 不是交易日，跳过所有股票资金流数据保存")
                status = 'skipped'
                db = SessionLocal()
                try:
                    SchedulerExecutionService.create_execution(
                        db=db,
                        job_id=job_id,
                        job_name=job_name,
                        execution_date=today,
                        execution_time=execution_start_time,
                        status=status,
                        duration_seconds=(get_utc8_now() - execution_start_time).total_seconds(),
                        is_trading_day=is_trading,
                        notes=f"非交易日，跳过执行"
                    )
                finally:
                    db.close()
                return
            
            # 记录保存的日期信息
            logger.info(f"📅 当前日期（北京时间）: {today}, 保存日期（当日交易日，北京时间）: {data_date}")
            if today != data_date:
                logger.warning(f"⚠️  注意: 当前日期 ({today}) 与保存日期 ({data_date}) 不同，这是正常的（非交易日情况）")
            
            # 验证数据库连接
            try:
                from database.db_supabase import engine
                from sqlalchemy import text
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                logger.info("✅ Supabase 数据库连接正常")
            except Exception as e:
                logger.error(f"❌ Supabase 数据库连接失败: {str(e)}")
                raise
            
            # 获取数据库会话
            db = SessionLocal()
            try:
                logger.info(f"📊 开始从 stock_fund_flow_individual 接口获取所有股票的资金流数据...")
                logger.info(f"📅 保存日期（当日交易日，北京时间）: {data_date}")
                
                # 导入个股资金流服务
                from services.stock_fund_flow_history_service import StockFundFlowHistoryService
                
                # 批量保存所有股票资金流数据
                results = StockFundFlowHistoryService.save_all_stocks_fund_flow_from_individual(
                    db=db,
                    target_date=data_date
                )
                
                # 统计结果
                success_count = results.get('success_count', 0)
                failed_count = results.get('failed_count', 0)
                total_count = results.get('total_count', 0)
                
                if failed_count > 0:
                    status = 'partial_success'
                    logger.warning(f"⚠️  {failed_count} 只股票的资金流数据保存失败")
                
                logger.info(f"✅ 成功保存 {success_count}/{total_count} 只股票的资金流数据")
                
                logger.info("=" * 60)
                logger.info("✅ 所有股票资金流数据保存任务完成")
                logger.info(f"📅 保存日期（当日交易日，北京时间）: {data_date}")
                logger.info(f"📅 执行日期（北京时间）: {today}")
                logger.info("=" * 60)
                
            except Exception as e:
                logger.error(f"数据库操作失败: {str(e)}", exc_info=True)
                status = 'failed'
                error_message = str(e)
                error_traceback = traceback.format_exc()
            finally:
                # 记录执行情况
                execution_end_time = get_utc8_now()
                duration = (execution_end_time - execution_start_time).total_seconds()
                
                try:
                    SchedulerExecutionService.create_execution(
                        db=db,
                        job_id=job_id,
                        job_name=job_name,
                        execution_date=today,
                        execution_time=execution_start_time,
                        status=status,
                        duration_seconds=duration,
                        error_message=error_message,
                        error_traceback=error_traceback,
                        is_trading_day=is_trading,
                        notes=f"总耗时: {duration:.2f}秒 | 成功: {success_count} | 失败: {failed_count} | 总计: {total_count} | 保存日期（当日交易日，北京时间）: {data_date} | 执行日期（北京时间）: {today}"
                    )
                    logger.info(f"✅ 执行记录已保存到数据库")
                except Exception as e:
                    logger.error(f"❌ 保存执行记录失败: {str(e)}", exc_info=True)
                finally:
                    db.close()
                    
        except Exception as e:
            logger.error(f"所有股票资金流定时任务执行失败: {str(e)}", exc_info=True)
            execution_end_time = get_utc8_now()
            duration = (execution_end_time - execution_start_time).total_seconds()
            db = SessionLocal()
            try:
                SchedulerExecutionService.create_execution(
                    db=db,
                    job_id=job_id,
                    job_name=job_name,
                    execution_date=today,
                    execution_time=execution_start_time,
                    status='failed',
                    duration_seconds=duration,
                    error_message=str(e),
                    error_traceback=traceback.format_exc(),
                    is_trading_day=is_trading,
                    notes="任务执行异常"
                )
            finally:
                db.close()
    
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

