# 交易日志表初始化说明

## 方法1: 使用Python脚本（推荐）

运行初始化脚本：

```bash
python scripts/init_trading_reviews_table.py
```

这个脚本会：
- 检查表是否存在
- 如果不存在，自动创建表
- 如果存在，检查并添加缺失的列（如止盈止损字段）
- 验证表结构

## 方法2: 使用SQL脚本（Supabase）

如果使用Supabase，可以直接在Supabase Dashboard的SQL编辑器中执行：

```sql
-- 文件位置: scripts/supabase_setup.sql
-- 或者直接执行以下SQL
```

执行 `scripts/supabase_setup.sql` 文件中的交易日志表创建部分。

## 方法3: 使用init_db()函数

在Python代码中调用：

```python
from database.db import init_db
init_db()
```

这会自动创建所有表，包括 `trading_reviews` 表。

## 表结构

交易日志表 (`trading_reviews`) 包含以下字段：

- `id`: 主键，自增
- `date`: 交易日期 (YYYY-MM-DD)
- `stock_code`: 股票代码
- `stock_name`: 股票名称
- `operation`: 操作类型 (buy/sell)
- `price`: 成交价格
- `quantity`: 成交数量
- `total_amount`: 成交总额
- `reason`: 交易原因
- `review`: 复盘总结
- `profit`: 盈亏金额（可选）
- `profit_percent`: 盈亏比例（可选）
- `take_profit_price`: 止盈价格（可选）
- `stop_loss_price`: 止损价格（可选）
- `created_at`: 创建时间
- `updated_at`: 更新时间

## 索引

表会自动创建以下索引：
- `idx_trading_reviews_date`: 日期索引
- `idx_trading_reviews_stock_code`: 股票代码索引
- `idx_trading_reviews_date_stock`: 日期+股票代码复合索引

## 验证

创建表后，可以通过以下方式验证：

1. 在Supabase Dashboard中查看表结构
2. 运行 `python scripts/check_database_tables.py` 检查表
3. 在交易日志页面尝试添加一条记录

## 注意事项

- 如果表已存在但缺少新字段（如止盈止损），运行初始化脚本会自动添加
- 建议在生产环境执行前先备份数据
- 确保数据库连接配置正确

