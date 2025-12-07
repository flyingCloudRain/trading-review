# Supabase数据库设计方案

## 1. Supabase简介

### 什么是Supabase
- **基于PostgreSQL**的开源Firebase替代品
- 提供PostgreSQL数据库、实时订阅、认证、存储等功能
- 支持SQL和RESTful API访问
- 提供Web管理界面

### 优势
- ✅ **PostgreSQL性能** - 完整的PostgreSQL功能
- ✅ **实时订阅** - 数据变更实时推送
- ✅ **自动API** - 自动生成RESTful API
- ✅ **Row Level Security** - 行级安全策略
- ✅ **免费额度** - 适合中小型应用
- ✅ **易于部署** - 支持自托管或云服务

---

## 2. 数据库表设计

### 2.1 交易复盘记录表

**表名**: `trading_reviews`

```sql
CREATE TABLE trading_reviews (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    stock_code VARCHAR(10) NOT NULL,
    stock_name VARCHAR(50) NOT NULL,
    operation VARCHAR(4) NOT NULL CHECK (operation IN ('buy', 'sell')),
    price DECIMAL(10, 2) NOT NULL,
    quantity INTEGER NOT NULL,
    total_amount DECIMAL(12, 2) NOT NULL,
    reason TEXT NOT NULL,
    review TEXT NOT NULL,
    profit DECIMAL(12, 2),
    profit_percent DECIMAL(6, 2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    user_id UUID REFERENCES auth.users(id) -- 关联用户（可选）
);

-- 索引
CREATE INDEX idx_trading_reviews_date ON trading_reviews(date);
CREATE INDEX idx_trading_reviews_stock_code ON trading_reviews(stock_code);
CREATE INDEX idx_trading_reviews_user_id ON trading_reviews(user_id);
CREATE INDEX idx_trading_reviews_date_stock ON trading_reviews(date, stock_code);

-- 更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_trading_reviews_updated_at 
    BEFORE UPDATE ON trading_reviews 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
```

---

### 2.2 板块历史数据表

**表名**: `sector_history`

```sql
CREATE TABLE sector_history (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    time TIME,
    index INTEGER NOT NULL,
    name VARCHAR(50) NOT NULL,
    change_percent DECIMAL(6, 2) NOT NULL,
    total_volume DECIMAL(12, 2) NOT NULL,
    total_amount DECIMAL(12, 2) NOT NULL,
    net_inflow DECIMAL(12, 2) NOT NULL,
    up_count INTEGER NOT NULL,
    down_count INTEGER NOT NULL,
    avg_price DECIMAL(10, 2) NOT NULL,
    leading_stock VARCHAR(50),
    leading_stock_price DECIMAL(10, 2),
    leading_stock_change_percent DECIMAL(6, 2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_sector_history_date ON sector_history(date);
CREATE INDEX idx_sector_history_name ON sector_history(name);
CREATE INDEX idx_sector_history_date_name ON sector_history(date, name);

-- 分区表（TimescaleDB风格，可选）
-- 如果使用TimescaleDB扩展
-- SELECT create_hypertable('sector_history', 'date');
```

---

### 2.3 涨停股票池历史表

**表名**: `zt_pool_history`

```sql
CREATE TABLE zt_pool_history (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    time TIME,
    index INTEGER NOT NULL,
    code VARCHAR(10) NOT NULL,
    name VARCHAR(50) NOT NULL,
    change_percent DECIMAL(6, 2) NOT NULL,
    latest_price DECIMAL(10, 2) NOT NULL,
    turnover DECIMAL(12, 2) NOT NULL,
    circulating_market_value DECIMAL(15, 2) NOT NULL,
    total_market_value DECIMAL(15, 2) NOT NULL,
    turnover_rate DECIMAL(6, 2) NOT NULL,
    sealing_funds DECIMAL(12, 2) NOT NULL,
    first_sealing_time TIME,
    last_sealing_time TIME,
    explosion_count INTEGER NOT NULL DEFAULT 0,
    zt_statistics VARCHAR(50),
    continuous_boards INTEGER NOT NULL DEFAULT 0,
    industry VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_zt_pool_date ON zt_pool_history(date);
CREATE INDEX idx_zt_pool_code ON zt_pool_history(code);
CREATE INDEX idx_zt_pool_date_code ON zt_pool_history(date, code);
CREATE INDEX idx_zt_pool_industry ON zt_pool_history(industry);
CREATE INDEX idx_zt_pool_continuous_boards ON zt_pool_history(continuous_boards);
```

---

### 2.4 炸板股票池历史表

**表名**: `zbgc_pool_history`

