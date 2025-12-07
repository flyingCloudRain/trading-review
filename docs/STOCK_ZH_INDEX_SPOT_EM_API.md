# stock_zh_index_spot_em 接口说明

## 接口概述

`akshare.stock_zh_index_spot_em()` 是获取A股指数实时行情的接口。

## 调用方式

```python
import akshare as ak

# 方式1: 获取所有指数
df = ak.stock_zh_index_spot_em()

# 方式2: 获取指定系列的指数
df_sh = ak.stock_zh_index_spot_em(symbol="上证系列指数")
df_sz = ak.stock_zh_index_spot_em(symbol="深证系列指数")
```

## 返回数据格式

接口返回一个 pandas DataFrame，包含以下列：

| 列名 | 说明 | 数据类型 | 示例 |
|------|------|----------|------|
| 代码 | 指数代码（可能包含前缀，如 sh000001, sz399006） | str | "sh000001" |
| 名称 | 指数名称 | str | "上证指数" |
| 最新价 | 最新价格 | float | 3000.00 |
| 涨跌幅 | 涨跌幅百分比 | float | 0.50 |
| 涨跌额 | 涨跌金额 | float | 15.00 |
| 成交量 | 成交量 | float | 1000000000 |
| 成交额 | 成交额 | float | 50000000000 |
| 今开 | 今日开盘价 | float | 2985.00 |
| 最高 | 最高价 | float | 3010.00 |
| 最低 | 最低价 | float | 2980.00 |
| 昨收 | 昨日收盘价 | float | 2985.00 |
| 振幅 | 振幅百分比 | float | 1.00 |
| 量比 | 量比 | float | 1.20 |

## 代码格式说明

### 代码前缀
- **sh**: 上海证券交易所指数（如 sh000001）
- **sz**: 深圳证券交易所指数（如 sz399006）

### 代码标准化
在 `StockIndexService.normalize_index_code()` 中，会去除前缀，统一为6位数字：
- `sh000001` → `000001`
- `sz399006` → `399006`

## 主要指数代码

### 上证系列指数
- `000001`: 上证指数
- `000016`: 上证50
- `000300`: 沪深300
- `000852`: 中证1000
- `000905`: 中证500

### 深证系列指数
- `399001`: 深证成指
- `399006`: 创业板指
- `399106`: 深证综指
- `399005`: 中小板指

## 注意事项

1. **网络连接**: 接口需要网络连接，如果连接失败会抛出异常
2. **数据更新**: 数据是实时行情，在交易时间内会持续更新
3. **数据量**: 获取所有指数时，返回的数据量较大（通常200+条）
4. **深证系列**: 如果不指定symbol，可能不包含所有深证系列指数，建议单独获取

## 使用示例

```python
from services.stock_index_service import StockIndexService

# 获取所有指数
indices = StockIndexService.get_index_spot()

# 获取上证系列指数
sh_indices = StockIndexService.get_index_spot(symbol="上证系列指数")

# 获取深证系列指数
sz_indices = StockIndexService.get_index_spot(symbol="深证系列指数")
```

## 数据转换

在 `StockIndexService.get_index_spot()` 中，DataFrame会被转换为字典列表，字段名转换为驼峰命名：

```python
{
    'code': '000001',           # 标准化后的代码（6位数字）
    'name': '上证指数',
    'currentPrice': 3000.00,
    'changePercent': 0.50,
    'change': 15.00,
    'volume': 1000000000,
    'amount': 50000000000,
    'open': 2985.00,
    'high': 3010.00,
    'low': 2980.00,
    'prevClose': 2985.00,
    'amplitude': 1.00,
    'volumeRatio': 1.20
}
```

## 测试脚本

运行 `test_index_spot_em.py` 可以测试接口：

```bash
python3 test_index_spot_em.py
```

## 常见问题

### Q: 为什么数据库中缺少深证系列指数？
A: 可能原因：
1. 获取数据时只调用了 `get_index_spot()` 而没有指定深证系列
2. API返回的数据中确实不包含某些深证指数
3. 代码标准化过程中出现问题

**解决方案**: 
- 在 `IndexHistoryService.save_today_indices()` 中，已添加逻辑自动检测并补充深证系列指数

### Q: 如何确保获取到所有需要的指数？
A: 
1. 先获取所有指数：`get_index_spot()`
2. 检查是否包含深证系列（399开头）
3. 如果没有，单独获取：`get_index_spot(symbol="深证系列指数")`
4. 合并数据并去重

