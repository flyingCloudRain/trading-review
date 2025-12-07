#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 stock_sz_a_spot_em 接口
分析深圳A股实时行情接口
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import akshare as ak
import pandas as pd
from datetime import datetime

def test_stock_sz_a_spot_em():
    """测试 stock_sz_a_spot_em 接口"""
    print("=" * 80)
    print("🔍 分析 stock_sz_a_spot_em 接口（深圳A股实时行情）")
    print("=" * 80)
    
    try:
        # 调用接口
        print("\n📊 调用 stock_sz_a_spot_em 接口...")
        print("-" * 80)
        start_time = datetime.now()
        df = ak.stock_sz_a_spot_em()
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"✅ 成功获取数据，耗时: {duration:.2f} 秒")
        print(f"📈 数据量: {len(df)} 条记录")
        
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
        print(f"\n📝 数据示例（前5条）:")
        print("-" * 80)
        print(df.head(5).to_string())
        
        # 统计信息
        print(f"\n📈 数据统计:")
        print("-" * 80)
        print(f"  总记录数: {len(df)}")
        print(f"  总列数: {len(df.columns)}")
        print(f"  内存使用: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
        
        # 检查关键列
        key_columns = ['代码', '名称', '最新价', '涨跌幅', '涨跌额', '成交量', '成交额']
        print(f"\n🔑 关键列检查:")
        print("-" * 80)
        for col in key_columns:
            if col in df.columns:
                print(f"  ✅ {col}: 存在")
                if df[col].dtype in ['float64', 'int64']:
                    print(f"      - 非空值: {df[col].notna().sum()}")
                    print(f"      - 空值: {df[col].isna().sum()}")
                    if df[col].notna().any():
                        print(f"      - 最小值: {df[col].min()}")
                        print(f"      - 最大值: {df[col].max()}")
                        print(f"      - 平均值: {df[col].mean():.2f}")
            else:
                print(f"  ❌ {col}: 不存在")
        
        # 代码格式分析
        if '代码' in df.columns:
            print(f"\n🔢 代码格式分析:")
            print("-" * 80)
            codes = df['代码'].astype(str)
            print(f"  总代码数: {len(codes)}")
            print(f"  唯一代码数: {codes.nunique()}")
            
            # 检查代码前缀
            has_prefix = codes.str.startswith('sz') | codes.str.startswith('sh') | codes.str.startswith('bj')
            print(f"  带前缀代码数: {has_prefix.sum()}")
            print(f"  无前缀代码数: {(~has_prefix).sum()}")
            
            # 显示代码前缀分布
            if has_prefix.any():
                prefix_counts = codes.str[:2].value_counts()
                print(f"\n  代码前缀分布:")
                for prefix, count in prefix_counts.head(10).items():
                    print(f"    {prefix}: {count}")
            
            # 显示代码长度分布
            code_lengths = codes.str.len().value_counts().sort_index()
            print(f"\n  代码长度分布:")
            for length, count in code_lengths.items():
                print(f"    {length}位: {count}")
            
            # 显示示例代码
            print(f"\n  代码示例（前10个）:")
            for code in codes.head(10):
                print(f"    {code}")
        
        # 涨跌幅分析
        if '涨跌幅' in df.columns:
            print(f"\n📊 涨跌幅分析:")
            print("-" * 80)
            change_pct = df['涨跌幅']
            print(f"  上涨股票数 (>0): {(change_pct > 0).sum()}")
            print(f"  下跌股票数 (<0): {(change_pct < 0).sum()}")
            print(f"  平盘股票数 (=0): {(change_pct == 0).sum()}")
            print(f"  涨停股票数 (>=9.9): {(change_pct >= 9.9).sum()}")
            print(f"  跌停股票数 (<=-9.9): {(change_pct <= -9.9).sum()}")
            print(f"  最大涨幅: {change_pct.max():.2f}%")
            print(f"  最大跌幅: {change_pct.min():.2f}%")
            print(f"  平均涨跌幅: {change_pct.mean():.2f}%")
        
        # 成交量分析
        if '成交量' in df.columns:
            print(f"\n📊 成交量分析:")
            print("-" * 80)
            volume = df['成交量']
            print(f"  总成交量: {volume.sum():,.0f}")
            print(f"  平均成交量: {volume.mean():,.0f}")
            print(f"  最大成交量: {volume.max():,.0f}")
            print(f"  最小成交量: {volume.min():,.0f}")
        
        # 成交额分析
        if '成交额' in df.columns:
            print(f"\n📊 成交额分析:")
            print("-" * 80)
            amount = df['成交额']
            print(f"  总成交额: {amount.sum():,.2f} 元")
            print(f"  总成交额: {amount.sum() / 100000000:,.2f} 亿元")
            print(f"  平均成交额: {amount.mean():,.2f} 元")
            print(f"  最大成交额: {amount.max():,.2f} 元")
            print(f"  最小成交额: {amount.min():,.2f} 元")
        
        # 对比其他接口
        print(f"\n🔄 与其他接口对比:")
        print("-" * 80)
        try:
            print("  正在获取 stock_zh_a_spot_em（所有A股）...")
            df_all = ak.stock_zh_a_spot_em()
            print(f"  ✅ stock_zh_a_spot_em: {len(df_all)} 条记录")
            print(f"  ✅ stock_sz_a_spot_em: {len(df)} 条记录")
            print(f"  📊 深圳A股占比: {len(df) / len(df_all) * 100:.2f}%")
        except Exception as e:
            print(f"  ⚠️ 无法对比: {str(e)}")
        
        print("\n" + "=" * 80)
        print("✅ 接口分析完成")
        print("=" * 80)
        
        return df
        
    except Exception as e:
        print(f"\n❌ 接口调用失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    df = test_stock_sz_a_spot_em()
    
    if df is not None:
        print(f"\n💾 数据已获取，DataFrame 形状: {df.shape}")
        print(f"   列名: {list(df.columns)}")