```sql
CREATE TABLE zbgc_pool_history (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    time TIME,
    index INTEGER NOT NULL,
    code VARCHAR(10) NOT NULL,
    name VARCHAR(50) NOT NULL,
    change_percent DECIMAL(6, 2) NOT NULL,
    latest_price DECIMAL(10, 2) NOT NULL,
    limit_price DECIMAL(10, 2) NOT NULL,
    turnover DECIMAL(12, 2) NOT NULL,
    circulating_market_value DECIMAL(15, 2) NOT NULL,
    total_market_value DECIMAL(15, 2) NOT NULL,
    turnover_rate DECIMAL(6, 2) NOT NULL,
    rise_speed DECIMAL(8, 4) NOT NULL,
    first_sealing_time TIME,
    explosion_count INTEGER NOT NULL DEFAULT 0,
    zt_statistics VARCHAR(50),
    amplitude DECIMAL(6, 2) NOT NULL,
    industry VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_zbgc_pool_date ON zbgc_pool_history(date);
CREATE INDEX idx_zbgc_pool_code ON zbgc_pool_history(code);
CREATE INDEX idx_zbgc_pool_date_code ON zbgc_pool_history(date, code);
CREATE INDEX idx_zbgc_pool_explosion_count ON zbgc_pool_history(explosion_count);
```

---

### 2.5 跌停股票池历史表

**表名**: `dtgc_pool_history`

```sql
CREATE TABLE dtgc_pool_history (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    time TIME,
    index INTEGER NOT NULL,
    code VARCHAR(10) NOT NULL,
    name VARCHAR(50) NOT NULL,
    change_percent DECIMAL(6, 2) NOT NULL,
    latest_price DECIMAL(10, 2) NOT NULL,
    turnover DECIMAL(12, 2) NOT NULL,
    circulating_market_value DECIMAL(15, 2) NOT NULL,
    total_market_value DECIMAL(15, 2) NOT NULL,
    pe_ratio DECIMAL(10, 2),
    turnover_rate DECIMAL(6, 2) NOT NULL,
    sealing_funds DECIMAL(12, 2) NOT NULL,
    last_sealing_time TIME,
    board_turnover DECIMAL(12, 2) NOT NULL,
    continuous_limit_down INTEGER NOT NULL DEFAULT 0,
    open_count INTEGER NOT NULL DEFAULT 0,
    industry VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_dtgc_pool_date ON dtgc_pool_history(date);
CREATE INDEX idx_dtgc_pool_code ON dtgc_pool_history(code);
CREATE INDEX idx_dtgc_pool_date_code ON dtgc_pool_history(date, code);
CREATE INDEX idx_dtgc_pool_continuous_limit_down ON dtgc_pool_history(continuous_limit_down);
```

---

### 2.6 板块异动历史表

**表名**: `board_change_history`

```sql
CREATE TABLE board_change_history (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    time TIME,
    name VARCHAR(50) NOT NULL,
    change_percent DECIMAL(6, 2) NOT NULL,
    net_inflow DECIMAL(12, 2) NOT NULL,
    total_change_count INTEGER NOT NULL,
    most_frequent_stock_code VARCHAR(10),
    most_frequent_stock_name VARCHAR(50),
    most_frequent_direction VARCHAR(10),
    change_types JSONB, -- 使用JSONB存储异动类型列表
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_board_change_date ON board_change_history(date);
CREATE INDEX idx_board_change_name ON board_change_history(name);
CREATE INDEX idx_board_change_date_name ON board_change_history(date, name);
CREATE INDEX idx_board_change_total_count ON board_change_history(total_change_count);
-- JSONB索引（GIN索引，用于JSON查询）
CREATE INDEX idx_board_change_types ON board_change_history USING GIN (change_types);
```

---

## 3. Row Level Security (RLS) 策略

### 3.1 交易复盘记录 - 用户只能访问自己的数据

```sql
-- 启用RLS
ALTER TABLE trading_reviews ENABLE ROW LEVEL SECURITY;

-- 策略：用户只能查看自己的记录
CREATE POLICY "Users can view own trading reviews"
    ON trading_reviews
    FOR SELECT
    USING (auth.uid() = user_id);

-- 策略：用户只能插入自己的记录
CREATE POLICY "Users can insert own trading reviews"
    ON trading_reviews
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- 策略：用户只能更新自己的记录
CREATE POLICY "Users can update own trading reviews"
    ON trading_reviews
    FOR UPDATE
    USING (auth.uid() = user_id);

-- 策略：用户只能删除自己的记录
CREATE POLICY "Users can delete own trading reviews"
    ON trading_reviews
    FOR DELETE
    USING (auth.uid() = user_id);
```

### 3.2 历史数据表 - 公开只读

