# 图表实现示例代码

## 一、核心组件示例

### 1.1 KPI指标卡片组件

```python
# components/kpi_cards.py
import streamlit as st

def render_kpi_cards(metrics: list):
    """
    渲染KPI指标卡片
    
    Args:
        metrics: [(label, value, delta), ...] 格式的指标列表
    """
    cols = st.columns(len(metrics))
    for i, metric in enumerate(metrics):
        with cols[i]:
            if len(metric) == 3:
                label, value, delta = metric
                st.metric(label, value, delta)
            else:
                label, value = metric
                st.metric(label, value)
```

### 1.2 日期选择器组件

```python
# components/date_selector.py
import streamlit as st
from datetime import date, timedelta
from utils.time_utils import get_utc8_date

def render_date_selector():
    """渲染日期选择器"""
    col1, col2 = st.columns(2)
    
    with col1:
        date_type = st.radio(
            "选择方式",
            ["单日", "日期范围"],
            horizontal=True
        )
    
    if date_type == "单日":
        today = get_utc8_date()
        selected_date = st.date_input(
            "选择日期",
            value=today,
            max_value=today
        )
        return selected_date, selected_date
    else:
        with col2:
            today = get_utc8_date()
            date_range = st.date_input(
                "选择日期范围",
                value=(today - timedelta(days=7), today),
                max_value=today
            )
            if len(date_range) == 2:
                return date_range[0], date_range[1]
            return today - timedelta(days=7), today
```

### 1.3 板块选择器组件

```python
# components/sector_selector.py
import streamlit as st
import pandas as pd

def render_sector_selector(df: pd.DataFrame, default_selected: list = None):
    """
    渲染板块选择器
    
    Args:
        df: 包含板块数据的DataFrame
        default_selected: 默认选中的板块列表
    """
    if df.empty or 'name' not in df.columns:
        return []
    
    all_sectors = sorted(df['name'].unique().tolist())
    
    col1, col2 = st.columns([3, 1])
    with col1:
        selected = st.multiselect(
            "选择板块（可多选）",
            options=all_sectors,
            default=default_selected or all_sectors[:10]  # 默认选择前10个
        )
    with col2:
        if st.button("全选"):
            selected = all_sectors
        if st.button("清空"):
            selected = []
    
    return selected
```

## 二、图表工具函数

### 2.1 板块趋势折线图

```python
# utils/chart_utils.py
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_sector_trend_chart(
    df: pd.DataFrame,
    sectors: list,
    date_col: str = 'date',
    value_col: str = 'changePercent',
    title: str = '板块涨跌幅趋势'
):
    """
    创建板块趋势折线图
    
    Args:
        df: 数据DataFrame
        sectors: 要显示的板块列表
        date_col: 日期列名
        value_col: 数值列名
        title: 图表标题
    """
    if df.empty:
        return go.Figure()
    
    # 筛选选中的板块
    filtered_df = df[df['name'].isin(sectors)].copy()
    
    if filtered_df.empty:
        return go.Figure()
    
    # 确保日期是datetime类型
    if not pd.api.types.is_datetime64_any_dtype(filtered_df[date_col]):
        filtered_df[date_col] = pd.to_datetime(filtered_df[date_col])
    
    fig = px.line(
        filtered_df,
        x=date_col,
        y=value_col,
        color='name',
        title=title,
        labels={
            date_col: '日期',
            value_col: '涨跌幅(%)',
            'name': '板块'
        },
        markers=True
    )
    
    # 添加零线
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    # 更新布局
    fig.update_layout(
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=500,
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray'
        )
    )
    
    return fig
```

### 2.2 涨跌幅排名柱状图

```python
def create_ranking_bar_chart(
    df: pd.DataFrame,
    value_col: str = 'changePercent',
    name_col: str = 'name',
    top_n: int = 10,
    ascending: bool = False,
    title: str = None
):
    """
    创建排名柱状图
    
    Args:
        df: 数据DataFrame
        value_col: 排序的数值列
        name_col: 名称列
        top_n: 显示前N名
        ascending: 是否升序
        title: 图表标题
    """
    if df.empty:
        return go.Figure()
    
    # 排序并取前N名
    sorted_df = df.nlargest(top_n, value_col) if not ascending else df.nsmallest(top_n, value_col)
    
    # 确定颜色方案
    if value_col == 'changePercent':
        color_scale = 'RdYlGn' if not ascending else 'RdYlGn_r'
    else:
        color_scale = 'Blues'
    
    fig = px.bar(
        sorted_df,
        x=value_col,
        y=name_col,
        orientation='h',
        title=title or f'{value_col}排名 TOP {top_n}',
        labels={
            value_col: value_col,
            name_col: '板块'
        },
        color=value_col,
        color_continuous_scale=color_scale
    )
    
    fig.update_layout(
        height=400,
        yaxis={'categoryorder': 'total ascending' if ascending else 'total descending'}
    )
    
    return fig
```

### 2.3 涨跌幅分布直方图

