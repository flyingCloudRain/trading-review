from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.trading_review import TradingReview
from datetime import datetime
import re

class TradingReviewService:
    """交易复盘记录服务"""
    
    @staticmethod
    def create_review(db: Session, review_data: Dict) -> TradingReview:
        """创建交易复盘记录"""
        # 验证数据
        TradingReviewService._validate_review(review_data)
        
        # 计算总金额（如果价格和数量都提供了）
        if 'totalAmount' not in review_data or review_data.get('totalAmount') is None:
            if 'price' in review_data and 'quantity' in review_data and review_data.get('price') is not None and review_data.get('quantity') is not None:
                review_data['totalAmount'] = review_data['price'] * review_data['quantity']
            else:
                review_data['totalAmount'] = None  # 如果价格或数量为空，总金额也为空
        
        # 处理股票代码和名称（确保至少有一个不为空）
        stock_code = review_data.get('stockCode', '').strip() if review_data.get('stockCode') else ''
        stock_name = review_data.get('stockName', '').strip() if review_data.get('stockName') else ''
        
        # 如果某个字段为空，使用另一个字段的值（如果另一个也不为空）
        if not stock_code and stock_name:
            stock_code = stock_name  # 如果代码为空但名称不为空，使用名称作为代码
        elif not stock_name and stock_code:
            stock_name = stock_code  # 如果名称为空但代码不为空，使用代码作为名称
        elif not stock_code and not stock_name:
            # 如果都为空，使用默认值（这种情况应该已经被验证逻辑捕获，但为了安全起见）
            stock_code = "未知"
            stock_name = "未知"
        
        # 创建记录
        review = TradingReview(
            date=review_data['date'],
            market=review_data.get('market', 'A股'),
            stock_code=stock_code,
            stock_name=stock_name,
            operation=review_data['operation'],
            price=review_data['price'],
            quantity=review_data['quantity'],
            total_amount=review_data.get('totalAmount'),
            reason=review_data['reason'],
            review=review_data.get('review'),
            profit=review_data.get('profit'),
            profit_percent=review_data.get('profitPercent'),
            take_profit_price=review_data.get('takeProfitPrice'),
            stop_loss_price=review_data.get('stopLossPrice'),
        )
        
        db.add(review)
        db.commit()
        db.refresh(review)
        return review
    
    @staticmethod
    def get_all_reviews(db: Session, limit: Optional[int] = None, offset: int = 0) -> List[TradingReview]:
        """获取所有交易复盘记录"""
        query = db.query(TradingReview).order_by(TradingReview.date.desc(), TradingReview.created_at.desc())
        
        if limit:
            query = query.limit(limit).offset(offset)
        
        return query.all()
    
    @staticmethod
    def get_review_by_id(db: Session, review_id: int) -> Optional[TradingReview]:
        """根据ID获取交易复盘记录"""
        return db.query(TradingReview).filter(TradingReview.id == review_id).first()
    
    @staticmethod
    def get_reviews_by_date(db: Session, date: str) -> List[TradingReview]:
        """根据日期获取交易复盘记录"""
        TradingReviewService._validate_date(date)
        return db.query(TradingReview).filter(TradingReview.date == date).order_by(TradingReview.created_at.desc()).all()
    
    @staticmethod
    def get_reviews_by_stock_code(db: Session, stock_code: str) -> List[TradingReview]:
        """根据股票代码获取交易复盘记录"""
        if not stock_code or not stock_code.strip():
            raise ValueError('Stock code is required')
        
        return db.query(TradingReview).filter(TradingReview.stock_code == stock_code.strip()).order_by(TradingReview.date.desc()).all()
    
    @staticmethod
    def update_review(db: Session, review_id: int, review_data: Dict) -> Optional[TradingReview]:
        """更新交易复盘记录"""
        review = TradingReviewService.get_review_by_id(db, review_id)
        if not review:
            return None
        
        # 更新字段
        if 'date' in review_data:
            TradingReviewService._validate_date(review_data['date'])
            review.date = review_data['date']
        
        if 'market' in review_data:
            if review_data['market'] not in ['A股', '美股']:
                raise ValueError('Market must be "A股" or "美股"')
            review.market = review_data['market']
        
        if 'stockCode' in review_data or 'stockName' in review_data:
            # 处理股票代码和名称（确保至少有一个不为空）
            stock_code = review_data.get('stockCode', '').strip() if review_data.get('stockCode') else ''
            stock_name = review_data.get('stockName', '').strip() if review_data.get('stockName') else ''
            
            # 如果某个字段为空，使用另一个字段的值（如果另一个也不为空）
            if not stock_code and stock_name:
                stock_code = stock_name  # 如果代码为空但名称不为空，使用名称作为代码
            elif not stock_name and stock_code:
                stock_name = stock_code  # 如果名称为空但代码不为空，使用代码作为名称
            elif not stock_code and not stock_name:
                # 如果都为空，使用默认值（这种情况应该已经被验证逻辑捕获，但为了安全起见）
                stock_code = "未知"
                stock_name = "未知"
            
            review.stock_code = stock_code
            review.stock_name = stock_name
        
        if 'operation' in review_data:
            if review_data['operation'] not in ['buy', 'sell']:
                raise ValueError('Operation must be "buy" or "sell"')
            review.operation = review_data['operation']
        
        if 'price' in review_data:
            if review_data['price'] is None or review_data['price'] <= 0:
                raise ValueError('Price is required and must be greater than 0')
            review.price = review_data['price']
        
        if 'quantity' in review_data:
            if review_data['quantity'] is None or review_data['quantity'] <= 0:
                raise ValueError('Quantity is required and must be greater than 0')
            review.quantity = review_data['quantity']
        
        if 'totalAmount' in review_data:
            review.total_amount = review_data['totalAmount']
        elif 'price' in review_data or 'quantity' in review_data:
            # 重新计算总金额
            review.total_amount = review.price * review.quantity
        
        if 'reason' in review_data:
            review.reason = review_data['reason']
        
        if 'review' in review_data:
            review.review = review_data['review']
        
        if 'profit' in review_data:
            review.profit = review_data['profit']
        
        if 'profitPercent' in review_data:
            review.profit_percent = review_data['profitPercent']
        
        if 'takeProfitPrice' in review_data:
            review.take_profit_price = review_data['takeProfitPrice']
        
        if 'stopLossPrice' in review_data:
            review.stop_loss_price = review_data['stopLossPrice']
        
        db.commit()
        db.refresh(review)
        return review
    
    @staticmethod
    def delete_review(db: Session, review_id: int) -> bool:
        """删除交易复盘记录"""
        review = TradingReviewService.get_review_by_id(db, review_id)
        if not review:
            return False
        
        db.delete(review)
        db.commit()
        return True
    
    @staticmethod
    def get_statistics(db: Session) -> Dict:
        """获取统计信息"""
        total_records = db.query(func.count(TradingReview.id)).scalar()
        
        # 计算盈亏统计
        from sqlalchemy import case
        profit_stats = db.query(
            func.sum(TradingReview.profit).label('total_profit'),
            func.sum(case((TradingReview.profit > 0, 1), else_=0)).label('win_count'),
            func.sum(case((TradingReview.profit < 0, 1), else_=0)).label('loss_count'),
        ).filter(TradingReview.profit.isnot(None)).first()
        
        return {
            'totalRecords': total_records or 0,
            'totalProfit': float(profit_stats.total_profit) if profit_stats.total_profit else 0,
            'winCount': profit_stats.win_count or 0,
            'lossCount': profit_stats.loss_count or 0,
        }
    
    @staticmethod
    def _validate_review(review_data: Dict):
        """验证交易复盘记录数据"""
        required_fields = ['date', 'operation', 'price', 'quantity', 'reason']
        for field in required_fields:
            if field not in review_data or review_data[field] is None:
                raise ValueError(f'{field} is required')
        
        # 股票代码和名称不能同时为空
        stock_code = review_data.get('stockCode', '').strip() if review_data.get('stockCode') else ''
        stock_name = review_data.get('stockName', '').strip() if review_data.get('stockName') else ''
        if not stock_code and not stock_name:
            raise ValueError('Stock code and stock name cannot both be empty')
        
        TradingReviewService._validate_date(review_data['date'])
        
        if review_data['operation'] not in ['buy', 'sell']:
            raise ValueError('Operation must be "buy" or "sell"')
        
        # 价格必须大于0
        if review_data['price'] is None or review_data['price'] <= 0:
            raise ValueError('Price is required and must be greater than 0')
        
        # 数量必须大于0
        if review_data['quantity'] is None or review_data['quantity'] <= 0:
            raise ValueError('Quantity is required and must be greater than 0')
    
    @staticmethod
    def _validate_date(date: str):
        """验证日期格式"""
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        if not date_pattern.match(date):
            raise ValueError('Date must be in format YYYY-MM-DD')
        
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise ValueError('Invalid date')

