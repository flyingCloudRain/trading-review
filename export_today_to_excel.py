#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出今日板块信息和涨停股票数据到Excel
从数据库读取数据并导出
"""
import sys
from pathlib import Path
import pandas as pd

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.db import SessionLocal
from services.sector_history_service import SectorHistoryService
from services.zt_pool_history_service import ZtPoolHistoryService
from utils.time_utils import get_utc8_date, get_utc8_date_str

def export_sectors_to_excel(target_date=None):
    """导出板块信息到Excel"""
    print("=" * 60)
    print("📊 导出板块信息到Excel")
    print("=" * 60)
    
    try:
        db = SessionLocal()
        
        # 如果没有指定日期，使用今日；如果今日没有数据，使用最新日期
        if target_date is None:
            today = get_utc8_date()
            sectors = SectorHistoryService.get_sectors_by_date(db, today)
            
            if not sectors:
                # 获取所有日期，使用最新日期
                dates = SectorHistoryService.get_all_dates(db)
                if dates:
                    target_date = dates[0]
                    print(f"⚠️  {today} 没有板块数据，使用最新日期: {target_date}")
                else:
                    print(f"⚠️  数据库中没有板块数据")
                    db.close()
                    return None
            else:
                target_date = today
        else:
            sectors = SectorHistoryService.get_sectors_by_date(db, target_date)
        
        # 从数据库获取板块数据
        print(f"⏳ 正在从数据库获取 {target_date} 的板块数据...")
        if not sectors:
            sectors = SectorHistoryService.get_sectors_by_date(db, target_date)
        
        if not sectors:
            print(f"⚠️  {target_date} 没有板块数据")
            db.close()
            return None
        
        print(f"✅ 成功获取 {len(sectors)} 条板块数据")
        
        # 转换为DataFrame
        df = pd.DataFrame(sectors)
        
        # 重命名列名为中文
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
            'date': '日期'
        })
        
        # 重新排列列的顺序
        column_order = ['序号', '板块', '日期', '涨跌幅(%)', '总成交量(万手)', 
                       '总成交额(亿元)', '净流入(亿元)', '上涨家数', '下跌家数', 
                       '均价', '领涨股', '领涨股-最新价', '领涨股-涨跌幅(%)']
        # 只保留存在的列
        column_order = [col for col in column_order if col in df_export.columns]
        df_export = df_export[column_order]
        
        # 保存到Excel
        excel_file = Path('data/板块信息历史.xlsx')
        excel_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 如果文件存在，读取现有数据并追加
        if excel_file.exists():
            try:
                existing_df = pd.read_excel(excel_file, sheet_name='板块信息')
                # 检查今天的数据是否已存在
                today_str = today.strftime('%Y-%m-%d')
                if today_str in existing_df['日期'].values:
                    # 如果今天的数据已存在，先删除
                    existing_df = existing_df[existing_df['日期'] != today_str]
                # 合并数据
                combined_df = pd.concat([existing_df, df_export], ignore_index=True)
                # 按日期排序
                combined_df = combined_df.sort_values('日期', ascending=False)
            except Exception as e:
                print(f"⚠️  读取现有Excel文件失败，将创建新文件: {str(e)}")
                combined_df = df_export
        else:
            combined_df = df_export
        
        # 写入Excel文件
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            combined_df.to_excel(writer, sheet_name='板块信息', index=False)
        
        print(f"✅ 成功导出到: {excel_file}")
        print(f"   共 {len(combined_df)} 条数据（包含历史数据）")
        
        db.close()
        return str(excel_file)
        
    except Exception as e:
        print(f"❌ 导出板块信息失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def export_zt_pool_to_excel():
    """导出涨停股票池到Excel"""
    print("\n" + "=" * 60)
    print("📈 导出涨停股票池到Excel")
    print("=" * 60)
    
    try:
        db = SessionLocal()
        today = get_utc8_date()
        
        # 从数据库获取今日涨停股票数据
        print(f"⏳ 正在从数据库获取 {today} 的涨停股票数据...")
        stocks = ZtPoolHistoryService.get_zt_pool_by_date(db, today)
        
        if not stocks:
            print(f"⚠️  {today} 没有涨停股票数据")
            db.close()
            return None
        
        print(f"✅ 成功获取 {len(stocks)} 条涨停股票数据")
        
        # 转换为DataFrame
        df = pd.DataFrame(stocks)
        
        # 重命名列名为中文
        df_export = df.rename(columns={
            'index': '序号',
            'code': '代码',
            'name': '名称',
            'changePercent': '涨跌幅(%)',
            'latestPrice': '最新价',
            'turnover': '成交额(亿元)',
            'circulatingMarketValue': '流通市值(亿元)',
            'totalMarketValue': '总市值(亿元)',
            'turnoverRate': '换手率(%)',
            'sealingFunds': '封板资金(亿元)',
            'firstSealingTime': '首次封板时间',
            'lastSealingTime': '最后封板时间',
            'explosionCount': '炸板次数',
            'ztStatistics': '涨停统计',
            'continuousBoards': '连板数',
            'industry': '所属行业',
            'date': '日期'
        })
        
        # 重新排列列的顺序
        column_order = ['序号', '代码', '名称', '日期', '涨跌幅(%)', '最新价', 
                       '成交额(亿元)', '流通市值(亿元)', '总市值(亿元)', '换手率(%)', 
                       '封板资金(亿元)', '首次封板时间', '最后封板时间', '炸板次数', 
                       '涨停统计', '连板数', '所属行业']
        # 只保留存在的列
        column_order = [col for col in column_order if col in df_export.columns]
        df_export = df_export[column_order]
        
        # 保存到Excel
        excel_file = Path('data/涨停股票池.xlsx')
        excel_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 如果文件存在，读取现有数据并追加
        if excel_file.exists():
            try:
                existing_df = pd.read_excel(excel_file, sheet_name='涨停股票')
                # 检查今天的数据是否已存在
                today_str = today.strftime('%Y-%m-%d')
                if today_str in existing_df['日期'].values:
                    # 如果今天的数据已存在，先删除
                    existing_df = existing_df[existing_df['日期'] != today_str]
                # 合并数据
                combined_df = pd.concat([existing_df, df_export], ignore_index=True)
                # 按日期排序
                combined_df = combined_df.sort_values('日期', ascending=False)
            except Exception as e:
                print(f"⚠️  读取现有Excel文件失败，将创建新文件: {str(e)}")
                combined_df = df_export
        else:
            combined_df = df_export
        
        # 写入Excel文件
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            combined_df.to_excel(writer, sheet_name='涨停股票', index=False)
        
        print(f"✅ 成功导出到: {excel_file}")
        print(f"   共 {len(combined_df)} 条数据（包含历史数据）")
        
        # 显示统计信息
        print(f"\n📊 今日涨停股票统计:")
        print(f"   股票数量: {len(df_export)}")
        if '涨跌幅(%)' in df_export.columns:
            print(f"   平均涨跌幅: {df_export['涨跌幅(%)'].mean():.2f}%")
        if '成交额(亿元)' in df_export.columns:
            print(f"   总成交额: {df_export['成交额(亿元)'].sum():.2f} 亿元")
        if '连板数' in df_export.columns:
            print(f"   平均连板数: {df_export['连板数'].mean():.2f}")
            print(f"   最大连板数: {df_export['连板数'].max()}")
        
        db.close()
        return str(excel_file)
        
    except Exception as e:
        print(f"❌ 导出涨停股票池失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🚀 开始导出今日数据到Excel")
    print("=" * 60)
    print(f"📅 日期: {get_utc8_date_str()}")
    print("=" * 60)
    
    # 导出板块信息
    sector_file = export_sectors_to_excel()
    
    # 导出涨停股票池
    zt_file = export_zt_pool_to_excel()
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 导出总结")
    print("=" * 60)
    if sector_file:
        print(f"✅ 板块信息: {sector_file}")
    else:
        print("❌ 板块信息: 导出失败")
    
    if zt_file:
        print(f"✅ 涨停股票: {zt_file}")
    else:
        print("❌ 涨停股票: 导出失败")
    print("=" * 60)
    
    if sector_file and zt_file:
        print("\n🎉 所有数据导出成功！")
    else:
        print("\n⚠️  部分数据导出失败，请检查错误信息")

if __name__ == '__main__':
    main()