```python
def create_distribution_histogram(
    df: pd.DataFrame,
    value_col: str = 'changePercent',
    title: str = '涨跌幅分布',
    bins: int = 30
):
    """创建分布直方图"""
    if df.empty or value_col not in df.columns:
        return go.Figure()
    
    fig = px.histogram(
        df,
        x=value_col,
        nbins=bins,
        title=title,
        labels={
            value_col: '涨跌幅(%)',
            'count': '板块数量'
        },
        color_discrete_sequence=['#1f77b4']
    )
    
    # 添加统计线
    mean_val = df[value_col].mean()
    median_val = df[value_col].median()
    
    fig.add_vline(
        x=mean_val,
        line_dash="dash",
        line_color="red",
        annotation_text=f"均值: {mean_val:.2f}%"
    )
    fig.add_vline(
        x=median_val,
        line_dash="dash",
        line_color="green",
        annotation_text=f"中位数: {median_val:.2f}%"
    )
    
    fig.update_layout(height=400)
    return fig
```

### 2.4 热力图

```python
def create_heatmap(
    df: pd.DataFrame,
    x_col: str = 'date',
    y_col: str = 'name',
    value_col: str = 'changePercent',
    title: str = '板块涨跌幅热力图'
):
    """创建热力图"""
    if df.empty:
        return go.Figure()
    
    # 透视表
    pivot_df = df.pivot_table(
        index=y_col,
        columns=x_col,
        values=value_col,
        aggfunc='mean'
    )
    
    fig = px.imshow(
        pivot_df,
        title=title,
        labels=dict(x='日期', y='板块', color='涨跌幅(%)'),
        color_continuous_scale='RdYlGn',
        aspect='auto'
    )
    
    fig.update_layout(height=600)
    return fig
```

### 2.5 散点图（涨跌幅 vs 成交量）

```python
def create_scatter_chart(
    df: pd.DataFrame,
    x_col: str = 'totalVolume',
    y_col: str = 'changePercent',
    size_col: str = 'totalAmount',
    color_col: str = 'changePercent',
    title: str = '涨跌幅 vs 成交量'
):
    """创建散点图（气泡图）"""
    if df.empty:
        return go.Figure()
    
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        size=size_col,
        color=color_col,
        hover_data=['name'],
        title=title,
        labels={
            x_col: '总成交量(万手)',
            y_col: '涨跌幅(%)',
            size_col: '总成交额(亿元)',
            color_col: '涨跌幅(%)',
            'name': '板块'
        },
        color_continuous_scale='RdYlGn'
    )
    
    # 添加象限线
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=df[x_col].median(), line_dash="dash", line_color="gray", opacity=0.5)
    
    fig.update_layout(height=500)
    return fig
```

## 三、数据加载工具

### 3.1 带缓存的数据加载

```python
# utils/data_loader.py
import streamlit as st
import pandas as pd
from database.db import SessionLocal
from services.sector_history_service import SectorHistoryService
from datetime import date
from functools import lru_cache

@st.cache_data(ttl=300)  # 缓存5分钟
def load_sector_data(
    start_date: date,
    end_date: date,
    sector_names: list = None
) -> pd.DataFrame:
    """
    加载板块数据（带缓存）
    
    Args:
        start_date: 开始日期
        end_date: 结束日期
        sector_names: 板块名称列表（可选）
    
    Returns:
        包含板块数据的DataFrame
    """
    db = SessionLocal()
    try:
        sectors = SectorHistoryService.get_sectors_by_date_range(
            db, start_date, end_date
        )
        df = pd.DataFrame(sectors)
        
        if sector_names and not df.empty:
            df = df[df['name'].isin(sector_names)]
        
        return df
    except Exception as e:
        st.error(f"加载数据失败: {str(e)}")
        return pd.DataFrame()
    finally:
        db.close()

@st.cache_data(ttl=300)
def load_sector_data_by_date(target_date: date) -> pd.DataFrame:
    """加载指定日期的板块数据"""
    db = SessionLocal()
    try:
        sectors = SectorHistoryService.get_sectors_by_date(db, target_date)
        return pd.DataFrame(sectors)
    except Exception as e:
        st.error(f"加载数据失败: {str(e)}")
        return pd.DataFrame()
    finally:
        db.close()

@st.cache_data(ttl=600)  # 缓存10分钟
def get_available_dates() -> list:
    """获取所有有数据的日期列表"""
    db = SessionLocal()
    try:
        dates = SectorHistoryService.get_all_dates(db)
        return [d.strftime('%Y-%m-%d') for d in dates]
    except Exception as e:
        st.error(f"获取日期列表失败: {str(e)}")
        return []
    finally:
        db.close()
```

## 四、完整页面示例

### 4.1 板块信息仪表盘页面

