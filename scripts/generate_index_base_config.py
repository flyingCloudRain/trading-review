#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从CSV文件生成指数基础配置
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.index_base_config import generate_base_config_from_csv

if __name__ == '__main__':
    print("=" * 80)
    print("📊 从CSV文件生成指数基础配置")
    print("=" * 80)
    
    try:
        indices = generate_base_config_from_csv()
        
        print(f"\n✅ 成功生成指数基础配置")
        print(f"   总指数数: {len(indices)}")
        print(f"\n前20个指数:")
        print("-" * 80)
        for i, idx in enumerate(indices[:20], 1):
            print(f"   {i:2d}. {idx['code']} - {idx['name']}")
        
        if len(indices) > 20:
            print(f"   ... 还有 {len(indices) - 20} 个指数")
        
        print(f"\n配置文件已保存到: data/index_base_config.json")
        
    except Exception as e:
        print(f"\n❌ 生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "=" * 80)
    print("✅ 完成")
    print("=" * 80)

