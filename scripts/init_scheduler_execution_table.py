#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动初始化 scheduler_execution 表
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.db import init_db, engine, Base
from models.scheduler_execution import SchedulerExecution

def main():
    """主函数"""
    print("=" * 80)
    print("🔧 初始化 scheduler_execution 表")
    print("=" * 80)
    print()
    
    try:
        # 导入所有模型，确保它们被注册
        from models.trading_review import TradingReview
        from models.sector_history import SectorHistory
        from models.zt_pool_history import ZtPoolHistory
        from models.zb_pool_history import ZbgcPoolHistory
        from models.dt_pool_history import DtgcPoolHistory
        from models.index_history import IndexHistory
        from models.scheduler_execution import SchedulerExecution
        
        print("📋 已导入所有模型:")
        print("  - TradingReview")
        print("  - SectorHistory")
        print("  - ZtPoolHistory")
        print("  - ZbgcPoolHistory")
        print("  - DtgcPoolHistory")
        print("  - IndexHistory")
        print("  - SchedulerExecution")
        print()
        
        # 创建所有表
        print("🔨 正在创建表...")
        Base.metadata.create_all(bind=engine)
        print("✅ 表创建完成")
        print()
        
        # 验证表是否创建成功
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if 'scheduler_execution' in tables:
            print("✅ scheduler_execution 表已成功创建")
            
            # 显示表的列信息
            columns = inspector.get_columns('scheduler_execution')
            print(f"   列数: {len(columns)}")
            print("   列名:")
            for col in columns:
                print(f"     - {col['name']} ({col['type']})")
        else:
            print("❌ scheduler_execution 表创建失败")
        
        print()
        print("=" * 80)
        print("🎉 初始化完成！")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ 初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

