#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跌停股票池查询页面
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
from pathlib import Path
import sys

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.db import SessionLocal
from services.dtgc_pool_history_service import DtgcPoolHistoryService
from utils.time_utils import get_utc8_date, get_data_date

st.set_page_config(
    page_title="跌停股票池",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 页面标题样式
st.markdown("""
    <style>
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

# 页面标题
st.markdown('<h1 class="main-header">📉 跌停股票池</h1>', unsafe_allow_html=True)

# 日期选择 - 如果未到下一交易日开盘时间，默认为前一交易日
default_date = get_data_date()
date_range = st.date_input(
    "📅 选择日期",
    value=default_date,
    max_value=get_utc8_date(),
    help="可以选择单日或日期范围查询（选择两个日期即为范围）。如果未到下一交易日开盘时间，默认显示前一交易日数据。"
)

# 解析日期范围
# 如果用户选择了两个日期（范围），date_range 会是元组
# 如果只选择了一个日期，date_range 会是单个 date 对象
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    if start_date is None:
        start_date = end_date
    if end_date is None:
        end_date = start_date
elif isinstance(date_range, date):
    # 单日选择
    start_date = end_date = date_range
else:
    # 默认使用数据日期（如果未到下一交易日开盘时间，使用前一交易日）
    start_date = end_date = get_data_date()

try:
    db = SessionLocal()
    
    # 加载数据
    if start_date == end_date:
        stocks = DtgcPoolHistoryService.get_dtgc_pool_by_date(db, start_date)
    else:
        stocks = DtgcPoolHistoryService.get_dtgc_pool_by_date_range(db, start_date, end_date)
    
    if stocks:
        df = pd.DataFrame(stocks)
    else:
        df = pd.DataFrame()
    
    db.close()
    
    # 显示数据
    if df.empty:
        if start_date == end_date:
            st.warning(f"⚠️ {start_date} 暂无跌停股票数据")
            
            # 检查是否为交易日
            from tasks.sector_scheduler import SectorScheduler
            scheduler = SectorScheduler()
            is_trading = scheduler._is_trading_day(start_date)
            
            if is_trading:
                st.info("💡 提示：跌停股票数据会在交易日15:10自动保存到数据库。如果数据应该存在但显示为空，可以：\n1. 前往「定时任务管理」页面手动执行任务\n2. 点击「🔄 清除缓存」按钮清除缓存后重试")
            else:
                st.info("💡 提示：该日期不是交易日，无法获取跌停股票数据。请选择其他交易日查看数据。")
            
            # 提供操作按钮
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 清除缓存", use_container_width=True, key="clear_cache_dt"):
                    st.success("✅ 缓存已清除，请刷新页面")
                    st.rerun()
            with col2:
                st.markdown("""
                <a href="/定时任务管理" target="_self">
                    <button style="width: 100%; padding: 0.5rem; background-color: #1f77b4; color: white; border: none; border-radius: 0.25rem; cursor: pointer;">
                        ⏰ 前往定时任务管理
                    </button>
                </a>
                """, unsafe_allow_html=True)
        else:
            st.warning(f"⚠️ {start_date} 至 {end_date} 暂无跌停股票数据")
            st.info("💡 提示：请选择其他日期范围查看数据，或前往「定时任务管理」页面手动执行任务获取数据")
    else:
        # 统计信息卡片
        st.markdown('<h2 class="section-header">📉 跌停股票池 - 统计信息</h2>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("股票数量", len(df))
        
        with col2:
            if 'changePercent' in df.columns:
                avg_change = df['changePercent'].mean()
                st.metric("平均涨跌幅", f"{avg_change:.2f}%")
        
        with col3:
            if 'turnover' in df.columns:
                total_turnover = df['turnover'].sum()
                st.metric("总成交额", f"{total_turnover:.2f}亿元")
        
        with col4:
            if 'date' in df.columns:
                unique_dates = df['date'].nunique()
                st.metric("日期数量", unique_dates)
            else:
                st.metric("数据日期", start_date.strftime('%Y-%m-%d'))
        
        # 最近2周每日跌停股票总数趋势
        st.markdown("#### 📈 最近2周每日跌停股票总数趋势")
        try:
            # 获取最近2周的数据
            trend_end_date = get_utc8_date()
            trend_start_date = trend_end_date - timedelta(days=13)  # 14天（包含今天）
            
            db_trend = SessionLocal()
            try:
                trend_stocks = DtgcPoolHistoryService.get_dtgc_pool_by_date_range(db_trend, trend_start_date, trend_end_date)
                db_trend.close()
                
                if trend_stocks:
                    trend_df = pd.DataFrame(trend_stocks)
                    
                    if 'date' in trend_df.columns and len(trend_df) > 0:
                        # 按日期统计每日跌停股票总数
                        daily_count = trend_df.groupby('date').size().reset_index(name='跌停股票数')
                        daily_count['date'] = pd.to_datetime(daily_count['date'])
                        
                        # 过滤非交易日
                        from utils.time_utils import filter_trading_days
                        daily_count = filter_trading_days(daily_count, date_column='date')
                        
                        if daily_count.empty:
                            st.info("暂无交易日数据")
                        else:
                            daily_count = daily_count.sort_values('date')
                            
                            # 创建折线图 - 使用统一配置
                            from chart_config.chart_config import LINE_CHART_CONFIG, LINE_CHART_COLORS
                            
                            fig_trend = go.Figure()
                            
                            # 主折线
                            fig_trend.add_trace(go.Scatter(
                                x=daily_count['date'],
                                y=daily_count['跌停股票数'],
                                mode='lines+markers',
                                name='跌停股票数',
                                line=dict(
                                    color=LINE_CHART_COLORS['danger'],
                                    width=LINE_CHART_CONFIG['line_width'],
                                    shape='spline'  # 平滑曲线
                                ),
                                marker=dict(
                                    color=LINE_CHART_COLORS['danger'],
                                    size=LINE_CHART_CONFIG['marker_size'],
                                    line=dict(
                                        width=LINE_CHART_CONFIG['marker_line_width'],
                                        color=LINE_CHART_CONFIG['marker_line_color']
                                    )
                                ),
                                fill='tozeroy',  # 填充到零线
                                fillcolor=f"rgba(239, 68, 68, {LINE_CHART_CONFIG['fill_opacity']})"  # 红色填充
                            ))
                            
                            # 添加平均值线
                            avg_count = daily_count['跌停股票数'].mean()
                            fig_trend.add_hline(
                                y=avg_count,
                                line_dash="dash",
                                line_color="#64748b",
                                opacity=0.7,
                                line_width=2,
                                annotation_text=f"平均值: {avg_count:.1f}",
                                annotation_position="right",
                                annotation_font_size=12,
                                annotation_bgcolor="rgba(100, 116, 139, 0.1)"
                            )
                            
                            fig_trend.update_layout(
                                title=dict(
                                    text="最近2周每日跌停股票总数趋势",
                                    font=dict(size=LINE_CHART_CONFIG['title_font_size']),
                                    x=0.5,
                                    xanchor='center'
                                ),
                                xaxis=dict(
                                    title=dict(text="日期", font=dict(size=LINE_CHART_CONFIG['axis_title_font_size'])),
                                    tickformat='%Y-%m-%d',
                                    dtick='D1',
                                    gridcolor=LINE_CHART_CONFIG['grid_color'],
                                    gridwidth=LINE_CHART_CONFIG['grid_width'],
                                    showgrid=True
                                ),
                                yaxis=dict(
                                    title=dict(text="跌停股票数", font=dict(size=LINE_CHART_CONFIG['axis_title_font_size'])),
                                    gridcolor=LINE_CHART_CONFIG['grid_color'],
                                    gridwidth=LINE_CHART_CONFIG['grid_width'],
                                    showgrid=True
                                ),
                                height=LINE_CHART_CONFIG['height'],
                                hovermode='x unified',
                                showlegend=True,
                                plot_bgcolor='rgba(0,0,0,0)',  # 透明背景，跟随系统主题
                                paper_bgcolor='rgba(0,0,0,0)',  # 透明背景，跟随系统主题
                                font=dict(
                                    family=LINE_CHART_CONFIG['font_family'],
                                    size=LINE_CHART_CONFIG['font_size']
                                )
                            )
                            
                            st.plotly_chart(fig_trend, use_container_width=True)
                    else:
                        st.info("暂无趋势数据")
                else:
                    st.info("暂无趋势数据")
            except Exception as e:
                if 'db_trend' in locals():
                    db_trend.close()
                st.warning(f"获取趋势数据失败: {str(e)}")
        except Exception as e:
            st.warning(f"显示趋势图失败: {str(e)}")
        
        # 连续跌停统计
        if 'continuousLimitDown' in df.columns:
            st.markdown("#### 📉 连续跌停统计")
            col1, col2 = st.columns(2)
            
            with col1:
                # 连续跌停分布（按值从大到小排序）
                limit_down_dist = df['continuousLimitDown'].value_counts().sort_values(ascending=False)
                fig_limit = px.bar(
                    x=limit_down_dist.index,
                    y=limit_down_dist.values,
                    labels={'x': '连续跌停数', 'y': '股票数量'},
                    title="连续跌停分布",
                    color=limit_down_dist.values,
                    color_continuous_scale='Reds'  # 红色系渐变，表示跌停
                )
                fig_limit.update_xaxes(tickangle=0)
                fig_limit.update_layout(showlegend=False)
                st.plotly_chart(fig_limit, use_container_width=True)
            
            with col2:
                # 连续跌停TOP 10
                top_limit_down = df.nlargest(10, 'continuousLimitDown')[['code', 'name', 'continuousLimitDown', 'changePercent']]
                st.dataframe(top_limit_down, use_container_width=True)
        
        # 开板次数统计
        if 'openCount' in df.columns:
            st.markdown("#### 🔓 开板次数统计")
            col1, col2 = st.columns(2)
            
            with col1:
                # 开板次数分布（按值从大到小排序）
                open_count_dist = df['openCount'].value_counts().sort_values(ascending=False)
                fig_open = px.bar(
                    x=open_count_dist.index,
                    y=open_count_dist.values,
                    labels={'x': '开板次数', 'y': '股票数量'},
                    title="开板次数分布",
                    color=open_count_dist.values,
                    color_continuous_scale='Reds'  # 红色系渐变，表示跌停
                )
                fig_open.update_xaxes(tickangle=0)
                fig_open.update_layout(showlegend=False)
                st.plotly_chart(fig_open, use_container_width=True)
            
            with col2:
                # 开板次数TOP 10
                top_open = df.nlargest(10, 'openCount')[['code', 'name', 'openCount', 'changePercent']]
                st.dataframe(top_open, use_container_width=True)
        
        # 封单资金统计
        if 'sealingFunds' in df.columns:
            st.markdown("#### 💵 封单资金TOP 10")
            top_sealing = df.nlargest(10, 'sealingFunds')[['code', 'name', 'sealingFunds', 'changePercent']]
            st.dataframe(top_sealing, use_container_width=True)
        
        # 成交额TOP 10
        if 'turnover' in df.columns:
            st.markdown("#### 💰 成交额TOP 10")
            top_turnover = df.nlargest(10, 'turnover')[['code', 'name', 'turnover', 'changePercent']]
            st.dataframe(top_turnover, use_container_width=True)
        
        # 行业分布
        if 'industry' in df.columns:
            st.markdown("#### 🏢 行业分布")
            industry_count = df['industry'].value_counts().sort_values(ascending=False)
            # 创建横向柱状图，使用渐变色配色
            fig = px.bar(
                x=industry_count.values,
                y=industry_count.index,
                orientation='h',
                labels={'x': '股票数量', 'y': '行业'},
                title="行业分布",
                color=industry_count.values,
                color_continuous_scale='Reds'  # 红色系渐变，表示跌停
            )
            fig.update_layout(
                height=max(400, len(industry_count) * 30),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 数据表格
        st.markdown('<h2 class="section-header">📋 完整数据</h2>', unsafe_allow_html=True)
        
        # 数据筛选
        df_display = df.copy()
        if 'name' in df_display.columns or 'code' in df_display.columns:
            search_term = st.text_input("🔍 搜索股票（代码或名称）", "", key="search_dt")
            if search_term:
                # 使用OR逻辑：匹配name或code中的任意一个
                mask = pd.Series([False] * len(df_display))
                if 'name' in df_display.columns:
                    # 确保name列是字符串类型，处理NaN值
                    name_mask = df_display['name'].fillna('').astype(str).str.contains(search_term, case=False, na=False)
                    mask = mask | name_mask
                if 'code' in df_display.columns:
                    # 确保code列是字符串类型，处理NaN值
                    code_mask = df_display['code'].fillna('').astype(str).str.contains(search_term, case=False, na=False)
                    mask = mask | code_mask
                df_display = df_display[mask]
        
        # 移除不需要显示的列（id, index）
        columns_to_drop = []
        if 'id' in df_display.columns:
            columns_to_drop.append('id')
        if 'index' in df_display.columns:
            columns_to_drop.append('index')
        if columns_to_drop:
            df_display = df_display.drop(columns=columns_to_drop)
        
        # 列名映射：英文转中文
        column_mapping = {
            'date': '日期',
            'time': '时间',
            'code': '代码',
            'name': '名称',
            'changePercent': '涨跌幅(%)',
            'latestPrice': '最新价',
            'turnover': '成交额(亿元)',
            'circulatingMarketValue': '流通市值(亿元)',
            'totalMarketValue': '总市值(亿元)',
            'peRatio': '动态市盈率',
            'turnoverRate': '换手率(%)',
            'sealingFunds': '封单资金(亿元)',
            'lastSealingTime': '最后封板时间',
            'boardTurnover': '板上成交额(亿元)',
            'continuousLimitDown': '连续跌停',
            'openCount': '开板次数',
            'industry': '所属行业',
            'createdAt': '创建时间'
        }
        # 重命名列
        df_display = df_display.rename(columns=column_mapping)
        
        # 显示数据表格（显示全部数据，不限制高度）
        st.dataframe(df_display, use_container_width=True)
        
        # 下载按钮
        csv = df_display.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 下载CSV",
            data=csv,
            file_name=f"跌停股票池_{start_date}_{end_date}.csv",
            mime="text/csv",
            key="download_dt"
        )
        
except Exception as e:
    st.error(f"❌ 加载数据失败: {str(e)}")
    import traceback
    st.code(traceback.format_exc())

