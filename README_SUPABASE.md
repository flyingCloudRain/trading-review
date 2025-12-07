# Supabase数据库使用指南

## 快速开始

### 1. 创建Supabase项目

1. 访问 [supabase.com](https://supabase.com)
2. 注册/登录账号
3. 创建新项目
4. 记录项目URL和API密钥

### 2. 执行初始化脚本

在Supabase Dashboard中：
1. 进入 **SQL Editor**
2. 复制 `scripts/supabase_setup.sql` 的内容
3. 执行SQL脚本

或使用命令行：
```bash
# 使用psql连接
psql "postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres" -f scripts/supabase_setup.sql
```

### 3. 配置环境变量

创建 `.env` 文件：
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
SUPABASE_DB_PASSWORD=your-db-password
SUPABASE_PROJECT_REF=your-project-ref
```

### 4. 安装依赖

```bash
pip install supabase
```

### 5. 更新配置

修改 `config.py`：
```python
class SupabaseConfig:
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')
    DATABASE_URL = f"postgresql://postgres:{os.environ.get('SUPABASE_DB_PASSWORD')}@db.{os.environ.get('SUPABASE_PROJECT_REF')}.supabase.co:5432/postgres"
```

## 使用Supabase客户端

### Python示例

```python
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 查询数据
response = supabase.table('sector_history').select('*').eq('date', '2025-11-17').execute()

# 插入数据
response = supabase.table('trading_reviews').insert({
    'date': '2025-11-17',
    'stock_code': '000001',
    'stock_name': '平安银行',
    'operation': 'buy',
    'price': 10.5,
    'quantity': 100,
    'total_amount': 1050.0,
    'reason': '看好',
    'review': '买入',
    'user_id': user_id
}).execute()
```

## RESTful API使用

Supabase自动生成RESTful API：

```bash
# 获取今日板块数据
curl 'https://your-project.supabase.co/rest/v1/sector_history?date=eq.2025-11-17' \
  -H "apikey: YOUR_ANON_KEY" \
  -H "Authorization: Bearer YOUR_ANON_KEY"

# 获取涨停股票（排序）
curl 'https://your-project.supabase.co/rest/v1/zt_pool_history?date=eq.2025-11-17&order=continuous_boards.desc' \
  -H "apikey: YOUR_ANON_KEY"
```

## 实时订阅

```javascript
// JavaScript示例
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY)

// 订阅板块数据变更
supabase
  .channel('sector_history')
  .on('postgres_changes',
    { event: 'INSERT', schema: 'public', table: 'sector_history' },
    (payload) => {
      console.log('新数据:', payload.new)
    }
  )
  .subscribe()
```

## 迁移数据

使用迁移脚本：
```bash
python3 scripts/migrate_to_supabase.py
```

## 详细文档

- [Supabase设计文档](docs/SUPABASE_DESIGN.md)
- [Supabase官方文档](https://supabase.com/docs)

