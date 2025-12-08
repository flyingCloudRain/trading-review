# IPv4 vs IPv6 默认行为说明

## 📋 当前代码的默认行为

### **默认强制使用 IPv4**

根据 `database/db_supabase.py` 中的代码逻辑：

1. **代码明确指定使用 IPv4**
   ```python
   # 只获取 IPv4 地址（AF_INET），忽略 IPv6
   ip_addresses = socket.getaddrinfo(hostname, None, socket.AF_INET, socket.SOCK_STREAM)
   ```
   - 使用 `socket.AF_INET` 明确指定只获取 IPv4 地址
   - 忽略 IPv6 地址（`AF_INET6`）

2. **自动转换逻辑**
   - 解析域名时，**优先获取 IPv4 地址**
   - 如果成功获取 IPv4，**使用 IPv4 地址替换域名**
   - 如果无法获取 IPv4，**回退到原始主机名**（可能是 IPv6 或域名）

3. **IPv6 检测和处理**
   - 如果检测到 IPv6 地址格式（包含 `::` 或 `[]`），会尝试强制转换为 IPv4
   - 如果转换失败，会记录警告但继续使用原始连接

---

## 🔍 为什么会出现 IPv6 连接错误？

### psycopg2 的默认行为

虽然代码中强制使用 IPv4，但 **psycopg2（PostgreSQL 驱动）的默认行为**是：

1. **系统 DNS 解析可能返回 IPv6**
   - 当解析 `db.uvtmbjgndhcmlupridss.supabase.co` 时
   - DNS 服务器可能同时返回 IPv4 和 IPv6 地址
   - psycopg2 可能优先尝试 IPv6（如果系统支持）

2. **Streamlit Cloud 环境限制**
   - Streamlit Cloud 的网络环境可能不支持 IPv6
   - 导致 IPv6 连接失败：`Cannot assign requested address`

3. **代码转换时机**
   - 代码在**连接前**尝试将域名转换为 IPv4 地址
   - 但如果转换失败或 psycopg2 仍然使用 IPv6，就会出现错误

---

## ✅ 解决方案

### 方案 1: 使用连接池 URI（推荐）

**连接池 URI 通常使用 IPv4**，可以避免 IPv6 问题：

```toml
DATABASE_POOLER_URL = "postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres?pgbouncer=true"
```

**优势**：
- ✅ 连接池通常配置为使用 IPv4
- ✅ 更好的性能和稳定性
- ✅ 避免 IPv6 连接问题

### 方案 2: 代码强制 IPv4（当前实现）

当前代码已经实现了强制 IPv4 的逻辑：

1. **DNS 解析时只获取 IPv4**
   ```python
   socket.getaddrinfo(hostname, None, socket.AF_INET, socket.SOCK_STREAM)
   ```

2. **使用 IPv4 地址替换域名**
   ```python
   database_url = f"postgresql://user:pass@{ipv4_address}:5432/db"
   ```

3. **检测并处理 IPv6 格式**
   - 如果检测到 IPv6 地址，尝试转换为 IPv4

---

## 🔧 如何确认使用的协议

### 查看日志

在应用启动时，查看日志输出：

```
✅ 使用 IPv4 地址连接: 1.2.3.4 (原始主机名: db.xxx.supabase.co)
```

如果看到这个日志，说明**成功使用 IPv4**。

### 如果看到 IPv6 错误

如果仍然出现 IPv6 连接错误：

1. **检查是否使用了连接池 URI**
   - 推荐使用 `DATABASE_POOLER_URL`
   - 连接池通常避免 IPv6 问题

2. **检查 DNS 解析**
   - 确认域名可以解析到 IPv4 地址
   - 如果只能解析到 IPv6，可能需要联系 Supabase 支持

3. **使用 IP 地址直接连接**（不推荐，但可以作为临时方案）
   - 手动获取 IPv4 地址
   - 在连接字符串中直接使用 IP 地址

---

## 📊 总结

| 项目 | 默认行为 | 说明 |
|------|---------|------|
| **代码逻辑** | **强制 IPv4** | 使用 `AF_INET` 只获取 IPv4 地址 |
| **psycopg2** | **可能优先 IPv6** | 如果系统支持，可能优先尝试 IPv6 |
| **Streamlit Cloud** | **可能不支持 IPv6** | 导致 IPv6 连接失败 |
| **推荐方案** | **使用连接池 URI** | 连接池通常使用 IPv4，避免问题 |

---

## 💡 最佳实践

1. **优先使用连接池 URI** (`DATABASE_POOLER_URL`)
   - 避免 IPv6 问题
   - 更好的性能

2. **如果必须使用标准连接**
   - 确保代码的 IPv4 转换逻辑正常工作
   - 查看日志确认使用 IPv4

3. **监控连接错误**
   - 如果出现 IPv6 错误，检查配置
   - 考虑切换到连接池 URI

---

## 🔍 相关代码位置

- **IPv4 强制逻辑**: `database/db_supabase.py` 第 43-105 行
- **连接池支持**: `config_supabase.py` 第 44-74 行
- **配置指南**: `STREAMLIT_CLOUD_SECRETS.md`

