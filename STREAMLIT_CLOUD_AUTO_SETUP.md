# Streamlit Cloud 自动配置指南

本指南将帮助你在 Streamlit Cloud 上自动配置所有必要的文件和环境。

## 🚀 快速开始

### 步骤1：准备仓库

确保你的代码已经推送到 GitHub 仓库：
```bash
git add .
git commit -m "准备部署到 Streamlit Cloud"
git push origin main
```

### 步骤2：在 Streamlit Cloud 中创建应用

1. 访问 [Streamlit Cloud](https://share.streamlit.io/)
2. 点击 **"New app"**
3. 选择你的 GitHub 仓库
4. 配置应用：
   - **Main file path**: `streamlit_app.py`
   - **Branch**: `main`
   - **Python version**: `3.11` (或更高版本)

### 步骤3：配置 Secrets（必需）

在应用设置中添加以下 Secrets（TOML 格式）：

```toml
# 必需配置
SUPABASE_PROJECT_REF = "your-project-ref"
SUPABASE_DB_PASSWORD = "your-db-password"

# 可选配置
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_ANON_KEY = "your-anon-key"
```

**如何获取这些配置？**
- 查看 [STREAMLIT_CLOUD_SECRETS.md](STREAMLIT_CLOUD_SECRETS.md) 获取详细说明

### 步骤4：部署

点击 **"Deploy"** 或 **"Save"**，Streamlit Cloud 会自动：
- ✅ 安装 `requirements.txt` 中的依赖
- ✅ 读取 `.streamlit/config.toml` 配置
- ✅ 运行 `streamlit_app.py`
- ✅ 初始化数据库连接

## 📁 自动配置的文件

项目已包含以下 Streamlit Cloud 配置文件：

### 1. `.streamlit/config.toml`
Streamlit 应用配置：
- 主题设置（颜色、字体）
- 服务器配置
- 浏览器设置
- 运行器配置

### 2. `packages.txt`
系统级包依赖（如果需要）：
- 当前为空，可根据需要添加

### 3. `requirements.txt`
Python 包依赖：
- 包含所有必需的 Python 包
- Streamlit Cloud 会自动安装

### 4. `streamlit_app.py`
主应用入口：
- 自动检测数据库配置
- 显示友好的错误提示
- 初始化数据库表

## 🔧 配置文件说明

### `.streamlit/config.toml`

```toml
[theme]
primaryColor = "#1f77b4"        # 主色调
backgroundColor = "#ffffff"      # 背景色
secondaryBackgroundColor = "#f0f2f6"  # 次要背景色
textColor = "#262730"            # 文字颜色
font = "sans serif"              # 字体

[server]
headless = true                  # 无头模式（Cloud 必需）
port = 8501                      # 端口
enableCORS = false               # 禁用 CORS
enableXsrfProtection = true      # 启用 XSRF 保护

[browser]
gatherUsageStats = false         # 不收集使用统计

[runner]
fastReruns = true                 # 快速重新运行
magicEnabled = true              # 启用魔法命令
```

### `requirements.txt`

包含所有必需的 Python 包：
- streamlit
- pandas
- plotly
- akshare
- sqlalchemy
- psycopg2-binary (Supabase PostgreSQL)
- 等等...

## ✅ 验证配置

部署完成后，检查以下几点：

1. **应用正常启动**
   - 访问应用 URL
   - 应该看到应用界面，而不是错误页面

2. **数据库连接**
   - 如果配置了 Supabase，应该能正常连接
   - 如果未配置，会显示友好的配置提示

3. **功能正常**
   - 测试各个页面功能
   - 检查数据加载是否正常

## 🔍 故障排查

### 问题1：应用无法启动

**检查**：
- `streamlit_app.py` 是否存在
- `requirements.txt` 是否包含所有依赖
- Python 版本是否兼容（建议 3.11+）

### 问题2：数据库连接失败

**检查**：
- Secrets 是否配置正确
- Supabase 项目是否正常运行
- 网络连接是否正常

**解决**：
- 查看应用日志（Streamlit Cloud 设置 → Logs）
- 检查错误信息
- 参考 [STREAMLIT_CLOUD_SECRETS.md](STREAMLIT_CLOUD_SECRETS.md)

### 问题3：依赖安装失败

**检查**：
- `requirements.txt` 格式是否正确
- 包名和版本是否正确
- Python 版本是否兼容

**解决**：
- 检查 Streamlit Cloud 日志
- 更新 `requirements.txt` 中的包版本
- 确保所有依赖都兼容 Python 3.11+

## 📚 相关文档

- [Streamlit Cloud Secrets 配置](STREAMLIT_CLOUD_SECRETS.md)
- [Supabase 设置指南](SUPABASE_SETUP.md)
- [Streamlit Cloud 部署指南](STREAMLIT_CLOUD_DEPLOY.md)
- [重新部署指南](STREAMLIT_REDEPLOY.md)

## 💡 提示

1. **首次部署**：可能需要几分钟时间安装依赖
2. **更新代码**：推送到 GitHub 后，Streamlit Cloud 会自动重新部署
3. **查看日志**：在应用设置中查看实时日志
4. **性能优化**：使用缓存（`@st.cache_data`）提高性能
5. **安全**：不要在代码中硬编码敏感信息，使用 Secrets

## 🎯 下一步

配置完成后，你可以：
- ✅ 访问应用并测试功能
- ✅ 配置定时任务（如果需要）
- ✅ 自定义主题和样式
- ✅ 添加更多功能页面

---

**需要帮助？** 查看项目文档或提交 Issue。

