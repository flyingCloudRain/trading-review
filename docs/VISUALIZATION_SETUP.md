# 可视化图表设置指南

## 推荐方案：PostgreSQL + TimescaleDB + Grafana

### 1. 安装PostgreSQL和TimescaleDB

#### macOS
```bash
# 安装PostgreSQL
brew install postgresql

# 安装TimescaleDB
brew install timescaledb

# 启动PostgreSQL
brew services start postgresql
```

#### Ubuntu/Debian
```bash
# 添加TimescaleDB仓库
sudo sh -c "echo 'deb https://packagecloud.io/timescale/timescaledb/ubuntu/ $(lsb_release -c -s) main' > /etc/apt/sources.list.d/timescaledb.list"
wget --quiet -O - https://packagecloud.io/timescale/timescaledb/gpgkey | sudo apt-key add -
sudo apt-get update

# 安装
sudo apt-get install postgresql postgresql-contrib
sudo apt-get install timescaledb-2-postgresql-14
```

### 2. 创建数据库和启用TimescaleDB

```sql
-- 创建数据库
CREATE DATABASE trading_review;

-- 连接到数据库
\c trading_review

-- 启用TimescaleDB扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;
```

### 3. 迁移数据表

修改 `config.py`:
```python
DATABASE_URL = 'postgresql://user:password@localhost/trading_review'
```

### 4. 创建超表（Hypertable）

```sql
-- 将板块历史表转换为超表
SELECT create_hypertable('sector_history', 'date');

-- 为其他时间序列表创建超表（如果创建了）
-- SELECT create_hypertable('zt_pool_history', 'date');
```

### 5. 安装Grafana

#### macOS
```bash
brew install grafana
brew services start grafana
```

#### Docker
```bash
docker run -d --name=grafana -p 3000:3000 grafana/grafana
```

### 6. 配置Grafana数据源

1. 访问 http://localhost:3000
2. 添加数据源 → PostgreSQL
3. 配置连接信息
4. 测试连接

### 7. 创建可视化图表

#### 示例1：板块涨跌幅趋势图（折线图）
```sql
SELECT 
    date as time,
    AVG(change_percent) as avg_change,
    MAX(change_percent) as max_change,
    MIN(change_percent) as min_change
FROM sector_history
WHERE date >= NOW() - INTERVAL '30 days'
GROUP BY date
ORDER BY date;
```

#### 示例2：板块排名（柱状图）
```sql
SELECT 
    name,
    change_percent
FROM sector_history
WHERE date = CURRENT_DATE
ORDER BY change_percent DESC
LIMIT 20;
```

#### 示例3：涨停股票统计（饼图）
```sql
SELECT 
    industry,
    COUNT(*) as count
FROM zt_pool_history
WHERE date = CURRENT_DATE
GROUP BY industry
ORDER BY count DESC;
```

---

## 替代方案：使用Python可视化

### 使用Plotly Dash

```python
# 安装
pip install dash plotly pandas

# 创建简单的Dash应用
import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
from database.db import SessionLocal
from services.sector_history_service import SectorHistoryService

app = dash.Dash(__name__)

@app.callback(
    dash.dependencies.Output('sector-trend', 'figure'),
    [dash.dependencies.Input('date-range', 'value')]
)
def update_chart(date_range):
    db = SessionLocal()
    sectors = SectorHistoryService.get_sectors_by_date_range(
        db, start_date, end_date
    )
    df = pd.DataFrame(sectors)
    fig = px.line(df, x='date', y='changePercent', color='name')
    return fig

app.run_server(debug=True)
```

### 使用Streamlit

```python
# 安装
pip install streamlit plotly

# 创建Streamlit应用
import streamlit as st
import plotly.express as px
import pandas as pd

st.title('A股交易复盘系统 - 数据可视化')

# 加载数据
df = pd.read_excel('data/板块信息历史.xlsx', sheet_name='板块信息')

# 创建图表
fig = px.line(df, x='日期', y='涨跌幅(%)', color='板块')
st.plotly_chart(fig)
```

---

## 推荐工具对比

| 工具 | 难度 | 功能 | 适用场景 |
|------|------|------|----------|
| Grafana | 中 | ⭐⭐⭐⭐⭐ | 专业时间序列可视化 |
| Metabase | 低 | ⭐⭐⭐⭐ | 简单易用的BI工具 |
| Superset | 中 | ⭐⭐⭐⭐⭐ | 功能强大的BI工具 |
| Plotly Dash | 中 | ⭐⭐⭐⭐ | Python定制化可视化 |
| Streamlit | 低 | ⭐⭐⭐ | 快速原型开发 |

---

## 总结

**最佳组合**: PostgreSQL + TimescaleDB + Grafana
- 数据库：PostgreSQL + TimescaleDB（时间序列优化）
- 可视化：Grafana（专业时间序列图表）

**简单方案**: SQLite + Streamlit
- 数据库：继续使用SQLite
- 可视化：Streamlit（Python快速开发）

