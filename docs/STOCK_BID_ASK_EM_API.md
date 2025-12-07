# stock_bid_ask_em 接口分析

## 接口概述

`akshare.stock_bid_ask_em()` 是获取**股票买卖盘（五档行情）**的接口，用于获取指定股票的实时买卖盘数据，包括五档买盘和五档卖盘的价格和数量。

## 调用方式

```python
import akshare as ak

# 获取指定股票的买卖盘数据
df = ak.stock_bid_ask_em(symbol="000001")  # 平安银行
```

## 接口特点

### 1. **数据格式**
- **长格式（Long Format）**：返回的数据是长格式的 DataFrame，包含两列：
  - `item`: 字段名称（如 `sell_5`, `buy_1`, `最新`, `涨幅` 等）
  - `value`: 对应的数值
- **数据量**：通常返回 36 行数据（包含五档买卖盘、实时行情、统计信息等）

### 2. **数据内容**
接口返回的数据包含以下信息：
- **五档卖盘**：`sell_5`, `sell_4`, `sell_3`, `sell_2`, `sell_1`（价格）
- **五档卖盘数量**：`sell_5_vol`, `sell_4_vol`, `sell_3_vol`, `sell_2_vol`, `sell_1_vol`
- **五档买盘**：`buy_1`, `buy_2`, `buy_3`, `buy_4`, `buy_5`（价格）
- **五档买盘数量**：`buy_1_vol`, `buy_2_vol`, `buy_3_vol`, `buy_4_vol`, `buy_5_vol`
- **实时行情**：最新价、均价、涨幅、涨跌、总手、金额、换手、量比等
- **价格信息**：最高、最低、今开、昨收、涨停、跌停
- **内外盘**：外盘、内盘

### 3. **适用场景**
- ✅ **实时交易分析**：查看当前买卖盘情况
- ✅ **价格压力分析**：分析买卖盘对价格的影响
- ✅ **流动性分析**：评估股票的流动性
- ✅ **交易决策**：辅助交易决策

## 返回数据格式

### 原始格式（长格式）

接口返回一个 pandas DataFrame，包含以下列：

| 列名 | 说明 | 数据类型 | 示例 |
|------|------|----------|------|
| item | 字段名称 | str | "sell_5", "buy_1", "最新" |
| value | 字段值 | float | 11.74, 11.69, 11.69 |

### 数据字段说明

| item | 说明 | 单位 | 示例 |
|------|------|------|------|
| sell_5 | 卖五价 | 元 | 11.74 |
| sell_5_vol | 卖五量 | 手 | 145900 |
| sell_4 | 卖四价 | 元 | 11.73 |
| sell_4_vol | 卖四量 | 手 | 91500 |
| sell_3 | 卖三价 | 元 | 11.72 |
| sell_3_vol | 卖三量 | 手 | 111300 |
| sell_2 | 卖二价 | 元 | 11.71 |
| sell_2_vol | 卖二量 | 手 | 102200 |
| sell_1 | 卖一价 | 元 | 11.70 |
| sell_1_vol | 卖一量 | 手 | 631600 |
| buy_1 | 买一价 | 元 | 11.69 |
| buy_1_vol | 买一量 | 手 | 29500 |
| buy_2 | 买二价 | 元 | 11.68 |
| buy_2_vol | 买二量 | 手 | 66200 |
| buy_3 | 买三价 | 元 | 11.67 |
| buy_3_vol | 买三量 | 手 | 522200 |
| buy_4 | 买四价 | 元 | 11.66 |
| buy_4_vol | 买四量 | 手 | 880800 |
| buy_5 | 买五价 | 元 | 11.65 |
| buy_5_vol | 买五量 | 手 | 1618700 |
| 最新 | 最新价 | 元 | 11.69 |
| 均价 | 平均价 | 元 | 11.75 |
| 涨幅 | 涨跌幅 | % | -1.35 |
| 涨跌 | 涨跌额 | 元 | -0.16 |
| 总手 | 总成交量 | 手 | 1465359 |
| 金额 | 总成交额 | 元 | 1721871000 |
| 换手 | 换手率 | % | 0.76 |
| 量比 | 量比 | - | 1.23 |
| 最高 | 最高价 | 元 | 11.88 |
| 最低 | 最低价 | 元 | 11.66 |
| 今开 | 今日开盘价 | 元 | 11.80 |
| 昨收 | 昨日收盘价 | 元 | 11.85 |
| 涨停 | 涨停价 | 元 | 13.04 |
| 跌停 | 跌停价 | 元 | 10.67 |
| 外盘 | 外盘成交量 | 手 | 602900 |
| 内盘 | 内盘成交量 | 手 | 862459 |

## 代码格式说明

### 支持的代码格式
- **标准6位代码**：`"000001"`（推荐）
- **带前缀代码**：`"sz000001"`, `"sh600000"`（可能支持）

