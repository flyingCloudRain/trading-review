# Streamlit Cloud 重新部署指南

## 🚀 快速重新部署

### 方法 1: 自动重新部署（推荐）

Streamlit Cloud 会自动检测 GitHub 仓库的更新并重新部署：

1. **推送代码到 GitHub**
   ```bash
   git add .
   git commit -m "更新应用"
   git push origin main
   ```

2. **等待自动部署**
   - Streamlit Cloud 会在几分钟内自动检测到更新
   - 自动开始重新构建和部署
   - 部署完成后应用会自动更新

**优点**：
- ✅ 自动化，无需手动操作
- ✅ 每次推送代码都会自动更新
- ✅ 可以查看部署日志

---

### 方法 2: 手动触发重新部署

如果自动部署没有触发，可以手动触发：

#### 步骤 1: 访问 Streamlit Cloud

1. 打开 [Streamlit Cloud](https://share.streamlit.io/)
2. 使用 GitHub 账号登录
3. 找到你的应用

#### 步骤 2: 触发重新部署

**选项 A: 使用 "Reboot app" 按钮**
1. 点击应用右上角的 **"⋮"** 菜单
2. 选择 **"Reboot app"**
3. 应用会立即重启（使用当前代码）

**选项 B: 使用 "Redeploy" 按钮**
1. 进入应用设置（点击应用名称或设置图标）
2. 找到 **"Redeploy"** 或 **"Deploy"** 按钮
3. 点击重新部署
4. 应用会重新从 GitHub 拉取最新代码并部署

**选项 C: 通过 Settings 页面**
1. 进入应用设置页面
2. 在 **"General"** 或 **"Deployment"** 标签
3. 找到 **"Redeploy"** 或 **"Rebuild"** 按钮
4. 点击触发重新部署

---

### 方法 3: 通过 GitHub 触发

如果代码已推送到 GitHub，但 Streamlit Cloud 没有自动部署：

1. **检查 GitHub 连接**
   - 进入 Streamlit Cloud 应用设置
   - 确认 GitHub 仓库连接正常
   - 检查分支设置（通常是 `main`）

2. **手动同步**
   - 在应用设置中点击 **"Sync"** 或 **"Refresh"**
   - 这会强制 Streamlit Cloud 检查最新代码

3. **重新连接仓库**
   - 如果连接有问题，可以断开并重新连接 GitHub 仓库

---

## 📊 查看部署状态

### 查看部署日志

1. 进入 Streamlit Cloud 应用页面
2. 点击 **"Deployment logs"** 或 **"Logs"** 标签
3. 查看构建和部署日志
4. 检查是否有错误信息

### 部署状态指示

- 🟢 **Running** - 应用正在运行
- 🟡 **Deploying** - 正在部署中
- 🔴 **Error** - 部署失败（查看日志）

---

## 🔧 常见问题

### 问题 1: 自动部署没有触发

**解决方法**：
1. 确认代码已成功推送到 GitHub
2. 检查 Streamlit Cloud 的 GitHub 连接
3. 手动触发重新部署（方法 2）

### 问题 2: 部署失败

**检查清单**：
- [ ] `requirements.txt` 包含所有依赖
- [ ] `streamlit_app.py` 文件存在且正确
- [ ] 环境变量（Secrets）配置正确
- [ ] 数据库连接配置正确
- [ ] 查看部署日志中的错误信息

**解决方法**：
1. 查看部署日志，找到错误原因
2. 修复代码或配置问题
3. 重新推送代码或手动触发部署

### 问题 3: 应用更新后没有变化

**可能原因**：
- 浏览器缓存
- Streamlit 缓存

**解决方法**：
1. 硬刷新浏览器（Ctrl+Shift+R 或 Cmd+Shift+R）
2. 清除浏览器缓存
3. 在 Streamlit Cloud 中清除应用缓存（如果支持）

---

## 📝 重新部署检查清单

在重新部署前，确认：

- [ ] 代码已推送到 GitHub
- [ ] 本地测试通过
- [ ] `requirements.txt` 已更新（如有新依赖）
- [ ] 环境变量（Secrets）配置正确
- [ ] 数据库连接配置正确
- [ ] 没有语法错误

---

## 🎯 最佳实践

1. **每次更新后推送代码**
   ```bash
   git add .
   git commit -m "描述你的更改"
   git push origin main
   ```

2. **查看部署日志**
   - 部署后检查日志，确保没有错误
   - 如有错误，及时修复

3. **测试部署**
   - 部署后访问应用，测试功能是否正常
   - 检查数据加载是否正常

4. **版本控制**
   - 使用有意义的提交信息
   - 重要更改添加标签（tag）

---

## 🔗 相关链接

- [Streamlit Cloud 文档](https://docs.streamlit.io/streamlit-community-cloud)
- [部署指南](STREAMLIT_CLOUD_DEPLOY.md)
- [快速部署](QUICK_DEPLOY.md)

---

**提示**：最简单的方式就是推送代码到 GitHub，Streamlit Cloud 会自动重新部署！🚀

