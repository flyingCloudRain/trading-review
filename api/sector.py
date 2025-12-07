from flask import jsonify, request
from api import api_bp
from services.sector_service import SectorService
from services.concept_service import ConceptService
from services.sector_history_service import SectorHistoryService
from database.db import get_db
from datetime import datetime, date

@api_bp.route('/sector', methods=['GET'])
def get_all_sectors():
    """
    获取所有板块信息（同花顺行业一览表或概念一览表）
    
    查询参数:
        save: 是否保存到数据库 (true/false, 默认false)
        date: 从数据库获取指定日期的数据 (格式: YYYY-MM-DD)
        type: 板块类型，'industry'（行业板块）或 'concept'（概念板块），默认'industry'
    """
    try:
        # 获取板块类型
        sector_type = request.args.get('type', 'industry').lower()
        if sector_type not in ['industry', 'concept']:
            return jsonify({
                'success': False,
                'error': "Invalid type parameter. Must be 'industry' or 'concept'"
            }), 400
        
        # 检查是否从数据库获取历史数据
        target_date_str = request.args.get('date')
        if target_date_str:
            try:
                target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
                db = next(get_db())
                sectors = SectorHistoryService.get_sectors_by_date(db, target_date, sector_type)
                return jsonify({
                    'success': True,
                    'data': sectors,
                    'count': len(sectors),
                    'date': target_date_str,
                    'type': sector_type,
                    'source': 'database'
                })
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                }), 400
        
        # 从API获取实时数据
        if sector_type == 'industry':
            sectors = SectorService.get_industry_summary()
        else:
            sectors = ConceptService.get_concept_summary()
        
        # 检查是否保存到数据库
        save_to_db = request.args.get('save', 'false').lower() == 'true'
        if save_to_db:
            try:
                db = next(get_db())
                saved_count = SectorHistoryService.save_today_sectors(db, sector_type)
                return jsonify({
                    'success': True,
                    'data': sectors,
                    'count': len(sectors),
                    'saved': True,
                    'saved_count': saved_count,
                    'type': sector_type,
                    'source': 'api'
                })
            except Exception as e:
                return jsonify({
                    'success': True,
                    'data': sectors,
                    'count': len(sectors),
                    'saved': False,
                    'save_error': str(e),
                    'type': sector_type,
                    'source': 'api'
                })
        
        return jsonify({
            'success': True,
            'data': sectors,
            'count': len(sectors),
            'type': sector_type,
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
    
    请求体参数（JSON）:
        type: 板块类型，'industry'（行业板块）或 'concept'（概念板块），默认'industry'
    """
    try:
        sector_type = request.json.get('type', 'industry').lower() if request.json else 'industry'
        if sector_type not in ['industry', 'concept']:
            return jsonify({
                'success': False,
                'error': "Invalid type parameter. Must be 'industry' or 'concept'"
            }), 400
        
        db = next(get_db())
        saved_count = SectorHistoryService.save_today_sectors(db, sector_type)
        return jsonify({
            'success': True,
            'message': f'Successfully saved {saved_count} {sector_type} sectors',
            'saved_count': saved_count,
            'type': sector_type
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
        type: 板块类型，'industry'（行业板块）或 'concept'（概念板块），None表示获取所有类型
    """
    try:
        db = next(get_db())
        
        # 获取板块类型
        sector_type = request.args.get('type')
        if sector_type and sector_type.lower() not in ['industry', 'concept']:
            return jsonify({
                'success': False,
                'error': "Invalid type parameter. Must be 'industry' or 'concept'"
            }), 400
        if sector_type:
            sector_type = sector_type.lower()
        
        # 获取所有日期列表
        if request.args.get('dates', 'false').lower() == 'true':
            dates = SectorHistoryService.get_all_dates(db)
            return jsonify({
                'success': True,
                'dates': [d.strftime('%Y-%m-%d') for d in dates],
                'count': len(dates),
                'type': sector_type
            })
        
        # 获取指定日期的数据
        date_str = request.args.get('date')
        if date_str:
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                sectors = SectorHistoryService.get_sectors_by_date(db, target_date, sector_type)
                return jsonify({
                    'success': True,
                    'data': sectors,
                    'count': len(sectors),
                    'date': date_str,
                    'type': sector_type
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
                sectors = SectorHistoryService.get_sectors_by_date_range(db, start_date, end_date, sector_type)
                return jsonify({
                    'success': True,
                    'data': sectors,
                    'count': len(sectors),
                    'start_date': start_date_str,
                    'end_date': end_date_str,
                    'type': sector_type
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
