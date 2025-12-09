#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase数据库连接配置
强制使用 Supabase PostgreSQL，不支持 SQLite 后备
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from config_supabase import SupabaseConfig
import logging

logger = logging.getLogger(__name__)

# 创建数据库引擎（强制使用Supabase PostgreSQL）
try:
    # 优先使用连接池 URI 或完整 URI（可以避免 IPv6 问题）
    # 如果失败，会自动回退到标准连接
    try:
        database_url = SupabaseConfig.get_database_url(use_pooler=True)
        if SupabaseConfig.DATABASE_POOLER_URL:
            logger.info("🔄 使用连接池 URI（DATABASE_POOLER_URL）...")
            print("🔄 使用连接池 URI（DATABASE_POOLER_URL）...")
        elif SupabaseConfig.DATABASE_URL:
            logger.info("🔄 使用完整连接 URI（DATABASE_URL）...")
            print("🔄 使用完整连接 URI（DATABASE_URL）...")
        else:
            logger.info("🔄 尝试使用连接池连接（端口 6543）...")
            print("🔄 尝试使用连接池连接（端口 6543）...")
    except Exception as e:
        logger.warning(f"⚠️ 连接池配置失败，使用标准连接: {e}")
        print(f"⚠️ 连接池配置失败，使用标准连接: {e}")
        database_url = SupabaseConfig.get_database_url(use_pooler=False)
    
    # 连接处理：优先使用 IPv4，避免 IPv6 连接问题
    # 如果 hostname 已经是 IP 地址，直接使用；否则使用主机名让 psycopg2 处理
    import urllib.parse
    
    parsed = urllib.parse.urlparse(database_url)
    hostname = parsed.hostname
    
    # 如果 hostname 已经是 IPv6 地址格式，需要特殊处理
    if hostname:
        import re
        # 检查是否是 IPv6 地址格式（包含冒号）
        is_ipv6_address = ':' in hostname and not hostname.startswith('[')
        
        # 如果是 IPv6 地址格式，尝试强制使用 IPv4 或主机名
        if is_ipv6_address:
            logger.warning(f"⚠️ 检测到 IPv6 地址格式，可能无法连接: {hostname}")
            print(f"⚠️ 检测到 IPv6 地址格式，可能无法连接: {hostname}")
            
            # 尝试从原始 URL 中提取主机名（如果可能）
            # 如果是从 DNS 解析得到的 IPv6，回退到使用主机名
            # 这里我们直接使用主机名，让 psycopg2 和系统自己处理
            logger.info("ℹ️ 使用主机名连接，让系统自动选择 IPv4/IPv6")
            print("ℹ️ 使用主机名连接，让系统自动选择 IPv4/IPv6")
            # 不修改 database_url，使用原始配置
        else:
            # IPv4 地址或域名，直接使用
            logger.info(f"✅ 使用主机名连接: {hostname}")
            print(f"✅ 使用主机名连接: {hostname}")
    
    # 连接参数：设置超时和连接选项
    connect_args = {
        'connect_timeout': 10,
        'keepalives': 1,
        'keepalives_idle': 30,
        'keepalives_interval': 10,
        'keepalives_count': 5
    }
    
    engine = create_engine(
        database_url,
        pool_pre_ping=True,  # 连接前ping，确保连接有效
        pool_size=5,  # 连接池大小
        max_overflow=10,  # 最大溢出连接数
        echo=False,  # 是否打印SQL语句
        connect_args=connect_args  # 连接参数
    )
    print("✅ 已连接到 Supabase PostgreSQL 数据库")
except ValueError as e:
    # 配置错误：提供详细的配置说明
    config_help = """
请在 Streamlit Cloud Secrets 中配置以下环境变量：

必需配置：
- SUPABASE_PROJECT_REF: Supabase项目引用ID
- SUPABASE_DB_PASSWORD: Supabase数据库密码

可选配置：
- SUPABASE_URL: Supabase项目URL
- SUPABASE_ANON_KEY: Supabase匿名密钥

配置步骤：
1. 进入 Streamlit Cloud 应用设置
2. 点击 "Secrets" 标签
3. 添加上述环境变量（使用 TOML 格式）
4. 保存并重新部署应用

示例 Secrets 配置：
```toml
SUPABASE_PROJECT_REF = "your-project-ref"
SUPABASE_DB_PASSWORD = "your-db-password"
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_ANON_KEY = "your-anon-key"
```

详细配置说明请查看: SUPABASE_SETUP.md
"""
    error_msg = f"Supabase配置不完整: {e}\n\n{config_help}"
    print(f"❌ {error_msg}")
    raise ValueError(error_msg)
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
    from models.trading_reason import TradingReason
    from models.sector_history import SectorHistory
    from models.zt_pool_history import ZtPoolHistory
    from models.zb_pool_history import ZbgcPoolHistory
    from models.dt_pool_history import DtgcPoolHistory
    from models.index_history import IndexHistory
    from models.scheduler_execution import SchedulerExecution
    from models.stock_fund_flow_history import StockFundFlowHistory
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 检查并添加 sector_type 列（如果不存在）
    _ensure_sector_type_column()
    
    # 检查并添加交易日志表的止盈止损字段（如果不存在）
    _ensure_trading_reviews_columns()

