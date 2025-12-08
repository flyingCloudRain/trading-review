#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
临时脚本：获取历史日期（12月1日-12月5日）的涨停、炸板、跌停股票池数据并存入数据库

注意：AKShare API 只能获取实时数据，无法获取历史数据。
此脚本尝试为指定日期获取数据，但实际获取的可能是当前实时数据。
"""
import sys
from pathlib import Path
from datetime import date, datetime, timedelta

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.db import SessionLocal
from services.zt_pool_history_service import ZtPoolHistoryService
from services.zbgc_pool_history_service import ZbgcPoolHistoryService
from services.dtgc_pool_history_service import DtgcPoolHistoryService
from utils.time_utils import get_utc8_date

def fetch_and_save_pool_data(target_date: date):
    """
    获取并保存指定日期的股票池数据
    
    Args:
        target_date: 目标日期
    """
    date_str = target_date.strftime('%Y%m%d')
    date_display = target_date.strftime('%Y-%m-%d')
    
    print("=" * 80)
    print(f"📅 开始处理日期: {date_display} ({date_str})")
    print("=" * 80)
    
    db = SessionLocal()
    try:
        # 1. 获取并保存涨停股票池数据
        print(f"\n📈 获取涨停股票池数据...")
        try:
            saved_zt = ZtPoolHistoryService.save_today_zt_pool(db, target_date=target_date)
            print(f"✅ 成功保存 {saved_zt} 条涨停股票数据")
        except Exception as e:
            print(f"❌ 获取涨停股票池数据失败: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # 2. 获取并保存炸板股票池数据
        print(f"\n💥 获取炸板股票池数据...")
        try:
            saved_zbgc = ZbgcPoolHistoryService.save_today_zbgc_pool(db, target_date=target_date)
            print(f"✅ 成功保存 {saved_zbgc} 条炸板股票数据")
        except Exception as e:
            print(f"❌ 获取炸板股票池数据失败: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # 3. 获取并保存跌停股票池数据
        print(f"\n📉 获取跌停股票池数据...")
        try:
            saved_dtgc = DtgcPoolHistoryService.save_today_dtgc_pool(db, target_date=target_date)
            print(f"✅ 成功保存 {saved_dtgc} 条跌停股票数据")
        except Exception as e:
            print(f"❌ 获取跌停股票池数据失败: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print(f"\n✅ 日期 {date_display} 的数据处理完成")
        
    except Exception as e:
        print(f"❌ 处理日期 {date_display} 时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def main():
    """主函数"""
    print("=" * 80)
    print("🚀 临时脚本：获取历史股票池数据（12月1日-12月5日）")
    print("=" * 80)
    print("\n⚠️  重要提示：")
    print("   AKShare API 只能获取实时数据，无法获取历史数据。")
    print("   此脚本尝试为指定日期获取数据，但实际获取的可能是当前实时数据。")
    print("   如果这些日期不是交易日，API可能返回空数据或错误。")
    print("=" * 80)
    
    # 定义日期范围：2024年12月1日到12月5日
    start_date = date(2024, 12, 1)
    end_date = date(2024, 12, 5)
    
    # 生成日期列表
    current_date = start_date
    dates_to_process = []
    
    while current_date <= end_date:
        dates_to_process.append(current_date)
        current_date += timedelta(days=1)
    
    print(f"\n📋 将处理以下日期（共 {len(dates_to_process)} 个）:")
    for d in dates_to_process:
        weekday = d.strftime('%A')
        print(f"   - {d.strftime('%Y-%m-%d')} ({weekday})")
    
    # 确认执行
    print("\n" + "=" * 80)
    response = input("是否继续执行？(y/n): ").strip().lower()
    if response != 'y':
        print("❌ 用户取消执行")
        return
    
    print("\n" + "=" * 80)
    print("🔄 开始执行...")
    print("=" * 80)
    
    # 处理每个日期
    success_count = 0
    fail_count = 0
    
    for target_date in dates_to_process:
        try:
            fetch_and_save_pool_data(target_date)
            success_count += 1
        except Exception as e:
            print(f"❌ 处理日期 {target_date} 失败: {str(e)}")
            fail_count += 1
        
        # 每个日期之间稍作延迟，避免请求过快
        import time
        time.sleep(1)
    
    # 总结
    print("\n" + "=" * 80)
    print("📊 执行总结")
    print("=" * 80)
    print(f"✅ 成功处理: {success_count} 个日期")
    print(f"❌ 失败: {fail_count} 个日期")
    print(f"📅 总计: {len(dates_to_process)} 个日期")
    print("=" * 80)

if __name__ == '__main__':
    main()

