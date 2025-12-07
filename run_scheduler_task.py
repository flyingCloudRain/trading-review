#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动执行定时任务 - 获取并保存今日数据
"""
import sys
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.db import SessionLocal
from services.sector_history_service import SectorHistoryService
from services.zt_pool_history_service import ZtPoolHistoryService
from services.zbgc_pool_history_service import ZbgcPoolHistoryService
from services.dtgc_pool_history_service import DtgcPoolHistoryService
from services.index_history_service import IndexHistoryService
from utils.excel_export import append_sectors_to_excel
from utils.time_utils import get_utc8_date
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def save_daily_data(force=False):
    """保存每日数据（板块、涨停、炸板、跌停、指数）"""
    try:
        logger.info("开始执行每日数据保存任务...")
        
        # 检查是否为交易日（除非强制执行）
        if not force:
            from tasks.sector_scheduler import SectorScheduler
            scheduler = SectorScheduler()
            today = get_utc8_date()
            if not scheduler._is_trading_day(today):
                logger.info(f"今日 ({today}) 不是交易日，跳过数据保存")
                print(f"\n⚠️  今日 ({today}) 不是交易日，跳过数据保存")
                print("💡 如需强制执行，请使用 --force 参数")
                return
        
        # 获取数据库会话
        db = SessionLocal()
        try:
            results = {}
            
            # 1. 保存板块数据
            try:
                saved_count = SectorHistoryService.save_today_sectors(db)
                logger.info(f"✅ 成功保存 {saved_count} 条板块数据到数据库")
                results['sectors'] = saved_count
                
                # 追加到Excel文件
                excel_file = append_sectors_to_excel()
                logger.info(f"✅ 成功追加板块数据到Excel文件: {excel_file}")
            except Exception as e:
                logger.error(f"❌ 保存板块数据失败: {str(e)}", exc_info=True)
                results['sectors'] = f"失败: {str(e)}"
            
            # 2. 保存涨停股票池数据
            try:
                zt_count = ZtPoolHistoryService.save_today_zt_pool(db)
                logger.info(f"✅ 成功保存 {zt_count} 条涨停股票数据到数据库")
                results['zt_pool'] = zt_count
            except Exception as e:
                logger.error(f"❌ 保存涨停股票数据失败: {str(e)}", exc_info=True)
                results['zt_pool'] = f"失败: {str(e)}"
            
            # 3. 保存炸板股票池数据
            try:
                zbgc_count = ZbgcPoolHistoryService.save_today_zbgc_pool(db)
                logger.info(f"✅ 成功保存 {zbgc_count} 条炸板股票数据到数据库")
                results['zbgc_pool'] = zbgc_count
            except Exception as e:
                logger.error(f"❌ 保存炸板股票数据失败: {str(e)}", exc_info=True)
                results['zbgc_pool'] = f"失败: {str(e)}"
            
            # 4. 保存跌停股票池数据
            try:
                dtgc_count = DtgcPoolHistoryService.save_today_dtgc_pool(db)
                logger.info(f"✅ 成功保存 {dtgc_count} 条跌停股票数据到数据库")
                results['dtgc_pool'] = dtgc_count
            except Exception as e:
                logger.error(f"❌ 保存跌停股票数据失败: {str(e)}", exc_info=True)
                results['dtgc_pool'] = f"失败: {str(e)}"
            
            # 5. 保存指数数据
            try:
                index_count = IndexHistoryService.save_today_indices(db)
                logger.info(f"✅ 成功保存 {index_count} 条指数数据到数据库")
                results['indices'] = index_count
            except Exception as e:
                logger.error(f"❌ 保存指数数据失败: {str(e)}", exc_info=True)
                results['indices'] = f"失败: {str(e)}"
            
            logger.info("每日数据保存任务完成")
            
            # 显示结果摘要
            print("\n" + "=" * 60)
            print("📊 数据保存结果摘要")
            print("=" * 60)
            print(f"  板块数据: {results.get('sectors', '未执行')}")
            print(f"  涨停股票池: {results.get('zt_pool', '未执行')}")
            print(f"  炸板股票池: {results.get('zbgc_pool', '未执行')}")
            print(f"  跌停股票池: {results.get('dtgc_pool', '未执行')}")
            print(f"  指数数据: {results.get('indices', '未执行')}")
            print("=" * 60)
            
        except Exception as e:
            logger.error(f"数据库操作失败: {str(e)}", exc_info=True)
            raise
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"定时任务执行失败: {str(e)}", exc_info=True)
        raise

def main():
    """手动执行定时任务"""
    parser = argparse.ArgumentParser(description='手动执行定时任务 - 获取并保存今日数据')
    parser.add_argument('--force', action='store_true', help='强制执行，跳过交易日检查')
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔄 手动执行定时任务 - 获取并保存今日数据")
    print("=" * 60)
    
    today = get_utc8_date()
    print(f"\n📅 目标日期: {today}")
    
    if args.force:
        print("⚠️  强制执行模式：跳过交易日检查")
    
    print("\n🚀 开始执行定时任务...")
    print("-" * 60)
    
    try:
        save_daily_data(force=args.force)
        print("\n" + "=" * 60)
        print("✅ 定时任务执行完成")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ 定时任务执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

