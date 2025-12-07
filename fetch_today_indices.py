#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取今日指数数据并存入数据库
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.db import SessionLocal
from services.index_history_service import IndexHistoryService
from utils.time_utils import get_utc8_date

def main():
    """获取今日指数数据并存入数据库"""
    print("=" * 60)
    print("📊 获取今日指数数据并存入数据库")
    print("=" * 60)
    
    today = get_utc8_date()
    print(f"\n📅 目标日期: {today}")
    
    # 获取数据库会话
    db = SessionLocal()
    try:
        print("\n🔄 正在获取指数数据...")
        saved_count = IndexHistoryService.save_today_indices(db)
        
        if saved_count > 0:
            print(f"\n✅ 成功保存 {saved_count} 条指数数据到数据库")
            
            # 验证保存的数据
            indices = IndexHistoryService.get_indices_by_date(db, today)
            print(f"\n📋 验证: 数据库中今日共有 {len(indices)} 条指数记录")
            
            if indices:
                print("\n📊 前10条指数数据:")
                print("-" * 100)
                print(f"{'序号':<6} {'代码':<10} {'名称':<25} {'最新价':<12} {'涨跌幅':<10} {'涨跌额':<12}")
                print("-" * 100)
                
                for i, idx in enumerate(indices[:10], 1):
                    code = idx.get('code', '')
                    name = idx.get('name', '')
                    price = idx.get('currentPrice', 0)
                    change_pct = idx.get('changePercent', 0)
                    change = idx.get('change', 0)
                    
                    print(f"{i:<6} {code:<10} {name[:25]:<25} {price:<12.2f} {change_pct:<10.2f}% {change:<12.2f}")
                
                print("-" * 100)
                
                # 显示主要指数
                print("\n🔍 主要指数信息:")
                main_indices_codes = ['000001', '399001', '399006', '000016', '000300', '000905']
                for idx in indices:
                    if idx.get('code') in main_indices_codes:
                        print(f"  • {idx.get('name')} ({idx.get('code')}): {idx.get('currentPrice'):.2f}, "
                              f"涨跌幅: {idx.get('changePercent'):+.2f}%, "
                              f"涨跌额: {idx.get('change'):+.2f}")
        else:
            print("\n⚠️  未获取到指数数据，可能的原因：")
            print("  1. 网络连接问题")
            print("  2. API接口暂时不可用")
            print("  3. 今日不是交易日")
            
    except Exception as e:
        print(f"\n❌ 保存指数数据失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()
    
    print("\n" + "=" * 60)
    print("✅ 操作完成")
    print("=" * 60)

if __name__ == '__main__':
    main()

