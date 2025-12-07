#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel导出工具
"""
import pandas as pd
from pathlib import Path
from utils.time_utils import get_utc8_now, get_utc8_date_str, get_utc8_time_str
from services.sector_service import SectorService

EXCEL_FILE_PATH = Path('data/板块信息历史.xlsx')
SHEET_NAME = '板块信息'

def append_sectors_to_excel() -> str:
    """
    追加板块数据到Excel文件
    如果文件不存在则创建，如果存在则追加到同一个sheet
    """
    try:
        # 获取当前板块数据
        sectors = SectorService.get_industry_summary()
        
        # 转换为DataFrame
        df = pd.DataFrame(sectors)
        
        # 添加日期和时间列（分开）- 使用UTC+8时区
        current_time = get_utc8_now()
        df['date'] = get_utc8_date_str()
        df['time'] = get_utc8_time_str()
        
        # 重命名列名为中文（更易读）
        df_export = df.rename(columns={
            'index': '序号',
            'name': '板块',
            'changePercent': '涨跌幅(%)',
            'totalVolume': '总成交量(万手)',
            'totalAmount': '总成交额(亿元)',
            'netInflow': '净流入(亿元)',
            'upCount': '上涨家数',
            'downCount': '下跌家数',
            'avgPrice': '均价',
            'leadingStock': '领涨股',
            'leadingStockPrice': '领涨股-最新价',
            'leadingStockChangePercent': '领涨股-涨跌幅(%)',
            'date': '日期',
            'time': '时间'
        })
        
        # 重新排列列的顺序，将日期和时间放在前面
        column_order = ['序号', '板块', '日期', '时间', '涨跌幅(%)', '总成交量(万手)', 
                       '总成交额(亿元)', '净流入(亿元)', '上涨家数', '下跌家数', 
                       '均价', '领涨股', '领涨股-最新价', '领涨股-涨跌幅(%)']
        df_export = df_export[column_order]
        
        # 确保输出目录存在
        EXCEL_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # 如果文件存在，读取现有数据并追加
        if EXCEL_FILE_PATH.exists():
            try:
                # 读取现有数据
                existing_df = pd.read_excel(EXCEL_FILE_PATH, sheet_name=SHEET_NAME)
                
                # 检查今天的数据是否已存在
                today = get_utc8_date_str()
                if today in existing_df['日期'].values:
                    # 如果今天的数据已存在，先删除
                    existing_df = existing_df[existing_df['日期'] != today]
                
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

