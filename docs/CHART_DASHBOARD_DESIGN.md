# 图表展示页面方案设计

## 一、方案概述

### 1.1 技术栈选择

**推荐方案：Streamlit + Plotly + Supabase PostgreSQL**

- ✅ **Streamlit**: 快速构建交互式Web应用，Python原生支持
- ✅ **Plotly**: 强大的交互式图表库，支持多种图表类型
- ✅ **Supabase PostgreSQL**: 已有数据库，支持复杂查询和实时数据

**备选方案**:
- **Dash**: 更灵活的Python Web框架，但开发复杂度更高
- **Grafana**: 专业时间序列可视化，需要额外部署
- **前端框架** (React/Vue) + Chart.js/ECharts: 需要前后端分离开发

### 1.2 架构设计

```
┌─────────────────┐
│  Streamlit App  │
│  (前端展示)      │
└────────┬────────┘
         │
         │ API调用 / 直接查询
         │
┌────────▼────────┐
│  Flask API      │  (可选，用于数据接口)
│  /api/sector    │
└────────┬────────┘
         │
         │ SQL查询
         │
┌────────▼────────┐
│ Supabase        │
│ PostgreSQL      │
│ (数据存储)       │
└─────────────────┘
```

## 二、功能模块设计

### 2.1 板块信息可视化模块

#### 2.1.1 实时数据看板
- **功能**: 显示当日板块数据概览
- **图表类型**:
  - 📊 **KPI指标卡片**: 总板块数、平均涨跌幅、上涨/下跌板块数
  - 📈 **涨跌幅TOP 10柱状图**: 横向/纵向柱状图
  - 📉 **涨跌幅BOTTOM 10柱状图**
  - 📊 **涨跌幅分布直方图**: 显示涨跌幅分布情况
  - 🎯 **涨跌幅热力图**: 板块名称 × 涨跌幅颜色映射

#### 2.1.2 历史趋势分析
- **功能**: 分析板块历史表现
- **图表类型**:
  - 📈 **时间序列折线图**: 
    - 单个板块涨跌幅趋势（可多选）
    - 平均涨跌幅趋势
    - 最大/最小涨跌幅趋势
  - 📊 **面积图**: 板块涨跌幅累计变化
  - 🔥 **热力图**: 板块 × 日期 × 涨跌幅（日历热力图）
  - 📉 **箱线图**: 板块涨跌幅分布统计

#### 2.1.3 板块对比分析
- **功能**: 多板块横向对比
- **图表类型**:
  - 📊 **雷达图**: 多维度对比（涨跌幅、成交量、成交额、净流入）
  - 📈 **分组柱状图**: 多个板块多指标对比
  - 📊 **散点图**: 涨跌幅 vs 成交量/成交额
  - 📈 **气泡图**: 涨跌幅 × 成交量 × 成交额（气泡大小）

#### 2.1.4 板块排名分析
- **功能**: 动态排名展示
- **图表类型**:
  - 📊 **动态排名柱状图**: 可切换不同指标排名
  - 📈 **排名变化折线图**: 板块排名历史变化
  - 📊 **排名热力图**: 板块排名 × 日期

### 2.2 涨停/炸板/跌停股票可视化模块

#### 2.2.1 涨停股票分析
- **图表类型**:
  - 📊 **连板数分布饼图/柱状图**
  - 📈 **行业分布柱状图**
  - 📊 **成交额TOP 10柱状图**
  - 📈 **连板数趋势折线图**（历史数据）

#### 2.2.2 炸板股票分析
- **图表类型**:
  - 💥 **炸板次数分布柱状图**
  - 📊 **炸板股票行业分布**
  - 📈 **炸板率趋势图**

#### 2.2.3 跌停股票分析
- **图表类型**:
  - 📉 **连续跌停分布柱状图**
  - 📊 **跌停股票行业分布**
  - 📈 **跌停数量趋势图**

### 2.3 板块异动可视化模块

#### 2.3.1 异动分析
- **图表类型**:
  - 🔔 **异动次数TOP 20柱状图**
  - 📈 **异动趋势折线图**
  - 🔥 **异动热力图**: 板块 × 日期 × 异动次数

### 2.4 交易复盘可视化模块

#### 2.4.1 交易分析
- **图表类型**:
  - 💰 **盈亏分布直方图**
  - 📈 **累计盈亏曲线**
  - 📊 **盈亏饼图**: 盈利/亏损占比
  - 📈 **交易频率折线图**
  - 📊 **股票盈亏排行**