### 代码类型
- **深圳A股**：以 `00`、`30` 开头（如 `000001`, `300001`）
- **上海A股**：以 `60` 开头（如 `600000`）

## 使用示例

### 示例1：获取买卖盘数据（原始格式）

```python
import akshare as ak

# 获取买卖盘数据
df = ak.stock_bid_ask_em(symbol="000001")

print(f"数据形状: {df.shape}")
print(df)
```

### 示例2：转换为宽格式（更易使用）

```python
import akshare as ak
import pandas as pd

# 获取买卖盘数据
df = ak.stock_bid_ask_em(symbol="000001")

# 转换为宽格式（字典）
data_dict = dict(zip(df['item'], df['value']))

# 访问数据
print(f"最新价: {data_dict.get('最新', 'N/A')}")
print(f"涨幅: {data_dict.get('涨幅', 'N/A')}%")
print(f"买一价: {data_dict.get('buy_1', 'N/A')}")
print(f"买一量: {data_dict.get('buy_1_vol', 'N/A')} 手")
print(f"卖一价: {data_dict.get('sell_1', 'N/A')}")
print(f"卖一量: {data_dict.get('sell_1_vol', 'N/A')} 手")
```

### 示例3：转换为DataFrame（宽格式）

```python
import akshare as ak
import pandas as pd

# 获取买卖盘数据
df_long = ak.stock_bid_ask_em(symbol="000001")

# 转换为宽格式DataFrame
df_wide = df_long.set_index('item').T

# 访问数据
print(f"最新价: {df_wide['最新'].values[0]}")
print(f"涨幅: {df_wide['涨幅'].values[0]}%")
print(f"买一价: {df_wide['buy_1'].values[0]}")
print(f"买一量: {df_wide['buy_1_vol'].values[0]} 手")
```

### 示例4：提取五档买卖盘

```python
import akshare as ak
import pandas as pd

# 获取买卖盘数据
df = ak.stock_bid_ask_em(symbol="000001")

# 转换为字典
data = dict(zip(df['item'], df['value']))

# 提取五档买盘
buy_orders = []
for i in range(1, 6):
    price_key = f'buy_{i}'
    vol_key = f'buy_{i}_vol'
    if price_key in data and vol_key in data:
        buy_orders.append({
            '档位': f'买{i}',
            '价格': data[price_key],
            '数量(手)': data[vol_key]
        })

# 提取五档卖盘
sell_orders = []
for i in range(1, 6):
    price_key = f'sell_{i}'
    vol_key = f'sell_{i}_vol'
    if price_key in data and vol_key in data:
        sell_orders.append({
            '档位': f'卖{i}',
            '价格': data[price_key],
            '数量(手)': data[vol_key]
        })

# 显示
print("五档卖盘:")
for order in reversed(sell_orders):  # 从卖五到卖一
    print(f"  {order['档位']}: {order['价格']:.2f} 元, {order['数量(手)']:.0f} 手")

print(f"\n最新价: {data.get('最新', 'N/A')}")

print("\n五档买盘:")
for order in buy_orders:  # 从买一到买五
    print(f"  {order['档位']}: {order['价格']:.2f} 元, {order['数量(手)']:.0f} 手")
```

### 示例5：计算买卖盘压力

```python
import akshare as ak

# 获取买卖盘数据
df = ak.stock_bid_ask_em(symbol="000001")
data = dict(zip(df['item'], df['value']))

# 计算买盘总量（五档）
total_buy_volume = sum([
    data.get(f'buy_{i}_vol', 0) for i in range(1, 6)
])

# 计算卖盘总量（五档）
total_sell_volume = sum([
    data.get(f'sell_{i}_vol', 0) for i in range(1, 6)
])

# 计算买盘总金额
total_buy_amount = sum([
    data.get(f'buy_{i}', 0) * data.get(f'buy_{i}_vol', 0) for i in range(1, 6)
])

# 计算卖盘总金额
total_sell_amount = sum([
    data.get(f'sell_{i}', 0) * data.get(f'sell_{i}_vol', 0) for i in range(1, 6)
])

print(f"买盘总量: {total_buy_volume:,.0f} 手")
print(f"卖盘总量: {total_sell_volume:,.0f} 手")
print(f"买盘总金额: {total_buy_amount:,.2f} 元")
print(f"卖盘总金额: {total_sell_amount:,.2f} 元")
print(f"买卖盘比例: {total_buy_volume / total_sell_volume:.2f}" if total_sell_volume > 0 else "N/A")
```

### 示例6：批量获取多只股票的买卖盘

