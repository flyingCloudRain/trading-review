#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
板块信息页面
Streamlit会自动识别pages目录下的文件作为独立页面
文件名前的数字用于排序
"""
import streamlit as st
import pandas as pd
from datetime import date
from pathlib import Path
import sys

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入组件和工具
from components.kpi_cards import render_kpi_cards
from components.sector_selector import render_sector_selector
from utils.data_loader import load_sector_data, load_sector_data_by_date, get_available_dates
from utils.chart_utils import (
    create_ranking_bar_chart,
    create_distribution_histogram,
    create_scatter_chart,
    create_heatmap,
    create_sector_trend_chart
)
from utils.time_utils import get_utc8_date, get_data_date
from datetime import timedelta

st.set_page_config(
    page_title="板块分析",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 应用统一样式
from utils.page_styles import apply_common_styles
apply_common_styles()

# 页面标题
st.markdown('<h1 class="main-header">📊 板块分析</h1>', unsafe_allow_html=True)

# 板块类型选择
sector_type = st.radio(
    "选择板块类型",
    options=['industry', 'concept'],
    format_func=lambda x: '🏭 行业板块' if x == 'industry' else '💡 概念板块',
    horizontal=True,
    help="选择要查看的板块类型：行业板块或概念板块"
)

# 使用标签页组织功能
tab1, tab2 = st.tabs(["📊 板块信息", "📈 趋势分析"])

# ==================== 标签页1: 板块信息 ====================
with tab1:
    # 根据选择的板块类型显示标题
    sector_type_title = '行业板块' if sector_type == 'industry' else '概念板块'
    st.markdown(f'<h2 class="section-header">📊 {sector_type_title}信息</h2>', unsafe_allow_html=True)

# 日期选择器（单选）
default_date = get_data_date()  # 使用get_data_date()，如果未到下一交易日开盘时间，使用前一交易日

# 日期选择器
selected_date = st.date_input(
    "📅选择日期",
    value=default_date,
    max_value=get_utc8_date(),
    label_visibility="visible",
    help="如果未到下一交易日开盘时间，默认显示前一交易日数据。"
)

# 处理日期
if selected_date is None:
    selected_date = get_data_date()

# 加载选择日期的单日数据用于统计和排名（按板块类型过滤）
df_selected_date = load_sector_data_by_date(selected_date, sector_type)

if df_selected_date.empty:
    st.warning(f"⚠️  {selected_date} 暂无数据，请选择其他日期")
    st.stop()

# 默认使用全部板块数据
selected_sectors = df_selected_date['name'].unique().tolist()

if df_selected_date.empty:
    st.warning("暂无数据")
    st.stop()

# 计算统计指标（基于选择日期的过滤后数据）
total_sectors = len(df_selected_date)
up_count = len(df_selected_date[df_selected_date['changePercent'] > 0])
down_count = len(df_selected_date[df_selected_date['changePercent'] < 0])
flat_count = len(df_selected_date[df_selected_date['changePercent'] == 0])
up_ratio = (up_count / total_sectors * 100) if total_sectors > 0 else 0
down_ratio = (down_count / total_sectors * 100) if total_sectors > 0 else 0

# 计算资金净流入/流出板块数和金额
if 'netInflow' in df_selected_date.columns:
    inflow_df = df_selected_date[df_selected_date['netInflow'] > 0]
    outflow_df = df_selected_date[df_selected_date['netInflow'] < 0]
    inflow_count = len(inflow_df)
    outflow_count = len(outflow_df)
    inflow_amount = inflow_df['netInflow'].sum() if len(inflow_df) > 0 else 0
    outflow_amount = abs(outflow_df['netInflow'].sum()) if len(outflow_df) > 0 else 0
else:
    inflow_count = 0
    outflow_count = 0
    inflow_amount = 0
    outflow_amount = 0

# 显示统计卡片 - 优化布局和样式（4列）
sector_type_label = '行业板块' if sector_type == 'industry' else '概念板块'
st.markdown(f'<h2 class="section-header">📊 {sector_type_label}统计</h2>', unsafe_allow_html=True)
col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

with col_stat1:
    st.metric(
        "📈 上涨板块",
        f"{up_count}",
        delta=f"{up_ratio:.1f}%",
        help="上涨板块数量及占比"
    )

with col_stat2:
    st.metric(
        "📉 下跌板块",
        f"{down_count}",
        delta=f"{down_ratio:.1f}%",
        delta_color="inverse",
        help="下跌板块数量及占比"
    )

with col_stat3:
    st.metric(
        "💰 资金净流入",
        f"{inflow_amount:.2f}亿元",
        delta=f"{inflow_count}个板块",
        help="资金净流入总额及板块数"
    )

with col_stat4:
    st.metric(
        "💸 资金净流出",
        f"{outflow_amount:.2f}亿元",
        delta=f"{outflow_count}个板块",
        delta_color="inverse",
        help="资金净流出总额及板块数"
    )

# 涨跌幅排名 - 两列布局
st.markdown('<h2 class="section-header">涨跌幅排名</h2>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    fig_top = create_ranking_bar_chart(
        df_selected_date,
        value_col='changePercent',
        top_n=10,
        ascending=False,
        title="涨幅TOP 10"
    )
    st.plotly_chart(fig_top, use_container_width=True)

with col2:
    fig_bottom = create_ranking_bar_chart(
        df_selected_date,
        value_col='changePercent',
        top_n=10,
        ascending=True,
        title="跌幅TOP 10"
    )
    st.plotly_chart(fig_bottom, use_container_width=True)

# 净资金流入/流出 - 两列布局
if 'netInflow' in df_selected_date.columns:
    st.markdown('<h2 class="section-header">资金流向分析</h2>', unsafe_allow_html=True)
    # 使用选择日期的数据
    df_netinflow = df_selected_date[['name', 'netInflow']].copy() if 'name' in df_selected_date.columns else df_selected_date.copy()
    
    col3, col4 = st.columns(2)
    
    with col3:
          # 筛选净流入为正的板块，按净流入降序排列
        inflow_df = df_netinflow[df_netinflow['netInflow'] > 0].copy()
        if not inflow_df.empty:
            fig_inflow = create_ranking_bar_chart(
                inflow_df,
                value_col='netInflow',
                top_n=10,
                ascending=False,
                title="净资金流入TOP 10"
            )
            st.plotly_chart(fig_inflow, use_container_width=True)
        else:
            st.info("暂无净资金流入数据")
    
    with col4:
        # 筛选净流入为负的板块，按净流入升序排列（绝对值最大的）
        outflow_df = df_netinflow[df_netinflow['netInflow'] < 0].copy()
        if not outflow_df.empty:
            fig_outflow = create_ranking_bar_chart(
                outflow_df,
                value_col='netInflow',
                top_n=10,
                ascending=True,
                title="净资金流出TOP 10"
            )
            st.plotly_chart(fig_outflow, use_container_width=True)
        else:
            st.info("暂无净资金流出数据")

# 数据分析 - 基于选择日期的数据
st.markdown('<h2 class="section-header">数据分析</h2>', unsafe_allow_html=True)

# 分布统计信息卡片 - 优化配色
col_dist1, col_dist2, col_dist3, col_dist4 = st.columns(4)

# 计算分布统计（基于选择日期的数据）
max_change = df_selected_date['changePercent'].max()
min_change = df_selected_date['changePercent'].min()
std_change = df_selected_date['changePercent'].std()
median_change = df_selected_date['changePercent'].median()
mean_change = df_selected_date['changePercent'].mean()

with col_dist1:
    st.metric(
        "📈 最大值",
        f"{max_change:+.2f}%",
        help="涨跌幅最大值"
    )

with col_dist2:
    st.metric(
        "📉 最小值",
        f"{min_change:+.2f}%",
        help="涨跌幅最小值"
    )

with col_dist3:
    st.metric(
        "📊 标准差",
        f"{std_change:.2f}%",
        help="涨跌幅标准差"
    )

with col_dist4:
    st.metric(
        "📐 中位数",
        f"{median_change:+.2f}%",
        help="涨跌幅中位数"
    )

# 涨跌幅分布图表 - 添加说明提示
st.markdown("""
    <div style="padding: 0.5rem 0; margin-bottom: 1rem; font-size: 0.85rem; color: #6b7280; line-height: 1.5;">
        💡 图表展示了板块涨跌幅的分布情况。红色虚线表示均值，绿色虚线表示中位数，紫色区域表示均值±1标准差区间。
    </div>
