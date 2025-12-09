#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化交易原因表 (trading_reasons)
创建表结构并迁移现有JSON数据到数据库
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from database.db import init_db, engine, Base, SessionLocal
    from models.trading_reason import TradingReason
    from services.trading_reason_service import TradingReasonService
    from sqlalchemy import inspect
    from utils.trading_reasons import get_trading_reasons as get_json_reasons, DEFAULT_REASONS
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

def migrate_json_to_db():
    """从JSON文件迁移数据到数据库"""
    db = SessionLocal()
    try:
        # 获取JSON中的交易原因
        json_reasons = get_json_reasons()
        
        if not json_reasons:
            json_reasons = DEFAULT_REASONS
        
        logger.info(f"从JSON文件读取到 {len(json_reasons)} 个交易原因")
        
        # 批量创建到数据库
        created_count = TradingReasonService.batch_create_reasons(db, json_reasons)
        
        if created_count > 0:
            logger.info(f"✅ 成功迁移 {created_count} 个交易原因到数据库")
        else:
            logger.info("✅ 所有交易原因已存在于数据库中")
        
        return created_count
    except Exception as e:
        logger.error(f"迁移数据时出错: {e}")
        db.rollback()
        return 0
    finally:
        db.close()

def main():
    """主函数"""
    print("=" * 80)
    print("🔧 初始化交易原因表 (trading_reasons)")
    print("=" * 80)
    print()
    
    try:
        # 导入所有模型，确保它们被注册
        from models.trading_reason import TradingReason
        from models.trading_review import TradingReview
        from models.sector_history import SectorHistory
        
        print("📋 已导入所有模型")
        print()
        
        # 检查表是否已存在
        if check_table_exists('trading_reasons'):
            print("✅ trading_reasons 表已存在")
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
        columns = inspector.get_columns('trading_reasons')
        
        print(f"✅ trading_reasons 表包含以下列:")
        for col in columns:
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            print(f"   - {col['name']}: {col['type']} {nullable}")
        
        # 检查索引
        print()
        print("🔍 检查索引...")
        indexes = inspector.get_indexes('trading_reasons')
        if indexes:
            print(f"✅ 找到 {len(indexes)} 个索引:")
            for idx in indexes:
                print(f"   - {idx['name']}: {', '.join(idx['column_names'])}")
        
        # 迁移JSON数据到数据库
        print()
        print("🔄 迁移JSON数据到数据库...")
        migrate_json_to_db()
        
        # 显示当前数据库中的交易原因
        print()
        print("📊 当前数据库中的交易原因:")
        db = SessionLocal()
        try:
            reasons = TradingReasonService.get_all_reasons(db)
            if reasons:
                for i, reason in enumerate(reasons, 1):
                    print(f"   {i}. {reason.reason} (ID: {reason.id}, 顺序: {reason.display_order})")
            else:
                print("   (无)")
        finally:
            db.close()
        
        print()
        print("=" * 80)
        print("✅ 交易原因表初始化完成！")
        print("=" * 80)
        print()
        print("💡 提示:")
        print("   - 表结构已创建/验证")
        print("   - JSON数据已迁移到数据库")
        print("   - 现在可以使用数据库存储交易原因")
        print("   - 可以通过交易日志页面管理交易原因")
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

