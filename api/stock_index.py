from flask import jsonify, request
from api import api_bp
from services.stock_index_service import StockIndexService

@api_bp.route('/stock-index', methods=['GET'])
def get_all_indices():
    """获取所有指数"""
    try:
        indices = StockIndexService.get_all_indices()
        return jsonify({
            'success': True,
            'data': indices,
            'count': len(indices)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/stock-index/<code>', methods=['GET'])
def get_index(code):
    """获取指定指数信息"""
    try:
        index = StockIndexService.get_index_info(code)
        return jsonify({
            'success': True,
            'data': index
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

@api_bp.route('/stock-index/search', methods=['GET'])
def search_index():
    """搜索指数"""
    keyword = request.args.get('keyword', '')
    if not keyword:
        return jsonify({
            'success': False,
            'error': 'Keyword parameter is required'
        }), 400
    
    try:
        indices = StockIndexService.search_by_name(keyword)
        return jsonify({
            'success': True,
            'data': indices,
            'count': len(indices)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/stock-index/codes', methods=['GET'])
def get_index_codes():
    """获取指数代码列表"""
    try:
        codes = StockIndexService.get_index_codes()
        return jsonify({
            'success': True,
            'data': codes
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/stock-index/spot', methods=['GET'])
def get_index_spot():
    """
    获取指数实时行情（使用 stock_zh_index_spot_em）
    
    查询参数:
        symbol: 指数系列，可选值：
               - "上证系列指数"
               - "深证系列指数"
               - 不传则获取所有指数
    
    返回所有指数的实时行情数据
    """
    try:
        symbol = request.args.get('symbol', None)
        indices = StockIndexService.get_index_spot(symbol=symbol)
        return jsonify({
            'success': True,
            'data': indices,
            'count': len(indices),
            'source': 'akshare.stock_zh_index_spot_em',
            'symbol': symbol if symbol else '全部指数'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

