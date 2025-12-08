from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date, time as dt_time
from models.zt_pool_history import ZtPoolHistory
from services.zt_pool_service import ZtPoolService
from utils.time_utils import get_data_date

class ZtPoolHistoryService:
    """涨停股票池历史数据服务"""
    
    @staticmethod
    def save_today_zt_pool(db: Session, target_date: Optional[date] = None) -> int:
        """
        保存涨停股票池数据（自动判断日期）
        - 如果在交易时间内，使用当前日期
        - 如果不在交易时间内，使用上一个交易日
        - 如果提供了target_date，则使用指定的日期
        
        优化：使用事务保护，确保数据不丢失
        
        Args:
            target_date: 可选，指定保存的日期。如果为None，则自动判断日期
        """
        if target_date is None:
            data_date = get_data_date()
        else:
            data_date = target_date
        
        try:
            # 先获取当前涨停股票池数据（在删除之前获取，避免数据丢失）
            stocks = ZtPoolService.get_zt_pool()
            
            if not stocks:
                print(f"⚠️  警告: {data_date} 没有获取到涨停股票数据")
                return 0
            
            # 开始事务：先准备新数据
            new_records = []
            for stock in stocks:
                # 解析时间字符串（格式：HH:MM:SS 或 HH:MM）
                first_sealing_time = None
                last_sealing_time = None
                
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
                
                history = ZtPoolHistory(
                    date=data_date,
                    index=stock.get('index', 0),
                    code=stock.get('code', ''),
                    name=stock.get('name', ''),
                    change_percent=stock.get('changePercent', 0),
                    latest_price=stock.get('latestPrice', 0),
                    turnover=stock.get('turnover', 0),
                    circulating_market_value=stock.get('circulatingMarketValue', 0),
                    total_market_value=stock.get('totalMarketValue', 0),
                    turnover_rate=stock.get('turnoverRate', 0),
                    sealing_funds=stock.get('sealingFunds', 0),
                    first_sealing_time=first_sealing_time,
                    last_sealing_time=last_sealing_time,
                    explosion_count=stock.get('explosionCount', 0),
                    zt_statistics=stock.get('ztStatistics'),
                    continuous_boards=stock.get('continuousBoards', 0),
                    industry=stock.get('industry'),
                )
                new_records.append(history)
            
            # 检查该日期的数据是否已存在
            existing = db.query(ZtPoolHistory).filter(ZtPoolHistory.date == data_date).first()
            if existing:
                # 如果已存在，先删除旧数据
                deleted_count = db.query(ZtPoolHistory).filter(ZtPoolHistory.date == data_date).delete()
                print(f"🗑️  删除 {data_date} 的旧数据: {deleted_count} 条")
            
            # 批量添加新数据
            for record in new_records:
                db.add(record)
            
            # 提交事务
            db.commit()
            print(f"✅ 成功保存 {len(new_records)} 条涨停股票数据到数据库 ({data_date})")
            return len(new_records)
            
        except Exception as e:
            # 如果出错，回滚事务
            db.rollback()
            print(f"❌ 保存涨停股票数据失败: {str(e)}")
            raise Exception(f'Failed to save zt pool data: {str(e)}')
    
    @staticmethod
    def get_zt_pool_by_date(db: Session, target_date: date) -> List[Dict]:
        """根据日期获取涨停股票池数据"""
        stocks = db.query(ZtPoolHistory).filter(
            ZtPoolHistory.date == target_date
        ).order_by(ZtPoolHistory.index).all()
        
        return [stock.to_dict() for stock in stocks]
    
    @staticmethod
    def get_zt_pool_by_date_range(db: Session, start_date: date, end_date: date) -> List[Dict]:
        """根据日期范围获取涨停股票池数据"""
        stocks = db.query(ZtPoolHistory).filter(
            and_(
                ZtPoolHistory.date >= start_date,
                ZtPoolHistory.date <= end_date
            )
        ).order_by(ZtPoolHistory.date.desc(), ZtPoolHistory.index).all()
        
        return [stock.to_dict() for stock in stocks]

