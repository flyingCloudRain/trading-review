# Streamlit + Plotly 可视化项目结构说明

## 📁 目录结构

```
review/
├── streamlit_app.py          # 主应用入口（保留兼容性）
├── pages/                     # Streamlit多页面（自动识别）
│   ├── __init__.py
│   ├── 1_板块仪表盘.py       # 板块信息仪表盘
│   └── 2_板块趋势分析.py     # 板块趋势分析
├── components/                # 可复用组件
│   ├── __init__.py
│   ├── kpi_cards.py          # KPI指标卡片组件
│   ├── date_selector.py      # 日期选择器组件
│   └── sector_selector.py    # 板块选择器组件
├── chart_config/              # 图表配置模块
│   ├── __init__.py
│   └── chart_config.py      # 图表配置（颜色、尺寸等）
├── utils/                     # 工具函数
│   ├── data_loader.py        # 数据加载工具（带缓存）
│   └── chart_utils.py        # 图表工具函数
└── ...
```

## 🎯 核心模块说明

### 1. Components（组件）

可复用的UI组件，遵循单一职责原则：

- **`kpi_cards.py`**: KPI指标卡片组件
  ```python
  from components.kpi_cards import render_kpi_cards
  metrics = [("总板块数", "90", None), ("平均涨跌幅", "2.5%", None)]
  render_kpi_cards(metrics)
  ```

- **`date_selector.py`**: 日期选择器组件
  ```python
  from components.date_selector import render_date_selector
  start_date, end_date = render_date_selector()
  ```

- **`sector_selector.py`**: 板块选择器组件
  ```python
  from components.sector_selector import render_sector_selector
  selected = render_sector_selector(df)
  ```

### 2. Config（配置）

图表和可视化相关的配置：

- **`chart_config.py`**: 
  - 颜色方案（涨跌幅颜色映射）
  - 图表尺寸配置
  - 布局配置
  - 数据采样配置

### 3. Utils（工具）

#### `data_loader.py` - 数据加载工具

所有数据加载函数都使用 `@st.cache_data` 装饰器，自动缓存5-10分钟：

```python
from utils.data_loader import load_sector_data, load_zt_pool_data

# 加载板块数据（自动缓存）
df = load_sector_data(start_date, end_date)

# 加载涨停股票数据
df = load_zt_pool_data(target_date)
```

#### `chart_utils.py` - 图表工具函数

统一的图表创建函数：

```python
from utils.chart_utils import (
    create_sector_trend_chart,      # 趋势折线图
    create_ranking_bar_chart,       # 排名柱状图
    create_distribution_histogram,  # 分布直方图
    create_heatmap,                 # 热力图
    create_scatter_chart,           # 散点图
    create_pie_chart                # 饼图
)

# 创建趋势图
fig = create_sector_trend_chart(df, sectors=['能源金属', 'IT服务'])
st.plotly_chart(fig, use_container_width=True)
```

### 4. Pages（多页面）

Streamlit会自动识别 `pages/` 目录下的 `.py` 文件作为独立页面：

- 文件名前的数字用于排序（如 `1_板块仪表盘.py`）
- 每个页面都是独立的模块
- 自动添加到侧边栏导航

## 🚀 使用示例

### 创建新页面

在 `pages/` 目录下创建新文件：

```python
# pages/3_涨停股票分析.py
import streamlit as st
from utils.data_loader import load_zt_pool_data
from utils.chart_utils import create_pie_chart
from components.date_selector import render_date_selector

st.set_page_config(page_title="涨停股票分析", page_icon="📈")

st.header("📈 涨停股票分析")

# 使用日期选择器
start_date, end_date = render_date_selector()

# 加载数据
df = load_zt_pool_data(start_date)

# 创建图表
fig = create_pie_chart(df, 'industry', title='行业分布')
st.plotly_chart(fig, use_container_width=True)
```

### 在主应用中使用组件

```python
# streamlit_app.py
import streamlit as st
from components.kpi_cards import render_kpi_cards
from utils.data_loader import load_sector_data_by_date
from utils.chart_utils import create_ranking_bar_chart

# 使用组件
metrics = [("总板块数", "90", None)]
render_kpi_cards(metrics)

# 加载数据
df = load_sector_data_by_date(date.today())

# 创建图表
fig = create_ranking_bar_chart(df, top_n=10)
st.plotly_chart(fig, use_container_width=True)
```

## 📊 图表类型

### 已实现的图表

1. **趋势折线图** - `create_sector_trend_chart()`
   - 多板块时间序列对比
   - 支持悬停提示
   - 自动添加零线

2. **排名柱状图** - `create_ranking_bar_chart()`
   - TOP/BOTTOM排名
   - 自动颜色映射
   - 横向/纵向布局

3. **分布直方图** - `create_distribution_histogram()`
   - 数据分布统计
   - 自动添加均值/中位数线

4. **热力图** - `create_heatmap()`
   - 板块 × 日期 × 涨跌幅
   - 颜色映射

5. **散点图** - `create_scatter_chart()`
   - 涨跌幅 vs 成交量
   - 气泡大小表示成交额

6. **饼图** - `create_pie_chart()`
   - 行业分布
   - 连板数分布等

## ⚡ 性能优化

### 数据缓存

所有数据加载函数都使用 `@st.cache_data`：

```python
@st.cache_data(ttl=300)  # 缓存5分钟
def load_sector_data(...):
    # 数据加载逻辑
    pass
```

### 数据采样

对于大量数据，可以自动采样：

```python
from config.chart_config import SAMPLING_CONFIG

if len(df) > SAMPLING_CONFIG['max_points']:
    df = df.sample(n=SAMPLING_CONFIG['max_points'])
```

## 🎨 自定义配置

修改 `config/chart_config.py` 来自定义：

- 颜色方案
- 图表尺寸
- 布局样式
- 数据采样参数

## 📝 最佳实践

1. **组件复用**: 使用 `components/` 中的组件，避免重复代码
2. **数据缓存**: 使用 `utils/data_loader.py` 中的函数，自动缓存
3. **图表统一**: 使用 `utils/chart_utils.py` 中的函数，保持样式一致
4. **配置集中**: 图表配置统一在 `config/chart_config.py`
5. **页面分离**: 复杂功能使用 `pages/` 目录创建独立页面

## 🔄 迁移现有代码

如果要将现有的 `streamlit_app.py` 迁移到新结构：

1. 提取组件到 `components/`
2. 提取图表函数到 `utils/chart_utils.py`
3. 提取数据加载到 `utils/data_loader.py`
4. 将不同功能模块拆分到 `pages/` 目录

## 📚 相关文档

- **完整方案设计**: `docs/CHART_DASHBOARD_DESIGN.md`
- **实现示例代码**: `docs/CHART_IMPLEMENTATION_EXAMPLES.md`
- **快速开始指南**: `docs/CHART_DASHBOARD_QUICK_START.md`

