#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试 stock_zh_a_spot_em 接口
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import akshare as ak
import pandas as pd
from datetime import datetime
import time

def test_stock_zh_a_spot_em():
    """测试 stock_zh_a_spot_em 接口"""
    print("=" * 80)
    print("🔍 测试 stock_zh_a_spot_em 接口")
    print("=" * 80)
    
    max_retries = 3
    retry_delay = 2
    
    for retry in range(max_retries):
        try:
            print(f"\n📊 测试获取全部A股实时行情数据 (尝试 {retry + 1}/{max_retries})")
            print("-" * 80)
            
            start_time = datetime.now()
            df = ak.stock_zh_a_spot_em()
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            if df.empty:
                print("  ⚠️ 返回数据为空")
            else:
                print(f"  ✅ 成功！耗时: {duration:.2f}秒")
                print(f"  📈 数据量: {len(df)} 条")
                print(f"  📋 列数: {len(df.columns)} 列")
                print(f"\n  📊 数据列名:")
                for i, col in enumerate(df.columns, 1):
                    print(f"    {i:2d}. {col}")
                
                print(f"\n  📋 前5条数据示例:")
                print(df.head().to_string())
                
                # 测试通过股票代码查询
                print(f"\n  🔍 测试通过股票代码查询:")
                test_codes = ["000001", "600000", "300001"]
                for code in test_codes:
                    result = df[df['代码'] == code]
                    if not result.empty:
                        stock_name = result.iloc[0]['名称']
                        latest_price = result.iloc[0]['最新价']
                        change_pct = result.iloc[0]['涨跌幅']
                        print(f"    ✅ {code} ({stock_name}): 最新价={latest_price:.2f}, 涨跌幅={change_pct:.2f}%")
                    else:
                        print(f"    ⚠️ {code}: 未找到")
                
                # 测试通过股票名称模糊查询
                print(f"\n  🔍 测试通过股票名称模糊查询:")
                test_names = ["平安", "浦发", "特锐"]
                for name in test_names:
                    result = df[df['名称'].str.contains(name, na=False)]
                    if not result.empty:
                        print(f"    ✅ 包含'{name}'的股票: {len(result)} 只")
                        for idx, row in result.head(3).iterrows():
                            print(f"      - {row['代码']} ({row['名称']}): {row['最新价']:.2f}")
                    else:
                        print(f"    ⚠️ 包含'{name}'的股票: 未找到")
            
            # 成功获取数据，跳出重试循环
            break
                    
        except Exception as e:
            if retry < max_retries - 1:
                print(f"  ⚠️ 失败，正在重试... ({retry + 1}/{max_retries})")
                print(f"  错误: {str(e)}")
                time.sleep(retry_delay * (retry + 1))
            else:
                print(f"  ❌ 失败（已重试{max_retries}次）: {str(e)}")
                import traceback
                traceback.print_exc()
                return
    
    print("\n" + "=" * 80)
    print("✅ 测试完成")
    print("=" * 80)

if __name__ == "__main__":
    test_stock_zh_a_spot_em()

