#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证数据库表结构并测试查询
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.db import SessionLocal, engine
from services.sector_history_service import SectorHistoryService
from sqlalchemy import text
from datetime import date, timedelta

def verify_table_structure():
    """验证表结构"""
    print("=" * 60)
    print("🔍 验证 sector_history 表结构")
    print("=" * 60)
    
    # 1. 检查表结构
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'sector_history'
            ORDER BY ordinal_position
        """))
        
        print("\n📋 表结构:")
        print("-" * 60)
        columns = []
        for row in result:
            columns.append(row[0])
            print(f"{row[0]:<30} {row[1]:<20} nullable={row[2]}")
        print("-" * 60)
        
        if 'index' in columns:
            print("✅ index 列存在")
        else:
            print("❌ index 列不存在，需要添加")
            return False
    
    # 2. 测试查询
    print("\n🔍 测试查询功能...")
    db = SessionLocal()
    try:
        # 测试获取所有日期
        dates = SectorHistoryService.get_all_dates(db)
        print(f"✅ 成功获取日期列表: {len(dates)} 个日期")
        if dates:
            print(f"   最新日期: {dates[0]}")
            print(f"   最早日期: {dates[-1]}")
        
        # 测试获取单日数据
        if dates:
            test_date = dates[0]
            sectors = SectorHistoryService.get_sectors_by_date(db, test_date)
            print(f"✅ 成功获取 {test_date} 的数据: {len(sectors)} 条")
            if sectors:
                print(f"   示例: {sectors[0].get('name')} - {sectors[0].get('changePercent')}%")
        
        # 测试日期范围查询
        if len(dates) >= 2:
            start_date = dates[-1]
            end_date = dates[0]
            sectors = SectorHistoryService.get_sectors_by_date_range(db, start_date, end_date)
            print(f"✅ 成功获取日期范围数据 ({start_date} 至 {end_date}): {len(sectors)} 条")
        
        print("\n✅ 所有查询测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 查询测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == '__main__':
    success = verify_table_structure()
    if success:
        print("\n✅ 表结构验证通过！")
    else:
        print("\n❌ 表结构验证失败，请检查错误信息")

