#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查指定日期的数据是否正确保存
"""
import sys
from pathlib import Path
from datetime import date, datetime

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

def check_date_data(target_date: date):
    """检查指定日期的数据"""
    print("=" * 80)
    print(f"📊 检查 {target_date} 的数据")
    print("=" * 80)
    print()
    
    db = SessionLocal()
    try:
        # 检查执行记录
        print("🔍 执行记录:")
        executions = SchedulerExecutionService.get_executions_by_date(db, target_date)
        if executions:
            for exec in executions:
                print(f"  - {exec.execution_time.strftime('%Y-%m-%d %H:%M:%S')} | {exec.job_name} | {exec.status}")
                print(f"    行业板块: {exec.industry_sectors_count or 0}, 概念板块: {exec.concept_sectors_count or 0}")
                print(f"    涨停: {exec.zt_pool_count or 0}, 炸板: {exec.zbgc_pool_count or 0}, 跌停: {exec.dtgc_pool_count or 0}, 指数: {exec.index_count or 0}")
        else:
            print("  ⚠️ 没有找到执行记录")
        print()
        
        # 检查板块数据
        print("🔍 板块数据:")
        industry_sectors = SectorHistoryService.get_sectors_by_date(db, target_date, 'industry')
        concept_sectors = SectorHistoryService.get_sectors_by_date(db, target_date, 'concept')
        print(f"  行业板块: {len(industry_sectors)} 条")
        if industry_sectors:
            print(f"    示例: {industry_sectors[0].get('name', 'N/A')} - 涨跌幅: {industry_sectors[0].get('changePercent', 0):.2f}%")
        print(f"  概念板块: {len(concept_sectors)} 条")
        if concept_sectors:
            print(f"    示例: {concept_sectors[0].get('name', 'N/A')} - 涨跌幅: {concept_sectors[0].get('changePercent', 0):.2f}%")
        print()
        
        # 检查涨停股票池
        print("🔍 涨停股票池:")
        zt_pool = ZtPoolHistoryService.get_zt_pool_by_date(db, target_date)
        print(f"  涨停股票: {len(zt_pool)} 条")
        if zt_pool:
            print(f"    示例: {zt_pool[0].get('name', 'N/A')} ({zt_pool[0].get('code', 'N/A')}) - 涨跌幅: {zt_pool[0].get('changePercent', 0):.2f}%")
        print()
        
        # 检查炸板股票池
        print("🔍 炸板股票池:")
        zb_pool = ZbgcPoolHistoryService.get_zbgc_pool_by_date(db, target_date)
        print(f"  炸板股票: {len(zb_pool)} 条")
        if zb_pool:
            print(f"    示例: {zb_pool[0].get('name', 'N/A')} ({zb_pool[0].get('code', 'N/A')}) - 涨跌幅: {zb_pool[0].get('changePercent', 0):.2f}%")
        print()
        
        # 检查跌停股票池
        print("🔍 跌停股票池:")
        dt_pool = DtgcPoolHistoryService.get_dtgc_pool_by_date(db, target_date)
        print(f"  跌停股票: {len(dt_pool)} 条")
        if dt_pool:
            print(f"    示例: {dt_pool[0].get('name', 'N/A')} ({dt_pool[0].get('code', 'N/A')}) - 涨跌幅: {dt_pool[0].get('changePercent', 0):.2f}%")
        print()
        
        # 检查指数数据
        print("🔍 指数数据:")
        indices = IndexHistoryService.get_indices_by_date(db, target_date)
        print(f"  指数: {len(indices)} 条")
        if indices:
            print(f"    示例: {indices[0].get('name', 'N/A')} - 涨跌幅: {indices[0].get('changePercent', 0):.2f}%")
        print()
        
        # 检查数据创建时间
        print("🔍 数据创建时间:")
        from models.sector_history import SectorHistory
        from sqlalchemy import func
        
        # 获取该日期最早和最晚的创建时间
        time_stats = db.query(
            func.min(SectorHistory.created_at).label('min_time'),
            func.max(SectorHistory.created_at).label('max_time'),
            func.count(SectorHistory.id).label('count')
        ).filter(SectorHistory.date == target_date).first()
        
        if time_stats and time_stats.count > 0:
            print(f"  最早创建时间: {time_stats.min_time}")
            print(f"  最晚创建时间: {time_stats.max_time}")
            print(f"  数据条数: {time_stats.count}")
        else:
            print("  ⚠️ 没有找到创建时间信息")
        
    finally:
        db.close()
    
    print("=" * 80)

def compare_dates(date1: date, date2: date):
    """比较两个日期的数据"""
    print("=" * 80)
    print(f"📊 比较 {date1} 和 {date2} 的数据")
    print("=" * 80)
    print()
    
    db = SessionLocal()
    try:
        # 比较板块数据
        print("🔍 比较板块数据:")
        sectors1 = SectorHistoryService.get_sectors_by_date(db, date1, 'industry')
        sectors2 = SectorHistoryService.get_sectors_by_date(db, date2, 'industry')
        
        print(f"  {date1}: {len(sectors1)} 条行业板块数据")
        print(f"  {date2}: {len(sectors2)} 条行业板块数据")
        
        if len(sectors1) > 0 and len(sectors2) > 0:
            # 比较前几条数据
            print()
            print("  前5条数据对比:")
            for i in range(min(5, len(sectors1), len(sectors2))):
                s1 = sectors1[i]
                s2 = sectors2[i]
                match = "✅" if s1.get('name') == s2.get('name') and abs(s1.get('changePercent', 0) - s2.get('changePercent', 0)) < 0.01 else "❌"
                print(f"    {match} {s1.get('name', 'N/A')}: {date1}={s1.get('changePercent', 0):.2f}%, {date2}={s2.get('changePercent', 0):.2f}%")
        
        # 比较涨停股票池
        print()
        print("🔍 比较涨停股票池:")
        zt1 = ZtPoolHistoryService.get_zt_pool_by_date(db, date1)
        zt2 = ZtPoolHistoryService.get_zt_pool_by_date(db, date2)
        
        print(f"  {date1}: {len(zt1)} 条涨停股票")
        print(f"  {date2}: {len(zt2)} 条涨停股票")
        
        if len(zt1) > 0 and len(zt2) > 0:
            # 比较前几条数据
            print()
            print("  前5条数据对比:")
            for i in range(min(5, len(zt1), len(zt2))):
                z1 = zt1[i]
                z2 = zt2[i]
                match = "✅" if z1.get('code') == z2.get('code') and abs(z1.get('changePercent', 0) - z2.get('changePercent', 0)) < 0.01 else "❌"
                print(f"    {match} {z1.get('name', 'N/A')} ({z1.get('code', 'N/A')}): {date1}={z1.get('changePercent', 0):.2f}%, {date2}={z2.get('changePercent', 0):.2f}%")
        
    finally:
        db.close()
    
    print("=" * 80)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="检查指定日期的数据")
    parser.add_argument('--date1', type=str, help="第一个日期 (YYYY-MM-DD)")
    parser.add_argument('--date2', type=str, help="第二个日期 (YYYY-MM-DD)")
    parser.add_argument('--date', type=str, help="要检查的日期 (YYYY-MM-DD)")
    
    args = parser.parse_args()
    
    if args.date1 and args.date2:
        date1 = datetime.strptime(args.date1, '%Y-%m-%d').date()
        date2 = datetime.strptime(args.date2, '%Y-%m-%d').date()
        compare_dates(date1, date2)
    elif args.date:
        target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
        check_date_data(target_date)
    else:
        # 默认检查 2025-12-08 和 2025-12-05
        date1 = date(2025, 12, 8)
        date2 = date(2025, 12, 5)
        check_date_data(date1)
        print()
        check_date_data(date2)
        print()
        compare_dates(date1, date2)

