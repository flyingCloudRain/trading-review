#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出板块异动到Excel脚本
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.board_change_excel_export import export_board_changes_to_excel

def main():
    """导出板块异动"""
    try:
        print("正在获取板块异动数据...")
        excel_file = export_board_changes_to_excel()
        
        print(f"\n✓ 板块异动已成功导出到: {excel_file}")
        
        # 读取文件统计信息
        import pandas as pd
        df = pd.read_excel(excel_file, sheet_name='板块异动')
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

