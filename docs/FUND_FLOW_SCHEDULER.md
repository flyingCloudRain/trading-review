# 即时资金流定时任务配置

## 概述

系统已配置定时任务，每日15:10（收盘后）自动获取概念板块的即时资金流数据，确保数据的完整性和准确性。

## 定时任务时间表

### 收盘后数据保存（最终数据）
- **时间**: 每日 15:10（北京时间）
- **任务**: `save_daily_data`
- **功能**: 保存所有板块和股票池数据（行业板块、概念板块、涨停、炸板、跌停、指数）
- **说明**: 这是收盘后的最终数据，用于历史记录和分析

### 即时资金流获取

每日15:10（收盘后）执行获取概念板块的即时资金流数据：

| 时间 | 任务ID | 说明 |
|------|--------|------|
| 15:10 | `save_realtime_fund_flow_1510` | 收盘后，获取当日最终资金流向数据 |

## 任务执行逻辑

### 交易日检查
- 所有任务都会检查是否为交易日
- 非交易日自动跳过执行

### 交易时间检查（即时资金流任务）
- 即时资金流任务在15:10执行，此时已收盘，无需检查交易时间

### 数据保存
- 即时资金流任务只保存概念板块数据（`sector_type='concept'`）
- 数据会覆盖当日的旧数据，确保数据为最新
- 收盘后任务保存所有类型的数据

## 数据来源

- **概念板块资金流**: 使用 `stock_fund_flow_concept` 接口
- **数据来源**: 同花顺概念资金流页面 (https://data.10jqka.com.cn/funds/gnzjl/)
- **数据字段**: 涨跌幅、流入资金、流出资金、净流入、领涨股等

## 使用方法

### 自动执行
定时任务会在应用启动时自动启动（通过 `app.py` 中的调度器）。

### 手动执行
可以通过以下方式手动执行：

```python
from tasks.sector_scheduler import get_scheduler
from services.sector_history_service import SectorHistoryService
from database.db import SessionLocal

# 获取调度器
scheduler = get_scheduler()

# 手动执行即时资金流保存
db = SessionLocal()
try:
    count = SectorHistoryService.save_today_sectors(db, sector_type='concept')
    print(f"成功保存 {count} 条概念板块数据")
finally:
    db.close()
```

### 使用脚本
```bash
# 保存指定日期的概念板块数据
python3 scripts/save_concept_data.py --date 2025-12-05
```

## 查看定时任务状态

### 在应用中查看
访问"定时任务管理"页面，可以查看所有定时任务的状态和执行历史。

### 通过日志查看
定时任务的执行日志会记录：
- 任务执行时间
- 保存的数据条数
- 错误信息（如果有）

## 注意事项

1. **数据覆盖**: 同一日期的即时资金流数据会被覆盖，只保留最后一次获取的数据
2. **网络延迟**: 如果API调用失败，任务会记录错误但不会中断其他任务
3. **时区设置**: 所有时间都使用 UTC+8（北京时间）
4. **交易日判断**: 系统会自动判断交易日，非交易日不会执行任务

## 配置修改

如需修改定时任务时间，编辑 `tasks/sector_scheduler.py` 文件中的 `_setup_jobs` 方法。

## 相关文件

- `tasks/sector_scheduler.py`: 定时任务调度器
- `services/concept_service.py`: 概念板块数据服务
- `services/sector_history_service.py`: 板块历史数据服务
- `scripts/save_concept_data.py`: 手动保存脚本

