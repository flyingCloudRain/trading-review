#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取今日板块信息和涨停股票信息
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.db import SessionLocal
from services.sector_service import SectorService
from services.sector_history_service import SectorHistoryService
from services.zt_pool_service import ZtPoolService
from services.zt_pool_history_service import ZtPoolHistoryService
from utils.time_utils import get_utc8_date, get_utc8_date_str
from datetime import datetime

def fetch_today_sector_data():
    """获取今日板块信息并保存到数据库"""
    print("=" * 60)
    print("📊 获取今日板块信息")
    print("=" * 60)
    
    try:
        # 获取板块数据
        print("⏳ 正在从API获取板块信息...")
        sectors = SectorService.get_industry_summary()
        print(f"✅ 成功获取 {len(sectors)} 个板块信息")
        
        # 保存到数据库
        print("⏳ 正在保存到数据库...")
        db = SessionLocal()
        try:
            saved_count = SectorHistoryService.save_today_sectors(db)
            print(f"✅ 成功保存 {saved_count} 个板块到数据库")
            
            # 显示部分数据
            print("\n📋 板块信息预览（前10个）:")
            print("-" * 80)
            print(f"{'序号':<6} {'板块名称':<20} {'涨跌幅':<12} {'净流入(亿元)':<15}")
            print("-" * 80)
            for i, sector in enumerate(sectors[:10], 1):
                name = sector.get('name', '')
                change = sector.get('changePercent', 0)
                net_inflow = sector.get('netInflow', 0)
                print(f"{i:<6} {name:<20} {change:<12.2f}% {net_inflow:<15.2f}")
            print("-" * 80)
            
            return True, len(sectors)
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ 获取板块信息失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, 0

def fetch_today_zt_pool():
    """获取今日涨停股票信息并保存到数据库"""
    print("\n" + "=" * 60)
    print("📈 获取今日涨停股票信息")
    print("=" * 60)
    
    try:
        # 获取涨停股票数据
        print("⏳ 正在从API获取涨停股票信息...")
        stocks = ZtPoolService.get_zt_pool()
        print(f"✅ 成功获取 {len(stocks)} 只涨停股票")
        
        # 保存到数据库
        print("⏳ 正在保存到数据库...")
        db = SessionLocal()
        try:
            saved_count = ZtPoolHistoryService.save_today_zt_pool(db)
            print(f"✅ 成功保存 {saved_count} 只涨停股票到数据库")
            
            # 显示部分数据
            print("\n📋 涨停股票预览（前10只）:")
            print("-" * 100)
            print(f"{'序号':<6} {'代码':<10} {'名称':<15} {'涨跌幅':<10} {'连板数':<8} {'成交额(亿元)':<15} {'行业':<20}")
            print("-" * 100)
            for i, stock in enumerate(stocks[:10], 1):
                code = stock.get('code', '')
                name = stock.get('name', '')
                change = stock.get('changePercent', 0)
                boards = stock.get('continuousBoards', 0)
                turnover = stock.get('turnover', 0)
                industry = stock.get('industry', '')
                print(f"{i:<6} {code:<10} {name:<15} {change:<10.2f}% {boards:<8} {turnover:<15.2f} {industry:<20}")
            print("-" * 100)
            
            # 统计信息
            if stocks:
                total_turnover = sum(s.get('turnover', 0) for s in stocks)
                avg_boards = sum(s.get('continuousBoards', 0) for s in stocks) / len(stocks)
                max_boards = max(s.get('continuousBoards', 0) for s in stocks)
                
                print(f"\n📊 统计信息:")
                print(f"   总成交额: {total_turnover:.2f} 亿元")
                print(f"   平均连板数: {avg_boards:.2f}")
                print(f"   最大连板数: {max_boards}")
            
            return True, len(stocks)
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ 获取涨停股票信息失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, 0

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🚀 开始获取今日数据")
    print("=" * 60)
    print(f"📅 日期: {get_utc8_date_str()}")
    print(f"🕐 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 获取板块信息
    sector_success, sector_count = fetch_today_sector_data()
    
    # 获取涨停股票信息
    zt_success, zt_count = fetch_today_zt_pool()
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 数据获取总结")
    print("=" * 60)
    print(f"板块信息: {'✅ 成功' if sector_success else '❌ 失败'} ({sector_count} 条)")
    print(f"涨停股票: {'✅ 成功' if zt_success else '❌ 失败'} ({zt_count} 条)")
    print("=" * 60)
    
    if sector_success and zt_success:
        print("\n🎉 所有数据获取并保存成功！")
    else:
        print("\n⚠️  部分数据获取失败，请检查错误信息")

if __name__ == '__main__':
    main()

