#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出炸板股票池到Excel脚本
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.zbgc_excel_export import export_zbgc_to_excel
from datetime import datetime
import argparse

def main():
    """导出炸板股票池"""
    parser = argparse.ArgumentParser(description='导出炸板股票池到Excel')
    parser.add_argument('-d', '--date', type=str, help='交易日，格式：YYYYMMDD，默认为今日')
    args = parser.parse_args()
    
    try:
        print("正在获取炸板股票池数据...")
        excel_file = export_zbgc_to_excel(date=args.date)
        
        print(f"\n✓ 炸板股票池已成功导出到: {excel_file}")
        
        # 读取文件统计信息
        import pandas as pd
        df = pd.read_excel(excel_file, sheet_name='炸板股票')
        print(f"  - 当前文件总记录数: {len(df)}")
        if len(df) > 0:
            print(f"  - 最新日期: {df['日期'].max()}")
            print(f"  - 最新记录数: {len(df[df['日期'] == df['日期'].max()])}")
        
    except Exception as e:
        print(f"✗ 导出失败: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

