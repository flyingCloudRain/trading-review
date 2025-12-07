# stock_sz_a_spot_em 接口分析

## 接口概述

`akshare.stock_sz_a_spot_em()` 是获取**深圳A股实时行情**的接口，专门用于获取深圳证券交易所A股股票的实时行情数据。

## 调用方式

```python
import akshare as ak

# 获取所有深圳A股实时行情
df = ak.stock_sz_a_spot_em()
```

## 接口特点

### 1. **数据范围**
- **专门针对深圳A股**：只返回深圳证券交易所的A股股票数据
- **实时行情**：返回当前交易时段的实时行情数据
- **数据量**：通常返回 2000+ 条深圳A股数据

### 2. **与其他接口的对比**

| 接口 | 数据范围 | 数据量 | 用途 |
|------|---------|--------|------|
| `stock_sz_a_spot_em()` | 仅深圳A股 | ~2000+ | 专门获取深圳A股 |
| `stock_sh_a_spot_em()` | 仅上海A股 | ~1800+ | 专门获取上海A股 |
| `stock_zh_a_spot_em()` | 所有A股（沪深） | ~4000+ | 获取全部A股数据 |

### 3. **适用场景**

- ✅ **需要专门分析深圳A股**时使用
- ✅ **减少数据量**：如果只需要深圳A股，使用此接口可以避免获取不必要的上海A股数据
- ✅ **提高效率**：数据量较小，获取速度更快
- ✅ **代码筛选**：深圳A股代码通常以 `00`、`30` 开头（如 `000001`、`300001`）

## 返回数据格式

接口返回一个 pandas DataFrame，包含以下列：

| 列名 | 说明 | 数据类型 | 示例 |
|------|------|----------|------|
| 代码 | 股票代码（可能包含前缀，如 sz000001） | str | "sz000001" 或 "000001" |
| 名称 | 股票名称 | str | "平安银行" |
| 最新价 | 最新成交价 | float | 12.50 |
| 涨跌幅 | 涨跌幅百分比 | float | 2.50 |
| 涨跌额 | 涨跌金额 | float | 0.30 |
| 成交量 | 成交量（手） | float | 1000000 |
| 成交额 | 成交额（元） | float | 125000000 |
| 今开 | 今日开盘价 | float | 12.20 |
| 最高 | 最高价 | float | 12.60 |
| 最低 | 最低价 | float | 12.10 |
| 昨收 | 昨日收盘价 | float | 12.20 |
| 振幅 | 振幅百分比 | float | 4.10 |
| 量比 | 量比 | float | 1.20 |
| 换手率 | 换手率百分比 | float | 3.50 |
| 市盈率 | 市盈率 | float | 15.30 |
| 总市值 | 总市值（元） | float | 250000000000 |
| 流通市值 | 流通市值（元） | float | 200000000000 |

## 代码格式说明

### 代码前缀
- **sz**: 深圳证券交易所（如 sz000001）
- **无前缀**: 部分接口可能返回无前缀的6位代码（如 000001）

### 代码标准化
如果需要统一代码格式，可以去除前缀：

```python
# 标准化代码格式
df['code_normalized'] = df['代码'].astype(str).str.replace('sz', '').str.replace('sh', '').str.replace('bj', '').str.strip()
```

### 深圳A股代码特征
- **主板**：以 `00` 开头（如 `000001` 平安银行）
- **中小板**：以 `002` 开头（如 `002001` 新和成）
- **创业板**：以 `30` 开头（如 `300001` 特锐德）

## 使用示例

### 示例1：获取所有深圳A股实时行情

```python
import akshare as ak
import pandas as pd

# 获取深圳A股实时行情
df = ak.stock_sz_a_spot_em()

print(f"获取到 {len(df)} 只深圳A股")
print(f"列名: {list(df.columns)}")

# 显示前5条数据
print(df.head())
```

### 示例2：筛选特定股票

```python
import akshare as ak

# 获取深圳A股实时行情
df = ak.stock_sz_a_spot_em()

# 标准化代码
df['code_normalized'] = df['代码'].astype(str).str.replace('sz', '').str.strip()

# 筛选特定股票（例如：000001）
target_code = '000001'
stock = df[df['code_normalized'] == target_code]

if not stock.empty:
    print(f"找到股票: {stock.iloc[0]['名称']}")
    print(f"最新价: {stock.iloc[0]['最新价']}")
    print(f"涨跌幅: {stock.iloc[0]['涨跌幅']}%")
else:
    print(f"未找到代码为 {target_code} 的股票")
```