""", unsafe_allow_html=True)

st.markdown('<h2 class="section-header">涨跌幅分布</h2>', unsafe_allow_html=True)
fig_dist = create_distribution_histogram(df_selected_date)
st.plotly_chart(fig_dist, use_container_width=True)

# 当日热力图 - 树状图（Treemap）模式，方块大小表示成交量
st.markdown("---")
st.markdown('<h2 class="section-header">板块涨跌幅热力图</h2>', unsafe_allow_html=True)

# 检查必要字段
if 'changePercent' in df_selected_date.columns and 'name' in df_selected_date.columns and len(df_selected_date) > 0:
    # 使用全部板块数据
    df_heatmap = df_selected_date.copy()
    
    # 准备数据
    import plotly.graph_objects as go
    import plotly.express as px
    import numpy as np
    
    # 检查是否有成交量字段
    volume_col = None
    if 'totalVolume' in df_heatmap.columns:
        volume_col = 'totalVolume'
    elif 'volume' in df_heatmap.columns:
        volume_col = 'volume'
    
    # 如果有成交量字段，使用成交量作为方块大小；否则使用涨跌幅绝对值
    if volume_col:
        # 确保成交量值有效，处理缺失值和0值
        df_heatmap['volume_value'] = df_heatmap[volume_col].fillna(0)
        # 确保最小值为0.01，避免方块太小
        df_heatmap['volume_value'] = df_heatmap['volume_value'].clip(lower=0.01)
    else:
        # 如果没有成交量字段，回退到使用涨跌幅绝对值
        df_heatmap['volume_value'] = df_heatmap['changePercent'].abs()
        if df_heatmap['volume_value'].sum() == 0:
            df_heatmap['volume_value'] = 1.0
        else:
            df_heatmap['volume_value'] = df_heatmap['volume_value'].clip(lower=0.1)
    
    # 创建颜色映射函数 - 根据涨跌方向设置颜色
    def get_color_category(value):
        """根据涨跌幅返回颜色类别"""
        if value > 0:
            return '上涨'
        elif value < 0:
            return '下跌'
        else:
            return '平盘'
    
    df_heatmap['color_category'] = df_heatmap['changePercent'].apply(get_color_category)
    
    # 创建自定义配色方案 - 优化涨跌颜色对比
    # 上涨：红色系（从浅红到深红）
    # 下跌：绿色系（从浅绿到深绿，使用柔和不刺眼的绿色）
    # 0值：中性灰色
    custom_colorscale = [
        [0.0, '#047857'],      # 深绿色 - 最大跌幅
        [0.2, '#059669'],     # 中深绿色
        [0.4, '#34d399'],     # 中绿色
        [0.5, '#9ca3af'],     # 灰色 - 0值附近
        [0.6, '#fca5a5'],     # 浅红色
        [0.8, '#f87171'],     # 中红色
        [1.0, '#ef4444']      # 深红色 - 最大涨幅
    ]
    
    # 格式化涨跌幅数据，确保精度正确
    df_heatmap['changePercent_formatted'] = df_heatmap['changePercent'].round(2)
    
    # 准备悬停数据 - 使用格式化后的数据
    hover_data_dict = {'changePercent_formatted': ':.2f'}
    if volume_col:
        hover_data_dict[volume_col] = ':.2f'
    
    # 创建树状图
    fig_heatmap = px.treemap(
        df_heatmap,
        path=['name'],  # 板块名称作为路径
        values='volume_value',  # 方块大小基于成交量
        color='changePercent',  # 颜色基于涨跌幅值
        color_continuous_scale=custom_colorscale,  # 自定义配色方案
        color_continuous_midpoint=0,  # 0值为中间点，确保颜色对称
        hover_data=hover_data_dict,  # 悬停时显示涨跌幅和成交量
        labels={'name': '板块', 'volume_value': '成交量(万手)' if volume_col else '涨跌幅绝对值(%)', 'changePercent': '涨跌幅(%)'},
        title=f"板块涨跌幅热力图 ({selected_date})"
    )
    
    # 优化样式 - 使用customdata显示涨跌幅，避免显示RGB值
    # 构建悬停模板
    if volume_col:
        hover_template = '<b>%{label}</b><br>涨跌幅: %{customdata[0]:+.2f}%<br>成交量: %{value:.2f}万手<extra></extra>'
    else:
        hover_template = '<b>%{label}</b><br>涨跌幅: %{customdata[0]:+.2f}%<br>绝对值: %{value:.2f}%<extra></extra>'
    
    # 获取格式化后的涨跌幅值用于显示，确保格式正确
    change_percent_values = df_heatmap['changePercent_formatted'].values
    # 将值转换为numpy数组并重塑为正确的形状
    import numpy as np
    customdata_array = np.array(change_percent_values).reshape(-1, 1)
    
    fig_heatmap.update_traces(
        textinfo='label+text',  # 显示标签和文本
        texttemplate='<b>%{label}</b><br>%{customdata[0]:+.2f}%',  # 使用customdata显示涨跌幅，避免显示RGB值
        hovertemplate=hover_template,
        customdata=customdata_array,  # 显式设置customdata，确保使用格式化后的值
        marker=dict(
            line=dict(width=2, color='white'),  # 白色边框
            cornerradius=4  # 圆角
        ),
        textfont=dict(size=13, color='white', family='Arial, sans-serif')  # 增大方块内文字
    )
    
    # 优化布局 - 增大整体尺寸
    num_sectors = len(df_heatmap)
    # 根据板块数量动态调整高度，最小800px，最大1200px
    dynamic_height = max(800, min(1200, num_sectors * 15))
    
    fig_heatmap.update_layout(
        height=dynamic_height,  # 动态高度，增大整体尺寸
        plot_bgcolor='rgba(0,0,0,0)',  # 透明背景
        paper_bgcolor='rgba(0,0,0,0)',  # 透明背景
        font=dict(size=13, family='Arial, sans-serif'),  # 增大字体
        title=dict(
            font=dict(size=22, color='#2c3e50', family='Arial, sans-serif'),  # 增大标题字体
            x=0.5,
            xanchor='center',
            pad=dict(b=30)
        ),
        coloraxis=dict(
            colorbar=dict(
                title=dict(text='涨跌幅(%)', font=dict(size=13, color='#2c3e50')),  # 增大颜色条标题
                tickfont=dict(size=12, color='#6b7280'),  # 增大刻度字体
                thickness=25,  # 增大颜色条厚度
                len=0.7,  # 增大颜色条长度
                bgcolor='rgba(0,0,0,0)',  # 透明背景
                bordercolor='rgba(0,0,0,0)',  # 透明边框
                outlinecolor='rgba(0,0,0,0)'  # 透明轮廓
            )
        ),
        margin=dict(l=15, r=130, t=90, b=15)  # 增大边距
    )
    
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # 添加图例说明 - 明确说明上涨幅度
    volume_desc = "成交量（万手）" if volume_col else "涨跌幅绝对值"
    st.markdown(f"""
        <div style="padding: 0.8rem 0; font-size: 0.9rem; color: #6b7280; line-height: 1.8;">
            <strong>💡 图例说明：</strong><br>
            • <strong>方块大小：</strong>表示{volume_desc}，方块越大表示{volume_desc}越大<br>
            • <strong>颜色表示：</strong><span style="color: #ef4444; font-weight: 600;">红色</span>表示上涨，<span style="color: #047857; font-weight: 600;">绿色</span>表示下跌<br>
            • <strong>上涨幅度：</strong>颜色越深（从浅红到深红）表示上涨幅度越大，深红色表示最大涨幅<br>
            • <strong>下跌幅度：</strong>颜色越深（从浅绿到深绿）表示下跌幅度越大，深绿色表示最大跌幅
        </div>
    """, unsafe_allow_html=True)
else:
    st.info("暂无涨跌幅数据生成热力图")

# 散点图 - 基于选择日期的数据
if 'totalVolume' in df_selected_date.columns and 'totalAmount' in df_selected_date.columns:
    st.markdown('<h2 class="section-header">涨跌幅 vs 成交量</h2>', unsafe_allow_html=True)
    fig_scatter = create_scatter_chart(df_selected_date)
    st.plotly_chart(fig_scatter, use_container_width=True)

# 数据表格 - 显示选择日期的全部数据
st.markdown('<h2 class="section-header">📋 完整数据</h2>', unsafe_allow_html=True)

# 板块类型筛选（在完整数据部分）
col_filter1, col_filter2 = st.columns([1, 3])
with col_filter1:
    filter_sector_type = st.selectbox(
        "筛选板块类型",
        options=['all', 'industry', 'concept'],
        format_func=lambda x: {
            'all': '全部',
            'industry': '🏭 行业板块',
            'concept': '💡 概念板块'
        }.get(x, x),
        help="选择要显示的板块类型",
        key="filter_sector_type_full_data"
    )

with col_filter2:
    # 添加搜索框 - 根据板块名称查询
    search_name = st.text_input(
        "🔍 搜索板块名称",
        value="",
        help="输入板块名称进行搜索，支持模糊匹配",
        key="sector_search"
    )

# 根据筛选条件加载数据
if filter_sector_type == 'all':
    # 加载所有板块类型的数据
    df_industry = load_sector_data_by_date(selected_date, 'industry')
    df_concept = load_sector_data_by_date(selected_date, 'concept')
    
    # 合并数据并添加板块类型标识
    if not df_industry.empty:
        df_industry['sectorType'] = '行业板块'
    if not df_concept.empty:
        df_concept['sectorType'] = '概念板块'
    
    # 合并数据
    if not df_industry.empty and not df_concept.empty:
        df_all_data = pd.concat([df_industry, df_concept], ignore_index=True)
    elif not df_industry.empty:
        df_all_data = df_industry
    elif not df_concept.empty:
        df_all_data = df_concept
    else:
        df_all_data = pd.DataFrame()
else:
    # 加载指定板块类型的数据
    df_all_data = load_sector_data_by_date(selected_date, filter_sector_type)
    if not df_all_data.empty:
        df_all_data['sectorType'] = '行业板块' if filter_sector_type == 'industry' else '概念板块'

# 准备显示的数据
df_display = df_all_data.copy()

# 根据搜索关键词过滤数据
if search_name and search_name.strip():
    search_keyword = search_name.strip()
    # 模糊匹配板块名称
    if 'name' in df_display.columns:
        df_display = df_display[df_display['name'].str.contains(search_keyword, case=False, na=False)].copy()
    
    if df_display.empty:
        st.info(f"未找到包含「{search_keyword}」的板块")
        st.stop()

# 移除不需要显示的列（id, index, createdAt）
columns_to_drop = []
if 'id' in df_display.columns:
    columns_to_drop.append('id')
if 'index' in df_display.columns:
    columns_to_drop.append('index')
if 'createdAt' in df_display.columns:
    columns_to_drop.append('createdAt')
if columns_to_drop:
    df_display = df_display.drop(columns=columns_to_drop)

# 列名映射：英文转中文
column_mapping = {
    'date': '日期',
    'sectorType': '板块类型',
    'name': '板块名称',
    'changePercent': '涨跌幅(%)',
    'totalVolume': '总成交量(万手)',
    'totalAmount': '总成交额(亿元)',
    'netInflow': '净流入(亿元)',
    'upCount': '上涨家数',
    'downCount': '下跌家数',
    'avgPrice': '均价',
    'leadingStock': '领涨股',
    'leadingStockPrice': '领涨股-最新价',
    'leadingStockChangePercent': '领涨股-涨跌幅(%)'
}
# 重命名列（只重命名存在的列）
df_display = df_display.rename(columns={k: v for k, v in column_mapping.items() if k in df_display.columns})

# 调整列顺序：如果有板块类型列，将其放在最前面（在日期之后）
if '板块类型' in df_display.columns:
    cols = []
    if '日期' in df_display.columns:
        cols.append('日期')
    cols.append('板块类型')
    # 添加其他列（排除已添加的列）
    for col in df_display.columns:
        if col not in cols:
            cols.append(col)
    df_display = df_display[cols]

# 显示前20条记录
df_display = df_display.head(20)
st.dataframe(df_display, use_container_width=True, height=400)

# ==================== 标签页2: 趋势分析 ====================
with tab2:
    # 根据选择的板块类型显示标题
    sector_type_title = '行业板块' if sector_type == 'industry' else '概念板块'
    st.markdown(f'<h2 class="section-header">📈 {sector_type_title}趋势分析</h2>', unsafe_allow_html=True)
    
    # 日期范围选择
    today = get_utc8_date()
    date_range = st.date_input(
        "选择日期范围",
        value=(today - timedelta(days=14), today),
        max_value=today,
        help="选择要查看的日期范围，支持单日或日期区间",
        key="trend_date_range"
    )
    
    # 处理日期范围
    if len(date_range) == 2:
        start_date, end_date = date_range[0], date_range[1]
    else:
        # 如果只选择了一个日期，使用该日期作为开始和结束
        start_date = end_date = date_range if isinstance(date_range, date) else today
    
    # 加载数据（按板块类型过滤）
    df_trend = load_sector_data(start_date, end_date, sector_type=sector_type)
    
    if df_trend.empty:
        st.warning("暂无数据，请选择其他日期范围")
    else:
        # 板块选择
        st.subheader("选择要分析的板块")
        selected_sectors = render_sector_selector(df_trend, max_display=15)
        
        if not selected_sectors:
            st.warning("请至少选择一个板块")
        else:
            # 趋势折线图 - 换行显示
            st.markdown("#### 📈 板块涨跌幅趋势")
            fig_trend = create_sector_trend_chart(
                df_trend,
                sectors=selected_sectors,
                value_col='changePercent',
                title=f"板块涨跌幅趋势 ({start_date} 至 {end_date})"
            )
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # 添加说明文字（无背景色）
            st.markdown("""
                <div style="padding: 0.5rem 0; margin-top: 0.5rem; font-size: 0.85rem; color: #6b7280; line-height: 1.5; background-color: transparent; border: none;">
                    💡 图表展示了选中板块在选定日期范围内的涨跌幅变化趋势。可以通过图例点击隐藏/显示特定板块，虚线为零线。
                </div>
            """, unsafe_allow_html=True)
            
            # 资金净流入趋势 - 换行显示
            if 'netInflow' in df_trend.columns or 'net_inflow' in df_trend.columns:
                st.markdown("#### 💰 资金净流入趋势")
                net_inflow_col = 'netInflow' if 'netInflow' in df_trend.columns else 'net_inflow'
                fig_inflow = create_sector_trend_chart(
                    df_trend,
                    sectors=selected_sectors,
                    value_col=net_inflow_col,
                    title=f"资金净流入趋势 ({start_date} 至 {end_date})"
                )
                st.plotly_chart(fig_inflow, use_container_width=True)
                
                # 添加说明文字（无背景色）
                st.markdown("""
                    <div style="padding: 0.5rem 0; margin-top: 0.5rem; font-size: 0.85rem; color: #6b7280; line-height: 1.5; background-color: transparent; border: none;">
                        💡 图表展示了选中板块在选定日期范围内的资金净流入变化趋势。可以通过图例点击隐藏/显示特定板块，虚线为零线。
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.info("暂无资金净流入数据")
            
            # 热力图
            if len(selected_sectors) <= 20:  # 热力图只显示前20个板块
                st.markdown("---")
                st.markdown('<h2 class="section-header">🔥 板块涨跌幅热力图</h2>', unsafe_allow_html=True)
                
                # 准备热力图数据
                df_heatmap_data = df_trend[df_trend['name'].isin(selected_sectors)].copy()
                
                # 检查数据是否为空
                if df_heatmap_data.empty:
                    st.warning("⚠️ 选中的板块在当前日期范围内没有数据")
                else:
                    # 检查必要的列是否存在
                    required_cols = ['date', 'name', 'changePercent']
                    missing_cols = [col for col in required_cols if col not in df_heatmap_data.columns]
                    
                    if missing_cols:
                        st.error(f"❌ 数据缺少必要的列: {', '.join(missing_cols)}")
                    else:
                        fig_heatmap = create_heatmap(
                            df_heatmap_data,
                            title="板块涨跌幅热力图"
                        )
                        
                        # 检查图表是否为空
                        if fig_heatmap.data:
                            st.plotly_chart(fig_heatmap, use_container_width=True)
                        else:
                            st.warning("⚠️ 热力图数据为空，可能是日期范围内数据不足或数据格式问题")
            else:
                st.info("板块数量过多，热力图仅显示前20个板块")

