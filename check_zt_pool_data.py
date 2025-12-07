#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查涨停股票池数据存储情况
"""
import sys
from pathlib import Path
from datetime import date, timedelta

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.db import SessionLocal
from services.zt_pool_history_service import ZtPoolHistoryService
from models.zt_pool_history import ZtPoolHistory
from utils.time_utils import get_utc8_date
from sqlalchemy import func, distinct

def check_zt_pool_data():
    """检查涨停股票池数据"""
    print("=" * 60)
    print("🔍 检查涨停股票池数据存储情况")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # 1. 检查所有日期
        print("\n📅 检查数据库中的日期记录...")
        dates = db.query(distinct(ZtPoolHistory.date)).order_by(ZtPoolHistory.date.desc()).all()
        dates_list = [d[0] for d in dates]
        
        if not dates_list:
            print("❌ 数据库中没有涨停股票池数据！")
            return
        
        print(f"✅ 找到 {len(dates_list)} 个日期的数据")
        print("\n📋 日期列表（最近10个）:")
        print("-" * 60)
        for i, d in enumerate(dates_list[:10], 1):
            count = db.query(ZtPoolHistory).filter(ZtPoolHistory.date == d).count()
            print(f"{i}. {d} - {count} 只股票")
        print("-" * 60)
        
        # 2. 检查最近7天的数据
        print("\n📊 最近7天的数据情况:")
        print("-" * 60)
        today = get_utc8_date()
        for i in range(7):
            check_date = today - timedelta(days=i)
            count = db.query(ZtPoolHistory).filter(ZtPoolHistory.date == check_date).count()
            status = "✅" if count > 0 else "❌"
            print(f"{status} {check_date}: {count} 只股票")
        print("-" * 60)
        
        # 3. 检查昨日数据
        yesterday = today - timedelta(days=1)
        print(f"\n🔍 详细检查昨日数据 ({yesterday}):")
        print("-" * 60)
        yesterday_data = db.query(ZtPoolHistory).filter(
            ZtPoolHistory.date == yesterday
        ).order_by(ZtPoolHistory.index).all()
        
        if yesterday_data:
            print(f"✅ 找到 {len(yesterday_data)} 只股票")
            print("\n📋 昨日涨停股票列表（前10只）:")
            print("-" * 100)
            print(f"{'序号':<6} {'代码':<10} {'名称':<15} {'涨跌幅':<10} {'连板数':<8} {'成交额(亿元)':<15} {'行业':<20}")
            print("-" * 100)
            for stock in yesterday_data[:10]:
                print(f"{stock.index:<6} {stock.code:<10} {stock.name:<15} {stock.change_percent:<10.2f}% "
                      f"{stock.continuous_boards:<8} {stock.turnover:<15.2f} {stock.industry or '':<20}")
            print("-" * 100)
            
            # 统计信息
            total_turnover = sum(s.turnover for s in yesterday_data)
            avg_boards = sum(s.continuous_boards for s in yesterday_data) / len(yesterday_data)
            max_boards = max(s.continuous_boards for s in yesterday_data)
            
            print(f"\n📊 昨日统计信息:")
            print(f"   总股票数: {len(yesterday_data)}")
            print(f"   总成交额: {total_turnover:.2f} 亿元")
            print(f"   平均连板数: {avg_boards:.2f}")
            print(f"   最大连板数: {max_boards}")
        else:
            print(f"❌ 昨日 ({yesterday}) 没有数据！")
            print("\n💡 可能的原因:")
            print("   1. 定时任务未执行")
            print("   2. 数据保存时出错")
            print("   3. 数据被意外删除")
            print("   4. 昨日是交易日但数据未保存")
        
        # 4. 检查数据完整性
        print("\n🔍 检查数据完整性...")
        print("-" * 60)
        
        # 检查是否有重复数据
        duplicate_dates = db.query(
            ZtPoolHistory.date,
            func.count(ZtPoolHistory.id).label('count')
        ).group_by(ZtPoolHistory.date).having(func.count(ZtPoolHistory.id) > 200).all()
        
        if duplicate_dates:
            print("⚠️  发现可能重复的日期数据:")
            for d, cnt in duplicate_dates:
                print(f"   {d}: {cnt} 条记录（可能重复）")
        else:
            print("✅ 未发现明显的重复数据")
        
        # 检查空值
        null_codes = db.query(ZtPoolHistory).filter(
            (ZtPoolHistory.code == None) | (ZtPoolHistory.code == '')
        ).count()
        null_names = db.query(ZtPoolHistory).filter(
            (ZtPoolHistory.name == None) | (ZtPoolHistory.name == '')
        ).count()
        
        if null_codes > 0 or null_names > 0:
            print(f"⚠️  发现空值数据: 代码空值 {null_codes} 条, 名称空值 {null_names} 条")
        else:
            print("✅ 未发现空值数据")
        
        # 5. 检查保存逻辑
        print("\n🔍 检查保存逻辑...")
        print("-" * 60)
        print("检查 save_today_zt_pool 方法:")
        print("   - 方法会先删除当日已存在的数据")
        print("   - 然后保存新的数据")
        print("   - 如果保存过程中出错，可能导致数据丢失")
        
        # 6. 建议
        print("\n💡 建议:")
        print("-" * 60)
        if yesterday not in dates_list:
            print("   1. 检查定时任务是否在昨日执行")
            print("   2. 检查定时任务的日志")
            print("   3. 手动执行保存操作: python fetch_today_data.py")
            print("   4. 检查数据库连接是否正常")
        else:
            print("   ✅ 昨日数据存在，数据正常")
        
    except Exception as e:
        print(f"❌ 检查过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == '__main__':
    check_zt_pool_data()

