# Streamlit Cloud 部署指南

本指南将帮助你将 A股交易复盘系统 部署到 Streamlit Cloud。

## 📋 前置条件

1. **GitHub 账号**：如果没有，请先注册 [GitHub](https://github.com)
2. **Streamlit Cloud 账号**：访问 [Streamlit Cloud](https://streamlit.io/cloud) 使用 GitHub 账号登录
3. **代码仓库**：将代码推送到 GitHub 仓库

---

## 🚀 快速部署步骤

### 步骤 1: 准备代码仓库

1. **初始化 Git 仓库**（如果还没有）
   ```bash
   git init
   git add .
   git commit -m "准备部署到 Streamlit Cloud"
   ```

2. **创建 GitHub 仓库**
   - 访问 [GitHub](https://github.com/new)
   - 创建新仓库（建议设为 Private 以保护数据）

3. **推送代码到 GitHub**
   ```bash
   git remote add origin https://github.com/你的用户名/你的仓库名.git
   git branch -M main
   git push -u origin main
   ```

### 步骤 2: 配置 Streamlit Cloud

1. **登录 Streamlit Cloud**
   - 访问 [Streamlit Cloud](https://share.streamlit.io/)
   - 使用 GitHub 账号登录

2. **创建新应用**
   - 点击 "New app"
   - 选择你的 GitHub 仓库
   - 选择分支（通常是 `main` 或 `master`）

3. **配置应用设置**
   - **Main file path**: `streamlit_app.py`
   - **Python version**: `3.11`（或你使用的版本）
   - **App URL**: 可以自定义（例如：`trading-review`）

### 步骤 3: 配置环境变量（Secrets）

在 Streamlit Cloud 中配置环境变量：

1. **进入应用设置**
   - 点击应用右上角的 "⋮" 菜单
   - 选择 "Settings"

2. **添加 Secrets**
   - 点击 "Secrets" 标签
   - 使用以下格式添加配置：

```toml
# 数据库配置
DATABASE_URL = "sqlite:///data/trading_review.db"
# 或使用 Supabase
# DATABASE_URL = "postgresql://user:password@host:5432/dbname"

# Flask 配置
SECRET_KEY = "your-secret-key-here-change-in-production"
FLASK_DEBUG = "False"

# Supabase 配置（如果使用）
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_ANON_KEY = "your-anon-key-here"
SUPABASE_DB_PASSWORD = "your-db-password-here"
SUPABASE_PROJECT_REF = "your-project-ref-here"

# akshare 配置
AKSHARE_TIMEOUT = "30"
```

**⚠️ 重要提示**：
- 不要在代码中硬编码密钥
- 使用 Streamlit Cloud 的 Secrets 功能管理敏感信息
- 不要将 `.env` 文件提交到 Git

### 步骤 4: 部署应用

1. **点击 "Deploy"**
   - Streamlit Cloud 会自动开始构建和部署
   - 首次部署可能需要几分钟

2. **查看部署日志**
   - 在部署过程中可以查看构建日志
   - 如果有错误，会在日志中显示

3. **访问应用**
   - 部署成功后，会显示应用 URL
   - 例如：`https://your-app-name.streamlit.app`

---

## ⚙️ 配置说明

### 数据库配置选项

#### 选项 1: SQLite（简单但不推荐用于生产）

```toml
DATABASE_URL = "sqlite:///data/trading_review.db"
```

**注意**：
- Streamlit Cloud 的文件系统是临时的
- 应用重启后数据会丢失
- 仅适合测试和演示

#### 选项 2: Supabase（推荐）

```toml
DATABASE_URL = "postgresql://postgres:password@db.project-ref.supabase.co:5432/postgres"
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_ANON_KEY = "your-anon-key"
SUPABASE_DB_PASSWORD = "your-db-password"
SUPABASE_PROJECT_REF = "your-project-ref"
```

**优势**：
- 数据持久化
- 支持并发访问
- 免费额度充足

详细配置见 [SUPABASE_SETUP.md](SUPABASE_SETUP.md)

### 应用配置

#### 主文件路径

确保 `streamlit_app.py` 在项目根目录，或者修改 Main file path。

#### Python 版本

在 `runtime.txt` 文件中指定（可选）：

```
python-3.11
```

#### 依赖管理

确保 `requirements.txt` 包含所有依赖：

```txt
akshare>=1.17.85
pandas>=2.0.0
sqlalchemy>=2.0.0
streamlit>=1.28.0
plotly>=5.17.0
python-dotenv>=1.0.0
openpyxl>=3.0.0
pytz>=2023.3
supabase>=2.0.0
```

---

## 🔧 常见问题排查

### 1. 应用无法启动

**检查**：
- 查看部署日志中的错误信息
- 确认 `streamlit_app.py` 路径正确
- 确认所有依赖都在 `requirements.txt` 中

### 2. 数据库连接失败

**检查**：
- Secrets 中的数据库 URL 格式是否正确
- 数据库服务是否可访问（Supabase 需要配置网络访问）
- 数据库用户权限是否正确

### 3. 数据丢失

**原因**：
- 使用 SQLite 且应用重启
- 文件系统是临时的

**解决**：
- 使用 Supabase 或其他外部数据库
- 定期备份数据

### 4. 导入错误

**检查**：
- 所有 Python 文件路径是否正确
- `__init__.py` 文件是否存在
- 依赖是否完整

### 5. 性能问题

**优化建议**：
- 使用 `@st.cache_data` 缓存数据
- 减少不必要的 API 调用
- 使用 Supabase 替代 SQLite

---

## 📝 部署检查清单

在部署前，请确认：

- [ ] 代码已推送到 GitHub
- [ ] `requirements.txt` 包含所有依赖
- [ ] `streamlit_app.py` 在项目根目录
- [ ] `.env` 文件已添加到 `.gitignore`
- [ ] 敏感信息已配置到 Streamlit Cloud Secrets
- [ ] 数据库已配置（Supabase 或其他）
- [ ] 应用可以本地运行
- [ ] 所有环境变量都已设置

---

## 🔄 更新应用

### 方法 1: 自动更新（推荐）

Streamlit Cloud 会自动检测 GitHub 仓库的更新：

1. 提交代码到 GitHub
   ```bash
   git add .
   git commit -m "更新应用"
   git push origin main
   ```

2. Streamlit Cloud 会自动重新部署

### 方法 2: 手动触发

1. 进入 Streamlit Cloud 应用设置
2. 点击 "Reboot app" 或 "Redeploy"

---

## 🔐 安全建议

1. **保护敏感信息**
   - 使用 Streamlit Cloud Secrets 管理密钥
   - 不要将 `.env` 文件提交到 Git
   - 定期轮换密钥

2. **访问控制**
   - 考虑将仓库设为 Private
   - 使用 Streamlit Cloud 的访问控制功能

3. **数据安全**
   - 使用 HTTPS（Streamlit Cloud 自动提供）
   - 定期备份数据库
   - 使用强密码

---

## 📊 监控和维护

### 查看应用状态

- **应用 URL**: 访问应用查看运行状态
- **部署日志**: 在 Streamlit Cloud 控制台查看
- **错误日志**: 应用中的错误会在控制台显示

### 性能监控

- Streamlit Cloud 提供基本的性能指标
- 使用 `@st.cache_data` 优化加载速度
- 监控 API 调用频率

---

## 🆘 获取帮助

如果遇到问题：

1. **查看日志**：Streamlit Cloud 控制台中的部署日志
2. **检查文档**：
   - [Streamlit Cloud 文档](https://docs.streamlit.io/streamlit-community-cloud)
   - [项目 README](README.md)
   - [部署文档](DEPLOYMENT.md)
3. **社区支持**：
   - [Streamlit 论坛](https://discuss.streamlit.io/)
   - [GitHub Issues](https://github.com/streamlit/streamlit/issues)

---

## 🎉 部署完成

部署成功后，你将获得：

- ✅ 公开的应用 URL
- ✅ 自动 HTTPS 支持
- ✅ 自动更新（GitHub 推送后）
- ✅ 免费托管（有使用限制）

**应用 URL 示例**：
```
https://your-app-name.streamlit.app
```

---

## 📚 相关文档

- [DEPLOYMENT.md](DEPLOYMENT.md) - 完整部署指南
- [SUPABASE_SETUP.md](SUPABASE_SETUP.md) - Supabase 配置
- [README.md](README.md) - 项目说明

---

**祝部署顺利！** 🚀

