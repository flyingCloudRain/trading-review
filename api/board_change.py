from flask import jsonify, request
from api import api_bp
from services.board_change_service import BoardChangeService
from utils.board_change_excel_export import export_board_changes_to_excel

@api_bp.route('/board-change', methods=['GET'])
def get_board_changes():
    """获取板块异动"""
    try:
        boards = BoardChangeService.get_board_changes()
        return jsonify({
            'success': True,
            'data': boards,
            'count': len(boards)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/board-change/export', methods=['POST'])
def export_board_changes():
    """导出板块异动到Excel"""
    try:
        excel_file = export_board_changes_to_excel()
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

