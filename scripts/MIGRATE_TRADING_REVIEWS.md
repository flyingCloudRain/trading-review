# 交易日志表迁移说明

## 问题描述

如果遇到以下错误：
```
column trading_reviews.take_profit_price does not exist
```

说明数据库表已存在，但缺少新添加的止盈止损字段。

## 解决方案

### 方法1: 使用SQL脚本（推荐，最简单）

1. 打开 Supabase Dashboard
2. 进入 SQL Editor
3. 复制并执行 `scripts/migrate_add_take_profit_stop_loss.sql` 文件中的SQL语句

或者直接执行以下SQL：

```sql
-- 添加 take_profit_price 列
ALTER TABLE trading_reviews 
ADD COLUMN IF NOT EXISTS take_profit_price DECIMAL(10, 2);

-- 添加 stop_loss_price 列
ALTER TABLE trading_reviews 
ADD COLUMN IF NOT EXISTS stop_loss_price DECIMAL(10, 2);
```

### 方法2: 使用Python迁移脚本

如果环境已配置好，可以运行：

```bash
python scripts/migrate_add_take_profit_stop_loss.py
```

### 方法3: 在Streamlit应用中自动迁移

可以在应用启动时自动检查并添加缺失的列。修改 `database/db_supabase.py` 中的 `init_db()` 函数，添加类似的检查逻辑。

## 验证

执行迁移后，可以通过以下SQL验证：

```sql
SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'trading_reviews'
    AND column_name IN ('take_profit_price', 'stop_loss_price')
ORDER BY column_name;
```

应该看到两行结果：
- `take_profit_price` | `numeric` | `YES`
- `stop_loss_price` | `numeric` | `YES`

## 注意事项

- 这两个字段都是可选的（nullable），不会影响现有数据
- 迁移是安全的，不会删除或修改现有数据
- 建议在生产环境执行前先备份数据

