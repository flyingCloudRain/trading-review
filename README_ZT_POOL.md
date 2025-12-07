# 涨停股票池功能说明

## 功能概述

系统支持获取当日涨停股票并导出到Excel文件。

## 接口说明

### akshare接口

使用 `stock_zt_pool_em` 接口获取涨停股票池数据：
- 接口：`ak.stock_zt_pool_em(date='YYYYMMDD')`
- 数据来源：东方财富网-行情中心-涨停板行情
- 返回字段：16个字段，包括代码、名称、涨跌幅、成交额、封板资金、连板数等

## 使用方法

### 1. 命令行导出

```bash
# 导出今日涨停股票
python3 scripts/export_zt_pool.py

# 导出指定日期的涨停股票
python3 scripts/export_zt_pool.py -d 20241115
```

### 2. API接口

#### 获取涨停股票池数据

```bash
# 获取今日涨停股票
curl http://localhost:5000/api/zt-pool

# 获取指定日期的涨停股票
curl "http://localhost:5000/api/zt-pool?date=20241115"
```

#### 导出到Excel

```bash
curl -X POST http://localhost:5000/api/zt-pool/export \
  -H "Content-Type: application/json" \
  -d '{"date": "20241115"}'
```

### 3. Python代码调用

```python
from services.zt_pool_service import ZtPoolService
from utils.zt_pool_excel_export import export_zt_pool_to_excel

# 获取涨停股票数据
stocks = ZtPoolService.get_zt_pool(date='20241115')

# 导出到Excel
excel_file = export_zt_pool_to_excel(date='20241115')
```

## Excel文件说明

- **文件路径**: `data/涨停股票池.xlsx`
- **工作表名称**: `涨停股票`
- **数据追加**: 新数据会追加到同一个sheet中
- **去重机制**: 如果同一天的数据已存在，会先删除旧数据再添加新数据

## 数据字段说明

Excel文件包含以下字段（共18列）：

1. **序号** - 排序序号
2. **代码** - 股票代码
3. **名称** - 股票名称
4. **日期** - 交易日
5. **时间** - 导出时间
6. **涨跌幅(%)** - 涨跌幅百分比
7. **最新价** - 最新价格
8. **成交额** - 成交金额
9. **流通市值** - 流通市值
10. **总市值** - 总市值
11. **换手率(%)** - 换手率百分比
12. **封板资金** - 封板资金
13. **首次封板时间** - 首次封板时间（格式：HHMMSS）
14. **最后封板时间** - 最后封板时间（格式：HHMMSS）
15. **炸板次数** - 炸板次数
16. **涨停统计** - 涨停统计（格式：X/Y）
17. **连板数** - 连续涨停板数
18. **所属行业** - 所属行业

## 注意事项

1. 日期格式必须为 `YYYYMMDD`（如：20241115）
2. 如果指定日期不是交易日或没有涨停股票，可能返回空数据
3. Excel文件会持续增长，建议定期备份或归档
4. 同一天多次导出会覆盖当天的数据

## 定时任务集成（可选）

如果需要每日自动导出涨停股票，可以在定时任务中添加：

```python
from utils.zt_pool_excel_export import export_zt_pool_to_excel

# 在定时任务中调用
export_zt_pool_to_excel()
```

