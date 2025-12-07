# 🚀 Streamlit Cloud 快速部署

## 5 步完成部署

### 1️⃣ 准备代码
```bash
# 检查部署准备
python3 check_deployment.py

# 提交代码（如果还没有）
git add .
git commit -m "准备部署到 Streamlit Cloud"
```

### 2️⃣ 推送到 GitHub
```bash
# 如果还没有 GitHub 仓库
git remote add origin https://github.com/你的用户名/你的仓库名.git
git push -u origin main
```

### 3️⃣ 登录 Streamlit Cloud
- 访问：https://share.streamlit.io/
- 使用 GitHub 账号登录

### 4️⃣ 创建应用
1. 点击 **"New app"**
2. 选择你的 GitHub 仓库
3. 设置：
   - **Main file path**: `streamlit_app.py`
   - **Python version**: `3.11`
   - **App URL**: 自定义（可选）

### 5️⃣ 配置 Secrets
在应用设置 → Secrets 中添加：

```toml
DATABASE_URL = "sqlite:///data/trading_review.db"
SECRET_KEY = "your-secret-key-here"
```

**或使用 Supabase**（推荐）：
```toml
DATABASE_URL = "postgresql://postgres:password@db.project.supabase.co:5432/postgres"
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_ANON_KEY = "your-anon-key"
SUPABASE_DB_PASSWORD = "your-password"
SUPABASE_PROJECT_REF = "your-project-ref"
```

### ✅ 完成！

应用 URL: `https://your-app-name.streamlit.app`

---

## 📚 详细文档

- **完整指南**: [STREAMLIT_CLOUD_DEPLOY.md](STREAMLIT_CLOUD_DEPLOY.md)
- **Supabase 配置**: [SUPABASE_SETUP.md](SUPABASE_SETUP.md)
- **通用部署**: [DEPLOYMENT.md](DEPLOYMENT.md)

---

## ⚠️ 重要提示

1. **不要提交敏感信息**：`.env` 和 `secrets.toml` 已在 `.gitignore` 中
2. **使用 Supabase**：SQLite 数据会在应用重启后丢失
3. **定期备份**：重要数据请定期备份

---

## 🆘 遇到问题？

1. 运行 `python3 check_deployment.py` 检查配置
2. 查看 [STREAMLIT_CLOUD_DEPLOY.md](STREAMLIT_CLOUD_DEPLOY.md) 的故障排查部分
3. 检查 Streamlit Cloud 的部署日志

