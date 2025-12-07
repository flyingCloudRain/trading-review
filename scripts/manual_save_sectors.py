#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动保存板块数据脚本（用于测试或手动触发）
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.db import SessionLocal, init_db
from services.sector_history_service import SectorHistoryService
from utils.excel_export import append_sectors_to_excel

def main():
    """手动保存板块数据"""
    try:
        # 初始化数据库
        init_db()
        
        # 获取数据库会话
        db = SessionLocal()
        try:
            # 保存到数据库
            print("正在保存板块数据到数据库...")
            saved_count = SectorHistoryService.save_today_sectors(db)
            print(f"✓ 成功保存 {saved_count} 条板块数据到数据库")
            
            # 追加到Excel文件
            print("正在追加板块数据到Excel文件...")
            excel_file = append_sectors_to_excel()
            print(f"✓ 成功追加板块数据到Excel文件: {excel_file}")
            
        except Exception as e:
            print(f"✗ 保存失败: {str(e)}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            sys.exit(1)
        finally:
            db.close()
            
    except Exception as e:
        print(f"✗ 执行失败: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

