# 交易原因表初始化说明

## 概述

交易原因列表已从JSON文件迁移到Supabase数据库，提供更好的数据管理和多用户支持。

## 创建表的方法

### 方法1: 使用SQL脚本（推荐，最快）

在 Supabase Dashboard 的 SQL Editor 中执行：

```sql
-- 执行 scripts/migrate_create_trading_reasons_table.sql
-- 或者执行 scripts/supabase_setup.sql 中的交易原因表部分
```

### 方法2: 使用Python初始化脚本

运行初始化脚本（会自动创建表并迁移JSON数据）：

```bash
python scripts/init_trading_reasons_table.py
```

这个脚本会：
- 检查表是否存在，如果不存在则创建
- 从JSON文件迁移现有数据到数据库
- 如果JSON文件不存在，插入默认的15个交易原因
- 验证表结构和数据

### 方法3: 使用init_db()函数

在Python代码中调用：

```python
from database.db import init_db
init_db()
```

这会自动创建所有表，包括 `trading_reasons` 表。

## 表结构

交易原因表 (`trading_reasons`) 包含以下字段：

- `id`: 主键，自增
- `reason`: 交易原因（唯一，最大100字符）
- `display_order`: 显示顺序（用于排序）
- `created_at`: 创建时间
- `updated_at`: 更新时间

## 索引

表会自动创建以下索引：
- `idx_trading_reasons_reason`: 交易原因索引（唯一）
- `idx_trading_reasons_display_order`: 显示顺序索引

## 默认数据

表创建后会自动插入15个默认交易原因：
1. 技术面突破
2. 技术面回调
3. 基本面改善
4. 基本面恶化
5. 消息面利好
6. 消息面利空
7. 资金面流入
8. 资金面流出
9. 板块轮动
10. 超跌反弹
11. 趋势跟随
12. 止盈离场
13. 止损离场
14. 调仓换股
15. 其他

## 数据迁移

如果之前使用JSON文件存储交易原因，初始化脚本会自动：
1. 读取JSON文件中的数据
2. 迁移到数据库
3. 保持原有顺序

## 向后兼容

`utils/trading_reasons.py` 已更新为：
- **优先从数据库读取**：如果数据库可用，从数据库读取
- **回退到JSON文件**：如果数据库不可用，从JSON文件读取（向后兼容）
- **自动迁移**：首次使用时自动将JSON数据迁移到数据库

## 验证

创建表后，可以通过以下方式验证：

1. 在Supabase Dashboard中查看表结构
2. 运行 `python scripts/init_trading_reasons_table.py` 查看数据
3. 在交易日志页面查看交易原因列表

## 注意事项

- 表创建后，建议删除或备份旧的JSON文件（`data/trading_reasons.json`）
- 如果数据库不可用，系统会自动回退到JSON文件
- 建议在生产环境执行前先备份数据

