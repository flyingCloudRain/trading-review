#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
板块异动Excel导出工具
"""
import pandas as pd
from pathlib import Path
from utils.time_utils import get_utc8_now, get_utc8_date_str, get_utc8_time_str
from services.board_change_service import BoardChangeService
import json

EXCEL_FILE_PATH = Path('data/板块异动.xlsx')
SHEET_NAME = '板块异动'

def export_board_changes_to_excel() -> str:
    """
    导出板块异动到Excel文件
    :return: Excel文件路径
    """
    try:
        # 获取板块异动数据
        boards = BoardChangeService.get_board_changes()
        
        if not boards:
            raise Exception('未获取到板块异动数据')
        
        # 转换为DataFrame
        df = pd.DataFrame(boards)
        
        # 添加日期和时间列 - 使用UTC+8时区
        date_str = get_utc8_date_str()
        time_str = get_utc8_time_str()
        
        df['date'] = date_str
        df['time'] = time_str
        
        # 将异动类型列表转换为字符串（便于Excel显示）
        df['changeTypesStr'] = df['changeTypes'].apply(
            lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, (list, dict)) else str(x)
        )
        
        # 重命名列名为中文（更易读）
        df_export = df.rename(columns={
            'name': '板块名称',
            'changePercent': '涨跌幅(%)',
            'netInflow': '主力净流入(亿元)',
            'totalChangeCount': '板块异动总次数',
            'mostFrequentStockCode': '最频繁个股代码',
            'mostFrequentStockName': '最频繁个股名称',
            'mostFrequentDirection': '买卖方向',
            'changeTypesStr': '异动类型列表',
            'date': '日期',
            'time': '时间'
        })
        
        # 重新排列列的顺序，将日期和时间放在前面
        column_order = ['板块名称', '日期', '时间', '涨跌幅(%)', '主力净流入(亿元)', 
                       '板块异动总次数', '最频繁个股代码', '最频繁个股名称', '买卖方向', '异动类型列表']
        df_export = df_export[column_order]
        
        # 确保输出目录存在
        EXCEL_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # 如果文件存在，读取现有数据并追加
        if EXCEL_FILE_PATH.exists():
            try:
                # 读取现有数据
                existing_df = pd.read_excel(EXCEL_FILE_PATH, sheet_name=SHEET_NAME)
                
                # 检查今天的数据是否已存在
                if date_str in existing_df['日期'].values:
                    # 如果今天的数据已存在，先删除
                    existing_df = existing_df[existing_df['日期'] != date_str]
                
                # 合并数据
                combined_df = pd.concat([existing_df, df_export], ignore_index=True)
                
                # 按日期和时间排序
                combined_df = combined_df.sort_values(['日期', '时间'], ascending=[False, False])
                
            except Exception as e:
                # 如果读取失败，使用新数据
                print(f"读取现有Excel文件失败，将创建新文件: {str(e)}")
                combined_df = df_export
        else:
            # 文件不存在，使用新数据
            combined_df = df_export
        
        # 写入Excel文件
        with pd.ExcelWriter(EXCEL_FILE_PATH, engine='openpyxl') as writer:
            combined_df.to_excel(writer, sheet_name=SHEET_NAME, index=False)
        
        return str(EXCEL_FILE_PATH)
        
    except Exception as e:
        raise Exception(f"导出Excel失败: {str(e)}")

