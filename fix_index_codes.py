#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复数据库中错误的指数代码
- 将代码统一转换为6位格式，保留前导0
- 删除空code记录
- 处理重复数据（保留最新的记录）
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.db import SessionLocal
from models.index_history import IndexHistory
from services.stock_index_service import StockIndexService
from sqlalchemy import func, and_

def fix_index_codes(dry_run=True):
    """
    修复指数代码
    
    Args:
        dry_run: 如果为True，只显示将要修改的记录，不实际修改
    """
    db = SessionLocal()
    try:
        print("=" * 80)
        print(f"🔧 修复指数代码（{'模拟运行' if dry_run else '实际执行'}）")
        print("=" * 80)
        
        updated_count = 0
        deleted_count = 0
        
        # 1. 删除空code记录
        print("\n1️⃣ 处理空code记录:")
        print("-" * 80)
        null_codes = db.query(IndexHistory).filter(
            (IndexHistory.code == None) | 
            (IndexHistory.code == '') |
            (IndexHistory.code.is_(None))
        ).all()
        
        if null_codes:
            print(f"   发现 {len(null_codes)} 条空code记录:")
            for record in null_codes:
                print(f"   - ID: {record.id}, Date: {record.date}, Name: {record.name}")
            
            if not dry_run:
                for record in null_codes:
                    db.delete(record)
                db.commit()
                deleted_count += len(null_codes)
                print(f"   ✅ 已删除 {len(null_codes)} 条空code记录")
            else:
                print(f"   💡 模拟：将删除 {len(null_codes)} 条空code记录")
        else:
            print("   ✅ 没有空code记录")
        
        # 2. 修复代码格式（统一为6位）
        print("\n2️⃣ 修复代码格式（统一为6位）:")
        print("-" * 80)
        
        # 获取所有需要修复的记录
        all_records = db.query(IndexHistory).all()
        records_to_fix = []
        
        for record in all_records:
            if not record.code:
                continue  # 空code已在上面处理
            
            current_code = str(record.code).strip()
            normalized_code = StockIndexService.normalize_index_code(current_code)
            
            # 如果代码格式不正确，需要修复
            if current_code != normalized_code:
                records_to_fix.append((record, current_code, normalized_code))
        
        if records_to_fix:
            print(f"   发现 {len(records_to_fix)} 条需要修复的记录")
            
            # 显示前20条
            print(f"\n   前20条需要修复的记录:")
            for i, (record, old_code, new_code) in enumerate(records_to_fix[:20], 1):
                print(f"   {i:2d}. ID: {record.id}, Date: {record.date}, Name: {record.name}")
                print(f"       旧代码: '{old_code}' -> 新代码: '{new_code}'")
            
            if len(records_to_fix) > 20:
                print(f"   ... 还有 {len(records_to_fix) - 20} 条记录")
            
            if not dry_run:
                # 更新代码
                for record, old_code, new_code in records_to_fix:
                    record.code = new_code
                    updated_count += 1
                
                db.commit()
                print(f"\n   ✅ 已更新 {updated_count} 条记录的代码")
            else:
                print(f"\n   💡 模拟：将更新 {len(records_to_fix)} 条记录的代码")
        else:
            print("   ✅ 所有代码格式正确")
        
        # 3. 处理重复的(date, code)组合
        print("\n3️⃣ 处理重复的(date, code)组合:")
        print("-" * 80)
        duplicates = db.query(
            IndexHistory.date,
            IndexHistory.code,
            func.count(IndexHistory.id).label('count')
        ).group_by(IndexHistory.date, IndexHistory.code).having(
            func.count(IndexHistory.id) > 1
        ).all()
        
        if duplicates:
            print(f"   发现 {len(duplicates)} 组重复数据")
            total_duplicates_to_delete = 0
            
            for dup in duplicates:
                # 获取该组合的所有记录，按创建时间降序排列
                records = db.query(IndexHistory).filter(
                    and_(IndexHistory.date == dup.date, IndexHistory.code == dup.code)
                ).order_by(IndexHistory.created_at.desc()).all()
                
                if len(records) > 1:
                    # 保留最新的记录，删除其他
                    to_delete = records[1:]  # 跳过第一条（最新的）
                    total_duplicates_to_delete += len(to_delete)
                    
                    if dry_run and total_duplicates_to_delete <= 20:
                        print(f"   - Date: {dup.date}, Code: {dup.code}, Count: {dup.count}")
                        print(f"     保留: ID {records[0].id} (创建时间: {records[0].created_at})")
                        print(f"     删除: {[r.id for r in to_delete]}")
                    elif not dry_run:
                        for record in to_delete:
                            db.delete(record)
            
            if not dry_run:
                db.commit()
                deleted_count += total_duplicates_to_delete
                print(f"   ✅ 已删除 {total_duplicates_to_delete} 条重复记录")
            else:
                print(f"   💡 模拟：将删除 {total_duplicates_to_delete} 条重复记录")
        else:
            print("   ✅ 没有重复数据")
        
        # 4. 验证修复结果
        print("\n4️⃣ 修复后验证:")
        print("-" * 80)
        if not dry_run:
            # 重新检查
            null_count = db.query(IndexHistory).filter(
                (IndexHistory.code == None) | 
                (IndexHistory.code == '') |
                (IndexHistory.code.is_(None))
            ).count()
            
            duplicate_count = db.query(
                IndexHistory.date,
                IndexHistory.code,
                func.count(IndexHistory.id).label('count')
            ).group_by(IndexHistory.date, IndexHistory.code).having(
                func.count(IndexHistory.id) > 1
            ).count()
            
            # 检查代码格式
            all_records = db.query(IndexHistory).all()
            wrong_format_count = 0
            for record in all_records:
                if record.code:
                    normalized = StockIndexService.normalize_index_code(record.code)
                    if str(record.code) != normalized:
                        wrong_format_count += 1
            
            total_count = db.query(IndexHistory).count()
            
            print(f"   总记录数: {total_count}")
            print(f"   空code记录: {null_count} 条")
            print(f"   重复组合: {duplicate_count} 组")
            print(f"   格式错误: {wrong_format_count} 条")
            print(f"   已更新: {updated_count} 条")
            print(f"   已删除: {deleted_count} 条")
            
            if null_count == 0 and duplicate_count == 0 and wrong_format_count == 0:
                print("\n   ✅ 所有错误已修复")
            else:
                print(f"\n   ⚠️  仍有错误需要处理")
        
        print("\n" + "=" * 80)
        if dry_run:
            print("💡 这是模拟运行，未实际修改数据")
            print("   要实际执行修复，请运行: python fix_index_codes.py --execute")
        else:
            print("✅ 修复完成")
        print("=" * 80)
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ 修复过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='修复数据库中错误的指数代码')
    parser.add_argument('--execute', action='store_true', help='实际执行修复（默认是模拟运行）')
    args = parser.parse_args()
    
    fix_index_codes(dry_run=not args.execute)

