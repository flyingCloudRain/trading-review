from flask import jsonify, request
from api import api_bp
from services.zt_pool_service import ZtPoolService
from services.zt_pool_history_service import ZtPoolHistoryService
from utils.zt_pool_excel_export import export_zt_pool_to_excel
from database.db import get_db
from datetime import datetime, date

@api_bp.route('/zt-pool', methods=['GET'])
def get_zt_pool():
    """
    获取涨停股票池
    
    查询参数:
        date: 从数据库获取指定日期的数据 (格式: YYYY-MM-DD)
        api_date: 从API获取指定日期的数据 (格式: YYYYMMDD)
        save: 是否保存到数据库 (true/false, 默认false)
    """
    try:
        # 检查是否从数据库获取历史数据
        target_date_str = request.args.get('date')
        if target_date_str:
            try:
                target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
                db = next(get_db())
                stocks = ZtPoolHistoryService.get_zt_pool_by_date(db, target_date)
                return jsonify({
                    'success': True,
                    'data': stocks,
                    'count': len(stocks),
                    'date': target_date_str,
                    'source': 'database'
                })
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                }), 400
        
        # 从API获取实时数据
        api_date = request.args.get('api_date')  # 格式：YYYYMMDD
        stocks = ZtPoolService.get_zt_pool(date=api_date)
        
        # 检查是否保存到数据库
        save_to_db = request.args.get('save', 'false').lower() == 'true'
        if save_to_db:
            try:
                db = next(get_db())
                saved_count = ZtPoolHistoryService.save_today_zt_pool(db)
                return jsonify({
                    'success': True,
                    'data': stocks,
                    'count': len(stocks),
                    'saved': True,
                    'saved_count': saved_count,
                    'source': 'api'
                })
            except Exception as e:
                return jsonify({
                    'success': True,
                    'data': stocks,
                    'count': len(stocks),
                    'saved': False,
                    'save_error': str(e),
                    'source': 'api'
                })
        
        return jsonify({
            'success': True,
            'data': stocks,
            'count': len(stocks),
            'source': 'api'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/zt-pool', methods=['POST'])
def save_zt_pool():
    """
    保存当前涨停股票池到数据库
    """
    try:
        db = next(get_db())
        saved_count = ZtPoolHistoryService.save_today_zt_pool(db)
        return jsonify({
            'success': True,
            'message': f'Successfully saved {saved_count} stocks',
            'saved_count': saved_count
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/zt-pool/history', methods=['GET'])
def get_zt_pool_history():
    """
    获取涨停股票池历史数据
    
    查询参数:
        date: 获取指定日期的数据 (格式: YYYY-MM-DD)
        start_date: 开始日期 (格式: YYYY-MM-DD)
        end_date: 结束日期 (格式: YYYY-MM-DD)
    """
    try:
        db = next(get_db())
        
        # 获取指定日期的数据
        date_str = request.args.get('date')
        if date_str:
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                stocks = ZtPoolHistoryService.get_zt_pool_by_date(db, target_date)
                return jsonify({
                    'success': True,
                    'data': stocks,
                    'count': len(stocks),
                    'date': date_str
                })
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                }), 400
        
        # 获取日期范围的数据
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        if start_date_str and end_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                stocks = ZtPoolHistoryService.get_zt_pool_by_date_range(db, start_date, end_date)
                return jsonify({
                    'success': True,
                    'data': stocks,
                    'count': len(stocks),
                    'start_date': start_date_str,
                    'end_date': end_date_str
                })
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                }), 400
        
        return jsonify({
            'success': False,
            'error': 'Please provide date or start_date/end_date parameter'
        }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/zt-pool/export', methods=['POST'])
def export_zt_pool():
    """导出涨停股票池到Excel"""
    data = request.get_json() or {}
    date = data.get('date')  # 格式：YYYYMMDD
    
    try:
        excel_file = export_zt_pool_to_excel(date=date)
        return jsonify({
            'success': True,
            'message': '导出成功',
            'file': excel_file
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

