# A股交易复盘系统

一个支持A股指数查询、板块信息查询和交易复盘记录的完整系统。

## 功能特性

- 📈 A股指数查询（使用akshare）
- 🏢 板块信息查询（同花顺行业一览表）
- 📈 涨停股票池查询和导出
- 💥 炸板股票池查询和导出
- 📉 跌停股票池查询和导出
- 🔔 板块异动查询和导出
- 📝 交易复盘记录（增删改查）
- 📊 Streamlit数据可视化
- 🔌 RESTful API接口
- 🧪 完整的单元测试覆盖

## 技术栈

- Python 3.11+
- Flask (Web框架)
- SQLAlchemy (ORM)
- SQLite (数据库)
- Streamlit (数据可视化)
- Plotly (交互式图表)
- akshare (股票数据接口)
- pandas (数据处理)

## 安装

```bash
# 安装依赖
pip install -r requirements.txt
```

## 运行

### API服务

```bash
# 开发模式
python app.py

# 或使用Flask CLI
flask run
```

API服务将在 `http://localhost:5000` 启动

### 数据可视化（Streamlit）

```bash
# 方式1：使用启动脚本
./start_visualization.sh

# 方式2：直接运行
streamlit run streamlit_app.py
```

可视化应用将在 `http://localhost:8501` 启动

详细说明请参考 [README_STREAMLIT.md](README_STREAMLIT.md)

## 项目结构

```
.
├── app.py                 # Flask应用入口
├── config.py             # 配置文件
├── models/               # 数据模型
│   ├── __init__.py
│   └── trading_review.py
├── services/             # 业务逻辑层
│   ├── __init__.py
│   ├── stock_index_service.py
│   ├── sector_service.py
│   └── trading_review_service.py
├── api/                  # API路由
│   ├── __init__.py
│   ├── stock_index.py
│   ├── sector.py
│   └── trading_review.py
├── database/             # 数据库相关
│   ├── __init__.py
│   └── db.py
├── tests/               # 单元测试
│   ├── __init__.py
│   └── test_*.py
└── data/                # 数据目录（SQLite数据库）
```

## API接口文档

### 1. A股指数查询

- `GET /api/stock-index` - 获取所有指数
- `GET /api/stock-index/<code>` - 获取指定指数信息
- `GET /api/stock-index/search?keyword=<keyword>` - 搜索指数

### 2. 板块信息查询

- `GET /api/sector` - 获取所有板块信息（同花顺行业一览表）

### 3. 涨停股票池

- `GET /api/zt-pool` - 获取涨停股票池（实时数据）
- `GET /api/zt-pool?date=YYYY-MM-DD` - 从数据库获取指定日期的数据
- `GET /api/zt-pool?api_date=YYYYMMDD` - 从API获取指定日期的数据
- `GET /api/zt-pool?save=true` - 获取数据并保存到数据库
- `POST /api/zt-pool` - 保存当前涨停股票池到数据库
- `GET /api/zt-pool/history?date=YYYY-MM-DD` - 获取历史数据
- `GET /api/zt-pool/history?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` - 获取日期范围数据
- `POST /api/zt-pool/export` - 导出涨停股票池到Excel

### 4. 炸板股票池

- `GET /api/zb-pool` - 获取炸板股票池（实时数据）
- `GET /api/zb-pool?date=YYYY-MM-DD` - 从数据库获取指定日期的数据
- `GET /api/zb-pool?api_date=YYYYMMDD` - 从API获取指定日期的数据
- `GET /api/zb-pool?save=true` - 获取数据并保存到数据库
- `POST /api/zb-pool` - 保存当前炸板股票池到数据库
- `GET /api/zb-pool/history?date=YYYY-MM-DD` - 获取历史数据
- `GET /api/zb-pool/history?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` - 获取日期范围数据
- `POST /api/zb-pool/export` - 导出炸板股票池到Excel

### 5. 跌停股票池

- `GET /api/dt-pool` - 获取跌停股票池（实时数据）
- `GET /api/dt-pool?date=YYYY-MM-DD` - 从数据库获取指定日期的数据
- `GET /api/dt-pool?api_date=YYYYMMDD` - 从API获取指定日期的数据
- `GET /api/dt-pool?save=true` - 获取数据并保存到数据库
- `POST /api/dt-pool` - 保存当前跌停股票池到数据库
- `GET /api/dt-pool/history?date=YYYY-MM-DD` - 获取历史数据
- `GET /api/dt-pool/history?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` - 获取日期范围数据
- `POST /api/dt-pool/export` - 导出跌停股票池到Excel

### 6. 板块异动

- `GET /api/board-change` - 获取当日板块异动详情
- `POST /api/board-change/export` - 导出板块异动到Excel

### 7. 交易复盘记录

- `GET /api/trading-review` - 获取所有记录
- `GET /api/trading-review/<id>` - 获取指定记录
- `POST /api/trading-review` - 创建新记录
- `PUT /api/trading-review/<id>` - 更新记录
- `DELETE /api/trading-review/<id>` - 删除记录
- `GET /api/trading-review/date/<date>` - 按日期查询
- `GET /api/trading-review/stock/<code>` - 按股票代码查询
- `GET /api/trading-review/statistics` - 获取统计信息

## 测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=. --cov-report=html
```

## 环境变量

创建 `.env` 文件：

```
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=sqlite:///data/trading_review.db
```

