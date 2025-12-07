#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
炸板股票池Excel导出工具
"""
import pandas as pd
from pathlib import Path
from utils.time_utils import get_utc8_now, get_utc8_date_str, get_utc8_time_str, get_data_date
from services.zbgc_service import ZbgcService

EXCEL_FILE_PATH = Path('data/炸板股票池.xlsx')
SHEET_NAME = '炸板股票'

def export_zbgc_to_excel(date: str = None) -> str:
    """
    导出炸板股票池到Excel文件
    :param date: 交易日，格式：YYYYMMDD，默认为今日
    :return: Excel文件路径
    """
    try:
        # 获取炸板股票数据
        stocks = ZbgcService.get_zbgc_pool(date=date)
        
        if not stocks:
            raise Exception('未获取到炸板股票数据')
        
        # 转换为DataFrame
        df = pd.DataFrame(stocks)
        
        # 添加日期和时间列 - 使用正确的数据日期
        current_time = get_utc8_now()
        if date:
            # 如果指定了日期，使用指定日期
            date_str = f"{date[:4]}-{date[4:6]}-{date[6:8]}"
        else:
            # 使用 get_data_date() 自动判断正确的数据日期
            data_date = get_data_date()
            date_str = data_date.strftime('%Y-%m-%d')
        
        df['date'] = date_str
        df['time'] = get_utc8_time_str()
        
        # 重命名列名为中文（更易读）
        df_export = df.rename(columns={
            'index': '序号',
            'code': '代码',
            'name': '名称',
            'changePercent': '涨跌幅(%)',
            'latestPrice': '最新价',
            'limitPrice': '涨停价',
            'turnover': '成交额(亿元)',
            'circulatingMarketValue': '流通市值(亿元)',
            'totalMarketValue': '总市值(亿元)',
            'turnoverRate': '换手率(%)',
            'riseSpeed': '涨速',
            'firstSealingTime': '首次封板时间',
            'explosionCount': '炸板次数',
            'ztStatistics': '涨停统计',
            'amplitude': '振幅(%)',
            'industry': '所属行业',
            'date': '日期',
            'time': '时间'
        })
        
        # 重新排列列的顺序，将日期和时间放在前面
        column_order = ['序号', '代码', '名称', '日期', '时间', '涨跌幅(%)', '最新价', '涨停价',
                       '成交额(亿元)', '流通市值(亿元)', '总市值(亿元)', '换手率(%)', '涨速',
                       '首次封板时间', '炸板次数', '涨停统计', '振幅(%)', '所属行业']
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

