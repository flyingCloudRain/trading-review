#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加 trading_reviews 表的 market 列
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from database.db_supabase import SessionLocal, engine
    from sqlalchemy import text
    print("✅ 成功连接到数据库")
except Exception as e:
    print(f"❌ 数据库连接失败: {e}")
    sys.exit(1)

def add_market_column():
    """添加 market 列到 trading_reviews 表"""
    db = SessionLocal()
    try:
        # 检查列是否已存在
        check_sql = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'trading_reviews' 
            AND column_name = 'market'
        """)
        result = db.execute(check_sql).fetchone()
        
        if result:
            print("✅ market 列已存在，无需添加")
            return
        
        print("🔨 正在添加 market 列...")
        
        # 先添加列（允许 NULL，并设置默认值）
        alter_sql = text("""
            ALTER TABLE trading_reviews 
            ADD COLUMN market VARCHAR(10) DEFAULT 'A股'
        """)
        db.execute(alter_sql)
        db.commit()
        print("  ✅ 已添加 market 列（允许 NULL）")
        
        # 更新现有数据，将所有 NULL 值设置为 'A股'
        update_sql = text("""
            UPDATE trading_reviews 
            SET market = 'A股' 
            WHERE market IS NULL
        """)
        db.execute(update_sql)
        db.commit()
        print("  ✅ 已更新现有数据")
        
        # 然后设置 NOT NULL 约束（在更新数据之后）
        alter_not_null_sql = text("""
            ALTER TABLE trading_reviews 
            ALTER COLUMN market SET NOT NULL
        """)
        db.execute(alter_not_null_sql)
        db.commit()
        print("  ✅ 已设置 NOT NULL 约束")
        
        # 设置默认值（确保新插入的记录有默认值）
        alter_default_sql = text("""
            ALTER TABLE trading_reviews 
            ALTER COLUMN market SET DEFAULT 'A股'
        """)
        db.execute(alter_default_sql)
        db.commit()
        print("  ✅ 已设置默认值")
        
        print("✅ 成功添加 market 列到 trading_reviews 表")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 添加 market 列时出错: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 80)
    print("🔧 添加 trading_reviews 表的 market 列")
    print("=" * 80)
    print()
    
    try:
        add_market_column()
        print()
        print("✅ 迁移完成！")
    except Exception as e:
        print()
        print(f"❌ 迁移失败: {e}")
        sys.exit(1)

