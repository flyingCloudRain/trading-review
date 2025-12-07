#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 stock_zh_index_spot_em 接口返回数据
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import akshare as ak
import pandas as pd
from services.stock_index_service import StockIndexService

def test_index_spot_em():
    """测试 stock_zh_index_spot_em 接口"""
    print("=" * 80)
    print("🔍 查询 stock_zh_index_spot_em 接口返回数据")
    print("=" * 80)
    
    try:
        # 方法1: 获取所有指数
        print("\n📊 方法1: 获取所有指数（不指定symbol）")
        print("-" * 80)
        df_all = ak.stock_zh_index_spot_em()
        print(f"✅ 成功获取 {len(df_all)} 条指数数据")
        
        # 显示列名
        print(f"\n📋 数据列名: {list(df_all.columns)}")
        
        # 查找目标指数
        target_codes = ['000001', '399106', '399006', '399001']
        print("\n🔍 查找主要指数:")
        found_indices = {}
        for code in target_codes:
            # 检查代码列
            matches = df_all[df_all['代码'].astype(str).str.contains(code, na=False)]
            if not matches.empty:
                for _, row in matches.iterrows():
                    raw_code = str(row.get('代码', ''))
                    name = str(row.get('名称', ''))
                    change_pct = row.get('涨跌幅', 0)
                    current_price = row.get('最新价', 0)
                    found_indices[code] = {
                        'raw_code': raw_code,
                        'name': name,
                        'change_pct': change_pct,
                        'current_price': current_price
                    }
                    print(f"  ✅ {code}: 代码={raw_code}, 名称={name}, 最新价={current_price:.2f}, 涨跌幅={change_pct:.2f}%")
            else:
                print(f"  ❌ {code}: 未找到")
        
        # 统计399开头的指数
        sz_indices = df_all[df_all['代码'].astype(str).str.contains('399', na=False)]
        print(f"\n📋 深证系列指数（399开头）: 共 {len(sz_indices)} 个")
        if len(sz_indices) > 0:
            print("前20个:")
            for i, (_, row) in enumerate(sz_indices.head(20).iterrows(), 1):
                code = str(row.get('代码', ''))
                name = str(row.get('名称', ''))
                change_pct = row.get('涨跌幅', 0)
                print(f"  {i:2d}. {code:15s} - {name:30s} 涨跌幅: {change_pct:+.2f}%")
        
        # 统计000开头的指数
        sh_indices = df_all[df_all['代码'].astype(str).str.contains('^000', na=False, regex=True)]
        print(f"\n📋 上证系列指数（000开头）: 共 {len(sh_indices)} 个")
        if len(sh_indices) > 0:
            print("前20个:")
            for i, (_, row) in enumerate(sh_indices.head(20).iterrows(), 1):
                code = str(row.get('代码', ''))
                name = str(row.get('名称', ''))
                change_pct = row.get('涨跌幅', 0)
                print(f"  {i:2d}. {code:15s} - {name:30s} 涨跌幅: {change_pct:+.2f}%")
        
        # 方法2: 分别获取上证和深证系列
        print("\n" + "=" * 80)
        print("📊 方法2: 分别获取上证系列和深证系列")
        print("-" * 80)
        
        try:
            df_sh = ak.stock_zh_index_spot_em(symbol="上证系列指数")
            print(f"✅ 上证系列指数: {len(df_sh)} 条")
            
            # 查找000001
            sh_matches = df_sh[df_sh['代码'].astype(str).str.contains('000001', na=False)]
            if not sh_matches.empty:
                for _, row in sh_matches.iterrows():
                    print(f"  ✅ 000001: {row.get('代码')} - {row.get('名称')}")
        except Exception as e:
            print(f"⚠️ 获取上证系列失败: {str(e)}")
        
        try:
            df_sz = ak.stock_zh_index_spot_em(symbol="深证系列指数")
            print(f"✅ 深证系列指数: {len(df_sz)} 条")
            
            # 查找399106和399006
            for code in ['399106', '399006']:
                sz_matches = df_sz[df_sz['代码'].astype(str).str.contains(code, na=False)]
                if not sz_matches.empty:
                    for _, row in sz_matches.iterrows():
                        raw_code = str(row.get('代码', ''))
                        name = str(row.get('名称', ''))
                        change_pct = row.get('涨跌幅', 0)
                        current_price = row.get('最新价', 0)
                        print(f"  ✅ {code}: 代码={raw_code}, 名称={name}, 最新价={current_price:.2f}, 涨跌幅={change_pct:.2f}%")
                else:
                    print(f"  ❌ {code}: 未找到")
            
            # 显示前10个深证指数
            if len(df_sz) > 0:
                print("\n深证系列指数前10个:")
                for i, (_, row) in enumerate(df_sz.head(10).iterrows(), 1):
                    code = str(row.get('代码', ''))
                    name = str(row.get('名称', ''))
                    print(f"  {i:2d}. {code:15s} - {name}")
        except Exception as e:
            print(f"⚠️ 获取深证系列失败: {str(e)}")
        
        # 显示一条示例数据
        print("\n" + "=" * 80)
        print("📋 示例数据（第一条）:")
        print("-" * 80)
        if not df_all.empty:
            first_row = df_all.iloc[0]
            for col in df_all.columns:
                print(f"  {col}: {first_row[col]}")
        
        # 测试代码标准化
        print("\n" + "=" * 80)
        print("📋 测试代码标准化:")
        print("-" * 80)
        if found_indices:
            for code, data in found_indices.items():
                raw_code = data['raw_code']
                normalized = StockIndexService.normalize_index_code(raw_code)
                print(f"  {code}: {raw_code} -> {normalized}")
        
        return found_indices
        
    except Exception as e:
        print(f"❌ 查询失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_index_spot_em()

