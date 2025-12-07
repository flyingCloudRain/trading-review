from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date, time as dt_time
from models.dt_pool_history import DtgcPoolHistory
from services.dtgc_service import DtgcService
from utils.time_utils import get_data_date

class DtgcPoolHistoryService:
    """跌停股票池历史数据服务"""
    
    @staticmethod
    def save_today_dtgc_pool(db: Session) -> int:
        """
        保存跌停股票池数据（自动判断日期）
        - 如果在交易时间内，使用当前日期
        - 如果不在交易时间内，使用上一个交易日
        """
        data_date = get_data_date()
        
        # 检查该日期的数据是否已存在
        existing = db.query(DtgcPoolHistory).filter(DtgcPoolHistory.date == data_date).first()
        if existing:
            # 如果已存在，先删除旧数据
            db.query(DtgcPoolHistory).filter(DtgcPoolHistory.date == data_date).delete()
        
        # 获取当前跌停股票池数据
        stocks = DtgcService.get_dtgc_pool()
        
        # 保存到数据库
        saved_count = 0
        for stock in stocks:
            # 解析时间字符串（格式：HH:MM:SS 或 HH:MM）
            last_sealing_time = None
            if stock.get('lastSealingTime'):
                try:
                    time_str = stock['lastSealingTime'].strip()
                    if time_str:
                        parts = time_str.split(':')
                        if len(parts) >= 2:
                            hour = int(parts[0])
                            minute = int(parts[1])
                            second = int(parts[2]) if len(parts) > 2 else 0
                            last_sealing_time = dt_time(hour, minute, second)
                except:
                    pass
            
            history = DtgcPoolHistory(
                date=data_date,
                index=stock.get('index', 0),
                code=stock.get('code', ''),
                name=stock.get('name', ''),
                change_percent=stock.get('changePercent', 0),
                latest_price=stock.get('latestPrice', 0),
                turnover=stock.get('turnover', 0),
                circulating_market_value=stock.get('circulatingMarketValue', 0),
                total_market_value=stock.get('totalMarketValue', 0),
                pe_ratio=stock.get('peRatio'),
                turnover_rate=stock.get('turnoverRate', 0),
                sealing_funds=stock.get('sealingFunds', 0),
                last_sealing_time=last_sealing_time,
                board_turnover=stock.get('boardTurnover', 0),
                continuous_limit_down=stock.get('continuousLimitDown', 0),
                open_count=stock.get('openCount', 0),
                industry=stock.get('industry'),
            )
            db.add(history)
            saved_count += 1
        
        db.commit()
        return saved_count
    
    @staticmethod
    def get_dtgc_pool_by_date(db: Session, target_date: date) -> List[Dict]:
        """根据日期获取跌停股票池数据"""
        stocks = db.query(DtgcPoolHistory).filter(
            DtgcPoolHistory.date == target_date
        ).order_by(DtgcPoolHistory.index).all()
        
        return [stock.to_dict() for stock in stocks]
    
    @staticmethod
    def get_dtgc_pool_by_date_range(db: Session, start_date: date, end_date: date) -> List[Dict]:
        """根据日期范围获取跌停股票池数据"""
        stocks = db.query(DtgcPoolHistory).filter(
            and_(
                DtgcPoolHistory.date >= start_date,
                DtgcPoolHistory.date <= end_date
            )
        ).order_by(DtgcPoolHistory.date.desc(), DtgcPoolHistory.index).all()
        
        return [stock.to_dict() for stock in stocks]

