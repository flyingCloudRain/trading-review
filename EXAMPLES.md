# 使用示例

## 启动服务

```bash
python app.py
```

服务将在 `http://localhost:5000` 启动

## API使用示例

### 1. 获取所有板块信息（同花顺行业一览表）

```bash
# 获取实时板块数据（从API）
curl http://localhost:5000/api/sector

# 获取实时板块数据并保存到数据库
curl "http://localhost:5000/api/sector?save=true"

# 从数据库获取指定日期的板块数据
curl "http://localhost:5000/api/sector?date=2025-11-18"
```

### 1.1. 保存板块信息到数据库

```bash
# 使用POST方法保存当前板块数据
curl -X POST http://localhost:5000/api/sector
```

### 1.2. 获取板块历史数据

```bash
# 获取所有有数据的日期列表
curl "http://localhost:5000/api/sector/history?dates=true"

# 获取指定日期的板块数据
curl "http://localhost:5000/api/sector/history?date=2025-11-18"

# 获取日期范围内的板块数据
curl "http://localhost:5000/api/sector/history?start_date=2025-11-01&end_date=2025-11-18"
```

### 2. 搜索板块

```bash
curl "http://localhost:5000/api/sector/search?keyword=银行"
```

### 3. 获取涨跌幅前10名

```bash
curl "http://localhost:5000/api/sector/top?limit=10"
```

### 4. 获取涨跌幅后10名

```bash
curl "http://localhost:5000/api/sector/bottom?limit=10"
```

### 5. 获取所有指数

```bash
curl http://localhost:5000/api/stock-index
```

### 6. 获取指定指数信息

```bash
curl http://localhost:5000/api/stock-index/000001
```

### 7. 创建交易复盘记录

```bash
curl -X POST http://localhost:5000/api/trading-review \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-01-15",
    "stockCode": "000001",
    "stockName": "平安银行",
    "operation": "buy",
    "price": 10.5,
    "quantity": 1000,
    "reason": "技术面突破",
    "review": "买入后继续观察",
    "profit": 500,
    "profitPercent": 4.76
  }'
```

### 8. 获取所有交易复盘记录

```bash
curl http://localhost:5000/api/trading-review
```

### 9. 按日期查询

```bash
curl http://localhost:5000/api/trading-review/date/2024-01-15
```

### 10. 按股票代码查询

```bash
curl http://localhost:5000/api/trading-review/stock/000001
```

### 11. 获取统计信息

```bash
curl http://localhost:5000/api/trading-review/statistics
```

### 12. 更新交易复盘记录

```bash
curl -X PUT http://localhost:5000/api/trading-review/1 \
  -H "Content-Type: application/json" \
  -d '{
    "price": 11.0,
    "quantity": 1200
  }'
```

### 13. 删除交易复盘记录

```bash
curl -X DELETE http://localhost:5000/api/trading-review/1
```

## Python代码示例

```python
import requests

BASE_URL = "http://localhost:5000/api"

# 获取板块信息
response = requests.get(f"{BASE_URL}/sector")
sectors = response.json()['data']
print(f"共获取 {len(sectors)} 个板块")

# 创建交易复盘记录
review_data = {
    "date": "2024-01-15",
    "stockCode": "000001",
    "stockName": "平安银行",
    "operation": "buy",
    "price": 10.5,
    "quantity": 1000,
    "reason": "技术面突破",
    "review": "买入后继续观察"
}
response = requests.post(f"{BASE_URL}/trading-review", json=review_data)
print(response.json())
```

