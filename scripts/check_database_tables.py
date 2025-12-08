#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库中是否存在对应的表
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.db import SessionLocal, engine
from sqlalchemy import text, inspect
from sqlalchemy.exc import OperationalError

def check_table_exists(table_name: str) -> bool:
    """检查表是否存在"""
    try:
        db = SessionLocal()
        try:
            # 使用 information_schema 查询表是否存在
            query = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = :table_name
                )
            """)
            result = db.execute(query, {"table_name": table_name}).scalar()
            return result
        finally:
            db.close()
    except Exception as e:
        print(f"❌ 检查表 {table_name} 时出错: {str(e)}")
        return False

def get_all_tables() -> list:
    """获取数据库中所有表名"""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        return tables
    except Exception as e:
        print(f"❌ 获取表列表时出错: {str(e)}")
        return []

def get_table_columns(table_name: str) -> list:
    """获取表的列信息"""
    try:
        inspector = inspect(engine)
        columns = inspector.get_columns(table_name)
        return columns
    except Exception as e:
        print(f"❌ 获取表 {table_name} 的列信息时出错: {str(e)}")
        return []

def main():
    """主函数"""
    print("=" * 80)
    print("📊 数据库表检查工具")
    print("=" * 80)
    print()
    
    # 需要检查的表列表
    required_tables = [
        'scheduler_execution',
        'sector_history',
        'zt_pool_history',
        'zb_pool_history',
        'dt_pool_history',
        'index_history',
        'trading_reviews'
    ]
    
    print("🔍 检查必需的表...")
    print("-" * 80)
    
    all_tables = get_all_tables()
    
    if not all_tables:
        print("❌ 无法连接到数据库或无法获取表列表")
        return
    
    print(f"✅ 数据库连接成功，共找到 {len(all_tables)} 个表")
    print()
    
    # 检查每个必需的表
    missing_tables = []
    existing_tables = []
    
    for table_name in required_tables:
        exists = check_table_exists(table_name)
        if exists:
            existing_tables.append(table_name)
            print(f"✅ 表 '{table_name}' 存在")
            
            # 显示表的列信息
            columns = get_table_columns(table_name)
            if columns:
                print(f"   列数: {len(columns)}")
                print(f"   列名: {', '.join([col['name'] for col in columns])}")
        else:
            missing_tables.append(table_name)
            print(f"❌ 表 '{table_name}' 不存在")
        print()
    
    # 显示所有表
    print("-" * 80)
    print(f"📋 数据库中的所有表（共 {len(all_tables)} 个）:")
    for table in sorted(all_tables):
        marker = "✅" if table in existing_tables else "  "
        print(f"{marker} {table}")
    print()
    
    # 总结
    print("=" * 80)
    print("📊 检查结果总结:")
    print(f"  ✅ 存在的表: {len(existing_tables)}/{len(required_tables)}")
    print(f"  ❌ 缺失的表: {len(missing_tables)}/{len(required_tables)}")
    
    if missing_tables:
        print()
        print("⚠️  缺失的表:")
        for table in missing_tables:
            print(f"    - {table}")
        print()
        print("💡 提示: 运行数据库初始化可以创建缺失的表")
        print("   方法: 在应用中访问任意页面，系统会自动初始化数据库")
    else:
        print()
        print("🎉 所有必需的表都已存在！")
    
    print("=" * 80)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"❌ 执行出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

