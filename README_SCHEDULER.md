# 定时任务说明

## 功能概述

系统已配置定时任务，每日15:10（北京时间）自动获取当日板块信息和股票池数据并保存到数据库。

## 定时任务配置

- **执行时间**: 每日 15:10（北京时间，UTC+8）
- **时区**: 使用UTC+8时区（Asia/Shanghai）
- **任务内容**:
  1. **板块信息**:
     - 获取当日同花顺行业一览表数据
     - 保存到数据库（`sector_history` 表）
     - 追加到Excel文件（`data/板块信息历史.xlsx`）
  2. **涨停股票池**:
     - 获取当日涨停股票数据
     - 保存到数据库（`zt_pool_history` 表）
  3. **炸板股票池**:
     - 获取当日炸板股票数据
     - 保存到数据库（`zbgc_pool_history` 表）
  4. **跌停股票池**:
     - 获取当日跌停股票数据
     - 保存到数据库（`dtgc_pool_history` 表）

## Excel文件说明

- **文件路径**: `data/板块信息历史.xlsx`
- **工作表名称**: `板块信息`
- **数据追加**: 新数据会追加到同一个sheet中
- **去重机制**: 如果同一天的数据已存在，会先删除旧数据再添加新数据

## 手动执行

如果需要手动触发保存（用于测试或补录数据）：

```bash
python3 scripts/manual_save_sectors.py
```

## 定时任务管理

定时任务会在Flask应用启动时自动启动。如果需要停止，可以：

1. 停止Flask应用
2. 或者在代码中调用 `scheduler.shutdown()`

## 数据库表结构

### 1. 板块历史表 (`sector_history`)
- `id`: 主键
- `date`: 日期
- `index`: 序号
- `name`: 板块名称
- `change_percent`: 涨跌幅(%)
- `total_volume`: 总成交量(万手)
- `total_amount`: 总成交额(亿元)
- `net_inflow`: 净流入(亿元)
- `up_count`: 上涨家数
- `down_count`: 下跌家数
- `avg_price`: 均价
- `leading_stock`: 领涨股
- `leading_stock_price`: 领涨股-最新价
- `leading_stock_change_percent`: 领涨股-涨跌幅(%)
- `created_at`: 创建时间

### 2. 涨停股票池历史表 (`zt_pool_history`)
- `id`: 主键
- `date`: 日期
- `code`: 股票代码
- `name`: 股票名称
- `change_percent`: 涨跌幅(%)
- `latest_price`: 最新价
- `turnover`: 成交额(亿元)
- `circulating_market_value`: 流通市值(亿元)
- `total_market_value`: 总市值(亿元)
- `turnover_rate`: 换手率(%)
- `sealing_funds`: 封板资金(亿元)
- `first_sealing_time`: 首次封板时间
- `last_sealing_time`: 最后封板时间
- `explosion_count`: 炸板次数
- `continuous_boards`: 连板数
- `industry`: 所属行业
- `created_at`: 创建时间

### 3. 炸板股票池历史表 (`zbgc_pool_history`)
- `id`: 主键
- `date`: 日期
- `code`: 股票代码
- `name`: 股票名称
- `change_percent`: 涨跌幅(%)
- `latest_price`: 最新价
- `limit_price`: 涨停价
- `turnover`: 成交额(亿元)
- `circulating_market_value`: 流通市值(亿元)
- `total_market_value`: 总市值(亿元)
- `turnover_rate`: 换手率(%)
- `rise_speed`: 涨速
- `first_sealing_time`: 首次封板时间
- `explosion_count`: 炸板次数
- `amplitude`: 振幅(%)
- `industry`: 所属行业
- `created_at`: 创建时间

### 4. 跌停股票池历史表 (`dtgc_pool_history`)
- `id`: 主键
- `date`: 日期
- `code`: 股票代码
- `name`: 股票名称
- `change_percent`: 涨跌幅(%)
- `latest_price`: 最新价
- `turnover`: 成交额(亿元)
- `circulating_market_value`: 流通市值(亿元)
- `total_market_value`: 总市值(亿元)
- `pe_ratio`: 动态市盈率
- `turnover_rate`: 换手率(%)
- `sealing_funds`: 封单资金(亿元)
- `last_sealing_time`: 最后封板时间
- `board_turnover`: 板上成交额(亿元)
- `continuous_limit_down`: 连续跌停
- `open_count`: 开板次数
- `industry`: 所属行业
- `created_at`: 创建时间

## 查询历史数据

### 板块历史数据

```python
from database.db import SessionLocal
from services.sector_history_service import SectorHistoryService
from datetime import date

db = SessionLocal()
# 获取指定日期的数据
sectors = SectorHistoryService.get_sectors_by_date(db, date(2025, 11, 17))
```

### 涨停股票池历史数据

```python
from database.db import SessionLocal
from services.zt_pool_history_service import ZtPoolHistoryService
from datetime import date

db = SessionLocal()
# 获取指定日期的数据
stocks = ZtPoolHistoryService.get_zt_pool_by_date(db, date(2025, 11, 17))
```

### 炸板股票池历史数据

```python
from database.db import SessionLocal
from services.zbgc_pool_history_service import ZbgcPoolHistoryService
from datetime import date

db = SessionLocal()
# 获取指定日期的数据
stocks = ZbgcPoolHistoryService.get_zbgc_pool_by_date(db, date(2025, 11, 17))
```

### 跌停股票池历史数据

```python
from database.db import SessionLocal
from services.dtgc_pool_history_service import DtgcPoolHistoryService
from datetime import date

db = SessionLocal()
# 获取指定日期的数据
stocks = DtgcPoolHistoryService.get_dtgc_pool_by_date(db, date(2025, 11, 17))
```

## 注意事项

1. 定时任务仅在非测试环境下启动
2. 确保系统时间正确，否则可能影响定时任务执行
3. Excel文件会持续增长，建议定期备份或归档
4. 如果某天数据获取失败，可以手动执行脚本补录