```sql
-- 板块历史数据 - 公开只读
ALTER TABLE sector_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read access"
    ON sector_history
    FOR SELECT
    USING (true);

-- 涨停股票池 - 公开只读
ALTER TABLE zt_pool_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read access"
    ON zt_pool_history
    FOR SELECT
    USING (true);

-- 其他历史数据表类似...
```

---

## 4. 实时订阅配置

### 4.1 启用实时订阅

在Supabase Dashboard中：
1. 进入 Database → Replication
2. 为需要的表启用实时订阅

或使用SQL：
```sql
-- 启用表的实时订阅
ALTER PUBLICATION supabase_realtime ADD TABLE trading_reviews;
ALTER PUBLICATION supabase_realtime ADD TABLE sector_history;
ALTER PUBLICATION supabase_realtime ADD TABLE zt_pool_history;
```

### 4.2 客户端订阅示例

```javascript
// JavaScript/TypeScript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

// 订阅交易复盘记录变更
const subscription = supabase
  .channel('trading_reviews')
  .on('postgres_changes', 
    { event: 'INSERT', schema: 'public', table: 'trading_reviews' },
    (payload) => {
      console.log('新记录:', payload.new)
    }
  )
  .subscribe()

// 订阅板块历史数据
const sectorSubscription = supabase
  .channel('sector_history')
  .on('postgres_changes',
    { event: '*', schema: 'public', table: 'sector_history' },
    (payload) => {
      console.log('板块数据变更:', payload)
    }
  )
  .subscribe()
```

---

## 5. 自动生成API

Supabase会自动为每个表生成RESTful API：

### 5.1 RESTful API端点

```
GET    /rest/v1/trading_reviews
POST   /rest/v1/trading_reviews
GET    /rest/v1/trading_reviews?id=eq.1
PATCH  /rest/v1/trading_reviews?id=eq.1
DELETE /rest/v1/trading_reviews?id=eq.1
```

### 5.2 查询示例

```bash
# 获取今日板块数据
curl 'https://your-project.supabase.co/rest/v1/sector_history?date=eq.2025-11-17' \
  -H "apikey: YOUR_ANON_KEY" \
  -H "Authorization: Bearer YOUR_ANON_KEY"

# 获取涨停股票（带过滤和排序）
curl 'https://your-project.supabase.co/rest/v1/zt_pool_history?date=eq.2025-11-17&order=continuous_boards.desc' \
  -H "apikey: YOUR_ANON_KEY" \
  -H "Authorization: Bearer YOUR_ANON_KEY"

# 使用PostgREST查询语法
curl 'https://your-project.supabase.co/rest/v1/zt_pool_history?select=code,name,continuous_boards&date=eq.2025-11-17&continuous_boards=gt.3' \
  -H "apikey: YOUR_ANON_KEY"
```

---

## 6. 数据库函数和视图

### 6.1 统计函数

```sql
-- 获取交易复盘统计
CREATE OR REPLACE FUNCTION get_trading_statistics(p_user_id UUID)
RETURNS TABLE (
    total_records BIGINT,
    total_profit DECIMAL,
    win_count BIGINT,
    loss_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT as total_records,
        COALESCE(SUM(profit), 0) as total_profit,
        COUNT(*) FILTER (WHERE profit > 0)::BIGINT as win_count,
        COUNT(*) FILTER (WHERE profit < 0)::BIGINT as loss_count
    FROM trading_reviews
    WHERE user_id = p_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### 6.2 视图 - 每日涨停统计

```sql
-- 每日涨停股票统计视图
CREATE VIEW daily_zt_statistics AS
SELECT 
    date,
    COUNT(*) as total_count,
    AVG(change_percent) as avg_change_percent,
    AVG(continuous_boards) as avg_continuous_boards,
    SUM(turnover) as total_turnover,
    COUNT(DISTINCT industry) as industry_count
FROM zt_pool_history
GROUP BY date
ORDER BY date DESC;
```

### 6.3 视图 - 板块涨跌幅排名

```sql
-- 板块涨跌幅排名视图
CREATE VIEW sector_ranking AS
SELECT 
    name,
    date,
    change_percent,
    net_inflow,
    ROW_NUMBER() OVER (PARTITION BY date ORDER BY change_percent DESC) as rank
FROM sector_history
ORDER BY date DESC, change_percent DESC;
```

---

## 7. 配置和连接

### 7.1 Python客户端配置

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class SupabaseConfig:
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')  # anon key
    SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')  # service_role key
    
    # 数据库连接（使用service_role key，绕过RLS）
    DATABASE_URL = f"postgresql://postgres:{os.environ.get('SUPABASE_DB_PASSWORD')}@db.{os.environ.get('SUPABASE_PROJECT_REF')}.supabase.co:5432/postgres"
```

### 7.2 使用Supabase Python客户端

