#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本：为 trading_reviews 表添加止盈价和止损价字段
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from database.db import SessionLocal, engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_add_take_profit_stop_loss():
    """为 trading_reviews 表添加止盈价和止损价字段"""
    db = SessionLocal()
    try:
        logger.info("开始数据库迁移：添加止盈价和止损价字段...")
        
        # 检查列是否已存在
        check_sql = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'trading_reviews' 
            AND column_name IN ('take_profit_price', 'stop_loss_price')
        """)
        result = db.execute(check_sql).fetchall()
        existing_columns = [row[0] for row in result]
        
        # 添加 take_profit_price 列（如果不存在）
        if 'take_profit_price' not in existing_columns:
            logger.info("正在添加 take_profit_price 列...")
            alter_sql = text("""
                ALTER TABLE trading_reviews 
                ADD COLUMN take_profit_price DECIMAL(10, 2)
            """)
            db.execute(alter_sql)
            db.commit()
            logger.info("✅ 成功添加 take_profit_price 列")
        else:
            logger.info("✅ take_profit_price 列已存在，跳过")
        
        # 添加 stop_loss_price 列（如果不存在）
        if 'stop_loss_price' not in existing_columns:
            logger.info("正在添加 stop_loss_price 列...")
            alter_sql = text("""
                ALTER TABLE trading_reviews 
                ADD COLUMN stop_loss_price DECIMAL(10, 2)
            """)
            db.execute(alter_sql)
            db.commit()
            logger.info("✅ 成功添加 stop_loss_price 列")
        else:
            logger.info("✅ stop_loss_price 列已存在，跳过")
        
        logger.info("✅ 数据库迁移完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据库迁移失败: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == '__main__':
    success = migrate_add_take_profit_stop_loss()
    sys.exit(0 if success else 1)

