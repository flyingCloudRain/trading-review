# 数据库ER图

## 实体关系图（文本版）

```
┌─────────────────────────────────┐
│      trading_reviews            │
│  (交易复盘记录)                  │
├─────────────────────────────────┤
│ id (PK)                         │
│ date                            │
│ stock_code (IX)                 │
│ stock_name                      │
│ operation                       │
│ price                           │
│ quantity                        │
│ total_amount                    │
│ reason                          │
│ review                          │
│ profit                          │
│ profit_percent                  │
│ created_at                      │
│ updated_at                      │
└─────────────────────────────────┘
         │
         │ stock_code
         │
         ▼
┌─────────────────────────────────┐
│      zt_pool_history            │
│  (涨停股票池历史)                 │
├─────────────────────────────────┤
│ id (PK)                         │
│ date (IX)                       │
│ time                            │
│ index                           │
│ code (IX) ──────────────────────┼──┐
│ name                            │  │
│ change_percent                  │  │
│ latest_price                    │  │
│ turnover                        │  │
│ circulating_market_value         │  │
│ total_market_value              │  │
│ turnover_rate                   │  │
│ sealing_funds                   │  │
│ first_sealing_time              │  │
│ last_sealing_time               │  │
│ explosion_count                 │  │
│ zt_statistics                   │  │
│ continuous_boards (IX)          │  │
│ industry (IX)                   │  │
│ created_at                      │  │
└─────────────────────────────────┘  │
                                      │
┌─────────────────────────────────┐  │
│      zbgc_pool_history          │  │
│  (炸板股票池历史)                 │  │
├─────────────────────────────────┤  │
│ id (PK)                         │  │
│ date (IX)                       │  │
│ time                            │  │
│ index                           │  │
│ code (IX) ──────────────────────┼──┤
│ name                            │  │
│ change_percent                  │  │
│ latest_price                    │  │
│ limit_price                     │  │
│ turnover                        │  │
│ circulating_market_value         │  │
│ total_market_value              │  │
│ turnover_rate                   │  │
│ rise_speed                      │  │
│ first_sealing_time              │  │
│ explosion_count (IX)            │  │
│ zt_statistics                   │  │
│ amplitude                       │  │
│ industry                        │  │
│ created_at                      │  │
└─────────────────────────────────┘  │
                                      │
┌─────────────────────────────────┐  │
│      dtgc_pool_history          │  │
│  (跌停股票池历史)                 │  │
├─────────────────────────────────┤  │
│ id (PK)                         │  │
│ date (IX)                       │  │
│ time                            │  │
│ index                           │  │
│ code (IX) ──────────────────────┼──┘
│ name                            │
│ change_percent                  │
│ latest_price                    │
│ turnover                        │
│ circulating_market_value         │
│ total_market_value              │
│ pe_ratio                        │
│ turnover_rate                   │
│ sealing_funds                   │
│ last_sealing_time               │
│ board_turnover                  │
│ continuous_limit_down (IX)      │
│ open_count                      │
│ industry                        │
│ created_at                      │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│      sector_history             │
│  (板块历史数据)                   │
├─────────────────────────────────┤
│ id (PK)                         │
│ date (IX)                       │
│ index                           │
│ name (IX) ──────────────────────┼──┐
│ change_percent                  │  │
│ total_volume                    │  │
│ total_amount                    │  │
│ net_inflow                      │  │
│ up_count                        │  │
│ down_count                       │  │
│ avg_price                       │  │
│ leading_stock                   │  │
│ leading_stock_price             │  │
│ leading_stock_change_percent    │  │
│ created_at                      │  │
└─────────────────────────────────┘  │
         │                             │
         │ name                        │
         │                             │
         ▼                             │
┌─────────────────────────────────┐   │
│      board_change_history       │   │
│  (板块异动历史)                   │   │
├─────────────────────────────────┤   │
│ id (PK)                         │   │
│ date (IX)                       │   │
│ time                            │   │
│ name (IX) ──────────────────────┼───┘
│ change_percent                  │
│ net_inflow                      │
│ total_change_count (IX)         │
│ most_frequent_stock_code        │
│ most_frequent_stock_name        │
│ most_frequent_direction         │
│ change_types (JSON)             │
│ created_at                      │
└─────────────────────────────────┘
```

## 关系说明

### 1. 股票代码关联
- `trading_reviews.stock_code` ↔ `zt_pool_history.code`
- `trading_reviews.stock_code` ↔ `zbgc_pool_history.code`
- `trading_reviews.stock_code` ↔ `dtgc_pool_history.code`

**用途**: 查询某只股票的交易记录和涨停/炸板/跌停历史

### 2. 板块名称关联
- `sector_history.name` ↔ `board_change_history.name`

**用途**: 查询某板块的历史数据和异动记录

### 3. 日期关联
所有表都通过 `date` 字段关联，支持：
- 跨表时间序列分析
- 按日期范围查询
- 时间序列可视化

## 索引说明

- **(PK)**: 主键
- **(IX)**: 索引
- **复合索引**: `(date, code)`, `(date, name)`

## 数据流向

```
外部数据源 (akshare)
    │
    ├─→ sector_history (板块信息)
    ├─→ zt_pool_history (涨停股票)
    ├─→ zbgc_pool_history (炸板股票)
    ├─→ dtgc_pool_history (跌停股票)
    └─→ board_change_history (板块异动)
    
用户输入
    └─→ trading_reviews (交易复盘)
```

## 查询场景

### 场景1: 查询股票历史表现
```sql
-- 查询某股票的所有涨停记录
SELECT * FROM zt_pool_history 
WHERE code = '000001' 
ORDER BY date DESC;

-- 查询该股票的交易复盘记录
SELECT * FROM trading_reviews 
WHERE stock_code = '000001'
ORDER BY date DESC;
```

### 场景2: 板块分析
```sql
-- 查询某板块的历史涨跌幅
SELECT date, change_percent 
FROM sector_history 
WHERE name = '银行' 
ORDER BY date DESC;

-- 查询该板块的异动记录
SELECT * FROM board_change_history 
WHERE name = '银行' 
ORDER BY date DESC;
```

### 场景3: 时间序列分析
```sql
-- 查询最近30天的涨停股票数量
SELECT date, COUNT(*) as count
FROM zt_pool_history
WHERE date >= DATE('now', '-30 days')
GROUP BY date
ORDER BY date;
```

