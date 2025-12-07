#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 stock_bid_ask_em 接口
分析股票买卖盘（五档行情）接口
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import akshare as ak
import pandas as pd
from datetime import datetime

def test_stock_bid_ask_em():
    """测试 stock_bid_ask_em 接口"""
    print("=" * 80)
    print("🔍 分析 stock_bid_ask_em 接口（股票买卖盘/五档行情）")
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
            print(f"\n🔄 调用 stock_bid_ask_em('{stock_code}')...")
            start_time = datetime.now()
            df = ak.stock_bid_ask_em(symbol=stock_code)
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
            
            # 显示完整数据
            print(f"\n📝 完整数据:")
            print("-" * 80)
            print(df.to_string())
            
            # 分析数据结构
            print(f"\n🔍 数据结构分析:")
            print("-" * 80)
            print(f"  总行数: {len(df)}")
            print(f"  总列数: {len(df.columns)}")
            
            # 检查关键列
            key_columns = ['买1', '买2', '买3', '买4', '买5', '卖1', '卖2', '卖3', '卖4', '卖5']
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
                            print(f"      - 值: {df[col].values}")
                else:
                    print(f"  ❌ {col}: 不存在")
            
            # 检查价格和数量列
            price_columns = [col for col in df.columns if '价' in col or 'price' in col.lower()]
            volume_columns = [col for col in df.columns if '量' in col or 'volume' in col.lower() or '手' in col]
            
            if price_columns:
                print(f"\n💰 价格相关列:")
                print("-" * 80)
                for col in price_columns:
                    print(f"  - {col}")
            
            if volume_columns:
                print(f"\n📊 数量相关列:")
                print("-" * 80)
                for col in volume_columns:
                    print(f"  - {col}")
            
        except Exception as e:
            print(f"\n❌ 接口调用失败: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    # 测试接口参数
    print(f"\n{'=' * 80}")
    print("🔍 测试接口参数")
    print(f"{'=' * 80}")
    
    # 尝试不同的参数格式
    test_params = [
        ("000001", "标准6位代码"),
        ("sz000001", "带前缀代码"),
        ("sh600000", "上海代码"),
    ]
    
    for param, desc in test_params:
        try:
            print(f"\n📝 测试参数: {param} ({desc})")
            df = ak.stock_bid_ask_em(symbol=param)
            if not df.empty:
                print(f"  ✅ 成功，返回 {len(df)} 行数据")
            else:
                print(f"  ⚠️ 返回空数据")
        except Exception as e:
            print(f"  ❌ 失败: {str(e)}")
    
    print("\n" + "=" * 80)
    print("✅ 接口分析完成")
    print("=" * 80)

if __name__ == "__main__":
    test_stock_bid_ask_em()

