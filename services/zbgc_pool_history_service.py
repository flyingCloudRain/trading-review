from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date, time as dt_time
from models.zb_pool_history import ZbgcPoolHistory
from services.zbgc_service import ZbgcService
from utils.time_utils import get_data_date

class ZbgcPoolHistoryService:
    """炸板股票池历史数据服务"""
    
    @staticmethod
    def save_today_zbgc_pool(db: Session, target_date: Optional[date] = None) -> int:
        """
        保存炸板股票池数据（自动判断日期）
        - 如果在交易时间内，使用当前日期
        - 如果不在交易时间内，使用上一个交易日
        - 如果提供了target_date，则使用指定的日期
        
        Args:
            target_date: 可选，指定保存的日期。如果为None，则自动判断日期
        """
        if target_date is None:
            data_date = get_data_date()
        else:
            data_date = target_date
        
        # 检查该日期的数据是否已存在
        existing = db.query(ZbgcPoolHistory).filter(ZbgcPoolHistory.date == data_date).first()
        if existing:
            # 如果已存在，先删除旧数据
            db.query(ZbgcPoolHistory).filter(ZbgcPoolHistory.date == data_date).delete()
        
        # 获取当前炸板股票池数据
        stocks = ZbgcService.get_zbgc_pool()
        
        # 保存到数据库
        saved_count = 0
        for stock in stocks:
            # 解析时间字符串（格式：HH:MM:SS 或 HH:MM）
            first_sealing_time = None
            if stock.get('firstSealingTime'):
                try:
                    time_str = stock['firstSealingTime'].strip()
                    if time_str:
                        parts = time_str.split(':')
                        if len(parts) >= 2:
                            hour = int(parts[0])
                            minute = int(parts[1])
                            second = int(parts[2]) if len(parts) > 2 else 0
                            first_sealing_time = dt_time(hour, minute, second)
                except:
                    pass
            
            history = ZbgcPoolHistory(
                date=data_date,
                index=stock.get('index', 0),
                code=stock.get('code', ''),
                name=stock.get('name', ''),
                change_percent=stock.get('changePercent', 0),
                latest_price=stock.get('latestPrice', 0),
                limit_price=stock.get('limitPrice', 0),
                turnover=stock.get('turnover', 0),
                circulating_market_value=stock.get('circulatingMarketValue', 0),
                total_market_value=stock.get('totalMarketValue', 0),
                turnover_rate=stock.get('turnoverRate', 0),
                rise_speed=stock.get('riseSpeed', 0),
                first_sealing_time=first_sealing_time,
                explosion_count=stock.get('explosionCount', 0),
                zt_statistics=stock.get('ztStatistics'),
                amplitude=stock.get('amplitude', 0),
                industry=stock.get('industry'),
            )
            db.add(history)
            saved_count += 1
        
        db.commit()
        return saved_count
    
    @staticmethod
    def get_zbgc_pool_by_date(db: Session, target_date: date) -> List[Dict]:
        """根据日期获取炸板股票池数据"""
        stocks = db.query(ZbgcPoolHistory).filter(
            ZbgcPoolHistory.date == target_date
        ).order_by(ZbgcPoolHistory.index).all()
        
        return [stock.to_dict() for stock in stocks]
    
    @staticmethod
    def get_zbgc_pool_by_date_range(db: Session, start_date: date, end_date: date) -> List[Dict]:
        """根据日期范围获取炸板股票池数据"""
        stocks = db.query(ZbgcPoolHistory).filter(
            and_(
                ZbgcPoolHistory.date >= start_date,
                ZbgcPoolHistory.date <= end_date
            )
        ).order_by(ZbgcPoolHistory.date.desc(), ZbgcPoolHistory.index).all()
        
        return [stock.to_dict() for stock in stocks]

