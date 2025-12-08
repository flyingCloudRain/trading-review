# Streamlit Cloud Secrets 配置指南

## 🔐 必需的环境变量

在 Streamlit Cloud 中配置以下 Secrets 才能正常运行应用：

### 方式 1: 使用 URI（推荐，最简单）

**从 Supabase Dashboard 复制连接字符串**：

1. 进入 **Settings -> Database**
2. 找到 **"Connection string"** 或 **"Connection Pooler URL"**
3. 复制完整的 URI

**在 Streamlit Cloud Secrets 中配置**：

```toml
# 方式 1A: 使用连接池 URI（强烈推荐，避免 IPv6 问题）
DATABASE_POOLER_URL = "postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres?pgbouncer=true"

# 或方式 1B: 使用标准连接 URI
DATABASE_URL = "postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres"
```

**⚠️ 注意**：只需要配置 `DATABASE_POOLER_URL` 或 `DATABASE_URL` 其中一个即可，推荐使用 `DATABASE_POOLER_URL`。

### 方式 2: 使用分离的配置（向后兼容）

如果不想使用 URI，也可以使用分离的配置：

```toml
# 必需配置
SUPABASE_PROJECT_REF = "your-project-ref"
SUPABASE_DB_PASSWORD = "your-db-password"

# 可选配置
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_ANON_KEY = "your-anon-key"
```

---

## 📋 配置步骤

### 1. 获取 Supabase 配置信息

#### 方式 1: 使用 URI（推荐）

1. 访问 [Supabase Dashboard](https://supabase.com/dashboard)
2. 选择你的项目
3. 进入 **Settings -> Database**
4. 找到 **"Connection Pooler URL"**（推荐）或 **"Connection string"**
5. 复制完整的 URI

**连接池 URI 示例**：
```
postgresql://postgres.uvtmbjgndhcmlupridss:[PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres?pgbouncer=true
```

**标准连接 URI 示例**：
```
postgresql://postgres:[PASSWORD]@db.uvtmbjgndhcmlupridss.supabase.co:5432/postgres
```

#### 方式 2: 使用分离的配置

1. 访问 [Supabase Dashboard](https://supabase.com/dashboard)
2. 选择你的项目
3. 获取以下信息：

**从 Settings -> General 获取**：
- **Reference ID**: 这就是 `SUPABASE_PROJECT_REF`

**从 Settings -> Database 获取**：
- **Database password**: 这就是 `SUPABASE_DB_PASSWORD`

**从 Settings -> API 获取（可选）**：
- **Project URL**: 这就是 `SUPABASE_URL`
- **anon public key**: 这就是 `SUPABASE_ANON_KEY`

### 2. 在 Streamlit Cloud 中配置

1. **进入应用设置**
   - 访问 [Streamlit Cloud](https://share.streamlit.io/)
   - 找到你的应用
   - 点击应用右上角的 **"⋮"** 菜单
   - 选择 **"Settings"**

2. **添加 Secrets**
   - 点击 **"Secrets"** 标签
   - 在编辑器中添加以下内容（使用 TOML 格式）：

#### 方式 1: 使用 URI（推荐）

```toml
# 推荐：使用连接池 URI（避免 IPv6 问题）
DATABASE_POOLER_URL = "postgresql://postgres.uvtmbjgndhcmlupridss:[你的密码]@aws-0-[区域].pooler.supabase.com:6543/postgres?pgbouncer=true"

# 或使用标准连接 URI
# DATABASE_URL = "postgresql://postgres:[你的密码]@db.uvtmbjgndhcmlupridss.supabase.co:5432/postgres"
```

#### 方式 2: 使用分离的配置

```toml
# 必需配置（与本地 .env 文件保持一致）
SUPABASE_PROJECT_REF = "uvtmbjgndhcmlupridss"
SUPABASE_DB_PASSWORD = "n/QSrA!T/P@Wf6."

# 可选配置（与本地 .env 文件保持一致）
SUPABASE_URL = "https://uvtmbjgndhcmlupridss.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2dG1iamduZGhjbWx1cHJpZHNzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM0MDA2MjksImV4cCI6MjA3ODk3NjYyOX0.KCu_julbsWVNtfVQKWZIefJKVMdqsBoHL8o44DwxbRY"
```

**⚠️ 注意**：
- 如果使用 URI 方式，只需要配置 `DATABASE_POOLER_URL` 或 `DATABASE_URL` 其中一个
- 推荐使用 `DATABASE_POOLER_URL`（连接池），可以避免 IPv6 问题
- 如果使用分离的配置，需要配置 `SUPABASE_PROJECT_REF` 和 `SUPABASE_DB_PASSWORD`

3. **保存并重新部署**
   - 点击 **"Save"** 保存配置
   - 应用会自动重新部署
   - 或手动点击 **"Reboot app"** 重启应用

---

## ✅ 验证配置

配置完成后，应用应该能够：
- ✅ 正常启动
- ✅ 连接 Supabase 数据库
- ✅ 显示数据页面

如果仍然出现错误，请检查：
1. Secrets 格式是否正确（TOML 格式）
2. 值是否正确（没有多余的空格或引号）
3. Supabase 项目是否正常运行

---

## 🔍 故障排查

### 错误：Supabase配置不完整

**原因**：缺少必需的环境变量

**解决方法**：
1. 检查 Secrets 中是否配置了 `SUPABASE_PROJECT_REF` 和 `SUPABASE_DB_PASSWORD`
2. 确认值是否正确
3. 保存后重新部署应用

### 错误：无法连接到 Supabase 数据库

**原因**：配置错误或网络问题

**解决方法**：
1. 检查 `SUPABASE_PROJECT_REF` 是否正确
2. 检查 `SUPABASE_DB_PASSWORD` 是否正确
3. 检查 Supabase 项目是否正常运行
4. 检查网络连接

---

## 📚 相关文档

- [Supabase 设置指南](SUPABASE_SETUP.md)
- [Streamlit Cloud 部署指南](STREAMLIT_CLOUD_DEPLOY.md)
- [重新部署指南](STREAMLIT_REDEPLOY.md)

---

## 💡 提示

- Secrets 中的值会加密存储，不会暴露在代码中
- 修改 Secrets 后需要重新部署应用才能生效
- 建议使用 Supabase 的强密码策略