```python
# pages/sector_dashboard.py
import streamlit as st
import pandas as pd
from datetime import date, timedelta
from utils.time_utils import get_utc8_date

# 导入组件和工具
from components.date_selector import render_date_selector
from components.sector_selector import render_sector_selector
from components.kpi_cards import render_kpi_cards
from utils.data_loader import load_sector_data, load_sector_data_by_date
from utils.chart_utils import (
    create_ranking_bar_chart,
    create_distribution_histogram,
    create_scatter_chart
)

st.header("📊 板块信息仪表盘")

# 日期选择
start_date, end_date = render_date_selector()

# 加载数据
if start_date == end_date:
    df = load_sector_data_by_date(start_date)
else:
    df = load_sector_data(start_date, end_date)

if df.empty:
    st.warning("暂无数据")
    st.stop()

# 如果是单日，显示KPI指标
if start_date == end_date:
    # 计算指标
    total_sectors = len(df)
    avg_change = df['changePercent'].mean()
    up_count = len(df[df['changePercent'] > 0])
    down_count = len(df[df['changePercent'] < 0])
    
    # 显示KPI卡片
    metrics = [
        ("总板块数", f"{total_sectors}", None),
        ("平均涨跌幅", f"{avg_change:.2f}%", None),
        ("上涨板块数", f"{up_count}", None),
        ("下跌板块数", f"{down_count}", None)
    ]
    render_kpi_cards(metrics)

# 板块选择
selected_sectors = render_sector_selector(df)

# 图表区域
st.subheader("📈 数据可视化")

# 两列布局
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 涨跌幅TOP 10")
    fig_top = create_ranking_bar_chart(
        df,
        value_col='changePercent',
        top_n=10,
        ascending=False,
        title="涨跌幅TOP 10"
    )
    st.plotly_chart(fig_top, use_container_width=True)

with col2:
    st.subheader("📉 涨跌幅BOTTOM 10")
    fig_bottom = create_ranking_bar_chart(
        df,
        value_col='changePercent',
        top_n=10,
        ascending=True,
        title="涨跌幅BOTTOM 10"
    )
    st.plotly_chart(fig_bottom, use_container_width=True)

# 涨跌幅分布
st.subheader("📊 涨跌幅分布")
fig_dist = create_distribution_histogram(df)
st.plotly_chart(fig_dist, use_container_width=True)

# 散点图
st.subheader("📊 涨跌幅 vs 成交量")
fig_scatter = create_scatter_chart(df)
st.plotly_chart(fig_scatter, use_container_width=True)

# 数据表格
st.subheader("📋 完整数据")
st.dataframe(df, use_container_width=True, height=400)
```

### 4.2 板块趋势分析页面

```python
# pages/sector_trend.py
import streamlit as st
from datetime import date, timedelta
from utils.time_utils import get_utc8_date
from components.date_selector import render_date_selector
from components.sector_selector import render_sector_selector
from utils.data_loader import load_sector_data, get_available_dates
from utils.chart_utils import create_sector_trend_chart, create_heatmap

st.header("📈 板块趋势分析")

# 日期范围选择
start_date, end_date = render_date_selector()

# 加载数据
df = load_sector_data(start_date, end_date)

if df.empty:
    st.warning("暂无数据")
    st.stop()

# 板块选择
st.subheader("选择要分析的板块")
selected_sectors = render_sector_selector(df)

if not selected_sectors:
    st.warning("请至少选择一个板块")
    st.stop()

# 趋势折线图
st.subheader("📈 板块涨跌幅趋势")
fig_trend = create_sector_trend_chart(
    df,
    sectors=selected_sectors,
    title=f"板块涨跌幅趋势 ({start_date} 至 {end_date})"
)
st.plotly_chart(fig_trend, use_container_width=True)

# 热力图
if len(selected_sectors) <= 20:  # 热力图只显示前20个板块
    st.subheader("🔥 板块涨跌幅热力图")
    fig_heatmap = create_heatmap(
        df[df['name'].isin(selected_sectors)],
        title="板块涨跌幅热力图"
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)
else:
    st.info("板块数量过多，热力图仅显示前20个板块")
```

## 五、使用说明

### 5.1 目录结构

创建以下目录结构：

```
streamlit_app.py (主应用)
components/
  ├── __init__.py
  ├── kpi_cards.py
  ├── date_selector.py
  └── sector_selector.py
utils/
  ├── __init__.py
  ├── data_loader.py
  └── chart_utils.py
pages/ (可选，用于多页面应用)
  ├── sector_dashboard.py
  └── sector_trend.py
```

### 5.2 在主应用中集成

```python
# streamlit_app.py
import streamlit as st
from pages.sector_dashboard import *
from pages.sector_trend import *

# 或者使用Streamlit的多页面功能
# 在项目根目录创建 pages/ 文件夹
# Streamlit会自动识别并添加到导航
```

## 六、性能优化建议

1. **使用缓存**: 所有数据加载函数使用 `@st.cache_data`
2. **懒加载**: 初始只加载关键图表
3. **数据采样**: 时间序列数据过长时自动采样
4. **异步加载**: 使用 `st.spinner` 显示加载状态

## 七、扩展功能

- 数据导出功能
- 图表配置保存
- 自定义主题
- 移动端适配

