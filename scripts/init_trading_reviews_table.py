#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化交易日志表 (trading_reviews)
创建表结构并添加必要的索引
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from database.db import init_db, engine, Base, SessionLocal
    from models.trading_review import TradingReview
    from sqlalchemy import inspect, text
    import logging
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    print()
    print("💡 请确保:")
    print("   1. 已安装所有依赖: pip install -r requirements.txt")
    print("   2. 已配置数据库连接（Supabase或SQLite）")
    print("   3. 环境变量或配置文件已正确设置")
    print()
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_table_exists(table_name: str) -> bool:
    """检查表是否存在"""
    try:
        inspector = inspect(engine)
        return table_name in inspector.get_table_names()
    except Exception as e:
        logger.error(f"检查表是否存在时出错: {e}")
        return False

def check_column_exists(table_name: str, column_name: str) -> bool:
    """检查列是否存在"""
    try:
        db = SessionLocal()
        try:
            check_sql = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = :table_name 
                AND column_name = :column_name
            """)
            result = db.execute(check_sql, {'table_name': table_name, 'column_name': column_name}).fetchone()
            return result is not None
        finally:
            db.close()
    except Exception as e:
        logger.error(f"检查列是否存在时出错: {e}")
        return False

def add_missing_columns():
    """添加缺失的列（止盈止损）"""
    db = SessionLocal()
    try:
        # 检查并添加 take_profit_price 列
        if not check_column_exists('trading_reviews', 'take_profit_price'):
            logger.info("正在添加 take_profit_price 列...")
            alter_sql = text("""
                ALTER TABLE trading_reviews 
                ADD COLUMN take_profit_price DECIMAL(10, 2)
            """)
            db.execute(alter_sql)
            db.commit()
            logger.info("✅ 成功添加 take_profit_price 列")
        else:
            logger.info("✅ take_profit_price 列已存在")
        
        # 检查并添加 stop_loss_price 列
        if not check_column_exists('trading_reviews', 'stop_loss_price'):
            logger.info("正在添加 stop_loss_price 列...")
            alter_sql = text("""
                ALTER TABLE trading_reviews 
                ADD COLUMN stop_loss_price DECIMAL(10, 2)
            """)
            db.execute(alter_sql)
            db.commit()
            logger.info("✅ 成功添加 stop_loss_price 列")
        else:
            logger.info("✅ stop_loss_price 列已存在")
    except Exception as e:
        logger.error(f"添加列时出错: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """主函数"""
    print("=" * 80)
    print("🔧 初始化交易日志表 (trading_reviews)")
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
        
        print("📋 已导入所有模型")
        print()
        
        # 检查表是否已存在
        if check_table_exists('trading_reviews'):
            print("✅ trading_reviews 表已存在")
            print()
            
            # 检查并添加缺失的列
            print("🔍 检查列结构...")
            add_missing_columns()
            print()
        else:
            # 创建所有表
            print("🔨 正在创建表...")
            Base.metadata.create_all(bind=engine)
            print("✅ 表创建完成")
            print()
        
        # 验证表结构
        print("🔍 验证表结构...")
        inspector = inspect(engine)
        columns = inspector.get_columns('trading_reviews')
        
        print(f"✅ trading_reviews 表包含以下列:")
        for col in columns:
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            print(f"   - {col['name']}: {col['type']} {nullable}")
        
        # 检查索引
        print()
        print("🔍 检查索引...")
        indexes = inspector.get_indexes('trading_reviews')
        if indexes:
            print(f"✅ 找到 {len(indexes)} 个索引:")
            for idx in indexes:
                print(f"   - {idx['name']}: {', '.join(idx['column_names'])}")
        else:
            print("⚠️  未找到索引，建议手动创建索引以提高查询性能")
        
        print()
        print("=" * 80)
        print("✅ 交易日志表初始化完成！")
        print("=" * 80)
        print()
        print("💡 提示:")
        print("   - 表结构已创建/更新")
        print("   - 如果使用 Supabase，建议在 Supabase Dashboard 中查看表结构")
        print("   - 可以通过交易日志页面添加交易记录")
        print()
        
    except Exception as e:
        print()
        print("=" * 80)
        print(f"❌ 初始化失败: {str(e)}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

