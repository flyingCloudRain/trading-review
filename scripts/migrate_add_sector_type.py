#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本：为 sector_history 表添加 sector_type 列
将现有数据标记为行业板块（industry）
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

def migrate_add_sector_type():
    """为 sector_history 表添加 sector_type 列"""
    db = SessionLocal()
    try:
        logger.info("开始数据库迁移：添加 sector_type 列...")
        
        # 检查列是否已存在
        check_sql = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'sector_history' 
            AND column_name = 'sector_type'
        """)
        result = db.execute(check_sql).fetchone()
        
        if result:
            logger.info("✅ sector_type 列已存在，跳过迁移")
            return True
        
        # 添加 sector_type 列，默认值为 'industry'
        logger.info("正在添加 sector_type 列...")
        alter_sql = text("""
            ALTER TABLE sector_history 
            ADD COLUMN sector_type VARCHAR(20) NOT NULL DEFAULT 'industry'
        """)
        db.execute(alter_sql)
        db.commit()
        logger.info("✅ 成功添加 sector_type 列")
        
        # 更新现有数据，确保所有记录都是 'industry'
        logger.info("正在更新现有数据...")
        update_sql = text("""
            UPDATE sector_history 
            SET sector_type = 'industry' 
            WHERE sector_type IS NULL OR sector_type = ''
        """)
        db.execute(update_sql)
        db.commit()
        logger.info("✅ 成功更新现有数据为行业板块")
        
        # 创建索引（如果不存在）
        logger.info("正在创建索引...")
        try:
            index_sql = text("""
                CREATE INDEX IF NOT EXISTS idx_sector_history_sector_type 
                ON sector_history(sector_type)
            """)
            db.execute(index_sql)
            db.commit()
            logger.info("✅ 成功创建索引")
        except Exception as e:
            logger.warning(f"创建索引时出现警告（可能已存在）: {e}")
        
        logger.info("🎉 数据库迁移完成！")
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ 数据库迁移失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == '__main__':
    print("=" * 60)
    print("数据库迁移：添加 sector_type 列")
    print("=" * 60)
    
    success = migrate_add_sector_type()
    
    if success:
        print("\n✅ 迁移成功完成！")
        print("现在可以正常使用行业板块和概念板块功能了。")
    else:
        print("\n❌ 迁移失败，请检查错误信息。")
        sys.exit(1)

