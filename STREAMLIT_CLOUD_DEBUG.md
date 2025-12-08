# Streamlit Cloud 查看详细信息指南

## 🔍 如何查看部署日志和错误信息

### 方法 1: 通过应用管理页面

1. **访问 Streamlit Cloud 主页**
   - 登录 https://share.streamlit.io/
   - 找到你的应用

2. **进入应用管理**
   - 点击应用右上角的 **"⋮"** (三个点) 菜单
   - 选择 **"Manage app"** 或 **"Settings"**

3. **查看部署日志**
   - 在管理页面中，你会看到 **"Logs"** 或 **"Deployment logs"** 部分
   - 这里显示完整的部署过程日志，包括：
     - 代码克隆过程
     - 依赖安装过程
     - 应用启动过程
     - 任何错误信息

### 方法 2: 通过应用设置页面

1. **进入设置**
   - 点击应用右上角的 **"⋮"** 菜单
   - 选择 **"Settings"**

2. **查看不同标签页**
   - **General**: 应用基本信息（主文件路径、分支等）
   - **Secrets**: 环境变量配置
   - **Advanced**: 高级设置
   - **Logs**: 部署和运行日志

### 方法 3: 直接查看终端输出

在部署过程中，Streamlit Cloud 会实时显示日志，包括：

```
[13:02:59] 🚀 Starting up repository: 'trading-review', branch: 'main'
[13:02:59] 🐙 Cloning repository...
[13:02:59] 📦 Processing dependencies...
[13:02:59] 📦 Apt dependencies were installed from packages.txt
[13:03:02] ❗️ Error during processing dependencies!
```

## 📋 常见错误类型及查看方法

### 1. 依赖安装错误

**错误提示**: `Error installing requirements`

**查看方法**:
- 在日志中查找 `📦 Processing dependencies...` 部分
- 查看 `apt-get` 或 `pip install` 的错误信息
- 常见问题：
  - `packages.txt` 格式错误（如包含注释）
  - `requirements.txt` 中的包不存在或版本冲突
  - 网络连接问题

**示例错误**:
```
E: Unable to locate package #
E: Unable to locate package Streamlit
```
这表示 `packages.txt` 中有注释被当作包名处理了。

### 2. 应用启动错误

**错误提示**: `Error running app` 或应用无法访问

**查看方法**:
- 在日志中查找 `🚀 Starting up` 或 `Running on` 部分
- 查看 Python 错误堆栈信息
- 常见问题：
  - 导入错误（缺少模块）
  - 数据库连接失败
  - 配置文件错误

### 3. 运行时错误

**错误提示**: 应用可以访问但功能异常

**查看方法**:
- 在应用页面查看错误信息（Streamlit 会显示错误）
- 在日志中查找运行时错误
- 使用浏览器开发者工具查看网络请求

## 🔧 如何修复常见问题

### 问题 1: packages.txt 格式错误

**错误信息**:
```
E: Unable to locate package #
E: Unable to locate package Streamlit
```

**解决方法**:
1. 检查 `packages.txt` 文件
2. 移除所有注释（`#` 开头的行）
3. 如果不需要系统包，保持文件为空或删除文件

**正确格式**:
```
# 如果需要系统包，每行一个包名
# build-essential
# python3-dev
```

### 问题 2: requirements.txt 安装失败

**错误信息**:
```
ERROR: Could not find a version that satisfies the requirement xxx
```

**解决方法**:
1. 检查包名是否正确
2. 检查版本号是否兼容
3. 移除不必要的依赖（如 Flask，Streamlit 应用不需要）
4. 添加版本上限避免未来不兼容

### 问题 3: 数据库连接失败

**错误信息**:
```
RuntimeError: Supabase配置不完整
```

**解决方法**:
1. 进入应用设置 → Secrets
2. 检查所有必需的配置项：
   - `SUPABASE_PROJECT_REF`
   - `SUPABASE_DB_PASSWORD`
3. 确保配置格式正确（TOML 格式）

## 📝 日志查看技巧

### 1. 搜索关键字

在日志中搜索以下关键字快速定位问题：
- `ERROR` - 错误信息
- `❗️` - 严重错误标记
- `❌` - 失败标记
- `📦` - 依赖安装相关
- `🚀` - 应用启动相关

### 2. 时间戳

日志包含时间戳，可以帮助你：
- 了解部署耗时
- 定位特定时间点的错误
- 追踪问题发生的时间

### 3. 完整日志

- 日志会显示完整的错误堆栈
- 复制错误信息用于搜索解决方案
- 分享错误信息到社区论坛获取帮助

## 🆘 获取帮助

如果问题仍然无法解决：

1. **查看官方文档**
   - https://docs.streamlit.io/streamlit-cloud

2. **社区论坛**
   - https://discuss.streamlit.io/
   - 在提问时附上：
     - 完整的错误日志
     - `requirements.txt` 内容
     - `packages.txt` 内容（如果有）
     - 应用配置信息

3. **GitHub Issues**
   - 如果是 Streamlit 的 bug，可以在 GitHub 上报告

## ✅ 检查清单

在查看日志前，确认：

- [ ] 代码已推送到 GitHub
- [ ] `requirements.txt` 格式正确
- [ ] `packages.txt` 格式正确（无注释）
- [ ] `streamlit_app.py` 路径正确
- [ ] Secrets 配置完整
- [ ] Python 版本匹配

---

**提示**: 每次推送代码后，Streamlit Cloud 会自动重新部署，你可以在日志中查看最新的部署状态。

