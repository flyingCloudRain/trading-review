from sqlalchemy import Column, Integer, String, Float, DateTime, Date
from sqlalchemy.sql import func
from database.db import Base

class IndexHistory(Base):
    """指数历史数据模型"""
    __tablename__ = 'index_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, index=True, comment='日期')
    code = Column(String(10), nullable=False, index=True, comment='指数代码')
    name = Column(String(50), nullable=False, comment='指数名称')
    current_price = Column(Float, nullable=False, comment='最新价')
    change_percent = Column(Float, nullable=False, comment='涨跌幅(%)')
    change = Column(Float, nullable=False, comment='涨跌额')
    volume = Column(Float, nullable=False, comment='成交量')
    amount = Column(Float, nullable=False, comment='成交额')
    open = Column(Float, nullable=False, comment='今开')
    high = Column(Float, nullable=False, comment='最高')
    low = Column(Float, nullable=False, comment='最低')
    prev_close = Column(Float, nullable=False, comment='昨收')
    amplitude = Column(Float, nullable=False, comment='振幅(%)')
    volume_ratio = Column(Float, nullable=False, comment='量比')
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'code': self.code,
            'name': self.name,
            'currentPrice': self.current_price,
            'changePercent': self.change_percent,
            'change': self.change,
            'volume': self.volume,
            'amount': self.amount,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'prevClose': self.prev_close,
            'amplitude': self.amplitude,
            'volumeRatio': self.volume_ratio,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }

