from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.trading_reason import TradingReason

class TradingReasonService:
    """交易原因服务"""
    
    @staticmethod
    def get_all_reasons(db: Session) -> List[TradingReason]:
        """获取所有交易原因，按显示顺序排序"""
        return db.query(TradingReason).order_by(
            TradingReason.display_order.asc(),
            TradingReason.id.asc()
        ).all()
    
    @staticmethod
    def get_reason_list(db: Session) -> List[str]:
        """获取交易原因列表（仅名称）"""
        reasons = TradingReasonService.get_all_reasons(db)
        return [r.reason for r in reasons]
    
    @staticmethod
    def get_reason_by_id(db: Session, reason_id: int) -> Optional[TradingReason]:
        """根据ID获取交易原因"""
        return db.query(TradingReason).filter(TradingReason.id == reason_id).first()
    
    @staticmethod
    def get_reason_by_name(db: Session, reason: str) -> Optional[TradingReason]:
        """根据名称获取交易原因"""
        return db.query(TradingReason).filter(TradingReason.reason == reason).first()
    
    @staticmethod
    def create_reason(db: Session, reason: str, display_order: Optional[int] = None) -> TradingReason:
        """创建交易原因"""
        # 检查是否已存在
        existing = TradingReasonService.get_reason_by_name(db, reason)
        if existing:
            return existing
        
        # 如果没有指定显示顺序，使用最大值+1
        if display_order is None:
            max_order = db.query(func.max(TradingReason.display_order)).scalar()
            display_order = (max_order or 0) + 1
        
        new_reason = TradingReason(
            reason=reason.strip(),
            display_order=display_order
        )
        db.add(new_reason)
        db.commit()
        db.refresh(new_reason)
        return new_reason
    
    @staticmethod
    def update_reason(db: Session, old_reason: str, new_reason: str) -> Optional[TradingReason]:
        """更新交易原因"""
        reason_obj = TradingReasonService.get_reason_by_name(db, old_reason)
        if not reason_obj:
            return None
        
        # 检查新名称是否已存在
        existing = TradingReasonService.get_reason_by_name(db, new_reason)
        if existing and existing.id != reason_obj.id:
            raise ValueError(f"交易原因 '{new_reason}' 已存在")
        
        reason_obj.reason = new_reason.strip()
        db.commit()
        db.refresh(reason_obj)
        return reason_obj
    
    @staticmethod
    def delete_reason(db: Session, reason: str) -> bool:
        """删除交易原因"""
        reason_obj = TradingReasonService.get_reason_by_name(db, reason)
        if not reason_obj:
            return False
        
        db.delete(reason_obj)
        db.commit()
        return True
    
    @staticmethod
    def batch_create_reasons(db: Session, reasons: List[str]) -> int:
        """批量创建交易原因"""
        created_count = 0
        max_order = db.query(func.max(TradingReason.display_order)).scalar() or 0
        
        for i, reason in enumerate(reasons):
            reason_trimmed = reason.strip()
            if not reason_trimmed:
                continue
            
            # 检查是否已存在
            existing = TradingReasonService.get_reason_by_name(db, reason_trimmed)
            if not existing:
                new_reason = TradingReason(
                    reason=reason_trimmed,
                    display_order=max_order + i + 1
                )
                db.add(new_reason)
                created_count += 1
        
        if created_count > 0:
            db.commit()
        
        return created_count
    
    @staticmethod
    def update_display_order(db: Session, reason_id: int, display_order: int) -> Optional[TradingReason]:
        """更新显示顺序"""
        reason_obj = db.query(TradingReason).filter(TradingReason.id == reason_id).first()
        if not reason_obj:
            return None
        
        reason_obj.display_order = display_order
        db.commit()
        db.refresh(reason_obj)
        return reason_obj

