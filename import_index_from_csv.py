#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从CSV文件导入指数信息到数据库
"""
import sys
import pandas as pd
from pathlib import Path
from datetime import date

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.db import SessionLocal
from models.index_history import IndexHistory

def import_index_from_csv(csv_file: str, target_date: date):
    """
    从CSV文件导入指数信息到数据库
    
    Args:
        csv_file: CSV文件路径
        target_date: 目标日期
    """
    print("=" * 60)
    print("📊 导入指数信息到数据库")
    print("=" * 60)
    print(f"📄 CSV文件: {csv_file}")
    print(f"📅 目标日期: {target_date}")
    print("=" * 60)
    
    # 读取CSV文件
    try:
        df = pd.read_csv(csv_file, encoding='utf-8-sig')
        print(f"\n✅ 成功读取CSV文件，共 {len(df)} 条记录")
        print(f"📋 列名: {list(df.columns)}")
    except Exception as e:
        print(f"❌ 读取CSV文件失败: {str(e)}")
        return False
    
    # 列名映射：中文列名 -> 数据库字段名
    column_mapping = {
        '代码': 'code',
        '名称': 'name',
        '最新价': 'current_price',
        '涨跌幅(%)': 'change_percent',
        '涨跌额': 'change',
        '成交量': 'volume',
        '成交额': 'amount',
        '今开': 'open',
        '最高': 'high',
        '最低': 'low',
        '昨收': 'prev_close',
        '振幅(%)': 'amplitude',
        '量比': 'volume_ratio'
    }
    
    # 检查必需的列是否存在
    missing_columns = [col for col in column_mapping.keys() if col not in df.columns]
    if missing_columns:
        print(f"❌ CSV文件缺少必需的列: {missing_columns}")
        return False
    
    # 获取数据库会话
    db = SessionLocal()
    try:
        # 检查该日期的数据是否已存在
        existing_count = db.query(IndexHistory).filter(IndexHistory.date == target_date).count()
        if existing_count > 0:
            print(f"\n⚠️  日期 {target_date} 已存在 {existing_count} 条数据")
            response = input("是否删除旧数据并重新导入？(y/n): ").strip().lower()
            if response == 'y':
                deleted_count = db.query(IndexHistory).filter(IndexHistory.date == target_date).delete()
                db.commit()
                print(f"🗑️  已删除 {deleted_count} 条旧数据")
            else:
                print("❌ 取消导入")
                return False
        
        # 导入数据
        saved_count = 0
        error_count = 0
        
        print(f"\n⏳ 正在导入数据...")
        for idx, row in df.iterrows():
            try:
                # 处理数据：确保数值类型正确
                index_data = IndexHistory(
                    date=target_date,
                    code=str(row['代码']).strip(),
                    name=str(row['名称']).strip(),
                    current_price=float(row['最新价']) if pd.notna(row['最新价']) else 0.0,
                    change_percent=float(row['涨跌幅(%)']) if pd.notna(row['涨跌幅(%)']) else 0.0,
                    change=float(row['涨跌额']) if pd.notna(row['涨跌额']) else 0.0,
                    volume=float(row['成交量']) if pd.notna(row['成交量']) else 0.0,
                    amount=float(row['成交额']) if pd.notna(row['成交额']) else 0.0,
                    open=float(row['今开']) if pd.notna(row['今开']) else 0.0,
                    high=float(row['最高']) if pd.notna(row['最高']) else 0.0,
                    low=float(row['最低']) if pd.notna(row['最低']) else 0.0,
                    prev_close=float(row['昨收']) if pd.notna(row['昨收']) else 0.0,
                    amplitude=float(row['振幅(%)']) if pd.notna(row['振幅(%)']) else 0.0,
                    volume_ratio=float(row['量比']) if pd.notna(row['量比']) else 0.0,
                )
                db.add(index_data)
                saved_count += 1
                
                if (saved_count + error_count) % 50 == 0:
                    print(f"  已处理 {saved_count + error_count}/{len(df)} 条...")
                    
            except Exception as e:
                error_count += 1
                print(f"  ⚠️  第 {idx + 1} 行数据导入失败: {str(e)}")
                continue
        
        # 提交事务
        db.commit()
        
        print(f"\n✅ 导入完成！")
        print(f"  成功导入: {saved_count} 条")
        if error_count > 0:
            print(f"  失败: {error_count} 条")
        
        # 验证导入的数据
        verify_count = db.query(IndexHistory).filter(IndexHistory.date == target_date).count()
        print(f"  数据库验证: {verify_count} 条数据")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ 导入失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def main():
    """主函数"""
    csv_file = 'data/指数信息.csv'
    target_date = date(2025, 11, 18)
    
    # 检查文件是否存在
    if not Path(csv_file).exists():
        print(f"❌ 文件不存在: {csv_file}")
        return
    
    # 执行导入
    success = import_index_from_csv(csv_file, target_date)
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 导入成功！")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ 导入失败")
        print("=" * 60)

if __name__ == '__main__':
    main()

