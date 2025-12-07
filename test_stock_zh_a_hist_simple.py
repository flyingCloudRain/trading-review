#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试 stock_zh_a_hist 接口
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import akshare as ak
import pandas as pd
from datetime import datetime

def test_stock_zh_a_hist():
    """测试 stock_zh_a_hist 接口"""
    print("=" * 80)
    print("🔍 测试 stock_zh_a_hist 接口")
    print("=" * 80)
    
    test_codes = ["000001", "600000", "300001"]
    
    for code in test_codes:
        print(f"\n📊 测试股票代码: {code}")
        print("-" * 80)
        
        try:
            start_time = datetime.now()
            df = ak.stock_zh_a_hist(symbol=code)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            if df.empty:
                print(f"  ⚠️ 返回数据为空")
            else:
                print(f"  ✅ 成功！耗时: {duration:.2f}秒")
                print(f"  📈 数据量: {len(df)} 条")
                print(f"  📋 列数: {len(df.columns)} 列")
                print(f"  📅 日期范围: {df['日期'].min()} 至 {df['日期'].max()}")
                print(f"  💰 最新收盘价: {df.iloc[-1]['收盘']:.2f}")
                print(f"  📊 最新涨跌幅: {df.iloc[-1]['涨跌幅']:.2f}%")
        except Exception as e:
            print(f"  ❌ 失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("✅ 测试完成")
    print("=" * 80)

if __name__ == "__main__":
    test_stock_zh_a_hist()

