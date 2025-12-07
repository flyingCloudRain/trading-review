from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Text
from sqlalchemy.sql import func
from database.db import Base

class SectorHistory(Base):
    """板块历史数据模型（支持行业板块和概念板块）"""
    __tablename__ = 'sector_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, index=True, comment='日期')
    sector_type = Column(String(20), nullable=False, default='industry', index=True, comment='板块类型: industry(行业板块) 或 concept(概念板块)')
    index = Column(Integer, nullable=False, comment='序号')
    name = Column(String(50), nullable=False, index=True, comment='板块名称')
    change_percent = Column(Float, nullable=False, comment='涨跌幅(%)')
    total_volume = Column(Float, nullable=False, comment='总成交量(万手)')
    total_amount = Column(Float, nullable=False, comment='总成交额(亿元)')
    net_inflow = Column(Float, nullable=False, comment='净流入(亿元)')
    up_count = Column(Integer, nullable=False, comment='上涨家数')
    down_count = Column(Integer, nullable=False, comment='下跌家数')
    avg_price = Column(Float, nullable=False, comment='均价')
    leading_stock = Column(String(50), nullable=True, comment='领涨股')
    leading_stock_price = Column(Float, nullable=True, comment='领涨股-最新价')
    leading_stock_change_percent = Column(Float, nullable=True, comment='领涨股-涨跌幅(%)')
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'sectorType': self.sector_type,
            'index': self.index,
            'name': self.name,
            'changePercent': self.change_percent,
            'totalVolume': self.total_volume,
            'totalAmount': self.total_amount,
            'netInflow': self.net_inflow,
            'upCount': self.up_count,
            'downCount': self.down_count,
            'avgPrice': self.avg_price,
            'leadingStock': self.leading_stock,
            'leadingStockPrice': self.leading_stock_price,
            'leadingStockChangePercent': self.leading_stock_change_percent,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }

