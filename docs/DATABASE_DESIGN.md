# 数据库方案设计文档

## 1. 数据库选择

### 当前阶段：SQLite
- **适用场景**: 数据量 < 100万条，单用户或小团队
- **优势**: 零配置，简单易用，单文件存储
- **文件位置**: `data/trading_review.db`

### 未来迁移：PostgreSQL + TimescaleDB
- **适用场景**: 数据量 > 100万条，需要可视化，多用户并发
- **优势**: 时间序列优化，高性能查询，支持复杂分析

---

## 2. 数据表设计

### 2.1 交易复盘记录表（已有）

**表名**: `trading_reviews`

**用途**: 存储用户的交易复盘记录

**字段设计**:
```sql
CREATE TABLE trading_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date VARCHAR(10) NOT NULL,                    -- 交易日期 YYYY-MM-DD
    stock_code VARCHAR(10) NOT NULL,              -- 股票代码
    stock_name VARCHAR(50) NOT NULL,               -- 股票名称
    operation VARCHAR(4) NOT NULL,                -- 操作类型：buy/sell
    price FLOAT NOT NULL,                          -- 成交价格
    quantity INTEGER NOT NULL,                    -- 成交数量
    total_amount FLOAT NOT NULL,                  -- 成交总额
    reason TEXT NOT NULL,                          -- 交易原因
    review TEXT NOT NULL,                          -- 复盘总结
    profit FLOAT,                                  -- 盈亏金额
    profit_percent FLOAT,                          -- 盈亏比例
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP, -- 创建时间
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP  -- 更新时间
);

-- 索引
CREATE INDEX idx_trading_reviews_date ON trading_reviews(date);
CREATE INDEX idx_trading_reviews_stock_code ON trading_reviews(stock_code);
CREATE INDEX idx_trading_reviews_operation ON trading_reviews(operation);
```

**约束**:
- `operation IN ('buy', 'sell')`
- `date` 格式：YYYY-MM-DD

---

### 2.2 板块历史数据表（已有）

**表名**: `sector_history`

**用途**: 存储每日板块信息快照

**字段设计**:
```sql
CREATE TABLE sector_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,                            -- 日期
    time VARCHAR(8),                               -- 时间 HH:MM:SS
    index INTEGER NOT NULL,                        -- 序号
    name VARCHAR(50) NOT NULL,                     -- 板块名称
    change_percent FLOAT NOT NULL,                  -- 涨跌幅(%)
    total_volume FLOAT NOT NULL,                    -- 总成交量(万手)
    total_amount FLOAT NOT NULL,                    -- 总成交额(亿元)
    net_inflow FLOAT NOT NULL,                     -- 净流入(亿元)
    up_count INTEGER NOT NULL,                     -- 上涨家数
    down_count INTEGER NOT NULL,                   -- 下跌家数
    avg_price FLOAT NOT NULL,                      -- 均价
    leading_stock VARCHAR(50),                     -- 领涨股
    leading_stock_price FLOAT,                     -- 领涨股-最新价
    leading_stock_change_percent FLOAT,            -- 领涨股-涨跌幅(%)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP  -- 创建时间
);

-- 索引
CREATE INDEX idx_sector_history_date ON sector_history(date);
CREATE INDEX idx_sector_history_name ON sector_history(name);
CREATE INDEX idx_sector_history_date_name ON sector_history(date, name);
```

**数据特点**:
- 每天约90条记录
- 按日期和板块名称查询
- 需要时间序列分析

---

### 2.3 涨停股票池历史表（建议新增）

**表名**: `zt_pool_history`

**用途**: 存储每日涨停股票池数据

**字段设计**:
```sql
CREATE TABLE zt_pool_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,                            -- 日期
    time VARCHAR(8),                               -- 时间 HH:MM:SS
    index INTEGER NOT NULL,                        -- 序号
    code VARCHAR(10) NOT NULL,                     -- 股票代码
    name VARCHAR(50) NOT NULL,                     -- 股票名称
    change_percent FLOAT NOT NULL,                 -- 涨跌幅(%)
    latest_price FLOAT NOT NULL,                   -- 最新价
    turnover FLOAT NOT NULL,                       -- 成交额(亿元)
    circulating_market_value FLOAT NOT NULL,        -- 流通市值(亿元)
    total_market_value FLOAT NOT NULL,              -- 总市值(亿元)
    turnover_rate FLOAT NOT NULL,                  -- 换手率(%)
    sealing_funds FLOAT NOT NULL,                  -- 封板资金(亿元)
    first_sealing_time VARCHAR(8),                 -- 首次封板时间
    last_sealing_time VARCHAR(8),                  -- 最后封板时间
    explosion_count INTEGER NOT NULL,              -- 炸板次数
    zt_statistics VARCHAR(50),                     -- 涨停统计
    continuous_boards INTEGER NOT NULL,            -- 连板数
    industry VARCHAR(50),                          -- 所属行业
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP  -- 创建时间
);

-- 索引
CREATE INDEX idx_zt_pool_date ON zt_pool_history(date);
CREATE INDEX idx_zt_pool_code ON zt_pool_history(code);
CREATE INDEX idx_zt_pool_date_code ON zt_pool_history(date, code);
CREATE INDEX idx_zt_pool_industry ON zt_pool_history(industry);
CREATE INDEX idx_zt_pool_continuous_boards ON zt_pool_history(continuous_boards);
```

**数据特点**:
- 每天约80条记录
- 按日期、股票代码、行业查询
- 需要统计连板数、行业分布

---

### 2.4 炸板股票池历史表（建议新增）

**表名**: `zbgc_pool_history`

**用途**: 存储每日炸板股票池数据

**字段设计**:
```sql
CREATE TABLE zbgc_pool_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,                            -- 日期
    time VARCHAR(8),                               -- 时间 HH:MM:SS
    index INTEGER NOT NULL,                        -- 序号
    code VARCHAR(10) NOT NULL,                     -- 股票代码
    name VARCHAR(50) NOT NULL,                     -- 股票名称
    change_percent FLOAT NOT NULL,                 -- 涨跌幅(%)
    latest_price FLOAT NOT NULL,                   -- 最新价
    limit_price FLOAT NOT NULL,                    -- 涨停价
    turnover FLOAT NOT NULL,                       -- 成交额(亿元)
    circulating_market_value FLOAT NOT NULL,        -- 流通市值(亿元)
    total_market_value FLOAT NOT NULL,              -- 总市值(亿元)
    turnover_rate FLOAT NOT NULL,                  -- 换手率(%)
    rise_speed FLOAT NOT NULL,                     -- 涨速
    first_sealing_time VARCHAR(8),                 -- 首次封板时间
    explosion_count INTEGER NOT NULL,              -- 炸板次数
    zt_statistics VARCHAR(50),                     -- 涨停统计
    amplitude FLOAT NOT NULL,                      -- 振幅(%)
    industry VARCHAR(50),                          -- 所属行业
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP  -- 创建时间
);

-- 索引
CREATE INDEX idx_zbgc_pool_date ON zbgc_pool_history(date);
CREATE INDEX idx_zbgc_pool_code ON zbgc_pool_history(code);
CREATE INDEX idx_zbgc_pool_date_code ON zbgc_pool_history(date, code);
CREATE INDEX idx_zbgc_pool_explosion_count ON zbgc_pool_history(explosion_count);
```

**数据特点**:
- 每天约25条记录
- 按日期、股票代码、炸板次数查询

---

### 2.5 跌停股票池历史表（建议新增）

**表名**: `dtgc_pool_history`

**用途**: 存储每日跌停股票池数据

**字段设计**:
```sql
CREATE TABLE dtgc_pool_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,                            -- 日期
    time VARCHAR(8),                               -- 时间 HH:MM:SS
    index INTEGER NOT NULL,                        -- 序号
    code VARCHAR(10) NOT NULL,                     -- 股票代码
    name VARCHAR(50) NOT NULL,                     -- 股票名称
    change_percent FLOAT NOT NULL,                 -- 涨跌幅(%)
    latest_price FLOAT NOT NULL,                   -- 最新价
    turnover FLOAT NOT NULL,                       -- 成交额(亿元)
    circulating_market_value FLOAT NOT NULL,        -- 流通市值(亿元)
    total_market_value FLOAT NOT NULL,              -- 总市值(亿元)
    pe_ratio FLOAT,                                -- 动态市盈率
    turnover_rate FLOAT NOT NULL,                  -- 换手率(%)
    sealing_funds FLOAT NOT NULL,                  -- 封单资金(亿元)
    last_sealing_time VARCHAR(8),                 -- 最后封板时间
    board_turnover FLOAT NOT NULL,                 -- 板上成交额(亿元)
    continuous_limit_down INTEGER NOT NULL,        -- 连续跌停
    open_count INTEGER NOT NULL,                   -- 开板次数
    industry VARCHAR(50),                          -- 所属行业
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP  -- 创建时间
);

-- 索引
CREATE INDEX idx_dtgc_pool_date ON dtgc_pool_history(date);
CREATE INDEX idx_dtgc_pool_code ON dtgc_pool_history(code);
CREATE INDEX idx_dtgc_pool_date_code ON dtgc_pool_history(date, code);
CREATE INDEX idx_dtgc_pool_continuous_limit_down ON dtgc_pool_history(continuous_limit_down);
```

**数据特点**:
- 每天约5条记录
- 按日期、股票代码、连续跌停数查询

---

### 2.6 板块异动历史表（建议新增）

**表名**: `board_change_history`

**用途**: 存储每日板块异动数据

**字段设计**:
```sql
CREATE TABLE board_change_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,                            -- 日期
    time VARCHAR(8),                               -- 时间 HH:MM:SS
    name VARCHAR(50) NOT NULL,                     -- 板块名称
    change_percent FLOAT NOT NULL,                 -- 涨跌幅(%)
    net_inflow FLOAT NOT NULL,                     -- 主力净流入(亿元)
    total_change_count INTEGER NOT NULL,            -- 板块异动总次数
    most_frequent_stock_code VARCHAR(10),          -- 最频繁个股代码
    most_frequent_stock_name VARCHAR(50),          -- 最频繁个股名称
    most_frequent_direction VARCHAR(10),            -- 买卖方向
    change_types TEXT,                             -- 异动类型列表(JSON)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP  -- 创建时间
);

-- 索引
CREATE INDEX idx_board_change_date ON board_change_history(date);
CREATE INDEX idx_board_change_name ON board_change_history(name);
CREATE INDEX idx_board_change_date_name ON board_change_history(date, name);
CREATE INDEX idx_board_change_total_count ON board_change_history(total_change_count);
```

**数据特点**:
- 每天约558条记录
- 按日期、板块名称、异动次数查询
- `change_types` 存储JSON格式的异动类型列表

---

## 3. 数据关系设计

### 3.1 表关系图

```
trading_reviews (交易复盘)
    └─ stock_code (股票代码)

sector_history (板块历史)
    └─ name (板块名称)

zt_pool_history (涨停股票池)
    ├─ code (股票代码)
    └─ industry (所属行业)

zbgc_pool_history (炸板股票池)
    ├─ code (股票代码)
    └─ industry (所属行业)

dtgc_pool_history (跌停股票池)
    ├─ code (股票代码)
    └─ industry (所属行业)

board_change_history (板块异动)
    └─ name (板块名称)
```

### 3.2 关联关系

- **股票代码关联**: `trading_reviews.stock_code` ↔ `zt_pool_history.code` / `zbgc_pool_history.code` / `dtgc_pool_history.code`
- **板块名称关联**: `sector_history.name` ↔ `board_change_history.name`
- **日期关联**: 所有表都通过 `date` 字段关联，支持跨表时间序列分析

---

## 4. 索引设计策略

### 4.1 单列索引

**日期索引**（所有表）:
- 用途：按日期范围查询
- 索引：`idx_*_date`

**股票代码索引**（股票相关表）:
- 用途：按股票代码查询
- 索引：`idx_*_code`

**板块名称索引**（板块相关表）:
- 用途：按板块名称查询
- 索引：`idx_*_name`

### 4.2 复合索引

**日期+代码复合索引**:
- `idx_zt_pool_date_code` - 查询某日某股票
- `idx_zbgc_pool_date_code`
- `idx_dtgc_pool_date_code`

**日期+名称复合索引**:
- `idx_sector_history_date_name` - 查询某日某板块
- `idx_board_change_date_name`

### 4.3 业务索引

**连板数索引**:
- `idx_zt_pool_continuous_boards` - 查询连板股票

**炸板次数索引**:
- `idx_zbgc_pool_explosion_count` - 查询炸板次数

**异动次数索引**:
- `idx_board_change_total_count` - 查询异动次数排名

---

## 5. 数据量估算

### 5.1 年度数据量

| 表名 | 每天记录数 | 年记录数（250交易日） | 单条大小 | 年数据量 |
|------|-----------|---------------------|---------|---------|
| sector_history | 90 | 22,500 | ~200B | ~4.5MB |
| zt_pool_history | 80 | 20,000 | ~250B | ~5MB |
| zbgc_pool_history | 25 | 6,250 | ~250B | ~1.6MB |
| dtgc_pool_history | 5 | 1,250 | ~250B | ~0.3MB |
| board_change_history | 558 | 139,500 | ~300B | ~42MB |
| trading_reviews | 不定 | 假设1,000 | ~500B | ~0.5MB |
| **总计** | - | **190,500** | - | **~54MB/年** |

### 5.2 存储规划

- **5年数据**: ~270MB
- **10年数据**: ~540MB
- **SQLite限制**: 建议 < 100GB
- **结论**: SQLite可支持10年以上数据存储

---

## 6. 查询优化建议

### 6.1 常用查询模式

**1. 按日期范围查询**
```sql
-- 优化：使用日期索引
SELECT * FROM sector_history 
WHERE date >= '2025-01-01' AND date <= '2025-12-31'
ORDER BY date, index;
```

**2. 按股票代码查询历史**
```sql
-- 优化：使用代码+日期复合索引
SELECT * FROM zt_pool_history 
WHERE code = '000001' AND date >= '2025-01-01'
ORDER BY date DESC;
```

**3. 统计查询**
```sql
-- 优化：使用聚合函数和索引
SELECT date, COUNT(*) as count, AVG(change_percent) as avg_change
FROM zt_pool_history
WHERE date >= '2025-01-01'
GROUP BY date
ORDER BY date;
```

### 6.2 性能优化

1. **定期VACUUM**: 清理碎片，优化空间
2. **ANALYZE**: 更新统计信息，优化查询计划
3. **批量插入**: 使用事务批量插入数据
4. **连接池**: 使用SQLAlchemy连接池

---

## 7. 数据迁移方案

### 7.1 SQLite → PostgreSQL迁移

**步骤1: 安装PostgreSQL**
```bash
# macOS
brew install postgresql

# Ubuntu
sudo apt-get install postgresql
```

**步骤2: 创建数据库**
```sql
CREATE DATABASE trading_review;
```

**步骤3: 修改配置**
```python
# config.py
DATABASE_URL = 'postgresql://user:password@localhost/trading_review'
```

**步骤4: 使用SQLAlchemy迁移**
- SQLAlchemy支持自动创建表结构
- 只需修改 `DATABASE_URL`，表结构会自动创建

**步骤5: 数据迁移脚本**
```python
# scripts/migrate_to_postgresql.py
from sqlalchemy import create_engine
import pandas as pd

# 连接SQLite
sqlite_engine = create_engine('sqlite:///data/trading_review.db')

# 连接PostgreSQL
pg_engine = create_engine('postgresql://user:password@localhost/trading_review')

# 迁移每个表
tables = ['trading_reviews', 'sector_history', ...]
for table in tables:
    df = pd.read_sql_table(table, sqlite_engine)
    df.to_sql(table, pg_engine, if_exists='append', index=False)
```

### 7.2 启用TimescaleDB（可选）

**步骤1: 安装TimescaleDB**
```bash
# macOS
brew install timescaledb

# 或使用Docker
docker run -d --name timescaledb -p 5432:5432 timescale/timescaledb
```

**步骤2: 创建超表**
```sql
-- 连接到数据库
\c trading_review

-- 启用TimescaleDB扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 将表转换为超表
SELECT create_hypertable('sector_history', 'date');
SELECT create_hypertable('zt_pool_history', 'date');
SELECT create_hypertable('zbgc_pool_history', 'date');
SELECT create_hypertable('dtgc_pool_history', 'date');
SELECT create_hypertable('board_change_history', 'date');
```

---

## 8. 数据备份策略

### 8.1 SQLite备份

**方式1: 直接复制文件**
```bash
cp data/trading_review.db data/trading_review_backup_$(date +%Y%m%d).db
```

**方式2: 使用SQLite备份命令**
```bash
sqlite3 data/trading_review.db ".backup data/trading_review_backup.db"
```

**方式3: 导出为SQL**
```bash
sqlite3 data/trading_review.db ".dump" > backup.sql
```

### 8.2 PostgreSQL备份

**使用pg_dump**
```bash
pg_dump -U user -d trading_review > backup_$(date +%Y%m%d).sql
```

**恢复**
```bash
psql -U user -d trading_review < backup_20251117.sql
```

### 8.3 自动化备份脚本

```bash
#!/bin/bash
# scripts/backup_database.sh

BACKUP_DIR="data/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# SQLite备份
if [ -f "data/trading_review.db" ]; then
    sqlite3 data/trading_review.db ".backup $BACKUP_DIR/trading_review_$DATE.db"
    echo "SQLite备份完成: $BACKUP_DIR/trading_review_$DATE.db"
fi

# 保留最近30天的备份
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
```

---

## 9. 数据维护建议

### 9.1 定期维护任务

1. **每日**: 数据备份
2. **每周**: VACUUM和ANALYZE（SQLite）
3. **每月**: 检查数据完整性
4. **每季度**: 清理过期数据（如需要）

### 9.2 数据清理策略

- **保留策略**: 建议保留所有历史数据
- **归档策略**: 超过5年的数据可归档到冷存储
- **删除策略**: 一般不删除，除非数据错误

---

## 10. 总结

### 当前阶段（SQLite）
- ✅ 简单易用，零配置
- ✅ 满足当前数据量需求
- ✅ 单文件存储，易于备份
- ⚠️ 适合数据量 < 100万条

### 未来迁移（PostgreSQL + TimescaleDB）
- ✅ 时间序列优化
- ✅ 高性能查询
- ✅ 支持复杂分析
- ✅ 适合可视化和多用户

### 建议
1. **当前**: 继续使用SQLite，添加建议的新表
2. **数据量增长**: 考虑迁移到PostgreSQL
3. **需要可视化**: 迁移到PostgreSQL + TimescaleDB
4. **定期备份**: 设置自动化备份脚本

