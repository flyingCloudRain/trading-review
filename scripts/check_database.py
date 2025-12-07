#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库状态
"""
import sqlite3
import os
from pathlib import Path

db_path = Path('data/trading_review.db')

if db_path.exists():
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # 获取所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print('当前数据库表:')
    total_records = 0
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        total_records += count
        print(f'  - {table[0]}: {count:,} 条记录')
    
    print(f'\n总记录数: {total_records:,}')
    
    # 获取数据库大小
    size = db_path.stat().st_size
    print(f'数据库文件大小: {size / 1024:.2f} KB ({size / 1024 / 1024:.2f} MB)')
    
    conn.close()
else:
    print('数据库文件不存在')

