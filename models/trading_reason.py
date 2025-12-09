from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from database.db import Base

class TradingReason(Base):
    """交易原因模型"""
    __tablename__ = 'trading_reasons'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    reason = Column(String(100), nullable=False, unique=True, index=True, comment='交易原因')
    display_order = Column(Integer, nullable=False, default=0, comment='显示顺序')
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    
    __table_args__ = (
        UniqueConstraint('reason', name='uq_trading_reason'),
        {'sqlite_autoincrement': True}
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'reason': self.reason,
            'displayOrder': self.display_order,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }

