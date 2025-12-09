#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易原因管理工具
从数据库读取和管理交易原因
"""
from typing import List

# 默认交易原因列表（用于初始化）
DEFAULT_REASONS = [
    "点位突破",
    "双突破趋势点位",
    "双突破趋势形态",
    "双突破趋势量能",
    "突破回调站稳",
    "回调非波拉切",
    "技术面突破",
    "技术面回调",
    "基本面改善",
    "基本面恶化",
    "消息面利好",
    "消息面利空",
    "资金面流入",
    "资金面流出",
    "板块轮动",
    "超跌反弹",
    "趋势跟随",
    "止盈离场",
    "止损离场",
    "调仓换股",
    "其他"
]

def get_trading_reasons() -> List[str]:
    """
    获取交易原因列表
    从数据库读取
    
    Returns:
        List[str]: 交易原因列表
    """
    try:
        from database.db import SessionLocal
        from services.trading_reason_service import TradingReasonService
        
        db = SessionLocal()
        try:
            reasons = TradingReasonService.get_reason_list(db)
            # 如果数据库为空，返回默认列表（用于初始化）
            if not reasons:
                return DEFAULT_REASONS.copy()
            return reasons
        finally:
            db.close()
    except Exception as e:
        # 数据库不可用，返回默认列表
        print(f"⚠️  从数据库读取交易原因失败: {e}")
        return DEFAULT_REASONS.copy()

def save_trading_reasons(reasons: List[str]) -> bool:
    """
    保存交易原因列表到数据库
    
    Args:
        reasons: 交易原因列表
    
    Returns:
        bool: 是否保存成功
    """
    try:
        from database.db import SessionLocal
        from services.trading_reason_service import TradingReasonService
        
        db = SessionLocal()
        try:
            # 批量创建
            created_count = TradingReasonService.batch_create_reasons(db, reasons)
            return True
        finally:
            db.close()
    except Exception as e:
        print(f"保存交易原因列表失败: {e}")
        return False

def add_trading_reason(reason: str) -> bool:
    """
    添加交易原因
    
    Args:
        reason: 交易原因
    
    Returns:
        bool: 是否添加成功
    """
    if not reason or not reason.strip():
        return False
    
    try:
        from database.db import SessionLocal
        from services.trading_reason_service import TradingReasonService
        
        db = SessionLocal()
        try:
            TradingReasonService.create_reason(db, reason.strip())
            return True
        finally:
            db.close()
    except Exception as e:
        print(f"添加交易原因失败: {e}")
        return False

def remove_trading_reason(reason: str) -> bool:
    """
    删除交易原因
    
    Args:
        reason: 要删除的交易原因
    
    Returns:
        bool: 是否删除成功
    """
    try:
        from database.db import SessionLocal
        from services.trading_reason_service import TradingReasonService
        
        db = SessionLocal()
        try:
            return TradingReasonService.delete_reason(db, reason)
        finally:
            db.close()
    except Exception as e:
        print(f"删除交易原因失败: {e}")
        return False

def update_trading_reason(old_reason: str, new_reason: str) -> bool:
    """
    更新交易原因
    
    Args:
        old_reason: 旧的交易原因
        new_reason: 新的交易原因
    
    Returns:
        bool: 是否更新成功
    """
    if not new_reason or not new_reason.strip():
        return False
    
    try:
        from database.db import SessionLocal
        from services.trading_reason_service import TradingReasonService
        
        db = SessionLocal()
        try:
            updated = TradingReasonService.update_reason(db, old_reason, new_reason.strip())
            return updated is not None
        finally:
            db.close()
    except Exception as e:
        print(f"更新交易原因失败: {e}")
        return False

