# Streamlit Cloud Secrets 配置指南

## 🔐 必需的环境变量

在 Streamlit Cloud 中配置以下 Secrets 才能正常运行应用：

### 必需配置

```toml
SUPABASE_PROJECT_REF = "your-project-ref"
SUPABASE_DB_PASSWORD = "your-db-password"
```

### 可选配置

```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_ANON_KEY = "your-anon-key"
```

---

## 📋 配置步骤

### 1. 获取 Supabase 配置信息

1. 访问 [Supabase Dashboard](https://supabase.com/dashboard)
2. 选择你的项目
3. 获取以下信息：

#### 从 Settings -> General 获取：
- **Reference ID**: 这就是 `SUPABASE_PROJECT_REF`

#### 从 Settings -> Database 获取：
- **Database password**: 这就是 `SUPABASE_DB_PASSWORD`

#### 从 Settings -> API 获取（可选）：
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

```toml
SUPABASE_PROJECT_REF = "你的项目引用ID"
SUPABASE_DB_PASSWORD = "你的数据库密码"
SUPABASE_URL = "https://你的项目.supabase.co"
SUPABASE_ANON_KEY = "你的匿名密钥"
```

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

