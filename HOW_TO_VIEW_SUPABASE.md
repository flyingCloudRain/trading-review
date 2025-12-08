# 如何查看 Supabase 配置

## 📋 访问 Supabase Dashboard

### 1. 登录 Supabase

1. **访问 Supabase Dashboard**
   - 打开浏览器，访问：https://supabase.com/dashboard
   - 使用你的账号登录

2. **选择项目**
   - 在项目列表中找到你的项目
   - 点击项目名称进入项目详情

---

## 🔍 查看配置信息

### 方法 1: Settings -> General（项目基本信息）

1. **进入设置**
   - 点击左侧菜单的 **"Settings"**（设置）
   - 选择 **"General"**（常规）

2. **查看项目信息**
   - **Reference ID**: 这就是 `SUPABASE_PROJECT_REF`
     - 例如：`uvtmbjgndhcmlupridss`
   - **Project URL**: 这就是 `SUPABASE_URL`
     - 例如：`https://uvtmbjgndhcmlupridss.supabase.co`

### 方法 2: Settings -> Database（数据库配置）

1. **进入数据库设置**
   - 点击左侧菜单的 **"Settings"**
   - 选择 **"Database"**（数据库）

2. **查看连接信息**
   - **Database password**: 这就是 `SUPABASE_DB_PASSWORD`
     - 如果忘记了，可以点击 "Reset database password" 重置
   - **Connection string**: 完整的连接字符串（可选）
   - **Connection pooling**: 连接池配置（重要！）

3. **查看连接池信息**
   - **Connection Pooling Mode**: 
     - `Transaction` 模式：端口 `6543`
     - `Session` 模式：端口 `5432`
   - **Connection Pooler URL**: 连接池 URL（推荐使用）

### 方法 3: Settings -> API（API 配置）

1. **进入 API 设置**
   - 点击左侧菜单的 **"Settings"**
   - 选择 **"API"**

2. **查看 API 密钥**
   - **Project URL**: `SUPABASE_URL`
   - **anon public key**: `SUPABASE_ANON_KEY`（用于客户端）
   - **service_role secret key**: `SUPABASE_SERVICE_KEY`（用于服务端，⚠️ 需保密）

---

## 🔧 检查 IP 封禁状态

### 如果遇到连接错误，可能是 IP 被封禁

1. **查看封禁的 IP**
   - 进入 **Settings -> Database**
   - 滚动到 **"Network Restrictions"** 部分
   - 查看 **"Banned IPs"** 列表

2. **解除 IP 封禁**
   - 在 **"Banned IPs"** 列表中找到你的 IP
   - 点击 **"Unban"** 按钮解除封禁
   - 或者等待 30 分钟自动解除

3. **添加 IP 白名单**（可选）
   - 在 **"Network Restrictions"** 中
   - 添加你的 IP 地址到白名单
   - 这样可以避免被封禁

---

## 🌐 使用连接池解决 IPv6 问题

### 为什么使用连接池？

- **避免 IPv6 问题**：连接池通常使用不同的端口和配置
- **更好的性能**：连接池可以复用连接
- **更稳定**：减少连接超时和错误

### 如何配置连接池

1. **获取连接池 URL**
   - 进入 **Settings -> Database**
   - 找到 **"Connection Pooling"** 部分
   - 复制 **"Connection Pooler URL"**

2. **连接池 URL 格式**
   ```
   postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres?pgbouncer=true
   ```

3. **使用连接池端口**
   - **Transaction 模式**: 端口 `6543`（推荐用于应用）
   - **Session 模式**: 端口 `5432`（不推荐，可能有 IPv6 问题）

---

## 📝 当前项目配置信息

根据你的项目，配置信息应该是：

```toml
# 项目基本信息（从 Settings -> General 获取）
SUPABASE_PROJECT_REF = "uvtmbjgndhcmlupridss"
SUPABASE_URL = "https://uvtmbjgndhcmlupridss.supabase.co"

# 数据库配置（从 Settings -> Database 获取）
SUPABASE_DB_PASSWORD = "你的数据库密码"

# API 配置（从 Settings -> API 获取）
SUPABASE_ANON_KEY = "你的 anon key"
```

---

## 🔍 检查数据库状态

### 1. 查看数据库运行状态

1. **进入 Database 页面**
   - 点击左侧菜单的 **"Database"**
   - 查看数据库是否正常运行

2. **查看连接数**
   - 在 **Database** 页面查看当前连接数
   - 如果连接数过多，可能需要使用连接池

### 2. 测试数据库连接

1. **使用 SQL Editor**
   - 点击左侧菜单的 **"SQL Editor"**
   - 执行简单查询：`SELECT version();`
   - 如果查询成功，说明数据库正常运行

2. **查看表结构**
   - 在 **SQL Editor** 中执行：
   ```sql
   SELECT table_name 
   FROM information_schema.tables 
   WHERE table_schema = 'public';
   ```
   - 查看已创建的表

---

## 🆘 常见问题排查

### 问题 1: 无法连接数据库

**检查步骤**：
1. ✅ 确认 `SUPABASE_PROJECT_REF` 正确
2. ✅ 确认 `SUPABASE_DB_PASSWORD` 正确
3. ✅ 检查 IP 是否被封禁
4. ✅ 尝试使用连接池 URL

### 问题 2: IPv6 连接错误

**解决方法**：
1. 使用连接池（端口 6543）
2. 检查网络环境是否支持 IPv6
3. 联系 Supabase 支持

### 问题 3: 密码错误

**解决方法**：
1. 进入 **Settings -> Database**
2. 点击 **"Reset database password"**
3. 设置新密码
4. 更新 Streamlit Cloud Secrets

---

## 📚 相关资源

- [Supabase 官方文档](https://supabase.com/docs)
- [连接池文档](https://supabase.com/docs/guides/database/connecting-to-postgres#connection-pooler)
- [网络限制文档](https://supabase.com/docs/guides/platform/network-restrictions)

---

## 💡 提示

- **定期检查**：定期查看 Supabase Dashboard 了解项目状态
- **保存配置**：将配置信息保存在安全的地方
- **使用连接池**：对于生产环境，强烈建议使用连接池
- **监控连接**：定期检查连接数和性能指标

