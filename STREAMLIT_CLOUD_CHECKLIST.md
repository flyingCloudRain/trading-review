# Streamlit Cloud 部署检查清单

在部署到 Streamlit Cloud 之前，请确认以下所有项目都已配置完成。

## ✅ 必需文件检查

- [x] `streamlit_app.py` - 主应用文件（在项目根目录）
- [x] `requirements.txt` - Python 依赖列表
- [x] `.streamlit/config.toml` - Streamlit 配置文件
- [x] `packages.txt` - 系统包依赖（如果需要）
- [x] `runtime.txt` - Python 版本指定（可选，推荐）
- [x] `.gitignore` - Git 忽略文件配置

## ✅ 代码检查

- [ ] 所有代码已推送到 GitHub
- [ ] 没有硬编码的敏感信息（密钥、密码等）
- [ ] 所有导入路径正确
- [ ] 应用可以在本地正常运行

## ✅ 依赖检查

- [x] `requirements.txt` 包含所有必需的包
- [x] 包含 `psycopg2-binary`（如果使用 Supabase）
- [x] 包含 `streamlit>=1.28.0`
- [x] 包含 `pandas>=2.0.0`
- [x] 包含 `plotly>=5.17.0`
- [x] 包含 `akshare>=1.17.85`

## ✅ Streamlit Cloud 配置

### 应用设置
- [ ] Main file path: `streamlit_app.py`
- [ ] Branch: `main`（或你的主分支）
- [ ] Python version: `3.11`（或更高）

### Secrets 配置（必需）
- [ ] `SUPABASE_PROJECT_REF` - Supabase 项目引用ID
- [ ] `SUPABASE_DB_PASSWORD` - Supabase 数据库密码

### Secrets 配置（可选）
- [ ] `SUPABASE_URL` - Supabase 项目URL
- [ ] `SUPABASE_ANON_KEY` - Supabase 匿名密钥

## ✅ 数据库配置

- [ ] Supabase 项目已创建
- [ ] 数据库密码已设置
- [ ] 数据库表已初始化（或应用会自动创建）
- [ ] 网络访问已配置（如果需要）

## ✅ 功能测试

部署后测试以下功能：
- [ ] 应用可以正常启动
- [ ] 数据库连接正常
- [ ] 首页可以正常显示
- [ ] 各个页面可以正常访问
- [ ] 数据加载功能正常
- [ ] 图表显示正常

## 📝 部署步骤

1. **准备代码**
   ```bash
   git add .
   git commit -m "准备部署到 Streamlit Cloud"
   git push origin main
   ```

2. **创建 Streamlit Cloud 应用**
   - 访问 https://share.streamlit.io/
   - 点击 "New app"
   - 选择仓库和分支
   - 配置 Main file path: `streamlit_app.py`

3. **配置 Secrets**
   - 进入应用设置
   - 点击 "Secrets" 标签
   - 添加必需的配置（参考 STREAMLIT_CLOUD_SECRETS.md）

4. **部署**
   - 点击 "Deploy" 或 "Save"
   - 等待部署完成
   - 检查部署日志

5. **验证**
   - 访问应用 URL
   - 测试各项功能
   - 检查错误日志（如果有）

## 🔍 常见问题

### 问题1：应用无法启动
- 检查 `streamlit_app.py` 路径是否正确
- 检查 `requirements.txt` 是否包含所有依赖
- 查看部署日志中的错误信息

### 问题2：数据库连接失败
- 检查 Secrets 配置是否正确
- 检查 Supabase 项目是否正常运行
- 查看应用日志中的错误信息

### 问题3：导入错误
- 检查所有 Python 文件路径是否正确
- 检查 `__init__.py` 文件是否存在
- 确保所有依赖都已安装

## 📚 相关文档

- [自动配置指南](STREAMLIT_CLOUD_AUTO_SETUP.md)
- [Secrets 配置指南](STREAMLIT_CLOUD_SECRETS.md)
- [部署指南](STREAMLIT_CLOUD_DEPLOY.md)
- [Supabase 设置](SUPABASE_SETUP.md)

---

**完成所有检查项后，即可开始部署！** 🚀

