from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date
from models.index_history import IndexHistory
from services.stock_index_service import StockIndexService
from utils.time_utils import get_data_date

class IndexHistoryService:
    """指数历史数据服务"""
    
    @staticmethod
    def save_today_indices(db: Session) -> int:
        """
        保存指数数据（自动判断日期）
        - 如果在交易时间内，使用当前日期
        - 如果不在交易时间内，使用上一个交易日
        """
        data_date = get_data_date()
        
        # 检查该日期的数据是否已存在
        existing = db.query(IndexHistory).filter(IndexHistory.date == data_date).first()
        if existing:
            # 如果已存在，先删除旧数据
            db.query(IndexHistory).filter(IndexHistory.date == data_date).delete()
            db.commit()
        
        # 获取当前指数数据（尝试多个数据源）
        indices = []
        error_msg = None
        
        # 方法1: 优先使用 stock_zh_index_spot_sina（新浪接口）作为主要数据源
        # 该接口数据更完整，包含所有深证系列指数（564条数据，包含355个深证指数）
        try:
            print("🔄 使用 stock_zh_index_spot_sina 接口获取指数数据（主要数据源）...")
            indices = StockIndexService.get_index_spot_sina()
            print(f"✅ 使用 stock_zh_index_spot_sina 成功获取 {len(indices)} 条指数数据")
        except Exception as e:
            error_msg = str(e)
            print(f"⚠️ 使用 stock_zh_index_spot_sina 获取指数数据失败: {error_msg}")
        
        # 方法2: 如果方法1失败，尝试使用 stock_zh_index_spot_em 作为备用数据源
        if not indices:
            try:
                print("🔄 尝试使用 stock_zh_index_spot_em 接口获取指数数据（备用数据源）...")
                indices = StockIndexService.get_index_spot()
                print(f"✅ 使用 stock_zh_index_spot_em 成功获取 {len(indices)} 条指数数据")
            except Exception as e:
                error_msg = str(e)
                print(f"⚠️ 使用 stock_zh_index_spot_em 获取指数数据失败: {error_msg}")
        
        # 方法2.5: 如果使用 stock_zh_index_spot_em 成功但缺少深证系列，尝试单独获取深证系列指数
        if indices:
            # 检查是否有399开头的指数
            has_sz_indices = any(str(idx.get('code', '')).startswith('399') for idx in indices)
            if not has_sz_indices:
                try:
                    print("🔄 检测到缺少深证系列指数，尝试单独获取...")
                    sz_indices = StockIndexService.get_index_spot(symbol="深证系列指数")
                    if sz_indices:
                        print(f"✅ 成功获取 {len(sz_indices)} 条深证系列指数数据")
                        # 合并数据，去重
                        existing_codes = {str(idx.get('code', '')) for idx in indices}
                        for sz_idx in sz_indices:
                            sz_code = str(sz_idx.get('code', ''))
                            if sz_code not in existing_codes:
                                indices.append(sz_idx)
                                existing_codes.add(sz_code)
                except Exception as e:
                    print(f"⚠️ 获取深证系列指数失败: {str(e)}")
        
        if not indices:
            raise Exception(f'Failed to get index spot data from all sources. Last error: {error_msg}')
        
        if not indices:
            return 0
        
        # 保存到数据库
        saved_count = 0
        for index_data in indices:
            history = IndexHistory(
                date=data_date,
                code=index_data.get('code', ''),
                name=index_data.get('name', ''),
                current_price=index_data.get('currentPrice', 0),
                change_percent=index_data.get('changePercent', 0),
                change=index_data.get('change', 0),
                volume=index_data.get('volume', 0),
                amount=index_data.get('amount', 0),
                open=index_data.get('open', 0),
                high=index_data.get('high', 0),
                low=index_data.get('low', 0),
                prev_close=index_data.get('prevClose', 0),
                amplitude=index_data.get('amplitude', 0),
                volume_ratio=index_data.get('volumeRatio', 0),
            )
            db.add(history)
            saved_count += 1
        
        db.commit()
        return saved_count
    
    @staticmethod
    def get_indices_by_date(db: Session, target_date: date) -> List[Dict]:
        """根据日期获取指数数据"""
        indices = db.query(IndexHistory).filter(
            IndexHistory.date == target_date
        ).order_by(IndexHistory.code).all()
        
        return [index.to_dict() for index in indices]
    
    @staticmethod
    def get_indices_by_date_range(db: Session, start_date: date, end_date: date) -> List[Dict]:
        """根据日期范围获取指数数据"""
        indices = db.query(IndexHistory).filter(
            and_(
                IndexHistory.date >= start_date,
                IndexHistory.date <= end_date
            )
        ).order_by(IndexHistory.date.desc(), IndexHistory.code).all()
        
        return [index.to_dict() for index in indices]
    
    @staticmethod
    def get_index_by_code_and_date_range(db: Session, code: str, start_date: date, end_date: date) -> List[Dict]:
        """根据指数代码和日期范围获取数据"""
        indices = db.query(IndexHistory).filter(
            and_(
                IndexHistory.code == code,
                IndexHistory.date >= start_date,
                IndexHistory.date <= end_date
            )
        ).order_by(IndexHistory.date.asc()).all()
        
        return [index.to_dict() for index in indices]

