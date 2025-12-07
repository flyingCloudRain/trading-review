#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从Excel文件导入板块信息到数据库
"""
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.db import SessionLocal
from models.sector_history import SectorHistory
from utils.time_utils import get_utc8_date

def import_sectors_from_excel(excel_file_path: str, target_date: str = None):
    """
    从Excel文件导入板块信息到数据库
    
    Args:
        excel_file_path: Excel文件路径
        target_date: 目标日期（格式：YYYY-MM-DD），如果不指定，从Excel中读取日期
    """
    print("=" * 60)
    print("📥 从Excel导入板块信息到数据库")
    print("=" * 60)
    
    excel_file = Path(excel_file_path)
    
    if not excel_file.exists():
        print(f"❌ 文件不存在: {excel_file_path}")
        return False
    
    print(f"📄 文件路径: {excel_file}")
    
    try:
        # 读取Excel文件
        print("⏳ 正在读取Excel文件...")
        df = pd.read_excel(excel_file)
        
        print(f"✅ 成功读取 {len(df)} 行数据")
        print(f"📋 列名: {list(df.columns)}")
        
        # 检查必要的列
        required_columns = ['板块', '涨跌幅(%)']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"❌ 缺少必要的列: {missing_columns}")
            return False
        
        # 确定日期
        if target_date:
            import_date = datetime.strptime(target_date, '%Y-%m-%d').date()
            print(f"📅 使用指定日期: {import_date}")
        elif '日期' in df.columns:
            # 从Excel中读取日期
            date_str = df['日期'].iloc[0] if len(df) > 0 else None
            if pd.notna(date_str):
                if isinstance(date_str, str):
                    import_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                else:
                    import_date = date_str.date() if hasattr(date_str, 'date') else pd.to_datetime(date_str).date()
                print(f"📅 从Excel读取日期: {import_date}")
            else:
                import_date = get_utc8_date()
                print(f"⚠️  Excel中日期为空，使用今日: {import_date}")
        else:
            import_date = get_utc8_date()
            print(f"⚠️  Excel中没有日期列，使用今日: {import_date}")
        
        # 映射列名（支持中英文）
        column_mapping = {
            '序号': 'index',
            'index': 'index',
            '板块': 'name',
            'name': 'name',
            '涨跌幅(%)': 'changePercent',
            'changePercent': 'changePercent',
            '总成交量(万手)': 'totalVolume',
            'totalVolume': 'totalVolume',
            '总成交额(亿元)': 'totalAmount',
            'totalAmount': 'totalAmount',
            '净流入(亿元)': 'netInflow',
            'netInflow': 'netInflow',
            '上涨家数': 'upCount',
            'upCount': 'upCount',
            '下跌家数': 'downCount',
            'downCount': 'downCount',
            '均价': 'avgPrice',
            'avgPrice': 'avgPrice',
            '领涨股': 'leadingStock',
            'leadingStock': 'leadingStock',
            '领涨股-最新价': 'leadingStockPrice',
            'leadingStockPrice': 'leadingStockPrice',
            '领涨股-涨跌幅(%)': 'leadingStockChangePercent',
            'leadingStockChangePercent': 'leadingStockChangePercent',
        }
        
        # 转换数据
        db = SessionLocal()
        try:
            # 检查该日期的数据是否已存在
            existing = db.query(SectorHistory).filter(SectorHistory.date == import_date).first()
            if existing:
                print(f"⚠️  {import_date} 的数据已存在，将删除旧数据...")
                deleted_count = db.query(SectorHistory).filter(SectorHistory.date == import_date).delete()
                print(f"🗑️  已删除 {deleted_count} 条旧数据")
            
            # 导入数据
            imported_count = 0
            for idx, row in df.iterrows():
                try:
                    # 获取字段值
                    index_val = int(row.get('序号', row.get('index', idx + 1)))
                    name_val = str(row.get('板块', row.get('name', '')))
                    change_percent_val = float(row.get('涨跌幅(%)', row.get('changePercent', 0)))
                    total_volume_val = float(row.get('总成交量(万手)', row.get('totalVolume', 0)))
                    total_amount_val = float(row.get('总成交额(亿元)', row.get('totalAmount', 0)))
                    net_inflow_val = float(row.get('净流入(亿元)', row.get('netInflow', 0)))
                    up_count_val = int(row.get('上涨家数', row.get('upCount', 0)))
                    down_count_val = int(row.get('下跌家数', row.get('downCount', 0)))
                    avg_price_val = float(row.get('均价', row.get('avgPrice', 0)))
                    leading_stock_val = str(row.get('领涨股', row.get('leadingStock', ''))) if pd.notna(row.get('领涨股', row.get('leadingStock', ''))) else None
                    leading_stock_price_val = float(row.get('领涨股-最新价', row.get('leadingStockPrice', 0))) if pd.notna(row.get('领涨股-最新价', row.get('leadingStockPrice', None))) else None
                    leading_stock_change_percent_val = float(row.get('领涨股-涨跌幅(%)', row.get('leadingStockChangePercent', 0))) if pd.notna(row.get('领涨股-涨跌幅(%)', row.get('leadingStockChangePercent', None))) else None
                    
                    # 创建记录
                    sector = SectorHistory(
                        date=import_date,
                        index=index_val,
                        name=name_val,
                        change_percent=change_percent_val,
                        total_volume=total_volume_val,
                        total_amount=total_amount_val,
                        net_inflow=net_inflow_val,
                        up_count=up_count_val,
                        down_count=down_count_val,
                        avg_price=avg_price_val,
                        leading_stock=leading_stock_val,
                        leading_stock_price=leading_stock_price_val,
                        leading_stock_change_percent=leading_stock_change_percent_val,
                    )
                    db.add(sector)
                    imported_count += 1
                except Exception as e:
                    print(f"⚠️  第 {idx + 1} 行导入失败: {str(e)}")
                    continue
            
            # 提交事务
            db.commit()
            print(f"\n✅ 成功导入 {imported_count} 条数据到数据库")
            print(f"📅 日期: {import_date}")
            
            # 显示部分数据预览
            print(f"\n📋 导入的数据预览（前5条）:")
            print("-" * 80)
            for i, row in df.head(5).iterrows():
                name = row.get('板块', row.get('name', ''))
                change = row.get('涨跌幅(%)', row.get('changePercent', 0))
                print(f"{i+1}. {name} - 涨跌幅: {change}%")
            print("-" * 80)
            
            return True
            
        except Exception as e:
            db.rollback()
            print(f"❌ 导入失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ 读取Excel文件失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法: python import_sectors_from_excel.py <Excel文件路径> [日期]")
        print("示例: python import_sectors_from_excel.py data/板块信息17.xlsx 2025-11-17")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    target_date = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = import_sectors_from_excel(excel_file, target_date)
    
    if success:
        print("\n🎉 数据导入成功！")
    else:
        print("\n❌ 数据导入失败！")