```python
# 安装: pip install supabase
from supabase import create_client, Client

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# 查询数据
response = supabase.table('trading_reviews').select('*').eq('user_id', user_id).execute()

# 插入数据
response = supabase.table('trading_reviews').insert({
    'date': '2025-11-17',
    'stock_code': '000001',
    'stock_name': '平安银行',
    'operation': 'buy',
    'price': 10.5,
    'quantity': 100,
    'total_amount': 1050.0,
    'reason': '看好',
    'review': '买入',
    'user_id': user_id
}).execute()
```

### 7.3 使用SQLAlchemy连接

```python
# database/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from config import SupabaseConfig

# 使用Supabase PostgreSQL连接
engine = create_engine(
    SupabaseConfig.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
```

---

## 8. 迁移方案

### 8.1 从SQLite迁移到Supabase

```python
# scripts/migrate_to_supabase.py
import sqlite3
from supabase import create_client
import pandas as pd
from config import SupabaseConfig

# 连接SQLite
sqlite_conn = sqlite3.connect('data/trading_review.db')

# 连接Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# 迁移每个表
tables = ['trading_reviews', 'sector_history']

for table in tables:
    # 从SQLite读取数据
    df = pd.read_sql(f'SELECT * FROM {table}', sqlite_conn)
    
    # 转换为字典列表
    records = df.to_dict('records')
    
    # 批量插入到Supabase（每次1000条）
    batch_size = 1000
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        supabase.table(table).insert(batch).execute()
        print(f'已迁移 {table}: {i+len(batch)}/{len(records)}')

print('迁移完成！')
```

### 8.2 数据验证

```python
# 验证迁移结果
sqlite_count = sqlite_conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
supabase_count = supabase.table(table).select('id', count='exact').execute().count

print(f'{table}: SQLite={sqlite_count}, Supabase={supabase_count}')
```

---

## 9. 性能优化

### 9.1 连接池配置

```python
# 使用连接池
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

### 9.2 查询优化

```sql
-- 使用EXPLAIN ANALYZE分析查询
EXPLAIN ANALYZE
SELECT * FROM zt_pool_history 
WHERE date >= '2025-01-01' 
ORDER BY date DESC 
LIMIT 100;

-- 创建部分索引（只索引最近的数据）
CREATE INDEX idx_zt_pool_recent_date 
ON zt_pool_history(date) 
WHERE date >= CURRENT_DATE - INTERVAL '90 days';
```

### 9.3 物化视图（缓存常用查询）

```sql
-- 创建物化视图
CREATE MATERIALIZED VIEW mv_daily_statistics AS
SELECT 
    date,
    COUNT(*) FILTER (WHERE table_name = 'zt_pool') as zt_count,
    COUNT(*) FILTER (WHERE table_name = 'zbgc_pool') as zbgc_count,
    COUNT(*) FILTER (WHERE table_name = 'dtgc_pool') as dtgc_count
FROM (
    SELECT date, 'zt_pool' as table_name FROM zt_pool_history
    UNION ALL
    SELECT date, 'zbgc_pool' FROM zbgc_pool_history
    UNION ALL
    SELECT date, 'dtgc_pool' FROM dtgc_pool_history
) t
GROUP BY date;

-- 创建唯一索引
CREATE UNIQUE INDEX ON mv_daily_statistics(date);

-- 刷新物化视图（定时任务）
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_statistics;
```

---

## 10. 监控和维护

### 10.1 监控查询性能

```sql
-- 查看慢查询
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### 10.2 数据库大小监控

```sql
-- 查看表大小
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## 11. 安全建议

### 11.1 API密钥管理

- **Anon Key**: 用于客户端，受RLS保护
- **Service Role Key**: 用于服务端，绕过RLS，需保密
- **不要**将Service Role Key暴露在客户端

### 11.2 RLS策略测试

```sql
-- 测试RLS策略
SET ROLE authenticated;
SET request.jwt.claim.sub = 'user-uuid-here';
SELECT * FROM trading_reviews; -- 应该只返回该用户的记录
```

---

## 12. 总结

### Supabase优势
- ✅ **PostgreSQL性能** - 完整的PostgreSQL功能
- ✅ **实时订阅** - 数据变更实时推送
- ✅ **自动API** - 自动生成RESTful API
- ✅ **Row Level Security** - 行级安全策略
- ✅ **易于使用** - Web界面管理
- ✅ **免费额度** - 适合中小型应用

### 适用场景
- 需要多用户支持
- 需要实时数据更新
- 需要RESTful API
- 需要用户认证
- 需要数据可视化

### 迁移建议
1. **创建Supabase项目**
2. **执行SQL脚本创建表**
3. **配置RLS策略**
4. **迁移数据**
5. **更新应用配置**
6. **测试功能**

