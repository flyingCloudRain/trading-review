#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase数据库连接配置
强制使用 Supabase PostgreSQL，不支持 SQLite 后备
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from config_supabase import SupabaseConfig

# 创建数据库引擎（强制使用Supabase PostgreSQL）
try:
    database_url = SupabaseConfig.get_database_url()
    engine = create_engine(
        database_url,
        pool_pre_ping=True,  # 连接前ping，确保连接有效
        pool_size=5,  # 连接池大小
        max_overflow=10,  # 最大溢出连接数
        echo=False  # 是否打印SQL语句
    )
    print("✅ 已连接到 Supabase PostgreSQL 数据库")
except ValueError as e:
    error_msg = f"""
❌ Supabase配置未完成: {e}

请配置以下环境变量：
- SUPABASE_PROJECT_REF: Supabase项目引用ID
- SUPABASE_DB_PASSWORD: Supabase数据库密码

或者在 Streamlit Cloud Secrets 中配置：
- SUPABASE_PROJECT_REF
- SUPABASE_DB_PASSWORD
- SUPABASE_URL (可选)
- SUPABASE_ANON_KEY (可选)

详细配置说明请查看: SUPABASE_SETUP.md
"""
    print(error_msg)
    raise RuntimeError("Supabase配置不完整，无法连接数据库。请配置必要的环境变量。") from e
except Exception as e:
    error_msg = f"""
❌ 连接 Supabase 数据库失败: {str(e)}

请检查：
1. Supabase 配置是否正确
2. 网络连接是否正常
3. Supabase 服务是否可用

详细配置说明请查看: SUPABASE_SETUP.md
"""
    print(error_msg)
    raise RuntimeError("无法连接到 Supabase 数据库") from e

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

