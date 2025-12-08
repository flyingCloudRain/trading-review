# Streamlit Cloud 快速配置指南（与本地环境同步）

本指南帮助你将本地环境的数据库配置同步到 Streamlit Cloud。

## 🚀 快速配置

### 方法1：使用同步脚本（推荐）

```bash
# 运行同步脚本，自动生成配置
python3 scripts/sync_streamlit_secrets.py
```

脚本会自动读取本地 `.env` 文件，生成 Streamlit Cloud Secrets 配置。

### 方法2：手动复制配置

直接使用以下配置（已与本地环境同步）：

```toml
# 必需配置
SUPABASE_PROJECT_REF = "uvtmbjgndhcmlupridss"
SUPABASE_DB_PASSWORD = "n/QSrA!T/P@Wf6."

# 可选配置
SUPABASE_URL = "https://uvtmbjgndhcmlupridss.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2dG1iamduZGhjbWx1cHJpZHNzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM0MDA2MjksImV4cCI6MjA3ODk3NjYyOX0.KCu_julbsWVNtfVQKWZIefJKVMdqsBoHL8o44DwxbRY"
```

## 📋 配置步骤

1. **访问 Streamlit Cloud**
   - 打开 https://share.streamlit.io/
   - 进入你的应用

2. **打开 Secrets 配置**
   - 点击应用右上角的 **"⋮"** 菜单
   - 选择 **"Settings"**
   - 点击 **"Secrets"** 标签

3. **粘贴配置**
   - 将上面的配置内容粘贴到编辑器中
   - 确保格式正确（TOML 格式）

4. **保存并部署**
   - 点击 **"Save"** 保存配置
   - 应用会自动重新部署

## ✅ 验证配置

配置完成后，检查：

- [ ] 应用可以正常启动
- [ ] 没有数据库连接错误
- [ ] 可以正常加载数据
- [ ] 各个页面功能正常

## 🔄 配置同步

如果本地 `.env` 文件更新了，可以：

1. **重新运行同步脚本**
   ```bash
   python3 scripts/sync_streamlit_secrets.py
   ```

2. **手动更新 Streamlit Cloud Secrets**
   - 复制新的配置值
   - 在 Streamlit Cloud 中更新 Secrets
   - 保存并重新部署

## 📚 相关文档

- [详细配置指南](STREAMLIT_CLOUD_SECRETS.md)
- [自动配置指南](STREAMLIT_CLOUD_AUTO_SETUP.md)
- [部署检查清单](STREAMLIT_CLOUD_CHECKLIST.md)

---

**提示**：配置已与本地环境同步，可以直接使用。

