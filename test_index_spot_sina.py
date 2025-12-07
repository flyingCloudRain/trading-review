#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 stock_zh_index_spot_sina 接口返回数据
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import akshare as ak
import pandas as pd
from services.stock_index_service import StockIndexService

def test_index_spot_sina():
    """测试 stock_zh_index_spot_sina 接口"""
    print("=" * 80)
    print("🔍 查询 stock_zh_index_spot_sina 接口返回数据")
    print("=" * 80)
    
    try:
        # 调用接口
        print("\n📊 调用 stock_zh_index_spot_sina 接口...")
        print("-" * 80)
        df = ak.stock_zh_index_spot_sina()
        print(f"✅ 成功获取 {len(df)} 条指数数据")
        
        # 显示列名
        print(f"\n📋 数据列名: {list(df.columns)}")
        
        # 查找目标指数
        target_codes = ['000001', '399106', '399006', '399001']
        print("\n🔍 查找主要指数:")
        found_indices = {}
        for code in target_codes:
            # 检查代码列
            matches = df[df['代码'].astype(str).str.contains(code, na=False)]
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
        sz_indices = df[df['代码'].astype(str).str.contains('399', na=False)]
        print(f"\n📋 深证系列指数（399开头）: 共 {len(sz_indices)} 个")
        if len(sz_indices) > 0:
            print("前20个:")
            for i, (_, row) in enumerate(sz_indices.head(20).iterrows(), 1):
                code = str(row.get('代码', ''))
                name = str(row.get('名称', ''))
                change_pct = row.get('涨跌幅', 0)
                current_price = row.get('最新价', 0)
                print(f"  {i:2d}. {code:15s} - {name:30s} 最新价: {current_price:8.2f} 涨跌幅: {change_pct:+.2f}%")
        else:
            print("  ❌ 没有找到399开头的指数")
        
        # 统计000开头的指数
        sh_indices = df[df['代码'].astype(str).str.contains('^000', na=False, regex=True)]
        print(f"\n📋 上证系列指数（000开头）: 共 {len(sh_indices)} 个")
        if len(sh_indices) > 0:
            print("前20个:")
            for i, (_, row) in enumerate(sh_indices.head(20).iterrows(), 1):
                code = str(row.get('代码', ''))
                name = str(row.get('名称', ''))
                change_pct = row.get('涨跌幅', 0)
                current_price = row.get('最新价', 0)
                print(f"  {i:2d}. {code:15s} - {name:30s} 最新价: {current_price:8.2f} 涨跌幅: {change_pct:+.2f}%")
        
        # 显示一条示例数据
        print("\n" + "=" * 80)
        print("📋 示例数据（第一条）:")
        print("-" * 80)
        if not df.empty:
            first_row = df.iloc[0]
            for col in df.columns:
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
        
        # 测试服务方法
        print("\n" + "=" * 80)
        print("📋 测试 StockIndexService.get_index_spot_sina():")
        print("-" * 80)
        try:
            indices = StockIndexService.get_index_spot_sina()
            print(f"✅ 成功获取 {len(indices)} 条指数数据")
            
            # 查找目标指数
            print("\n🔍 查找主要指数（标准化后）:")
            for code in target_codes:
                found = [idx for idx in indices if idx.get('code') == code]
                if found:
                    idx = found[0]
                    print(f"  ✅ {code}: {idx.get('name')}, 最新价={idx.get('currentPrice'):.2f}, 涨跌幅={idx.get('changePercent'):+.2f}%")
                else:
                    print(f"  ❌ {code}: 未找到")
        except Exception as e:
            print(f"❌ 测试服务方法失败: {str(e)}")
            import traceback
            traceback.print_exc()
        
        return found_indices
        
    except Exception as e:
        print(f"❌ 查询失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_index_spot_sina()

