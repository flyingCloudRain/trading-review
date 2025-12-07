import pytest
from datetime import datetime
from services.trading_review_service import TradingReviewService
from database.db import SessionLocal, Base, engine
from models.trading_review import TradingReview

@pytest.fixture
def db_session():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.rollback()
    db.close()

@pytest.fixture
def sample_review_data():
    """示例交易复盘数据"""
    return {
        'date': '2024-01-15',
        'stockCode': '000001',
        'stockName': '平安银行',
        'operation': 'buy',
        'price': 10.5,
        'quantity': 1000,
        'totalAmount': 10500,
        'reason': '技术面突破',
        'review': '买入后继续观察',
        'profit': 500,
        'profitPercent': 4.76
    }

class TestTradingReviewService:
    """交易复盘服务测试"""
    
    def test_create_review(self, db_session, sample_review_data):
        """测试创建交易复盘记录"""
        review = TradingReviewService.create_review(db_session, sample_review_data)
        assert review.id is not None
        assert review.stock_code == sample_review_data['stockCode']
        assert review.operation == sample_review_data['operation']
    
    def test_create_review_auto_calculate_total(self, db_session, sample_review_data):
        """测试自动计算总金额"""
        del sample_review_data['totalAmount']
        review = TradingReviewService.create_review(db_session, sample_review_data)
        assert review.total_amount == sample_review_data['price'] * sample_review_data['quantity']
    
    def test_create_review_validation(self, db_session, sample_review_data):
        """测试创建记录时的验证"""
        # 缺少必填字段
        invalid_data = sample_review_data.copy()
        del invalid_data['date']
        
        with pytest.raises(ValueError):
            TradingReviewService.create_review(db_session, invalid_data)
    
    def test_get_all_reviews(self, db_session, sample_review_data):
        """测试获取所有记录"""
        # 创建几条记录
        TradingReviewService.create_review(db_session, sample_review_data)
        sample_review_data['stockCode'] = '000002'
        TradingReviewService.create_review(db_session, sample_review_data)
        
        reviews = TradingReviewService.get_all_reviews(db_session)
        assert len(reviews) >= 2
    
    def test_get_review_by_id(self, db_session, sample_review_data):
        """测试根据ID获取记录"""
        review = TradingReviewService.create_review(db_session, sample_review_data)
        found_review = TradingReviewService.get_review_by_id(db_session, review.id)
        assert found_review is not None
        assert found_review.id == review.id
    
    def test_get_reviews_by_date(self, db_session, sample_review_data):
        """测试按日期查询"""
        TradingReviewService.create_review(db_session, sample_review_data)
        reviews = TradingReviewService.get_reviews_by_date(db_session, '2024-01-15')
        assert len(reviews) > 0
        for review in reviews:
            assert review.date == '2024-01-15'
    
    def test_get_reviews_by_stock_code(self, db_session, sample_review_data):
        """测试按股票代码查询"""
        TradingReviewService.create_review(db_session, sample_review_data)
        reviews = TradingReviewService.get_reviews_by_stock_code(db_session, '000001')
        assert len(reviews) > 0
        for review in reviews:
            assert review.stock_code == '000001'
    
    def test_update_review(self, db_session, sample_review_data):
        """测试更新记录"""
        review = TradingReviewService.create_review(db_session, sample_review_data)
        update_data = {'price': 11.0, 'quantity': 1200}
        updated_review = TradingReviewService.update_review(db_session, review.id, update_data)
        assert updated_review.price == 11.0
        assert updated_review.quantity == 1200
    
    def test_delete_review(self, db_session, sample_review_data):
        """测试删除记录"""
        review = TradingReviewService.create_review(db_session, sample_review_data)
        success = TradingReviewService.delete_review(db_session, review.id)
        assert success is True
        
        # 验证已删除
        found_review = TradingReviewService.get_review_by_id(db_session, review.id)
        assert found_review is None
    
    def test_get_statistics(self, db_session, sample_review_data):
        """测试获取统计信息"""
        TradingReviewService.create_review(db_session, sample_review_data)
        stats = TradingReviewService.get_statistics(db_session)
        assert 'totalRecords' in stats
        assert 'totalProfit' in stats
        assert 'winCount' in stats
        assert 'lossCount' in stats