```python
import akshare as ak
import pandas as pd
import time

stock_codes = ["000001", "600000", "300001"]
results = []

for code in stock_codes:
    try:
        df = ak.stock_bid_ask_em(symbol=code)
        data = dict(zip(df['item'], df['value']))
        
        results.append({
            '代码': code,
            '最新价': data.get('最新', 0),
            '涨幅': data.get('涨幅', 0),
            '买一价': data.get('buy_1', 0),
            '买一量': data.get('buy_1_vol', 0),
            '卖一价': data.get('sell_1', 0),
            '卖一量': data.get('sell_1_vol', 0),
        })
        
        # 避免请求过快
        time.sleep(0.5)
    except Exception as e:
        print(f"获取 {code} 失败: {str(e)}")

df_results = pd.DataFrame(results)
print(df_results)
```

## 数据转换工具函数

### 转换为字典格式

```python
def bid_ask_to_dict(df):
    """将买卖盘数据转换为字典"""
    return dict(zip(df['item'], df['value']))
```

### 转换为宽格式DataFrame

```python
def bid_ask_to_wide(df):
    """将买卖盘数据转换为宽格式DataFrame"""
    return df.set_index('item').T
```

### 提取五档数据

```python
def extract_bid_ask_levels(df):
    """提取五档买卖盘数据"""
    data = dict(zip(df['item'], df['value']))
    
    buy_levels = []
    sell_levels = []
    
    for i in range(1, 6):
        buy_levels.append({
            '档位': i,
            '价格': data.get(f'buy_{i}', 0),
            '数量': data.get(f'buy_{i}_vol', 0)
        })
        
        sell_levels.append({
            '档位': i,
            '价格': data.get(f'sell_{i}', 0),
            '数量': data.get(f'sell_{i}_vol', 0)
        })
    
    return {
        'buy': buy_levels,
        'sell': sell_levels,
        'current_price': data.get('最新', 0),
        'change_pct': data.get('涨幅', 0)
    }
```

## 在项目中的应用

### 潜在应用场景

1. **涨停股票分析**
   - 分析涨停股票的买卖盘情况
   - 判断封板强度（买一量 vs 卖一量）
   - 评估后续走势

2. **交易决策辅助**
   - 查看买卖盘压力
   - 判断价格支撑和阻力
   - 评估流动性

3. **实时监控**
   - 监控重点股票的买卖盘变化
   - 及时发现异常情况

### 使用建议

```python
# 在涨停股票池页面中，可以添加买卖盘分析
def analyze_bid_ask(stock_code):
    """分析股票的买卖盘情况"""
    try:
        df = ak.stock_bid_ask_em(symbol=stock_code)
        data = dict(zip(df['item'], df['value']))
        
        return {
            'current_price': data.get('最新', 0),
            'buy_1_price': data.get('buy_1', 0),
            'buy_1_volume': data.get('buy_1_vol', 0),
            'sell_1_price': data.get('sell_1', 0),
            'sell_1_volume': data.get('sell_1_vol', 0),
            'spread': data.get('sell_1', 0) - data.get('buy_1', 0),  # 买卖价差
            'buy_pressure': sum([data.get(f'buy_{i}_vol', 0) for i in range(1, 6)]),
            'sell_pressure': sum([data.get(f'sell_{i}_vol', 0) for i in range(1, 6)])
        }
    except Exception as e:
        return None
```

## 注意事项

1. **网络连接**: 接口需要网络连接，如果连接失败会抛出异常
2. **数据更新**: 数据是实时行情，在交易时间内会持续更新
3. **调用频率**: 避免频繁调用，建议添加延迟（如 0.5-1 秒）
4. **交易时间**: 非交易时间可能返回空数据或上一交易日数据
5. **数据格式**: 返回的是长格式，需要转换为宽格式才能更方便使用
6. **代码格式**: 推荐使用标准6位代码（如 `"000001"`），避免使用前缀

## 异常处理

```python
import akshare as ak
import time

def get_bid_ask_with_retry(stock_code, max_retries=3, delay=1):
    """带重试机制的获取买卖盘数据"""
    for attempt in range(max_retries):
        try:
            df = ak.stock_bid_ask_em(symbol=stock_code)
            if df.empty:
                if attempt < max_retries - 1:
                    print(f"返回空数据，{delay} 秒后重试...")
                    time.sleep(delay)
                    continue
                else:
                    return None
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

- `stock_zh_a_spot_em()`: 获取所有A股实时行情
- `stock_sz_a_spot_em()`: 获取深圳A股实时行情
- `stock_sh_a_spot_em()`: 获取上海A股实时行情

## 总结

`stock_bid_ask_em()` 接口是获取股票买卖盘（五档行情）数据的专用接口，适合以下场景：
- ✅ 需要查看实时买卖盘情况
- ✅ 分析价格压力和支撑
- ✅ 评估流动性和交易活跃度
- ✅ 辅助交易决策

**数据格式特点**：
- 返回长格式 DataFrame（需要转换）
- 包含五档买卖盘、实时行情、统计信息等
- 数据实时更新，适合交易时间内使用