def _ensure_sector_type_column():
    """确保 sector_history 表有 sector_type 列（向后兼容）"""
    try:
        db = SessionLocal()
        try:
            # 检查列是否已存在
            check_sql = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'sector_history' 
                AND column_name = 'sector_type'
            """)
            result = db.execute(check_sql).fetchone()
            
            if result:
                # 列已存在，无需操作
                return
            
            # 列不存在，需要添加
            logger.info("检测到 sector_history 表缺少 sector_type 列，正在添加...")
            
            # 先添加列（允许 NULL，因为现有数据可能没有这个值）
            alter_sql = text("""
                ALTER TABLE sector_history 
                ADD COLUMN sector_type VARCHAR(20) DEFAULT 'industry'
            """)
            db.execute(alter_sql)
            db.commit()
            logger.info("✅ 成功添加 sector_type 列")
            
            # 更新现有数据，将所有 NULL 值设置为 'industry'
            update_sql = text("""
                UPDATE sector_history 
                SET sector_type = 'industry' 
                WHERE sector_type IS NULL
            """)
            db.execute(update_sql)
            db.commit()
            logger.info("✅ 成功更新现有数据为行业板块")
            
            # 将列设置为 NOT NULL（在更新数据之后）
            alter_not_null_sql = text("""
                ALTER TABLE sector_history 
                ALTER COLUMN sector_type SET NOT NULL
            """)
            db.execute(alter_not_null_sql)
            db.commit()
            
            # 设置默认值
            alter_default_sql = text("""
                ALTER TABLE sector_history 
                ALTER COLUMN sector_type SET DEFAULT 'industry'
            """)
            db.execute(alter_default_sql)
            db.commit()
            
            # 创建索引（如果不存在）
            try:
                index_sql = text("""
                    CREATE INDEX IF NOT EXISTS idx_sector_history_sector_type 
                    ON sector_history(sector_type)
                """)
                db.execute(index_sql)
                db.commit()
                logger.info("✅ 成功创建索引")
            except Exception as e:
                logger.warning(f"创建索引时出现警告（可能已存在）: {e}")
            
            logger.info("🎉 sector_type 列迁移完成")
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 添加 sector_type 列失败: {str(e)}")
            # 不抛出异常，允许应用继续运行
        finally:
            db.close()
    except Exception as e:
        logger.error(f"❌ 检查 sector_type 列时出错: {str(e)}")
        # 不抛出异常，允许应用继续运行

def _ensure_trading_reviews_columns():
    """确保 trading_reviews 表有止盈止损列和市场列，并将review列改为可空（向后兼容）"""
    try:
        db = SessionLocal()
        try:
            # 检查列是否已存在
            check_sql = text("""
                SELECT column_name, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'trading_reviews' 
                AND column_name IN ('take_profit_price', 'stop_loss_price', 'market', 'review')
            """)
            result = db.execute(check_sql).fetchall()
            existing_columns = {row[0]: row[1] for row in result}
            
            # 添加 take_profit_price 列（如果不存在）
            if 'take_profit_price' not in existing_columns:
                alter_sql = text("""
                    ALTER TABLE trading_reviews 
                    ADD COLUMN take_profit_price DECIMAL(10, 2)
                """)
                db.execute(alter_sql)
                db.commit()
                print("✅ 已为 trading_reviews 表添加 take_profit_price 列")
            
            # 添加 stop_loss_price 列（如果不存在）
            if 'stop_loss_price' not in existing_columns:
                alter_sql = text("""
                    ALTER TABLE trading_reviews 
                    ADD COLUMN stop_loss_price DECIMAL(10, 2)
                """)
                db.execute(alter_sql)
                db.commit()
                print("✅ 已为 trading_reviews 表添加 stop_loss_price 列")
            
            # 将 review 列改为可空（如果当前是 NOT NULL）
            if 'review' in existing_columns and existing_columns['review'] == 'NO':
                try:
                    alter_sql = text("""
                        ALTER TABLE trading_reviews 
                        ALTER COLUMN review DROP NOT NULL
                    """)
                    db.execute(alter_sql)
                    db.commit()
                    print("✅ 已将 trading_reviews 表的 review 列改为可空")
                except Exception as e:
                    print(f"⚠️  修改 review 列为可空时出错: {e}")
                    db.rollback()
            
            # 添加 market 列（如果不存在）
            if 'market' not in existing_columns:
                # 先添加列（允许 NULL，并设置默认值）
                alter_sql = text("""
                    ALTER TABLE trading_reviews 
                    ADD COLUMN market VARCHAR(10) DEFAULT 'A股'
                """)
                db.execute(alter_sql)
                db.commit()
                
                # 更新现有数据，将所有 NULL 值设置为 'A股'
                update_sql = text("""
                    UPDATE trading_reviews 
                    SET market = 'A股' 
                    WHERE market IS NULL
                """)
                db.execute(update_sql)
                db.commit()
                
                # 然后设置 NOT NULL 约束（在更新数据之后）
                alter_not_null_sql = text("""
                    ALTER TABLE trading_reviews 
                    ALTER COLUMN market SET NOT NULL
                """)
                db.execute(alter_not_null_sql)
                db.commit()
                
                # 设置默认值（确保新插入的记录有默认值）
                alter_default_sql = text("""
                    ALTER TABLE trading_reviews 
                    ALTER COLUMN market SET DEFAULT 'A股'
                """)
                db.execute(alter_default_sql)
                db.commit()
                
                print("✅ 已为 trading_reviews 表添加 market 列")
        finally:
            db.close()
    except Exception as e:
        print(f"⚠️  检查/添加 trading_reviews 表列时出错: {e}")
        # 不抛出异常，允许应用继续运行

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