### 示例3：筛选涨停股票

```python
import akshare as ak

# 获取深圳A股实时行情
df = ak.stock_sz_a_spot_em()

# 筛选涨停股票（涨跌幅 >= 9.9%）
zt_stocks = df[df['涨跌幅'] >= 9.9]

print(f"深圳A股涨停股票数: {len(zt_stocks)}")
print(zt_stocks[['代码', '名称', '最新价', '涨跌幅']])
```

### 示例4：按涨跌幅排序

```python
import akshare as ak

# 获取深圳A股实时行情
df = ak.stock_sz_a_spot_em()

# 按涨跌幅降序排序
df_sorted = df.sort_values('涨跌幅', ascending=False)

# 显示涨幅TOP10
print("深圳A股涨幅TOP10:")
print(df_sorted.head(10)[['代码', '名称', '最新价', '涨跌幅']])
```

### 示例5：统计涨跌情况

```python
import akshare as ak

# 获取深圳A股实时行情
df = ak.stock_sz_a_spot_em()

# 统计涨跌情况
up_count = len(df[df['涨跌幅'] > 0])
down_count = len(df[df['涨跌幅'] < 0])
flat_count = len(df[df['涨跌幅'] == 0])

print(f"深圳A股统计:")
print(f"  上涨: {up_count} 只")
print(f"  下跌: {down_count} 只")
print(f"  平盘: {flat_count} 只")
print(f"  平均涨跌幅: {df['涨跌幅'].mean():.2f}%")
```

## 在项目中的应用

### 当前使用场景

在 `pages/4_涨停股票池.py` 中，我们使用了 `stock_zh_a_spot_em()` 来获取所有A股实时行情，用于查询"前一交易日涨停股票今日表现"。

### 优化建议

如果需要专门查询深圳A股的表现，可以使用 `stock_sz_a_spot_em()` 来提高效率：

```python
# 原代码（获取所有A股）
today_stocks_df = ak.stock_zh_a_spot_em()

# 优化后（如果只需要深圳A股）
today_stocks_df = ak.stock_sz_a_spot_em()
```

### 代码匹配示例

在"前一交易日涨停股票今日表现"功能中，如果前一交易日的涨停股票都是深圳A股，可以使用此接口：

```python
import akshare as ak

# 获取前一交易日的涨停股票代码
prev_zt_stocks = [...]  # 从数据库获取
prev_stock_codes = [stock.get('code') for stock in prev_zt_stocks]

# 判断是否都是深圳A股（代码以 00 或 30 开头）
is_all_sz = all(
    code.startswith('00') or code.startswith('30') 
    for code in prev_stock_codes
    if code and len(code) >= 2
)

if is_all_sz:
    # 使用深圳A股专用接口
    today_stocks_df = ak.stock_sz_a_spot_em()
else:
    # 使用全部A股接口
    today_stocks_df = ak.stock_zh_a_spot_em()
```

## 注意事项

1. **网络连接**: 接口需要网络连接，如果连接失败会抛出异常
2. **数据更新**: 数据是实时行情，在交易时间内会持续更新
3. **数据量**: 获取所有深圳A股时，返回的数据量较大（通常2000+条）
4. **代码格式**: 返回的代码可能包含 `sz` 前缀，需要标准化处理
5. **交易时间**: 非交易时间可能返回空数据或上一交易日数据
6. **接口稳定性**: 接口可能因网络或服务器问题暂时不可用，需要添加异常处理

## 异常处理

```python
import akshare as ak
import time

def get_sz_stocks_with_retry(max_retries=3, delay=1):
    """带重试机制的获取深圳A股数据"""
    for attempt in range(max_retries):
        try:
            df = ak.stock_sz_a_spot_em()
            return df
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"第 {attempt + 1} 次尝试失败，{delay} 秒后重试...")
                time.sleep(delay)
            else:
                print(f"获取数据失败: {str(e)}")
                raise
    return None
```

## 相关接口

- `stock_sh_a_spot_em()`: 获取上海A股实时行情
- `stock_zh_a_spot_em()`: 获取所有A股实时行情（沪深）
- `stock_bj_a_spot_em()`: 获取北京A股实时行情（如果存在）

## 总结

`stock_sz_a_spot_em()` 接口是专门用于获取深圳A股实时行情的接口，适合以下场景：
- ✅ 只需要深圳A股数据时
- ✅ 需要减少数据量提高效率时
- ✅ 专门分析深圳市场时

在项目中，可以根据实际需求选择使用 `stock_sz_a_spot_em()` 或 `stock_zh_a_spot_em()`。

