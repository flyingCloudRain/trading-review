import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 项目根目录
BASE_DIR = Path(__file__).parent

# 数据目录
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)

class Config:
    """应用配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 数据库配置
    DATABASE_URL = os.environ.get('DATABASE_URL') or f'sqlite:///{DATA_DIR}/trading_review.db'
    
    # Flask配置
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = False
    
    # API配置
    JSON_AS_ASCII = False  # 支持中文JSON响应
    
    # akshare配置
    AKSHARE_TIMEOUT = 30  # 请求超时时间（秒）

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'

# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

