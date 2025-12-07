#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 stock_individual_fund_flow 接口
分析个股资金流接口
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import akshare as ak
import pandas as pd
from datetime import datetime

def test_stock_individual_fund_flow():
    """测试 stock_individual_fund_flow 接口"""
    print("=" * 80)
    print("🔍 分析 stock_individual_fund_flow 接口（个股资金流）")
    print("=" * 80)
    
    # 测试股票代码（深圳A股和上海A股各一个）
    test_codes = [
        "000001",  # 平安银行（深圳）
        "600000",  # 浦发银行（上海）
        "300001",  # 特锐德（创业板）
    ]
    
    for stock_code in test_codes:
        print(f"\n{'=' * 80}")
        print(f"📊 测试股票代码: {stock_code}")
        print(f"{'=' * 80}")
        
        try:
            # 调用接口
            print(f"\n🔄 调用 stock_individual_fund_flow('{stock_code}')...")
            start_time = datetime.now()
            df = ak.stock_individual_fund_flow(stock=stock_code)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print(f"✅ 成功获取数据，耗时: {duration:.2f} 秒")
            print(f"📈 数据形状: {df.shape}")
            
            if df.empty:
                print("⚠️ 返回数据为空")
                continue
            
            # 显示列名
            print(f"\n📋 数据列名 ({len(df.columns)} 列):")
            print("-" * 80)
            for i, col in enumerate(df.columns, 1):
                print(f"  {i:2d}. {col}")
            
            # 显示数据类型
            print(f"\n📊 数据类型:")
            print("-" * 80)
            print(df.dtypes)
            
            # 显示前几条数据示例
            print(f"\n📝 数据示例（前10条）:")
            print("-" * 80)
            print(df.head(10).to_string())
            
            # 分析数据结构
            print(f"\n🔍 数据结构分析:")
            print("-" * 80)
            print(f"  总行数: {len(df)}")
            print(f"  总列数: {len(df.columns)}")
            
            # 检查关键列
            key_columns = ['日期', '主力净流入', '小单净流入', '中单净流入', '大单净流入', '超大单净流入']
            print(f"\n🔑 关键列检查:")
            print("-" * 80)
            for col in key_columns:
                if col in df.columns:
                    print(f"  ✅ {col}: 存在")
                    if df[col].dtype in ['float64', 'int64']:
                        non_null = df[col].notna().sum()
                        null = df[col].isna().sum()
                        print(f"      - 非空值: {non_null}")
                        print(f"      - 空值: {null}")
                        if non_null > 0:
                            print(f"      - 最小值: {df[col].min():,.2f}")
                            print(f"      - 最大值: {df[col].max():,.2f}")
                            print(f"      - 平均值: {df[col].mean():,.2f}")
                else:
                    print(f"  ❌ {col}: 不存在")
            
            # 检查日期列
            if '日期' in df.columns:
                print(f"\n📅 日期范围:")
                print("-" * 80)
                print(f"  最早日期: {df['日期'].min()}")
                print(f"  最新日期: {df['日期'].max()}")
                print(f"  数据天数: {df['日期'].nunique()}")
            
        except Exception as e:
            print(f"\n❌ 接口调用失败: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    print("\n" + "=" * 80)
    print("✅ 接口分析完成")
    print("=" * 80)

if __name__ == "__main__":
    test_stock_individual_fund_flow()

