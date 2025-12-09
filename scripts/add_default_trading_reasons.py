#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加默认交易原因到数据库
如果原因已存在，则跳过；如果不存在，则添加
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from database.db_supabase import SessionLocal
    from services.trading_reason_service import TradingReasonService
    print("✅ 成功连接到数据库")
except Exception as e:
    print(f"❌ 数据库连接失败: {e}")
    sys.exit(1)

# 新的默认交易原因（按优先级排序）
NEW_DEFAULT_REASONS = [
    "点位突破",
    "双突破趋势点位",
    "双突破趋势形态",
    "双突破趋势量能",
    "突破回调站稳",
    "回调非波拉切",
]

def add_default_reasons():
    """添加默认交易原因到数据库"""
    db = SessionLocal()
    try:
        from models.trading_reason import TradingReason
        from sqlalchemy import func
        
        # 获取现有的交易原因
        existing_reasons = TradingReasonService.get_reason_list(db)
        existing_set = set(existing_reasons)
        
        # 找出需要添加的原因
        reasons_to_add = [r for r in NEW_DEFAULT_REASONS if r not in existing_set]
        
        if not reasons_to_add:
            print("✅ 所有默认交易原因已存在")
            # 检查显示顺序，确保新原因排在前面
            all_reasons = TradingReasonService.get_all_reasons(db)
            new_reasons_in_db = [r for r in all_reasons if r.reason in NEW_DEFAULT_REASONS]
            other_reasons = [r for r in all_reasons if r.reason not in NEW_DEFAULT_REASONS]
            
            # 如果新原因不在前面，调整顺序
            if new_reasons_in_db and other_reasons:
                new_max_order = max([r.display_order for r in new_reasons_in_db])
                other_min_order = min([r.display_order for r in other_reasons])
                if new_max_order > other_min_order:
                    print("📝 调整显示顺序，确保新原因排在前面...")
                    # 将新原因移到前面（1-6），其他原因移到后面（7+）
                    for i, reason_obj in enumerate(new_reasons_in_db, start=1):
                        if reason_obj.reason in NEW_DEFAULT_REASONS:
                            idx = NEW_DEFAULT_REASONS.index(reason_obj.reason)
                            TradingReasonService.update_display_order(db, reason_obj.id, idx + 1)
                    
                    # 将其他原因移到后面
                    offset = len(NEW_DEFAULT_REASONS)
                    for i, reason_obj in enumerate(other_reasons, start=1):
                        TradingReasonService.update_display_order(db, reason_obj.id, offset + i)
                    
                    print("✅ 显示顺序已调整")
        else:
            print(f"📝 准备添加 {len(reasons_to_add)} 个新的交易原因...")
            
            # 获取所有现有原因对象
            all_reason_objs = TradingReasonService.get_all_reasons(db)
            other_reasons = [r for r in all_reason_objs if r.reason not in NEW_DEFAULT_REASONS]
            
            # 先调整现有原因的显示顺序，为新的原因腾出位置
            if other_reasons:
                print("📝 调整现有原因的显示顺序...")
                offset = len(NEW_DEFAULT_REASONS)
                for i, reason_obj in enumerate(other_reasons, start=1):
                    TradingReasonService.update_display_order(db, reason_obj.id, offset + i)
            
            # 添加新的原因（从1开始，确保它们排在最前面）
            added_count = 0
            for i, reason in enumerate(NEW_DEFAULT_REASONS, start=1):
                try:
                    # 检查是否已存在
                    existing = TradingReasonService.get_reason_by_name(db, reason)
                    if existing:
                        # 如果已存在，更新显示顺序
                        TradingReasonService.update_display_order(db, existing.id, i)
                        print(f"  ✅ 已更新显示顺序: {reason}")
                    else:
                        # 如果不存在，创建新原因
                        TradingReasonService.create_reason(db, reason, display_order=i)
                        added_count += 1
                        print(f"  ✅ 已添加: {reason}")
                except Exception as e:
                    print(f"  ❌ 处理失败: {reason} - {e}")
        
        db.commit()
        print(f"\n✅ 完成！")
        
        # 显示更新后的列表
        print("\n📋 当前所有交易原因（按显示顺序）:")
        updated_reasons = TradingReasonService.get_reason_list(db)
        for i, reason in enumerate(updated_reasons, start=1):
            marker = "⭐" if reason in NEW_DEFAULT_REASONS else "  "
            print(f"  {marker} {i}. {reason}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 添加默认交易原因时出错: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 80)
    print("🔧 添加默认交易原因到数据库")
    print("=" * 80)
    print()
    
    try:
        add_default_reasons()
        print()
        print("✅ 完成！")
    except Exception as e:
        print()
        print(f"❌ 失败: {e}")
        sys.exit(1)

