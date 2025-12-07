#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 sector_history 表结构，添加缺失的 index 列
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.db import SessionLocal, engine
from sqlalchemy import text

def fix_sector_history_table():
    """修复 sector_history 表结构"""
    print("=" * 60)
    print("🔧 修复 sector_history 表结构")
    print("=" * 60)
    
    try:
        # 检查表是否存在 index 列
        with engine.connect() as conn:
            # 检查列是否存在
            check_sql = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'sector_history' 
            AND column_name = 'index'
            """
            result = conn.execute(text(check_sql))
            exists = result.fetchone() is not None
            
            if exists:
                print("✅ index 列已存在，无需修复")
                return
            
            print("⚠️  index 列不存在，正在添加...")
            
            # 添加 index 列
            alter_sql = """
            ALTER TABLE sector_history 
            ADD COLUMN IF NOT EXISTS index INTEGER;
            """
            conn.execute(text(alter_sql))
            conn.commit()
            
            print("✅ 成功添加 index 列")
            
            # 如果表中已有数据，需要为现有数据设置默认值
            update_sql = """
            UPDATE sector_history 
            SET index = 0 
            WHERE index IS NULL
            """
            result = conn.execute(text(update_sql))
            updated_count = result.rowcount
            conn.commit()
            
            if updated_count > 0:
                print(f"✅ 已为 {updated_count} 条现有数据设置默认 index 值")
            
            # 设置 NOT NULL 约束（如果表为空或所有数据都有值）
            try:
                set_not_null_sql = """
                ALTER TABLE sector_history 
                ALTER COLUMN index SET NOT NULL;
                """
                conn.execute(text(set_not_null_sql))
                conn.commit()
                print("✅ 成功设置 index 列为 NOT NULL")
            except Exception as e:
                print(f"⚠️  设置 NOT NULL 约束失败（可能表中有 NULL 值）: {str(e)}")
                print("   建议：先清理数据或手动设置 index 值")
            
    except Exception as e:
        print(f"❌ 修复失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = fix_sector_history_table()
    if success:
        print("\n✅ 表结构修复完成！")
    else:
        print("\n❌ 表结构修复失败，请检查错误信息")

