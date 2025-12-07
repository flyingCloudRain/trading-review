from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import date, datetime, time
from models.sector_history import SectorHistory
from services.sector_service import SectorService
from services.concept_service import ConceptService
from utils.time_utils import get_data_date

class SectorHistoryService:
    """板块历史数据服务（支持行业板块和概念板块）"""
    
    @staticmethod
    def save_today_sectors(db: Session, sector_type: str = 'industry') -> int:
        """
        保存板块数据（自动判断日期）
        - 如果在交易时间内，使用当前日期
        - 如果不在交易时间内，使用上一个交易日
        
        使用事务和锁机制防止重复数据：
        1. 先获取数据（避免在删除后获取数据时出现问题）
        2. 在事务中删除旧数据
        3. 在事务中保存新数据
        
        Args:
            sector_type: 板块类型，'industry'（行业板块）或 'concept'（概念板块）
        """
        data_date = get_data_date()
        
        # 验证板块类型
        if sector_type not in ['industry', 'concept']:
            raise ValueError(f"Invalid sector_type: {sector_type}. Must be 'industry' or 'concept'")
        
        try:
            # 根据类型获取板块数据
            if sector_type == 'industry':
                sectors = SectorService.get_industry_summary()
            else:
                sectors = ConceptService.get_concept_summary()
            
            if not sectors:
                print(f"⚠️  警告: {data_date} 没有获取到{sector_type}板块数据")
                return 0
            
            # 在事务中删除旧数据并保存新数据
            # 检查该日期和类型的数据是否已存在
            existing_count = db.query(SectorHistory).filter(
                SectorHistory.date == data_date,
                SectorHistory.sector_type == sector_type
            ).count()
            if existing_count > 0:
                # 如果已存在，先删除旧数据
                deleted_count = db.query(SectorHistory).filter(
                    SectorHistory.date == data_date,
                    SectorHistory.sector_type == sector_type
                ).delete()
                print(f"🗑️  删除 {data_date} 的{sector_type}板块旧数据: {deleted_count} 条")
                # 立即提交删除操作，确保数据一致性
                db.commit()
            
            # 保存新数据
            saved_count = 0
            for sector in sectors:
                history = SectorHistory(
                    date=data_date,
                    sector_type=sector_type,
                    index=sector['index'],
                    name=sector['name'],
                    change_percent=sector['changePercent'],
                    total_volume=sector['totalVolume'],
                    total_amount=sector['totalAmount'],
                    net_inflow=sector['netInflow'],
                    up_count=sector['upCount'],
                    down_count=sector['downCount'],
                    avg_price=sector['avgPrice'],
                    leading_stock=sector['leadingStock'],
                    leading_stock_price=sector['leadingStockPrice'],
                    leading_stock_change_percent=sector['leadingStockChangePercent'],
                )
                db.add(history)
                saved_count += 1
            
            # 提交新数据
            db.commit()
            print(f"✅ 成功保存 {saved_count} 条{sector_type}板块数据到数据库 ({data_date})")
            return saved_count
            
        except Exception as e:
            db.rollback()
            print(f"❌ 保存{sector_type}板块数据失败: {str(e)}")
            raise
    
    @staticmethod
    def get_sectors_by_date(db: Session, target_date: date, sector_type: Optional[str] = None) -> List[Dict]:
        """
        根据日期获取板块数据
        
        Args:
            target_date: 目标日期
            sector_type: 板块类型，'industry'（行业板块）或 'concept'（概念板块），None表示获取所有类型
        """
        query = db.query(SectorHistory).filter(SectorHistory.date == target_date)
        
        if sector_type:
            query = query.filter(SectorHistory.sector_type == sector_type)
        
        sectors = query.order_by(SectorHistory.index).all()
        
        return [sector.to_dict() for sector in sectors]
    
    @staticmethod
    def get_sectors_by_date_range(db: Session, start_date: date, end_date: date, sector_type: Optional[str] = None) -> List[Dict]:
        """
        根据日期范围获取板块数据
        时间范围：开始日期从00:00:00开始，结束日期到23:59:59
        
        注意：由于date字段是Date类型，查询已包含完整的一天
        如果将来需要基于created_at进行精确时间查询，可以使用datetime范围
        
        Args:
            start_date: 开始日期（包含，从00:00:00开始）
            end_date: 结束日期（包含，到23:59:59结束）
            sector_type: 板块类型，'industry'（行业板块）或 'concept'（概念板块），None表示获取所有类型
        """
        # 查询date字段在范围内的数据
        query = db.query(SectorHistory).filter(
            and_(
                SectorHistory.date >= start_date,
                SectorHistory.date <= end_date
            )
        )
        
        if sector_type:
            query = query.filter(SectorHistory.sector_type == sector_type)
        
        sectors = query.order_by(SectorHistory.date.desc(), SectorHistory.index).all()
        
        return [sector.to_dict() for sector in sectors]
    
    @staticmethod
    def get_all_dates(db: Session) -> List[date]:
        """获取所有有数据的日期"""
        dates = db.query(SectorHistory.date).distinct().order_by(SectorHistory.date.desc()).all()
        return [d[0] for d in dates]

