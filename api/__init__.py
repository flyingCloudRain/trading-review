from flask import Blueprint

# 创建API蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')

# 导入所有路由（必须在蓝图创建后导入）
from . import stock_index, sector, trading_review, zt_pool, zb_pool, dt_pool, board_change

