#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
保存概念板块数据到数据库
可以指定日期保存（注意：API只能获取当前数据，但可以保存为指定日期）
"""
import sys
from pathlib import Path
from datetime import date, datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.db import SessionLocal
from services.concept_service import ConceptService
from services.sector_history_service import SectorHistoryService
from models.sector_history import SectorHistory
from utils.time_utils import get_data_date

def save_concept_data(target_date: date = None):
    """
    保存概念板块数据到数据库
    
    Args:
        target_date: 目标日期，如果为None则使用当前日期（或上一个交易日）
    """
    if target_date is None:
        target_date = get_data_date()
    
    print("=" * 60)
    print(f"📊 获取概念板块数据并保存到数据库")
    print(f"📅 目标日期: {target_date}")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # 获取概念板块数据
        print("\n⏳ 正在从API获取概念板块数据...")
        concepts = ConceptService.get_concept_summary()
        print(f"✅ 成功获取 {len(concepts)} 个概念板块")
        
        if not concepts:
            print("⚠️  警告: 没有获取到概念板块数据")
            return 0
        
        # 检查该日期的数据是否已存在
        existing_count = db.query(SectorHistory).filter(
            SectorHistory.date == target_date,
            SectorHistory.sector_type == 'concept'
        ).count()
        
        if existing_count > 0:
            # 如果已存在，先删除旧数据
            deleted_count = db.query(SectorHistory).filter(
                SectorHistory.date == target_date,
                SectorHistory.sector_type == 'concept'
            ).delete()
            print(f"🗑️  删除 {target_date} 的旧概念板块数据: {deleted_count} 条")
            db.commit()
        
        # 保存新数据
        print(f"\n⏳ 正在保存到数据库...")
        saved_count = 0
        for concept in concepts:
            history = SectorHistory(
                date=target_date,
                sector_type='concept',
                index=concept['index'],
                name=concept['name'],
                change_percent=concept['changePercent'],
                total_volume=concept['totalVolume'],
                total_amount=concept['totalAmount'],
                net_inflow=concept['netInflow'],
                up_count=concept['upCount'],
                down_count=concept['downCount'],
                avg_price=concept['avgPrice'],
                leading_stock=concept['leadingStock'],
                leading_stock_price=concept['leadingStockPrice'],
                leading_stock_change_percent=concept['leadingStockChangePercent'],
            )
            db.add(history)
            saved_count += 1
        
        # 提交新数据
        db.commit()
        print(f"✅ 成功保存 {saved_count} 条概念板块数据到数据库 ({target_date})")
        
        # 显示部分数据
        print("\n📋 概念板块数据预览（前10个）:")
        print("-" * 80)
        print(f"{'序号':<6} {'概念名称':<20} {'涨跌幅':<12} {'净流入(亿元)':<15} {'领涨股':<15}")
        print("-" * 80)
        for i, concept in enumerate(concepts[:10], 1):
            name = concept.get('name', '')
            change = concept.get('changePercent', 0)
            net_inflow = concept.get('netInflow', 0)
            leading_stock = concept.get('leadingStock', '')
            print(f"{i:<6} {name:<20} {change:<12.2f}% {net_inflow:<15.2f} {leading_stock:<15}")
        print("-" * 80)
        
        return saved_count
        
    except Exception as e:
        db.rollback()
        print(f"❌ 保存概念板块数据失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='保存概念板块数据到数据库')
    parser.add_argument(
        '--date',
        type=str,
        help='目标日期，格式：YYYY-MM-DD（例如：2025-12-05）。如果不指定，使用当前日期或上一个交易日'
    )
    
    args = parser.parse_args()
    
    target_date = None
    if args.date:
        try:
            target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
        except ValueError:
            print(f"❌ 日期格式错误: {args.date}，请使用 YYYY-MM-DD 格式")
            sys.exit(1)
    
    try:
        saved_count = save_concept_data(target_date)
        print("\n" + "=" * 60)
        print("🎉 概念板块数据保存完成！")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ 执行失败: {str(e)}")
        sys.exit(1)

