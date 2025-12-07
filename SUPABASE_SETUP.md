# Supabase连接设置指南

## 快速开始

### 1. 获取Supabase项目信息

1. 访问 [Supabase Dashboard](https://supabase.com/dashboard)
2. 选择你的项目
3. 获取以下信息：

#### 从 Settings -> API 获取：
- **Project URL**: `https://your-project.supabase.co`
- **anon public key**: 用于客户端
- **service_role secret key**: 用于服务端（⚠️ 需保密）

#### 从 Settings -> Database 获取：
- **Database password**: 数据库密码
- **Connection string**: 连接字符串（可选）

#### 从 Settings -> General 获取：
- **Reference ID**: 项目引用ID（用于构建数据库URL）

---

### 2. 配置环境变量

在项目根目录创建或编辑 `.env` 文件：

```bash
# Supabase配置
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-role-key-here
SUPABASE_DB_PASSWORD=your-database-password-here
SUPABASE_PROJECT_REF=your-project-ref-here
```

**⚠️ 重要提示**：
- 不要将 `.env` 文件提交到Git
- `SUPABASE_SERVICE_KEY` 有完整权限，请妥善保管

---

### 3. 运行设置脚本

```bash
# 查看设置说明
python3 scripts/setup_supabase_connection.py

# 测试连接
python3 scripts/test_supabase_connection.py
```

---

### 4. 执行数据库初始化

在Supabase Dashboard中：

1. 进入 **SQL Editor**
2. 点击 **New Query**
3. 复制 `scripts/supabase_setup.sql` 的内容
4. 粘贴并执行

或使用命令行：

```bash
# 使用psql连接（需要安装PostgreSQL客户端）
psql "postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres" -f scripts/supabase_setup.sql
```

---

### 5. 测试连接

```bash
python3 scripts/test_supabase_connection.py
```

如果看到 "✅ 所有连接测试通过！"，说明连接成功。

---

## 使用Supabase客户端

### Python示例

```python
from supabase import create_client
from config_supabase import SupabaseConfig

# 创建客户端
supabase = create_client(
    SupabaseConfig.SUPABASE_URL,
    SupabaseConfig.SUPABASE_ANON_KEY
)

# 查询数据
response = supabase.table('sector_history').select('*').eq('date', '2025-11-18').execute()
print(response.data)

# 插入数据
response = supabase.table('trading_reviews').insert({
    'date': '2025-11-18',
    'stock_code': '000001',
    'stock_name': '平安银行',
    'operation': 'buy',
    'price': 10.5,
    'quantity': 100,
    'total_amount': 1050.0,
    'reason': '看好',
    'review': '买入'
}).execute()
```

---

## 使用SQLAlchemy连接

### 方式1: 使用Supabase数据库配置

```python
from database.db_supabase import SessionLocal, init_db

# 初始化数据库
init_db()

# 使用会话
db = SessionLocal()
try:
    # 执行查询
    sectors = db.query(SectorHistory).all()
finally:
    db.close()
```

### 方式2: 在应用中切换

修改 `config.py` 或 `database/db.py`：

```python
# 使用Supabase
from config_supabase import SupabaseConfig
DATABASE_URL = SupabaseConfig.get_database_url()

# 或继续使用SQLite
from config import Config
DATABASE_URL = Config.DATABASE_URL
```

---

## RESTful API使用

Supabase自动为每个表生成RESTful API：

```bash
# 获取今日板块数据
curl 'https://your-project.supabase.co/rest/v1/sector_history?date=eq.2025-11-18' \
  -H "apikey: YOUR_ANON_KEY" \
  -H "Authorization: Bearer YOUR_ANON_KEY"

# 获取涨停股票（排序）
curl 'https://your-project.supabase.co/rest/v1/zt_pool_history?date=eq.2025-11-18&order=continuous_boards.desc' \
  -H "apikey: YOUR_ANON_KEY"
```

---

## 实时订阅

```javascript
// JavaScript示例
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

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

---

## 迁移数据

```bash
# 从SQLite迁移到Supabase
python3 scripts/migrate_to_supabase.py
```

---

## 常见问题

### Q: 连接失败怎么办？

1. 检查 `.env` 文件配置是否正确
2. 确认Supabase项目状态正常
3. 检查网络连接
4. 验证数据库密码是否正确

### Q: 如何查看数据库表？

在Supabase Dashboard中：
- 进入 **Table Editor**
- 查看所有已创建的表

### Q: 如何启用实时订阅？

在Supabase Dashboard中：
- 进入 **Database** -> **Replication**
- 为需要的表启用实时订阅

### Q: 如何查看API文档？

在Supabase Dashboard中：
- 进入 **API** -> **REST**
- 查看自动生成的API文档

---

## 下一步

1. ✅ 完成连接设置
2. ✅ 执行数据库初始化脚本
3. ✅ 测试连接
4. 📦 迁移现有数据
5. 🔄 更新应用配置
6. 🧪 测试功能

