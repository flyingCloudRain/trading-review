from sqlalchemy import Column, Integer, String, Float, DateTime, Text, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.db import Base

class TradingReview(Base):
    """交易复盘记录模型"""
    __tablename__ = 'trading_reviews'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String(10), nullable=False, comment='交易日期 YYYY-MM-DD')
    market = Column(String(10), nullable=False, default='A股', comment='市场类型：A股/美股')
    stock_code = Column(String(10), nullable=False, default='', index=True, comment='股票代码')
    stock_name = Column(String(50), nullable=False, default='', comment='股票名称')
    operation = Column(String(4), nullable=False, comment='操作类型：buy/sell')
    price = Column(Float, nullable=False, comment='成交价格')
    quantity = Column(Integer, nullable=False, comment='成交数量')
    total_amount = Column(Float, nullable=True, comment='成交总额')
    reason = Column(Text, nullable=False, comment='交易原因')
    review = Column(Text, nullable=True, comment='复盘总结')
    profit = Column(Float, nullable=True, comment='盈亏金额')
    profit_percent = Column(Float, nullable=True, comment='盈亏比例')
    take_profit_price = Column(Float, nullable=True, comment='止盈价格')
    stop_loss_price = Column(Float, nullable=True, comment='止损价格')
    
    # 关联字段：用于关联买入和卖出记录
    parent_id = Column(Integer, ForeignKey('trading_reviews.id'), nullable=True, index=True, comment='父记录ID（卖出记录关联对应的买入记录）')
    trade_group_id = Column(Integer, nullable=True, index=True, comment='交易组ID（同一只股票的多次买卖归为一组）')
    
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    
    # 关系定义
    parent = relationship('TradingReview', remote_side=[id], backref='children')
    
    __table_args__ = (
        CheckConstraint("operation IN ('buy', 'sell')", name='check_operation'),
        CheckConstraint("market IN ('A股', '美股')", name='check_market'),
        {'sqlite_autoincrement': True}
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'date': self.date,
            'market': self.market,
            'stockCode': self.stock_code,
            'stockName': self.stock_name,
            'operation': self.operation,
            'price': self.price,
            'quantity': self.quantity,
            'totalAmount': self.total_amount,
            'reason': self.reason,
            'review': self.review,
            'profit': self.profit,
            'profitPercent': self.profit_percent,
            'takeProfitPrice': self.take_profit_price,
            'stopLossPrice': self.stop_loss_price,
            'parentId': self.parent_id,
            'tradeGroupId': self.trade_group_id,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }

