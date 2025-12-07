#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase数据库连接配置
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from config_supabase import SupabaseConfig

# 创建数据库引擎（使用Supabase PostgreSQL）
try:
    database_url = SupabaseConfig.get_database_url()
    engine = create_engine(
        database_url,
        pool_pre_ping=True,  # 连接前ping，确保连接有效
        pool_size=5,  # 连接池大小
        max_overflow=10,  # 最大溢出连接数
        echo=False  # 是否打印SQL语句
    )
except ValueError as e:
    print(f"⚠️  Supabase配置未完成: {e}")
    print("   请先配置 .env 文件中的Supabase连接信息")
    # 使用默认SQLite作为后备
    from config import Config
    engine = create_engine(
        Config.DATABASE_URL,
        connect_args={'check_same_thread': False} if 'sqlite' in Config.DATABASE_URL else {},
        echo=False
    )

# 创建会话工厂
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# 创建基类
Base = declarative_base()

def init_db():
    """初始化数据库"""
    # 导入所有模型，确保它们被注册
    from models.trading_review import TradingReview
    from models.sector_history import SectorHistory
    from models.zt_pool_history import ZtPoolHistory
    from models.zb_pool_history import ZbgcPoolHistory
    from models.dt_pool_history import DtgcPoolHistory
    from models.index_history import IndexHistory
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

