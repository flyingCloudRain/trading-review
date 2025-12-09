#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动初始化 stock_fund_flow_history 表
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.db import init_db, engine, Base
from models.stock_fund_flow_history import StockFundFlowHistory
from sqlalchemy import inspect

def check_table_exists(table_name: str) -> bool:
    """检查表是否存在"""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        return table_name in tables
    except Exception as e:
        print(f"❌ 检查表时出错: {e}")
        return False

def main():
    """主函数"""
    print("=" * 80)
    print("🔧 初始化 stock_fund_flow_history 表")
    print("=" * 80)
    print()
    
    try:
        # 导入所有模型，确保它们被注册
        from models.trading_review import TradingReview
        from models.trading_reason import TradingReason
        from models.sector_history import SectorHistory
        from models.zt_pool_history import ZtPoolHistory
        from models.zb_pool_history import ZbgcPoolHistory
        from models.dt_pool_history import DtgcPoolHistory
        from models.index_history import IndexHistory
        from models.scheduler_execution import SchedulerExecution
        from models.stock_fund_flow_history import StockFundFlowHistory
        
        print("📋 已导入所有模型:")
        print("  - TradingReview")
        print("  - TradingReason")
        print("  - SectorHistory")
        print("  - ZtPoolHistory")
        print("  - ZbgcPoolHistory")
        print("  - DtgcPoolHistory")
        print("  - IndexHistory")
        print("  - SchedulerExecution")
        print("  - StockFundFlowHistory")
        print()
        
        # 检查表是否已存在
        table_name = 'stock_fund_flow_history'
        if check_table_exists(table_name):
            print(f"✅ {table_name} 表已存在")
            print()
        else:
            # 创建所有表
            print("🔨 正在创建表...")
            Base.metadata.create_all(bind=engine)
            print(f"✅ {table_name} 表创建完成")
            print()
        
        # 验证表是否创建成功
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if table_name in tables:
            print(f"✅ 验证成功: {table_name} 表已存在")
            print()
            
            # 显示表结构
            print("🔍 表结构:")
            columns = inspector.get_columns(table_name)
            for col in columns:
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                print(f"   - {col['name']}: {col['type']} {nullable}")
            
            print()
            print("🔍 检查索引...")
            indexes = inspector.get_indexes(table_name)
            if indexes:
                print(f"✅ 找到 {len(indexes)} 个索引:")
                for idx in indexes:
                    print(f"   - {idx['name']}: {', '.join(idx['column_names'])}")
            else:
                print("⚠️  未找到索引（可能需要手动创建）")
        else:
            print(f"❌ 验证失败: {table_name} 表不存在")
            return 1
        
        print()
        print("=" * 80)
        print("✅ 初始化完成")
        print("=" * 80)
        return 0
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit(main())

