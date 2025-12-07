#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
板块趋势分析页面
"""
import streamlit as st
from datetime import date, timedelta
from pathlib import Path
import sys

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.time_utils import get_utc8_date
from components.sector_selector import render_sector_selector
from utils.data_loader import load_sector_data, get_available_dates
from utils.chart_utils import create_sector_trend_chart, create_heatmap

st.set_page_config(
    page_title="板块趋势分析",
    page_icon="📈",
    layout="wide"
)

# 统一标题样式
st.markdown("""
    <style>
    /* 统一主标题样式 */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #1f77b4;
    }
    /* 统一二级标题样式 - 无背景色 */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e0e0e0;
        background: transparent;
    }
    </style>
""", unsafe_allow_html=True)

# 板块类型选择
sector_type = st.radio(
    "选择板块类型",
    options=['industry', 'concept'],
    format_func=lambda x: '🏭 行业板块' if x == 'industry' else '💡 概念板块',
    horizontal=True,
    help="选择要查看的板块类型：行业板块或概念板块"
)

# 根据选择的板块类型显示标题
sector_type_title = '行业板块' if sector_type == 'industry' else '概念板块'
st.markdown(f'<h1 class="main-header">📈 {sector_type_title}趋势分析</h1>', unsafe_allow_html=True)

# 日期范围选择
today = get_utc8_date()
date_range = st.date_input(
    "选择日期范围",
    value=(today - timedelta(days=14), today),
    max_value=today,
    help="选择要查看的日期范围，支持单日或日期区间"
)

# 处理日期范围
if len(date_range) == 2:
    start_date, end_date = date_range[0], date_range[1]
else:
    # 如果只选择了一个日期，使用该日期作为开始和结束
    start_date = end_date = date_range if isinstance(date_range, date) else today

# 加载数据（按板块类型过滤）
df = load_sector_data(start_date, end_date, sector_type=sector_type)

if df.empty:
    st.warning("暂无数据，请选择其他日期范围")
    st.stop()

# 板块选择
st.subheader("选择要分析的板块")
selected_sectors = render_sector_selector(df, max_display=15)

if not selected_sectors:
    st.warning("请至少选择一个板块")
    st.stop()

# 趋势折线图 - 换行显示
st.markdown("#### 📈 板块涨跌幅趋势")
fig_trend = create_sector_trend_chart(
    df,
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
if 'netInflow' in df.columns or 'net_inflow' in df.columns:
    st.markdown("#### 💰 资金净流入趋势")
    net_inflow_col = 'netInflow' if 'netInflow' in df.columns else 'net_inflow'
    fig_inflow = create_sector_trend_chart(
        df,
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
    df_heatmap_data = df[df['name'].isin(selected_sectors)].copy()
    
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

