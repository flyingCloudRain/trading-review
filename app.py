from flask import Flask, jsonify
from flask_cors import CORS
from config import config
from database.db import init_db
from api import api_bp
from tasks.sector_scheduler import get_scheduler

def create_app(config_name='default'):
    """创建Flask应用"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 启用CORS
    CORS(app)
    
    # 初始化数据库
    init_db()
    
    # 注册蓝图
    app.register_blueprint(api_bp)
    
    # 启动定时任务（仅在非测试环境）
    if not app.config.get('TESTING'):
        scheduler = get_scheduler()
        scheduler.start()
    
    # 根路由
    @app.route('/')
    def index():
        return jsonify({
            'message': 'A股交易复盘系统 API',
            'version': '1.0.0',
            'endpoints': {
                'stock-index': '/api/stock-index',
                'stock-index-spot': '/api/stock-index/spot',
                'sector': '/api/sector',
                'zt-pool': '/api/zt-pool',
                'zb-pool': '/api/zb-pool',
                'dt-pool': '/api/dt-pool',
                'board-change': '/api/board-change',
                'trading-review': '/api/trading-review'
            }
        })
    
    # 健康检查
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'message': 'Service is running'
        })
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)

