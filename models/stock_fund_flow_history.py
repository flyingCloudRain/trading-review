from sqlalchemy import Column, Integer, String, Float, DateTime, Date
from sqlalchemy.sql import func
from database.db import Base

class StockFundFlowHistory(Base):
    """个股资金流即时数据模型（基于 stock_fund_flow_individual 接口）"""
    __tablename__ = 'stock_fund_flow_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, index=True, comment='日期')
    stock_code = Column(String(10), nullable=False, index=True, comment='股票代码')
    stock_name = Column(String(50), nullable=True, comment='股票简称')
    
    # 价格和涨跌信息
    latest_price = Column(Float, nullable=True, comment='最新价')
    change_percent = Column(Float, nullable=True, comment='涨跌幅(%)')
    turnover_rate = Column(Float, nullable=True, comment='换手率(%)')
    
    # 资金流信息
    inflow = Column(Float, nullable=True, comment='流入资金(元)')
    outflow = Column(Float, nullable=True, comment='流出资金(元)')
    net_amount = Column(Float, nullable=True, comment='净额(元)')
    turnover = Column(Float, nullable=True, comment='成交额(元)')
    
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'stockCode': self.stock_code,
            'stockName': self.stock_name,
            'latestPrice': self.latest_price,
            'changePercent': self.change_percent,
            'turnoverRate': self.turnover_rate,
            'inflow': self.inflow,
            'outflow': self.outflow,
            'netAmount': self.net_amount,
            'turnover': self.turnover,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }

