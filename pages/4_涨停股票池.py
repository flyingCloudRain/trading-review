#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
涨停股票池查询页面
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
from services.zt_pool_history_service import ZtPoolHistoryService
from utils.time_utils import get_utc8_date, get_data_date, get_last_trading_day
import akshare as ak
import time

st.set_page_config(
    page_title="涨停股票池",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 应用统一样式
from utils.page_styles import apply_common_styles
apply_common_styles()

# 页面标题
st.markdown('<h1 class="main-header">📈 涨停股票池</h1>', unsafe_allow_html=True)

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
        stocks = ZtPoolHistoryService.get_zt_pool_by_date(db, start_date)
    else:
        stocks = ZtPoolHistoryService.get_zt_pool_by_date_range(db, start_date, end_date)
    
    if stocks:
        df = pd.DataFrame(stocks)
    else:
        df = pd.DataFrame()
    
    db.close()
    
    # 显示数据
    if df.empty:
        if start_date == end_date:
            st.warning(f"⚠️ {start_date} 暂无涨停股票数据")
            
            # 检查是否为交易日
            from tasks.sector_scheduler import SectorScheduler
            scheduler = SectorScheduler()
            is_trading = scheduler._is_trading_day(start_date)
            
            if not is_trading:
                st.info("💡 提示：该日期不是交易日，无法获取涨停股票数据。请选择其他交易日查看数据。")
        else:
            st.warning(f"⚠️ {start_date} 至 {end_date} 暂无涨停股票数据")
    else:
        # 统计信息卡片
        st.markdown('<h2 class="section-header">📈 涨停股票池 - 统计信息</h2>', unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
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
            # 计算连板率（连板数>1的股票数 / 涨停股票总数）
            if 'continuousBoards' in df.columns and len(df) > 0:
                # 连板数大于1的股票数
                continuous_count = len(df[df['continuousBoards'] > 1])
                # 连板率 = 连板股票数 / 涨停股票总数 * 100%
                continuous_rate = (continuous_count / len(df)) * 100 if len(df) > 0 else 0
                st.metric(
                    "🔗 连板率",
                    f"{continuous_rate:.1f}%",
                    delta=f"{continuous_count}/{len(df)}",
                    help=f"连板股票数（连板数>1）占涨停股票总数的比例，共{continuous_count}只连板股票"
                )
            else:
                st.metric("🔗 连板率", "N/A", help="暂无连板数据")
        
        with col5:
            if 'date' in df.columns:
                unique_dates = df['date'].nunique()
                st.metric("日期数量", unique_dates)
            else:
                st.metric("数据日期", start_date.strftime('%Y-%m-%d'))
        
        # 最近1个月每日涨停股票总数趋势
        st.markdown("#### 📈 最近1个月每日涨停股票总数趋势")
        try:
            # 获取最近1个月的数据
            trend_end_date = get_utc8_date()
            trend_start_date = trend_end_date - timedelta(days=29)  # 30天（包含今天）
            
            db_trend = SessionLocal()
            try:
                trend_stocks = ZtPoolHistoryService.get_zt_pool_by_date_range(db_trend, trend_start_date, trend_end_date)
                db_trend.close()
                
                if trend_stocks:
                    trend_df = pd.DataFrame(trend_stocks)
                    
                    if 'date' in trend_df.columns and len(trend_df) > 0:
                        # 按日期统计每日涨停股票总数
                        daily_count = trend_df.groupby('date').size().reset_index(name='涨停股票数')
                        daily_count['date'] = pd.to_datetime(daily_count['date'])
                        
                        # 过滤非交易日
                        from utils.time_utils import filter_trading_days
                        daily_count = filter_trading_days(daily_count, date_column='date')
                        
                        if daily_count.empty:
                            st.info("暂无交易日数据")
                        else:
                            daily_count = daily_count.sort_values('date')
                            
                            # 确保date列是datetime类型，然后转换为字符串格式，用于X轴显示（避免非交易日空白）
                            if not pd.api.types.is_datetime64_any_dtype(daily_count['date']):
                                daily_count['date'] = pd.to_datetime(daily_count['date'])
                            daily_count['date_str'] = daily_count['date'].dt.strftime('%Y-%m-%d')
                            
                            # 创建折线图 - 使用统一配置
                            from chart_config.chart_config import LINE_CHART_CONFIG, LINE_CHART_COLORS
                            
                            fig_trend = go.Figure()
                            
                            # 主折线 - 使用日期字符串作为X轴，确保数据点连续无空白
                            fig_trend.add_trace(go.Scatter(
                                x=daily_count['date_str'],
                                y=daily_count['涨停股票数'],
                                mode='lines+markers',
                                name='涨停股票数',
                                line=dict(
                                    color=LINE_CHART_COLORS['warning'],
                                    width=LINE_CHART_CONFIG['line_width'],
                                    shape='spline'  # 平滑曲线
                                ),
                                marker=dict(
                                    color=LINE_CHART_COLORS['warning'],
                                    size=LINE_CHART_CONFIG['marker_size'],
                                    line=dict(
                                        width=LINE_CHART_CONFIG['marker_line_width'],
                                        color=LINE_CHART_CONFIG['marker_line_color']
                                    )
                                ),
                                fill='tozeroy',  # 填充到零线
                                fillcolor=f"rgba(245, 158, 11, {LINE_CHART_CONFIG['fill_opacity']})"  # 橙色填充
                            ))
                            
                            # 添加平均值线
                            avg_count = daily_count['涨停股票数'].mean()
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
                            
                            # X轴使用类别模式，只显示交易日，数据点连续无空白
                            fig_trend.update_layout(
                                title=dict(
                                    text="最近1个月每日涨停股票总数趋势",
                                    font=dict(size=LINE_CHART_CONFIG['title_font_size']),
                                    x=0.5,
                                    xanchor='center'
                                ),
                                xaxis=dict(
                                    type='category',  # 使用类别轴，避免非交易日空白
                                    title=dict(text="日期", font=dict(size=LINE_CHART_CONFIG['axis_title_font_size'])),
                                    gridcolor=LINE_CHART_CONFIG['grid_color'],
                                    gridwidth=LINE_CHART_CONFIG['grid_width'],
                                    showgrid=True
                                ),
                                yaxis=dict(
                                    title=dict(text="涨停股票数", font=dict(size=LINE_CHART_CONFIG['axis_title_font_size'])),
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
        
        # 前一交易日涨停股票（暂时只显示前日涨停股票）
        st.markdown("---")
        st.markdown('<h2 class="section-header">📊 前一交易日涨停股票</h2>', unsafe_allow_html=True)
        
        try:
            # 获取前一交易日
            today = get_utc8_date()
            prev_trading_day = get_last_trading_day()
            
            # 如果前一交易日就是今天或大于今天，尝试获取数据库中的历史数据来找到真正的前一交易日
            if prev_trading_day >= today:
                db_check = SessionLocal()
                try:
                    # 查询数据库中最近有数据的日期
                    from models.zt_pool_history import ZtPoolHistory
                    recent_dates = db_check.query(ZtPoolHistory.date).distinct().order_by(ZtPoolHistory.date.desc()).limit(5).all()
                    if recent_dates:
                        # 找到小于今天的最大日期
                        for date_tuple in recent_dates:
                            if date_tuple[0] < today:
                                prev_trading_day = date_tuple[0]
                                break
                finally:
                    db_check.close()
            
            if prev_trading_day >= today:
                st.info("⚠️ 无法获取前一交易日数据")
            else:
                # 获取前一交易日的涨停股票
                db_prev = SessionLocal()
                try:
                    prev_zt_stocks = ZtPoolHistoryService.get_zt_pool_by_date(db_prev, prev_trading_day)
                    db_prev.close()
                    
                    if prev_zt_stocks and len(prev_zt_stocks) > 0:
                        # 转换为DataFrame用于显示
                        display_data = []
                        for stock in prev_zt_stocks:
                            display_data.append({
                                '代码': stock.get('code', ''),
                                '名称': stock.get('name', ''),
                                '涨跌幅(%)': stock.get('changePercent', 0),
                                '最新价': stock.get('latestPrice', 0),
                                '成交额(亿)': stock.get('turnover', 0),
                                '流通市值(亿)': stock.get('circulatingMarketValue', 0),
                                '总市值(亿)': stock.get('totalMarketValue', 0),
                                '换手率(%)': stock.get('turnoverRate', 0),
                                '封板资金(亿)': stock.get('sealingFunds', 0),
                                '首次封板时间': stock.get('firstSealingTime', ''),
                                '最后封板时间': stock.get('lastSealingTime', ''),
                                '炸板次数': stock.get('explosionCount', 0),
                                '连板数': stock.get('continuousBoards', 0),
                                '所属行业': stock.get('industry', '')
                            })
                        
                        df_display = pd.DataFrame(display_data)
                        
                        # 在格式化之前计算统计信息
                        continuous_boards_count = len(df_display[df_display['连板数'] > 1]) if '连板数' in df_display.columns else 0
                        total_sealing_funds = df_display['封板资金(亿)'].sum() if '封板资金(亿)' in df_display.columns else 0
                        
                        # 按连板数降序排序，然后按涨跌幅降序排序
                        df_display = df_display.sort_values(['连板数', '涨跌幅(%)'], ascending=[False, False])
                        
                        # 格式化数值列
                        if '涨跌幅(%)' in df_display.columns:
                            df_display['涨跌幅(%)'] = df_display['涨跌幅(%)'].apply(lambda x: f"{x:+.2f}%" if pd.notna(x) else "N/A")
                        if '最新价' in df_display.columns:
                            df_display['最新价'] = df_display['最新价'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
                        if '成交额(亿)' in df_display.columns:
                            df_display['成交额(亿)'] = df_display['成交额(亿)'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
                        if '流通市值(亿)' in df_display.columns:
                            df_display['流通市值(亿)'] = df_display['流通市值(亿)'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
                        if '总市值(亿)' in df_display.columns:
                            df_display['总市值(亿)'] = df_display['总市值(亿)'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
                        if '换手率(%)' in df_display.columns:
                            df_display['换手率(%)'] = df_display['换手率(%)'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
                        if '封板资金(亿)' in df_display.columns:
                            df_display['封板资金(亿)'] = df_display['封板资金(亿)'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
                        if '连板数' in df_display.columns:
                            df_display['连板数'] = df_display['连板数'].apply(lambda x: str(int(x)) if pd.notna(x) else "N/A")
                        if '炸板次数' in df_display.columns:
                            df_display['炸板次数'] = df_display['炸板次数'].apply(lambda x: str(int(x)) if pd.notna(x) else "N/A")
                        
                        # 显示统计信息
                        col_stat1, col_stat2, col_stat3 = st.columns(3)
                        with col_stat1:
                            st.metric("📊 涨停股票数", len(df_display))
                        with col_stat2:
                            st.metric("📈 连板股票数", continuous_boards_count, delta=f"{continuous_boards_count}/{len(df_display)}")
                        with col_stat3:
                            st.metric("💰 总封板资金", f"{total_sealing_funds:.2f}亿")
                        
                        # 显示数据表格
                        st.dataframe(df_display, use_container_width=True, height=400)
                    else:
                        st.info(f"📭 前一交易日（{prev_trading_day}）没有涨停股票数据")
                except Exception as e:
                    if 'db_prev' in locals():
                        db_prev.close()
                    st.warning(f"⚠️ 获取前一交易日数据失败: {str(e)}")
        except Exception as e:
            st.warning(f"⚠️ 显示前一交易日涨停股票失败: {str(e)}")
        
        # 行业分布
        if 'industry' in df.columns:
            st.markdown("#### 🏢 行业分布")
            industry_count = df['industry'].value_counts().sort_values(ascending=False)
            # 创建横向柱状图，使用渐变色配色
            # 确保按值从大到小排序（值大的在上方）
            # 对于横向柱状图，需要反转Y轴顺序才能让值大的在上方
            fig = px.bar(
                x=industry_count.values,
                y=industry_count.index,
                orientation='h',
                labels={'x': '股票数量', 'y': '行业'},
                title="行业分布",
                color=industry_count.values,
                color_continuous_scale='Oranges'  # 橙色系渐变
            )
            # 设置Y轴顺序，使值大的在上方
            # 对于横向柱状图，Y轴从上到下显示，需要反转数组让值大的在上方
            # industry_count已经按值从大到小排序，反转后值大的会在上方
            fig.update_layout(
                height=max(400, len(industry_count) * 30),
                showlegend=False,
                yaxis={'categoryorder': 'array', 'categoryarray': list(reversed(industry_count.index))}  # 反转顺序，值大的在上方
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 连板数统计
        if 'continuousBoards' in df.columns:
            st.markdown("#### 📊 连板数统计")
            col1, col2 = st.columns(2)
            
            with col1:
                # 连板数分布（按值从大到小排序）
                board_dist = df['continuousBoards'].value_counts().sort_values(ascending=False)
                # 使用 Plotly 创建柱状图，设置 X 轴标签角度和配色
                # 创建DataFrame以便更好地控制颜色映射
                board_df = pd.DataFrame({
                    '连板数': board_dist.index,
                    '股票数量': board_dist.values
                })
                fig_board = px.bar(
                    board_df,
                    x='连板数',
                    y='股票数量',
                    labels={'连板数': '连板数', '股票数量': '股票数量'},
                    title="连板数分布",
                    color='股票数量',
                    color_continuous_scale='Oranges',  # 橙色系渐变
                    color_continuous_midpoint=None  # 确保从最小值到最大值渐变
                )
                fig_board.update_xaxes(tickangle=0)  # 设置 X 轴标签角度为 0（水平显示）
                fig_board.update_layout(
                    showlegend=False,
                    coloraxis_showscale=False  # 隐藏颜色条，因为数值越大颜色越深已经很明显
                )
                st.plotly_chart(fig_board, use_container_width=True)
            
            with col2:
                # 连板股票（连板数>1）
                st.markdown("#### 📊 连板股票")
                if 'continuousBoards' in df.columns:
                    # 筛选连板股票（连板数>1），按连板数降序排列
                    continuous_stocks = df[df['continuousBoards'] > 1].copy()
                    if not continuous_stocks.empty:
                        continuous_stocks = continuous_stocks.sort_values('continuousBoards', ascending=False)
                        display_cols = ['code', 'name', 'continuousBoards', 'changePercent']
                        available_cols = [col for col in display_cols if col in continuous_stocks.columns]
                        # 转换为中文列名
                        continuous_display = continuous_stocks[available_cols].copy()
                        col_mapping = {
                            'code': '代码',
                            'name': '名称',
                            'continuousBoards': '连板数',
                            'changePercent': '涨跌幅(%)'
                        }
                        continuous_display = continuous_display.rename(columns={k: v for k, v in col_mapping.items() if k in continuous_display.columns})
                        st.dataframe(continuous_display, use_container_width=True)
                    else:
                        st.info("暂无连板股票（连板数>1）")
                else:
                    st.info("暂无连板数据")
        
        # 封板资金统计
        if 'sealingFunds' in df.columns:
            st.markdown("#### 💵 封板资金TOP 10")
            top_sealing = df.nlargest(10, 'sealingFunds')[['code', 'name', 'sealingFunds', 'continuousBoards']].copy()
            # 创建横向柱状图
            fig_sealing = px.bar(
                top_sealing,
                x='sealingFunds',
                y='name',
                orientation='h',
                labels={'sealingFunds': '封板资金(亿元)', 'name': '股票名称'},
                title="封板资金TOP 10",
                color='sealingFunds',
                color_continuous_scale='Oranges',
                text='sealingFunds'  # 在柱状图上显示数值
            )
            fig_sealing.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            fig_sealing.update_layout(
                height=400,
                showlegend=False,
                coloraxis_showscale=False,
                yaxis={'categoryorder': 'total ascending'}  # 按值从大到小排序
            )
            st.plotly_chart(fig_sealing, use_container_width=True)
        
        # 成交额TOP 10
        if 'turnover' in df.columns:
            st.markdown("#### 💰 成交额TOP 10")
            top_turnover = df.nlargest(10, 'turnover')[['code', 'name', 'turnover', 'continuousBoards']].copy()
            # 创建横向柱状图
            fig_turnover = px.bar(
                top_turnover,
                x='turnover',
                y='name',
                orientation='h',
                labels={'turnover': '成交额(亿元)', 'name': '股票名称'},
                title="成交额TOP 10",
                color='turnover',
                color_continuous_scale='Oranges',
                text='turnover'  # 在柱状图上显示数值
            )
            fig_turnover.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            fig_turnover.update_layout(
                height=400,
                showlegend=False,
                coloraxis_showscale=False,
                yaxis={'categoryorder': 'total ascending'}  # 按值从大到小排序
            )
            st.plotly_chart(fig_turnover, use_container_width=True)
        
      
        
        # 数据表格
        st.markdown('<h2 class="section-header">📋 完整数据</h2>', unsafe_allow_html=True)
        
        # 数据筛选
        df_display = df.copy()
        if 'name' in df_display.columns or 'code' in df_display.columns:
            search_term = st.text_input("🔍 搜索股票（代码或名称）", "", key="search_zt")
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
            'turnoverRate': '换手率(%)',
            'sealingFunds': '封板资金(亿元)',
            'firstSealingTime': '首次封板时间',
            'lastSealingTime': '最后封板时间',
            'explosionCount': '炸板次数',
            'ztStatistics': '涨停统计',
            'continuousBoards': '连板数',
            'industry': '所属行业',
            'createdAt': '创建时间'
        }
        # 重命名列
        df_display = df_display.rename(columns=column_mapping)
        
        # 显示前20条记录
        df_display = df_display.head(20)
        st.dataframe(df_display, use_container_width=True)
        
        # 下载按钮
        csv = df_display.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 下载CSV",
            data=csv,
            file_name=f"涨停股票池_{start_date}_{end_date}.csv",
            mime="text/csv",
            key="download_zt"
        )
        
except Exception as e:
    st.error(f"❌ 加载数据失败: {str(e)}")
    import traceback
    st.code(traceback.format_exc())

