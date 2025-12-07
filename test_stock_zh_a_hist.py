#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 stock_zh_a_hist 接口
验证接口是否能够调通
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

def test_stock_zh_a_hist():
    """测试 stock_zh_a_hist 接口"""
    print("=" * 80)
    print("🔍 测试 stock_zh_a_hist 接口（A股历史行情）")
    print("=" * 80)
    
    # 测试股票代码
    test_codes = [
        ("000001", "平安银行"),
        ("600000", "浦发银行"),
        ("300001", "特锐德"),
    ]
    
    for stock_code, stock_name in test_codes:
        print(f"\n{'=' * 80}")
        print(f"📊 测试股票: {stock_code} ({stock_name})")
        print(f"{'=' * 80}")
        
        try:
            # 测试不同的参数组合
            test_cases = [
                {
                    "name": "默认参数（最近数据）",
                    "params": {"symbol": stock_code}
                },
                {
                    "name": "指定开始日期",
                    "params": {
                        "symbol": stock_code,
                        "start_date": "20240101",
                        "end_date": "20240131"
                    }
                },
                {
                    "name": "最近30天",
                    "params": {
                        "symbol": stock_code,
                        "period": "daily",
                        "adjust": ""
                    }
                },
            ]
            
            for i, test_case in enumerate(test_cases, 1):
                print(f"\n📝 测试用例 {i}: {test_case['name']}")
                print("-" * 80)
                
                try:
                    start_time = datetime.now()
                    
                    # 调用接口
                    if "start_date" in test_case["params"]:
                        df = ak.stock_zh_a_hist(
                            symbol=test_case["params"]["symbol"],
                            start_date=test_case["params"]["start_date"],
                            end_date=test_case["params"]["end_date"]
                        )
                    elif "period" in test_case["params"]:
                        df = ak.stock_zh_a_hist(
                            symbol=test_case["params"]["symbol"],
                            period=test_case["params"]["period"],
                            adjust=test_case["params"]["adjust"]
                        )
                    else:
                        df = ak.stock_zh_a_hist(symbol=test_case["params"]["symbol"])
                    
                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()
                    
                    print(f"✅ 接口调用成功！")
                    print(f"⏱️  耗时: {duration:.2f} 秒")
                    print(f"📈 数据形状: {df.shape}")
                    print(f"📊 总记录数: {len(df)} 条")
                    print(f"📋 总列数: {len(df.columns)} 列")
                    
                    if df.empty:
                        print("⚠️ 返回数据为空")
                        continue
                    
                    # 显示列名
                    print(f"\n📋 数据列名:")
                    for i, col in enumerate(df.columns, 1):
                        print(f"  {i:2d}. {col}")
                    
                    # 显示前几条数据示例
                    print(f"\n📝 数据示例（前5条）:")
                    print(df.head(5).to_string())
                    
                    # 检查关键列
                    key_columns = ['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '涨跌幅', '涨跌额']
                    print(f"\n🔑 关键列检查:")
                    missing_cols = []
                    for col in key_columns:
                        if col in df.columns:
                            print(f"  ✅ {col}: 存在")
                        else:
                            print(f"  ❌ {col}: 不存在")
                            missing_cols.append(col)
                    
                    if missing_cols:
                        print(f"\n⚠️  缺少关键列: {', '.join(missing_cols)}")
                    else:
                        print(f"\n✅ 所有关键列都存在")
                    
                    # 日期范围分析
                    if '日期' in df.columns:
                        print(f"\n📅 日期范围分析:")
                        df['日期'] = pd.to_datetime(df['日期'])
                        print(f"  最早日期: {df['日期'].min()}")
                        print(f"  最新日期: {df['日期'].max()}")
                        print(f"  数据天数: {df['日期'].nunique()}")
                    
                    # 价格分析
                    if '收盘' in df.columns:
                        print(f"\n💰 价格分析:")
                        close_price = df['收盘']
                        if close_price.notna().any():
                            print(f"  最低价: {close_price.min():.2f}")
                            print(f"  最高价: {close_price.max():.2f}")
                            print(f"  平均价: {close_price.mean():.2f}")
                            print(f"  最新价: {close_price.iloc[-1]:.2f}")
                    
                    # 涨跌幅分析
                    if '涨跌幅' in df.columns:
                        print(f"\n📊 涨跌幅分析:")
                        change_pct = df['涨跌幅']
                        if change_pct.notna().any():
                            print(f"  最大涨幅: {change_pct.max():.2f}%")
                            print(f"  最大跌幅: {change_pct.min():.2f}%")
                            print(f"  平均涨跌幅: {change_pct.mean():.2f}%")
                    
                    # 成交量分析
                    if '成交量' in df.columns:
                        print(f"\n📊 成交量分析:")
                        volume = df['成交量']
                        if volume.notna().any():
                            print(f"  最小成交量: {volume.min():,.0f}")
                            print(f"  最大成交量: {volume.max():,.0f}")
                            print(f"  平均成交量: {volume.mean():,.0f}")
                    
                    break  # 如果第一个测试用例成功，就跳出循环
                    
                except Exception as e:
                    print(f"❌ 测试用例 {i} 失败: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    continue
            
        except Exception as e:
            print(f"\n❌ 接口调用失败: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    print("\n" + "=" * 80)
    print("✅ 接口测试完成")
    print("=" * 80)

if __name__ == "__main__":
    test_stock_zh_a_hist()

