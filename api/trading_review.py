from flask import jsonify, request
from api import api_bp
from services.trading_review_service import TradingReviewService
from database.db import get_db

@api_bp.route('/trading-review', methods=['GET'])
def get_all_reviews():
    """获取所有交易复盘记录"""
    limit = request.args.get('limit', type=int)
    offset = request.args.get('offset', 0, type=int)
    
    db = next(get_db())
    try:
        reviews = TradingReviewService.get_all_reviews(db, limit=limit, offset=offset)
        return jsonify({
            'success': True,
            'data': [review.to_dict() for review in reviews],
            'count': len(reviews)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/trading-review/<int:review_id>', methods=['GET'])
def get_review(review_id):
    """获取指定交易复盘记录"""
    db = next(get_db())
    try:
        review = TradingReviewService.get_review_by_id(db, review_id)
        if not review:
            return jsonify({
                'success': False,
                'error': 'Review not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': review.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/trading-review', methods=['POST'])
def create_review():
    """创建交易复盘记录"""
    data = request.get_json()
    if not data:
        return jsonify({
            'success': False,
            'error': 'Request body is required'
        }), 400
    
    db = next(get_db())
    try:
        review = TradingReviewService.create_review(db, data)
        return jsonify({
            'success': True,
            'data': review.to_dict()
        }), 201
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/trading-review/<int:review_id>', methods=['PUT'])
def update_review(review_id):
    """更新交易复盘记录"""
    data = request.get_json()
    if not data:
        return jsonify({
            'success': False,
            'error': 'Request body is required'
        }), 400
    
    db = next(get_db())
    try:
        review = TradingReviewService.update_review(db, review_id, data)
        if not review:
            return jsonify({
                'success': False,
                'error': 'Review not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': review.to_dict()
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/trading-review/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    """删除交易复盘记录"""
    db = next(get_db())
    try:
        success = TradingReviewService.delete_review(db, review_id)
        if not success:
            return jsonify({
                'success': False,
                'error': 'Review not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Review deleted successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/trading-review/date/<date>', methods=['GET'])
def get_reviews_by_date(date):
    """按日期查询交易复盘记录"""
    db = next(get_db())
    try:
        reviews = TradingReviewService.get_reviews_by_date(db, date)
        return jsonify({
            'success': True,
            'data': [review.to_dict() for review in reviews],
            'count': len(reviews)
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/trading-review/stock/<stock_code>', methods=['GET'])
def get_reviews_by_stock(stock_code):
    """按股票代码查询交易复盘记录"""
    db = next(get_db())
    try:
        reviews = TradingReviewService.get_reviews_by_stock_code(db, stock_code)
        return jsonify({
            'success': True,
            'data': [review.to_dict() for review in reviews],
            'count': len(reviews)
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/trading-review/statistics', methods=['GET'])
def get_statistics():
    """获取统计信息"""
    db = next(get_db())
    try:
        stats = TradingReviewService.get_statistics(db)
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