## 三、页面布局设计

### 3.1 主页面结构

```
┌─────────────────────────────────────────────────┐
│  标题栏: A股交易复盘系统 - 数据可视化            │
├─────────────────────────────────────────────────┤
│  侧边栏          │  主内容区                     │
│  ┌───────────┐  │  ┌─────────────────────────┐  │
│  │ 导航菜单   │  │  │  筛选器区域              │  │
│  │ - 板块信息 │  │  │  [日期选择] [板块选择]  │  │
│  │ - 涨停股票 │  │  └─────────────────────────┘  │
│  │ - 炸板股票 │  │  ┌─────────────────────────┐  │
│  │ - 跌停股票 │  │  │  KPI指标卡片 (4列)      │  │
│  │ - 板块异动 │  │  └─────────────────────────┘  │
│  │ - 交易复盘 │  │  ┌─────────────────────────┐  │
│  └───────────┘  │  │  图表区域 (2列布局)      │  │
│                  │  │  [图表1] [图表2]        │  │
│                  │  │  [图表3] [图表4]        │  │
│                  │  └─────────────────────────┘  │
│                  │  ┌─────────────────────────┐  │
│                  │  │  数据表格区域            │  │
│                  │  └─────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

### 3.2 响应式布局

- **桌面端**: 2-3列布局，充分利用屏幕空间
- **平板端**: 2列布局
- **移动端**: 单列布局，图表自适应宽度

## 四、交互功能设计

### 4.1 数据筛选

- **日期选择器**: 
  - 单日选择
  - 日期范围选择
  - 快捷选项（今日、近7天、近30天、近90天）
- **板块选择器**: 
  - 多选下拉框
  - 搜索功能
  - 全选/反选
- **指标选择器**: 
  - 涨跌幅、成交量、成交额、净流入等

### 4.2 图表交互

- **Plotly交互功能**:
  - 缩放（Zoom）
  - 平移（Pan）
  - 框选（Box Select）
  - 悬停提示（Hover Tooltip）
  - 图例点击（显示/隐藏系列）
  - 数据点点击（显示详情）

### 4.3 数据导出

- **图表导出**: PNG、SVG、PDF格式
- **数据导出**: CSV、Excel格式
- **报表生成**: PDF报告（可选）

## 五、性能优化方案

### 5.1 数据查询优化

```python
# 1. 使用索引优化查询
# 数据库已有 date 和 name 索引

# 2. 数据缓存
import streamlit as st
from functools import lru_cache

@st.cache_data(ttl=300)  # 缓存5分钟
def get_sector_data(date):
    # 查询逻辑
    pass

# 3. 分页加载
# 大数据集使用分页，避免一次性加载所有数据

# 4. 预聚合数据
# 对于常用统计，可以预计算并存储
```

### 5.2 图表渲染优化

- **懒加载**: 初始只加载关键图表，其他图表按需加载
- **数据采样**: 时间序列数据过长时自动采样
- **虚拟滚动**: 数据表格使用虚拟滚动

## 六、实现步骤

### 阶段1: 基础框架搭建（1-2天）

1. ✅ 已有Streamlit应用基础
2. 优化页面布局和导航
3. 实现数据查询接口封装
4. 添加数据缓存机制

### 阶段2: 核心图表实现（3-5天）

1. **板块信息模块**:
   - KPI指标卡片
   - 涨跌幅TOP/BOTTOM柱状图
   - 涨跌幅分布直方图
   - 时间序列折线图

2. **历史趋势分析**:
   - 多板块趋势对比
   - 热力图
   - 箱线图

### 阶段3: 高级功能（3-5天）

1. **交互功能**:
   - 日期范围选择
   - 板块多选
   - 图表联动

2. **其他模块**:
   - 涨停/炸板/跌停股票可视化
   - 板块异动可视化
   - 交易复盘可视化

### 阶段4: 优化和测试（2-3天）

1. 性能优化
2. 响应式布局调整
3. 用户体验优化
4. 测试和bug修复

## 七、代码结构设计

```
streamlit_app.py (主应用)
├── pages/
│   ├── sector_dashboard.py      # 板块信息仪表盘
│   ├── sector_trend.py          # 板块趋势分析
│   ├── sector_comparison.py     # 板块对比分析
│   ├── zt_pool.py              # 涨停股票分析
│   ├── zbgc_pool.py            # 炸板股票分析
│   ├── dtgc_pool.py            # 跌停股票分析
│   ├── board_change.py         # 板块异动分析
│   └── trading_review.py        # 交易复盘分析
├── components/
│   ├── kpi_cards.py            # KPI指标卡片组件
│   ├── date_selector.py        # 日期选择器组件
│   ├── sector_selector.py      # 板块选择器组件
│   └── chart_factory.py        # 图表工厂（统一创建图表）
├── utils/
│   ├── data_loader.py          # 数据加载工具
│   ├── chart_utils.py          # 图表工具函数
│   └── cache_manager.py        # 缓存管理
└── config/
    └── chart_config.py         # 图表配置
