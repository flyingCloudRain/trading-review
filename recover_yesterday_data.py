#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
恢复昨日涨停股票池数据（如果API支持历史数据查询）
"""
import sys
from pathlib import Path
from datetime import date, timedelta

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.db import SessionLocal
from services.zt_pool_service import ZtPoolService
from services.zt_pool_history_service import ZtPoolHistoryService
from models.zt_pool_history import ZtPoolHistory
from utils.time_utils import get_utc8_date, get_utc8_date_compact_str

def recover_yesterday_data():
    """尝试恢复昨日数据"""
    print("=" * 60)
    print("🔄 尝试恢复昨日涨停股票池数据")
    print("=" * 60)
    
    yesterday = get_utc8_date() - timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y%m%d')
    
    print(f"📅 目标日期: {yesterday} ({yesterday_str})")
    
    # 检查数据库中是否已有数据
    db = SessionLocal()
    try:
        existing = db.query(ZtPoolHistory).filter(
            ZtPoolHistory.date == yesterday
        ).first()
        
        if existing:
            count = db.query(ZtPoolHistory).filter(
                ZtPoolHistory.date == yesterday
            ).count()
            print(f"⚠️  数据库中已存在 {yesterday} 的数据: {count} 条")
            print("   如需重新获取，请先删除旧数据")
            return
        
        # 尝试从API获取昨日数据
        print(f"\n⏳ 正在从API获取 {yesterday} 的涨停股票数据...")
        try:
            stocks = ZtPoolService.get_zt_pool(date=yesterday_str)
            
            if not stocks:
                print(f"❌ API返回空数据，可能原因：")
                print(f"   1. {yesterday} 不是交易日")
                print(f"   2. API不支持历史数据查询")
                print(f"   3. 数据源暂时不可用")
                return
            
            print(f"✅ 成功获取 {len(stocks)} 只股票数据")
            
            # 保存到数据库
            print(f"⏳ 正在保存到数据库...")
            
            # 手动创建记录（因为save_today_zt_pool只保存今天的数据）
            saved_count = 0
            from datetime import time as dt_time
            for stock in stocks:
                
                # 解析时间字符串
                first_sealing_time = None
                last_sealing_time = None
                
                if stock.get('firstSealingTime'):
                    try:
                        time_str = stock['firstSealingTime'].strip()
                        if time_str:
                            parts = time_str.split(':')
                            if len(parts) >= 2:
                                hour = int(parts[0])
                                minute = int(parts[1])
                                second = int(parts[2]) if len(parts) > 2 else 0
                                first_sealing_time = dt_time(hour, minute, second)
                    except:
                        pass
                
                if stock.get('lastSealingTime'):
                    try:
                        time_str = stock['lastSealingTime'].strip()
                        if time_str:
                            parts = time_str.split(':')
                            if len(parts) >= 2:
                                hour = int(parts[0])
                                minute = int(parts[1])
                                second = int(parts[2]) if len(parts) > 2 else 0
                                last_sealing_time = dt_time(hour, minute, second)
                    except:
                        pass
                
                history = ZtPoolHistory(
                    date=yesterday,
                    index=stock.get('index', 0),
                    code=stock.get('code', ''),
                    name=stock.get('name', ''),
                    change_percent=stock.get('changePercent', 0),
                    latest_price=stock.get('latestPrice', 0),
                    turnover=stock.get('turnover', 0),
                    circulating_market_value=stock.get('circulatingMarketValue', 0),
                    total_market_value=stock.get('totalMarketValue', 0),
                    turnover_rate=stock.get('turnoverRate', 0),
                    sealing_funds=stock.get('sealingFunds', 0),
                    first_sealing_time=first_sealing_time,
                    last_sealing_time=last_sealing_time,
                    explosion_count=stock.get('explosionCount', 0),
                    zt_statistics=stock.get('ztStatistics'),
                    continuous_boards=stock.get('continuousBoards', 0),
                    industry=stock.get('industry'),
                )
                db.add(history)
                saved_count += 1
            
            db.commit()
            print(f"✅ 成功保存 {saved_count} 条数据到数据库")
            
            # 显示部分数据
            print(f"\n📋 恢复的数据预览（前5只）:")
            print("-" * 80)
            for i, stock in enumerate(stocks[:5], 1):
                print(f"{i}. {stock.get('code')} {stock.get('name')} - "
                      f"涨跌幅: {stock.get('changePercent'):.2f}%, "
                      f"连板数: {stock.get('continuousBoards')}")
            print("-" * 80)
            
        except Exception as e:
            print(f"❌ 获取或保存数据失败: {str(e)}")
            db.rollback()
            import traceback
            traceback.print_exc()
            
    finally:
        db.close()

if __name__ == '__main__':
    recover_yesterday_data()

