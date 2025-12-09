#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迁移 stock_fund_flow_history 表结构
根据实际接口返回的字段更新表结构
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.db import engine, SessionLocal
from sqlalchemy import text, inspect

def main():
    """主函数"""
    print("=" * 80)
    print("🔧 迁移 stock_fund_flow_history 表结构")
    print("=" * 80)
    print()
    
    db = SessionLocal()
    try:
        # 检查表是否存在
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if 'stock_fund_flow_history' not in tables:
            print("❌ stock_fund_flow_history 表不存在，请先运行 init_stock_fund_flow_table.py")
            return 1
        
        print("✅ 表已存在，开始迁移...")
        print()
        
        # 获取当前列
        columns = inspector.get_columns('stock_fund_flow_history')
        existing_column_names = [col['name'] for col in columns]
        
        print(f"当前列: {', '.join(existing_column_names)}")
        print()
        
        # 需要删除的旧列
        old_columns = [
            'main_net_inflow',
            'main_net_inflow_percent',
            'super_large_net_inflow',
            'super_large_net_inflow_percent',
            'large_net_inflow',
            'large_net_inflow_percent',
            'medium_net_inflow',
            'medium_net_inflow_percent',
            'small_net_inflow',
            'small_net_inflow_percent',
        ]
        
        # 需要添加的新列
        new_columns = {
            'stock_name': 'VARCHAR(50)',
            'latest_price': 'DOUBLE PRECISION',
            'change_percent': 'DOUBLE PRECISION',
            'turnover_rate': 'DOUBLE PRECISION',
            'inflow': 'DOUBLE PRECISION',
            'outflow': 'DOUBLE PRECISION',
            'net_amount': 'DOUBLE PRECISION',
            'turnover': 'DOUBLE PRECISION',
        }
        
        # 删除旧列
        print("🗑️  删除旧列...")
        for col_name in old_columns:
            if col_name in existing_column_names:
                try:
                    drop_sql = text(f"ALTER TABLE stock_fund_flow_history DROP COLUMN IF EXISTS {col_name}")
                    db.execute(drop_sql)
                    db.commit()
                    print(f"   ✅ 已删除列: {col_name}")
                except Exception as e:
                    print(f"   ⚠️  删除列 {col_name} 时出错: {e}")
                    db.rollback()
        
        print()
        
        # 添加新列
        print("➕ 添加新列...")
        for col_name, col_type in new_columns.items():
            if col_name not in existing_column_names:
                try:
                    add_sql = text(f"ALTER TABLE stock_fund_flow_history ADD COLUMN IF NOT EXISTS {col_name} {col_type}")
                    db.execute(add_sql)
                    db.commit()
                    print(f"   ✅ 已添加列: {col_name} ({col_type})")
                except Exception as e:
                    print(f"   ⚠️  添加列 {col_name} 时出错: {e}")
                    db.rollback()
            else:
                print(f"   ℹ️  列已存在: {col_name}")
        
        print()
        
        # 验证最终表结构
        print("🔍 验证最终表结构...")
        columns = inspector.get_columns('stock_fund_flow_history')
        print(f"✅ 表包含以下列:")
        for col in columns:
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            print(f"   - {col['name']}: {col['type']} {nullable}")
        
        print()
        print("=" * 80)
        print("✅ 迁移完成")
        print("=" * 80)
        return 0
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return 1
    finally:
        db.close()

if __name__ == '__main__':
    exit(main())