```

## 八、示例代码

### 8.1 KPI指标卡片组件

```python
# components/kpi_cards.py
import streamlit as st

def render_kpi_cards(metrics):
    """渲染KPI指标卡片"""
    cols = st.columns(len(metrics))
    for i, (label, value, delta) in enumerate(metrics):
        with cols[i]:
            st.metric(label, value, delta)
```

### 8.2 板块趋势折线图

```python
# utils/chart_utils.py
import plotly.express as px
import pandas as pd

def create_sector_trend_chart(df, sectors, date_col='date', value_col='changePercent'):
    """创建板块趋势折线图"""
    fig = px.line(
        df[df['name'].isin(sectors)],
        x=date_col,
        y=value_col,
        color='name',
        title='板块涨跌幅趋势',
        labels={
            date_col: '日期',
            value_col: '涨跌幅(%)',
            'name': '板块'
        }
    )
    fig.update_layout(
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig
```

### 8.3 数据加载（带缓存）

```python
# utils/data_loader.py
import streamlit as st
from database.db import SessionLocal
from services.sector_history_service import SectorHistoryService
from datetime import date

@st.cache_data(ttl=300)  # 缓存5分钟
def load_sector_data(start_date: date, end_date: date, sector_names: list = None):
    """加载板块数据（带缓存）"""
    db = SessionLocal()
    try:
        sectors = SectorHistoryService.get_sectors_by_date_range(db, start_date, end_date)
        df = pd.DataFrame(sectors)
        
        if sector_names:
            df = df[df['name'].isin(sector_names)]
        
        return df
    finally:
        db.close()
```

## 九、图表配置建议

### 9.1 颜色方案

```python
# 涨跌幅颜色映射
COLOR_SCALE = {
    'positive': '#00ff00',  # 绿色 - 上涨
    'negative': '#ff0000',  # 红色 - 下跌
    'neutral': '#808080'    # 灰色 - 平盘
}

# Plotly颜色方案
COLOR_PALETTE = px.colors.qualitative.Set3  # 12色方案
```

### 9.2 图表尺寸

```python
CHART_CONFIG = {
    'height': 400,  # 标准图表高度
    'width': '100%',  # 自适应宽度
    'margin': dict(l=50, r=50, t=50, b=50)  # 边距
}
```

## 十、部署方案

### 10.1 本地运行

```bash
streamlit run streamlit_app.py --server.port 8501
```

### 10.2 生产环境部署

**方案1: Streamlit Cloud** (推荐)
- 免费托管
- 自动部署
- 支持GitHub集成

**方案2: Docker部署**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**方案3: 云服务器部署**
- 使用Nginx反向代理
- 使用systemd管理服务
- 配置SSL证书

## 十一、后续扩展建议

### 11.1 实时数据更新
- WebSocket连接
- 定时刷新机制
- 数据变更通知

### 11.2 高级分析功能
- 技术指标计算（MA、MACD等）
- 相关性分析
- 预测模型集成

### 11.3 用户功能
- 用户登录/注册
- 自定义仪表盘
- 数据收藏/分享

## 十二、总结

### 推荐实施方案

1. **短期（1-2周）**: 
   - 基于现有Streamlit应用扩展
   - 实现核心图表功能
   - 优化用户体验

2. **中期（1个月）**:
   - 完善所有模块
   - 添加高级交互功能
   - 性能优化

3. **长期（持续）**:
   - 实时数据更新
   - 高级分析功能
   - 移动端适配

### 技术优势

- ✅ **开发快速**: Streamlit + Plotly组合，快速原型
- ✅ **交互性强**: Plotly原生交互功能丰富
- ✅ **易于维护**: Python统一技术栈
- ✅ **扩展性好**: 模块化设计，易于添加新功能

