from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Time
from sqlalchemy.sql import func
from database.db import Base

class ZbgcPoolHistory(Base):
    """炸板股票池历史数据模型"""
    __tablename__ = 'zb_pool_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, index=True, comment='日期')
    time = Column(Time, nullable=True, comment='时间')
    index = Column(Integer, nullable=False, comment='序号')
    code = Column(String(10), nullable=False, index=True, comment='股票代码')
    name = Column(String(50), nullable=False, comment='股票名称')
    change_percent = Column(Float, nullable=False, comment='涨跌幅(%)')
    latest_price = Column(Float, nullable=False, comment='最新价')
    limit_price = Column(Float, nullable=False, comment='涨停价')
    turnover = Column(Float, nullable=False, comment='成交额(亿元)')
    circulating_market_value = Column(Float, nullable=False, comment='流通市值(亿元)')
    total_market_value = Column(Float, nullable=False, comment='总市值(亿元)')
    turnover_rate = Column(Float, nullable=False, comment='换手率(%)')
    rise_speed = Column(Float, nullable=False, comment='涨速')
    first_sealing_time = Column(Time, nullable=True, comment='首次封板时间')
    explosion_count = Column(Integer, nullable=False, default=0, index=True, comment='炸板次数')
    zt_statistics = Column(String(50), nullable=True, comment='涨停统计')
    amplitude = Column(Float, nullable=False, comment='振幅(%)')
    industry = Column(String(50), nullable=True, comment='所属行业')
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'time': self.time.strftime('%H:%M:%S') if self.time else None,
            'index': self.index,
            'code': self.code,
            'name': self.name,
            'changePercent': self.change_percent,
            'latestPrice': self.latest_price,
            'limitPrice': self.limit_price,
            'turnover': self.turnover,
            'circulatingMarketValue': self.circulating_market_value,
            'totalMarketValue': self.total_market_value,
            'turnoverRate': self.turnover_rate,
            'riseSpeed': self.rise_speed,
            'firstSealingTime': self.first_sealing_time.strftime('%H:%M:%S') if self.first_sealing_time else None,
            'explosionCount': self.explosion_count,
            'ztStatistics': self.zt_statistics,
            'amplitude': self.amplitude,
            'industry': self.industry,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }

