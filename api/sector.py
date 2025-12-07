from flask import jsonify, request
from api import api_bp
from services.sector_service import SectorService
from services.sector_history_service import SectorHistoryService
from database.db import get_db
from datetime import datetime, date

@api_bp.route('/sector', methods=['GET'])
def get_all_sectors():
    """
    获取所有板块信息（同花顺行业一览表）
    
    查询参数:
        save: 是否保存到数据库 (true/false, 默认false)
        date: 从数据库获取指定日期的数据 (格式: YYYY-MM-DD)
    """
    try:
        # 检查是否从数据库获取历史数据
        target_date_str = request.args.get('date')
        if target_date_str:
            try:
                target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
                db = next(get_db())
                sectors = SectorHistoryService.get_sectors_by_date(db, target_date)
                return jsonify({
                    'success': True,
                    'data': sectors,
                    'count': len(sectors),
                    'date': target_date_str,
                    'source': 'database'
                })
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                }), 400
        
        # 从API获取实时数据
        sectors = SectorService.get_industry_summary()
        
        # 检查是否保存到数据库
        save_to_db = request.args.get('save', 'false').lower() == 'true'
        if save_to_db:
            try:
                db = next(get_db())
                saved_count = SectorHistoryService.save_today_sectors(db)
                return jsonify({
                    'success': True,
                    'data': sectors,
                    'count': len(sectors),
                    'saved': True,
                    'saved_count': saved_count,
                    'source': 'api'
                })
            except Exception as e:
                return jsonify({
                    'success': True,
                    'data': sectors,
                    'count': len(sectors),
                    'saved': False,
                    'save_error': str(e),
                    'source': 'api'
                })
        
        return jsonify({
            'success': True,
            'data': sectors,
            'count': len(sectors),
            'source': 'api'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/sector', methods=['POST'])
def save_sectors():
    """
    保存当前板块信息到数据库
    """
    try:
        db = next(get_db())
        saved_count = SectorHistoryService.save_today_sectors(db)
        return jsonify({
            'success': True,
            'message': f'Successfully saved {saved_count} sectors',
            'saved_count': saved_count
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/sector/history', methods=['GET'])
def get_sector_history():
    """
    获取板块历史数据
    
    查询参数:
        date: 获取指定日期的数据 (格式: YYYY-MM-DD)
        start_date: 开始日期 (格式: YYYY-MM-DD)
        end_date: 结束日期 (格式: YYYY-MM-DD)
        dates: 获取所有有数据的日期列表 (true/false)
    """
    try:
        db = next(get_db())
        
        # 获取所有日期列表
        if request.args.get('dates', 'false').lower() == 'true':
            dates = SectorHistoryService.get_all_dates(db)
            return jsonify({
                'success': True,
                'dates': [d.strftime('%Y-%m-%d') for d in dates],
                'count': len(dates)
            })
        
        # 获取指定日期的数据
        date_str = request.args.get('date')
        if date_str:
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                sectors = SectorHistoryService.get_sectors_by_date(db, target_date)
                return jsonify({
                    'success': True,
                    'data': sectors,
                    'count': len(sectors),
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
                sectors = SectorHistoryService.get_sectors_by_date_range(db, start_date, end_date)
                return jsonify({
                    'success': True,
                    'data': sectors,
                    'count': len(sectors),
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
            'error': 'Please provide date, start_date/end_date, or dates=true parameter'
        }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
