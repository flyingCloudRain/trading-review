# 应用部署指南

本文档介绍如何将A股交易复盘系统部署到生产环境。

## 目录

1. [Streamlit Cloud 部署（推荐）](#1-streamlit-cloud-部署推荐)
2. [Docker 容器化部署](#2-docker-容器化部署)
3. [自托管服务器部署](#3-自托管服务器部署)
4. [云平台部署](#4-云平台部署)
5. [环境变量配置](#5-环境变量配置)
6. [数据库配置](#6-数据库配置)
7. [定时任务配置](#7-定时任务配置)

---

## 1. Streamlit Cloud 部署（推荐）

Streamlit Cloud 是官方提供的免费托管服务，最适合快速部署 Streamlit 应用。

### 前置条件

1. GitHub 账号
2. 将代码推送到 GitHub 仓库

### 部署步骤

1. **准备代码仓库**
   ```bash
   # 确保代码已提交到GitHub
   git add .
   git commit -m "准备部署"
   git push origin main
   ```

2. **创建 Streamlit Cloud 账号**
   - 访问 [Streamlit Cloud](https://streamlit.io/cloud)
   - 使用 GitHub 账号登录

3. **部署应用**
   - 点击 "New app"
   - 选择你的 GitHub 仓库
   - 设置应用路径：`streamlit_app.py`
   - 选择 Python 版本：3.11
   - 点击 "Deploy"

4. **配置环境变量**
   - 在应用设置中添加环境变量（见下方"环境变量配置"部分）

5. **访问应用**
   - Streamlit Cloud 会提供一个公开的 URL
   - 例如：`https://your-app-name.streamlit.app`

### 注意事项

- ⚠️ **免费版限制**：应用在无活动时会休眠，首次访问需要几秒启动时间
- ⚠️ **数据持久化**：SQLite 数据库在重启后会丢失，建议使用 Supabase
- ⚠️ **定时任务**：Streamlit Cloud 不支持后台定时任务，需要外部调度

---

## 2. Docker 容器化部署

使用 Docker 可以确保环境一致性，便于部署到任何支持 Docker 的平台。

### 创建 Dockerfile

创建 `Dockerfile` 文件：

```dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p /app/data

# 暴露端口
EXPOSE 8501

# 启动命令
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 创建 .dockerignore

```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv
.env
*.db
*.sqlite
.git/
.gitignore
README.md
*.md
```

### 构建和运行

```bash
# 构建镜像
docker build -t trading-review-app .

# 运行容器
docker run -d \
  -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  --name trading-review \
  --env-file .env \
  trading-review-app

# 查看日志
docker logs -f trading-review
```

### Docker Compose（推荐）

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  streamlit:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./.env:/app/.env
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  scheduler:
    build: .
    command: python run_scheduler_task.py
    volumes:
      - ./data:/app/data
      - ./.env:/app/.env
    environment:
      - DATABASE_URL=${DATABASE_URL}
    restart: unless-stopped
    # 使用 cron 调度（需要额外配置）
```

运行：

```bash
docker-compose up -d
```

---

## 3. 自托管服务器部署

### 使用 systemd 服务（Linux）

创建服务文件 `/etc/systemd/system/trading-review.service`：

```ini
[Unit]
Description=A股交易复盘系统 Streamlit 应用
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/trading-review
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable trading-review
sudo systemctl start trading-review
sudo systemctl status trading-review
```

### 使用 Nginx 反向代理

创建 Nginx 配置 `/etc/nginx/sites-available/trading-review`：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/trading-review /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 使用 SSL（Let's Encrypt）

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 4. 云平台部署

### Heroku

1. **安装 Heroku CLI**
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku
   ```

2. **创建 Procfile**
   ```
   web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
   ```

3. **部署**
   ```bash
   heroku login
   heroku create your-app-name
   heroku config:set DATABASE_URL=your-database-url
   git push heroku main
   ```

### Railway

1. 访问 [Railway](https://railway.app)
2. 连接 GitHub 仓库
3. 设置启动命令：`streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0`
4. 配置环境变量

### Render

1. 访问 [Render](https://render.com)
2. 创建新的 Web Service
3. 连接 GitHub 仓库
4. 设置：
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0`

### AWS EC2 / DigitalOcean / Linode

1. 创建虚拟机实例
2. 安装 Python 3.11 和依赖
3. 克隆代码仓库
4. 配置环境变量
5. 使用 systemd 或 Docker 运行应用
6. 配置防火墙开放 8501 端口

---

## 5. 环境变量配置

创建 `.env` 文件（不要提交到 Git）：

```bash
# 数据库配置
DATABASE_URL=sqlite:///data/trading_review.db
# 或使用 Supabase
# DATABASE_URL=postgresql://user:password@host:5432/dbname

# Supabase 配置（如果使用）
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_DB_PASSWORD=your-db-password
SUPABASE_PROJECT_REF=your-project-ref

# Flask 配置
SECRET_KEY=your-secret-key-change-in-production
FLASK_DEBUG=False

# akshare 配置
AKSHARE_TIMEOUT=30
```

### 在 Streamlit Cloud 中配置

1. 进入应用设置
2. 点击 "Secrets"
3. 添加环境变量（使用 TOML 格式）：

```toml
DATABASE_URL = "sqlite:///data/trading_review.db"
SECRET_KEY = "your-secret-key"
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_ANON_KEY = "your-anon-key"
```

---

## 6. 数据库配置

### 选项 1：SQLite（简单，但不适合生产）

- 适合：单用户、开发环境
- 缺点：不支持并发、数据持久化问题

### 选项 2：Supabase（推荐）

1. 创建 Supabase 项目
2. 配置环境变量（见上方）
3. 执行数据库初始化脚本

详细步骤见 `SUPABASE_SETUP.md`

### 选项 3：PostgreSQL（自托管）

```bash
# 安装 PostgreSQL
sudo apt install postgresql postgresql-contrib

# 创建数据库
sudo -u postgres createdb trading_review

# 配置连接
DATABASE_URL=postgresql://user:password@localhost:5432/trading_review
```

---

## 7. 定时任务配置

### 选项 1：使用 cron（Linux/macOS）

```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每日15:10执行）
10 15 * * 1-5 cd /path/to/trading-review && /path/to/venv/bin/python run_scheduler_task.py
```

### 选项 2：使用 systemd timer

创建 `/etc/systemd/system/trading-review-scheduler.service`：

```ini
[Unit]
Description=A股交易复盘系统定时任务
After=network.target

[Service]
Type=oneshot
User=your-user
WorkingDirectory=/path/to/trading-review
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python run_scheduler_task.py
```

创建 `/etc/systemd/system/trading-review-scheduler.timer`：

```ini
[Unit]
Description=每日15:10执行定时任务

[Timer]
OnCalendar=Mon-Fri 15:10:00
Persistent=true

[Install]
WantedBy=timers.target
```

启用：

```bash
sudo systemctl enable trading-review-scheduler.timer
sudo systemctl start trading-review-scheduler.timer
```

### 选项 3：使用外部调度服务

- **GitHub Actions**：使用 cron 表达式触发
- **AWS EventBridge**：定时触发 Lambda 函数
- **Google Cloud Scheduler**：定时触发 Cloud Function

---

## 部署检查清单

- [ ] 代码已推送到版本控制
- [ ] 环境变量已配置
- [ ] 数据库已初始化
- [ ] 依赖已安装（`pip install -r requirements.txt`）
- [ ] 应用可以本地运行
- [ ] 防火墙端口已开放（8501）
- [ ] SSL 证书已配置（生产环境）
- [ ] 定时任务已配置
- [ ] 日志记录已配置
- [ ] 备份策略已制定

---

## 故障排查

### 应用无法启动

1. 检查日志：`docker logs trading-review` 或 `journalctl -u trading-review`
2. 检查端口是否被占用：`lsof -i :8501`
3. 检查环境变量是否正确
4. 检查数据库连接

### 数据库连接失败

1. 检查数据库服务是否运行
2. 检查连接字符串格式
3. 检查防火墙规则
4. 检查数据库用户权限

### 定时任务不执行

1. 检查 cron/systemd timer 状态
2. 检查日志文件
3. 手动执行测试：`python run_scheduler_task.py --force`

---

## 性能优化

1. **使用 Supabase 或 PostgreSQL**：替代 SQLite 提升并发性能
2. **启用缓存**：Streamlit 内置缓存机制
3. **使用 CDN**：加速静态资源加载
4. **数据库索引**：为常用查询字段添加索引
5. **连接池**：配置数据库连接池

---

## 安全建议

1. **使用 HTTPS**：生产环境必须使用 SSL
2. **保护密钥**：不要将 `.env` 文件提交到 Git
3. **限制访问**：使用防火墙限制访问来源
4. **定期更新**：保持依赖包最新
5. **监控日志**：设置日志监控和告警

---

## 支持

如有问题，请查看：
- [README.md](README.md)
- [README_STREAMLIT.md](README_STREAMLIT.md)
- [SUPABASE_SETUP.md](SUPABASE_SETUP.md)

