#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
个股表现查询页面
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

import akshare as ak
import time
from utils.time_utils import get_utc8_date, get_data_date

st.set_page_config(
    page_title="个股表现",
    page_icon="📊",
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
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-top: 2.5rem;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e0e0e0;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">📊 个股表现</h1>', unsafe_allow_html=True)

# 股票代码输入
stock_code = None
stock_name = None

code_input = st.text_input(
        "📊 股票代码",
        value="000001",
        help="请输入6位股票代码，如：000001（平安银行）、600000（浦发银行）、300001（特锐德）",
        placeholder="000001"
    )

if code_input:
    code_input = code_input.strip()
    
    # 去除前缀
    if code_input.startswith('sh') or code_input.startswith('sz') or code_input.startswith('bj'):
        code_input = code_input[2:]
    
    # 验证是否为6位数字
    if code_input.isdigit() and len(code_input) == 6:
        stock_code = code_input
    else:
        st.error("❌ 请输入有效的6位股票代码")
        st.stop()
    
# 验证股票代码
if not stock_code:
    st.info("💡 请输入股票代码进行查询")
    st.stop()

# 获取股票数据
if stock_code:
    try:
        # 获取资金流数据（带重试机制）
        with st.spinner("🔄 正在获取个股数据..."):
            df_fund = None
            max_retries = 3
            retry_delay = 2
            
            for retry in range(max_retries):
                try:
                    df_fund = ak.stock_individual_fund_flow(stock=stock_code)
                    break  # 成功获取，跳出重试循环
                except Exception as e:
                    if retry < max_retries - 1:
                        st.warning(f"⚠️ 获取资金流数据失败，{retry_delay}秒后重试... ({retry + 1}/{max_retries})")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # 指数退避
                    else:
                        raise e
            
            # 获取历史行情数据（带重试机制）
            hist_df = None
            retry_delay = 2
            
            for retry in range(max_retries):
                try:
                    hist_df = ak.stock_zh_a_hist(symbol=stock_code)
                    break  # 成功获取，跳出重试循环
                except Exception as e:
                    if retry < max_retries - 1:
                        st.warning(f"⚠️ 获取历史行情数据失败，{retry_delay}秒后重试... ({retry + 1}/{max_retries})")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # 指数退避
                    else:
                        raise e
        
        if df_fund.empty:
            st.warning(f"⚠️ 未找到股票代码 {stock_code} 的资金流数据")
            st.stop()
        
        if hist_df.empty:
            st.warning(f"⚠️ 未找到股票代码 {stock_code} 的历史行情数据")
            st.stop()
        
        # 转换日期列为日期类型
        if '日期' in df_fund.columns:
            df_fund['日期'] = pd.to_datetime(df_fund['日期'])
            df_fund = df_fund.sort_values('日期', ascending=False)
        
        # 处理历史行情数据
        if '日期' in hist_df.columns:
            hist_df['日期'] = pd.to_datetime(hist_df['日期'])
            hist_df = hist_df.sort_values('日期', ascending=False)
        
        # 股票名称（使用代码作为显示名称）
        if not stock_name:
            stock_name = stock_code
        
        # 显示股票基本信息
        if len(hist_df) > 0:
            latest_hist = hist_df.iloc[0]
            latest_fund = df_fund.iloc[0] if len(df_fund) > 0 else None
            st.markdown("---")
            
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            with col1:
                st.metric("股票代码", stock_code)
            with col2:
                st.metric("股票名称", stock_name)
            with col3:
                if '收盘' in latest_hist:
                    st.metric("最新收盘价", f"{latest_hist['收盘']:.2f}")
            with col4:
                if '涨跌幅' in latest_hist:
                    change_pct = latest_hist['涨跌幅']
                    delta_color = "normal" if change_pct >= 0 else "inverse"
                    st.metric("涨跌幅", f"{change_pct:.2f}%", delta=f"{change_pct:.2f}%", delta_color=delta_color)
            with col5:
                if '成交量' in latest_hist:
                    volume = latest_hist['成交量']
                    st.metric("成交量", f"{volume/10000:.2f}万手" if volume >= 10000 else f"{volume:.0f}手")
            with col6:
                if '日期' in latest_hist:
                    st.metric("最新日期", latest_hist['日期'].strftime('%Y-%m-%d') if pd.notna(latest_hist['日期']) else "N/A")
        
        # 价格统计信息
        if len(hist_df) > 0:
            latest_hist = hist_df.iloc[0]
            st.markdown('<h2 class="section-header">📊 价格统计</h2>', unsafe_allow_html=True)
            
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            with col1:
                if '开盘' in latest_hist:
                    st.metric("今开", f"{latest_hist['开盘']:.2f}")
            with col2:
                if '最高' in latest_hist:
                    st.metric("最高", f"{latest_hist['最高']:.2f}")
            with col3:
                if '最低' in latest_hist:
                    st.metric("最低", f"{latest_hist['最低']:.2f}")
            with col4:
                if '振幅' in latest_hist:
                    st.metric("振幅", f"{latest_hist['振幅']:.2f}%")
            with col5:
                if '换手率' in latest_hist:
                    st.metric("换手率", f"{latest_hist['换手率']:.2f}%")
            with col6:
                if '成交额' in latest_hist:
                    amount = latest_hist['成交额']
                    st.metric("成交额", f"{amount/100000000:.2f}亿" if amount >= 100000000 else f"{amount/10000:.2f}万")
        
        # 价格走势图
        st.markdown('<h2 class="section-header">📈 价格走势</h2>', unsafe_allow_html=True)
        
        # 选择显示天数
        days_options = [30, 60, 90, 180, 365]
        selected_days = st.selectbox("选择显示天数", days_options, index=2, key="price_days")
        
        hist_chart = hist_df.head(selected_days).copy()
        hist_chart = hist_chart.sort_values('日期', ascending=True)
        
        # 过滤非交易日（如果日期列存在）
        if '日期' in hist_chart.columns:
            from utils.time_utils import filter_trading_days
            hist_chart = filter_trading_days(hist_chart, date_column='日期')
        
        # K线图
        fig_kline = go.Figure()
        
        # 添加K线
        fig_kline.add_trace(go.Candlestick(
            x=hist_chart['日期'],
            open=hist_chart['开盘'],
            high=hist_chart['最高'],
            low=hist_chart['最低'],
            close=hist_chart['收盘'],
            name='K线'
        ))
        
        fig_kline.update_layout(
            title="K线图",
            xaxis_title="日期",
            yaxis_title="价格（元）",
            height=500,
            xaxis_rangeslider_visible=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12)
        )
        
        st.plotly_chart(fig_kline, use_container_width=True)
        
        # 价格和成交量对比
        col1, col2 = st.columns(2)
        
        with col1:
            # 收盘价走势
            fig_price = go.Figure()
            
            fig_price.add_trace(go.Scatter(
                x=hist_chart['日期'],
                y=hist_chart['收盘'],
                mode='lines+markers',
                name='收盘价',
                line=dict(color='#1f77b4', width=2),
                marker=dict(size=4)
            ))
            
            fig_price.update_layout(
                title="收盘价走势",
                xaxis_title="日期",
                yaxis_title="价格（元）",
                height=400,
                hovermode='x unified',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12)
            )
            
            st.plotly_chart(fig_price, use_container_width=True)
        
        with col2:
            # 成交量走势
            fig_volume = go.Figure()
            
            colors = ['#2ca02c' if hist_chart.iloc[i]['收盘'] >= hist_chart.iloc[i]['开盘'] else '#d62728' 
                     for i in range(len(hist_chart))]
            
            fig_volume.add_trace(go.Bar(
                x=hist_chart['日期'],
                y=hist_chart['成交量'] / 10000,  # 转换为万手
                name='成交量',
                marker_color=colors
            ))
            
            fig_volume.update_layout(
                title="成交量走势",
                xaxis_title="日期",
                yaxis_title="成交量（万手）",
                height=400,
                hovermode='x unified',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12)
            )
            
            st.plotly_chart(fig_volume, use_container_width=True)
        
        # 涨跌幅统计
        st.markdown('<h2 class="section-header">📊 涨跌幅统计</h2>', unsafe_allow_html=True)
        
        if '涨跌幅' in hist_chart.columns:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                up_days = len(hist_chart[hist_chart['涨跌幅'] > 0])
                st.metric("上涨天数", f"{up_days}", delta=f"{up_days}/{len(hist_chart)}")
            
            with col2:
                down_days = len(hist_chart[hist_chart['涨跌幅'] < 0])
                st.metric("下跌天数", f"{down_days}", delta=f"{down_days}/{len(hist_chart)}")
            
            with col3:
                avg_change = hist_chart['涨跌幅'].mean()
                st.metric("平均涨跌幅", f"{avg_change:+.2f}%")
            
            with col4:
                max_change = hist_chart['涨跌幅'].max()
                min_change = hist_chart['涨跌幅'].min()
                st.metric("最大涨跌幅", f"{max_change:+.2f}% / {min_change:+.2f}%")
        
        # 历史数据表格
        st.markdown('<h2 class="section-header">📋 历史行情数据</h2>', unsafe_allow_html=True)
        
        display_hist = hist_chart.copy()
        
        # 格式化数值
        if '收盘' in display_hist.columns:
            display_hist['收盘'] = display_hist['收盘'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
        if '开盘' in display_hist.columns:
            display_hist['开盘'] = display_hist['开盘'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
        if '最高' in display_hist.columns:
            display_hist['最高'] = display_hist['最高'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
        if '最低' in display_hist.columns:
            display_hist['最低'] = display_hist['最低'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
        if '涨跌幅' in display_hist.columns:
            display_hist['涨跌幅'] = display_hist['涨跌幅'].apply(lambda x: f"{x:+.2f}%" if pd.notna(x) else "N/A")
        if '涨跌额' in display_hist.columns:
            display_hist['涨跌额'] = display_hist['涨跌额'].apply(lambda x: f"{x:+.2f}" if pd.notna(x) else "N/A")
        if '成交量' in display_hist.columns:
            display_hist['成交量'] = display_hist['成交量'].apply(lambda x: f"{x/10000:.2f}万" if pd.notna(x) and x >= 10000 else f"{x:.0f}" if pd.notna(x) else "N/A")
        if '成交额' in display_hist.columns:
            display_hist['成交额'] = display_hist['成交额'].apply(lambda x: f"{x/100000000:.2f}亿" if pd.notna(x) and x >= 100000000 else f"{x/10000:.2f}万" if pd.notna(x) else "N/A")
        if '振幅' in display_hist.columns:
            display_hist['振幅'] = display_hist['振幅'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
        if '换手率' in display_hist.columns:
            display_hist['换手率'] = display_hist['换手率'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
        
        # 格式化日期
        if '日期' in display_hist.columns:
            display_hist['日期'] = display_hist['日期'].dt.strftime('%Y-%m-%d')
        
        # 选择显示的列
        display_cols = ['日期', '开盘', '收盘', '最高', '最低', '涨跌幅', '涨跌额', '成交量', '成交额', '振幅', '换手率']
        available_cols = [col for col in display_cols if col in display_hist.columns]
        
        st.dataframe(display_hist[available_cols], use_container_width=True, height=400)
        
        # 资金流统计
        if len(df_fund) > 0:
            df = df_fund  # 为了兼容后续代码
        
        # 资金流统计
        st.markdown('<h2 class="section-header">💰 资金流统计</h2>', unsafe_allow_html=True)
        
        if len(df_fund) > 0:
            latest_data = df_fund.iloc[0]
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                if '主力净流入-净额' in latest_data:
                    main_net = latest_data['主力净流入-净额']
                    main_pct = latest_data.get('主力净流入-净占比', 0)
                    st.metric(
                        "主力净流入",
                        f"{main_net/100000000:.2f}亿" if abs(main_net) >= 100000000 else f"{main_net/10000:.2f}万",
                        delta=f"{main_pct:.2f}%",
                        delta_color="normal" if main_net >= 0 else "inverse"
                    )
            
            with col2:
                if '超大单净流入-净额' in latest_data:
                    super_large_net = latest_data['超大单净流入-净额']
                    super_large_pct = latest_data.get('超大单净流入-净占比', 0)
                    st.metric(
                        "超大单净流入",
                        f"{super_large_net/100000000:.2f}亿" if abs(super_large_net) >= 100000000 else f"{super_large_net/10000:.2f}万",
                        delta=f"{super_large_pct:.2f}%",
                        delta_color="normal" if super_large_net >= 0 else "inverse"
                    )
            
            with col3:
                if '大单净流入-净额' in latest_data:
                    large_net = latest_data['大单净流入-净额']
                    large_pct = latest_data.get('大单净流入-净占比', 0)
                    st.metric(
                        "大单净流入",
                        f"{large_net/100000000:.2f}亿" if abs(large_net) >= 100000000 else f"{large_net/10000:.2f}万",
                        delta=f"{large_pct:.2f}%",
                        delta_color="normal" if large_net >= 0 else "inverse"
                    )
            
            with col4:
                if '中单净流入-净额' in latest_data:
                    medium_net = latest_data['中单净流入-净额']
                    medium_pct = latest_data.get('中单净流入-净占比', 0)
                    st.metric(
                        "中单净流入",
                        f"{medium_net/100000000:.2f}亿" if abs(medium_net) >= 100000000 else f"{medium_net/10000:.2f}万",
                        delta=f"{medium_pct:.2f}%",
                        delta_color="normal" if medium_net >= 0 else "inverse"
                    )
            
            with col5:
                if '小单净流入-净额' in latest_data:
                    small_net = latest_data['小单净流入-净额']
                    small_pct = latest_data.get('小单净流入-净占比', 0)
                    st.metric(
                        "小单净流入",
                        f"{small_net/100000000:.2f}亿" if abs(small_net) >= 100000000 else f"{small_net/10000:.2f}万",
                        delta=f"{small_pct:.2f}%",
                        delta_color="normal" if small_net >= 0 else "inverse"
                    )
        
        # 资金流趋势图
        st.markdown('<h2 class="section-header">💰 资金流趋势</h2>', unsafe_allow_html=True)
        
        # 选择显示天数
        days_options = [30, 60, 90, 120]
        selected_days = st.selectbox("选择显示天数", days_options, index=2, key="fund_days")
        
        df_chart = df_fund.head(selected_days).copy()
        df_chart = df_chart.sort_values('日期', ascending=True)
        
        # 主力净流入趋势
        fig_main = go.Figure()
        
        fig_main.add_trace(go.Scatter(
            x=df_chart['日期'],
            y=df_chart['主力净流入-净额'] / 100000000,  # 转换为亿元
            mode='lines+markers',
            name='主力净流入',
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=4),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 180, 0.1)'
        ))
        
        fig_main.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        
        fig_main.update_layout(
            title="主力净流入趋势",
            xaxis_title="日期",
            yaxis_title="净流入（亿元）",
            height=400,
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12)
        )
        
        st.plotly_chart(fig_main, use_container_width=True)
        
        # 各类资金流对比
        col1, col2 = st.columns(2)
        
        with col1:
            fig_compare = go.Figure()
            
            # 超大单
            fig_compare.add_trace(go.Scatter(
                x=df_chart['日期'],
                y=df_chart['超大单净流入-净额'] / 100000000,
                mode='lines',
                name='超大单',
                line=dict(color='#ff7f0e', width=2)
            ))
            
            # 大单
            fig_compare.add_trace(go.Scatter(
                x=df_chart['日期'],
                y=df_chart['大单净流入-净额'] / 100000000,
                mode='lines',
                name='大单',
                line=dict(color='#2ca02c', width=2)
            ))
            
            # 中单
            fig_compare.add_trace(go.Scatter(
                x=df_chart['日期'],
                y=df_chart['中单净流入-净额'] / 100000000,
                mode='lines',
                name='中单',
                line=dict(color='#d62728', width=2)
            ))
            
            # 小单
            fig_compare.add_trace(go.Scatter(
                x=df_chart['日期'],
                y=df_chart['小单净流入-净额'] / 100000000,
                mode='lines',
                name='小单',
                line=dict(color='#9467bd', width=2)
            ))
            
            fig_compare.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
            
            fig_compare.update_layout(
                title="各类资金流对比",
                xaxis_title="日期",
                yaxis_title="净流入（亿元）",
                height=400,
                hovermode='x unified',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig_compare, use_container_width=True)
        
        with col2:
            # 资金流占比趋势
            fig_pct = go.Figure()
            
            fig_pct.add_trace(go.Scatter(
                x=df_chart['日期'],
                y=df_chart['主力净流入-净占比'],
                mode='lines+markers',
                name='主力净占比',
                line=dict(color='#1f77b4', width=2),
                marker=dict(size=4)
            ))
            
            fig_pct.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
            
            fig_pct.update_layout(
                title="主力净流入占比趋势",
                xaxis_title="日期",
                yaxis_title="净占比（%）",
                height=400,
                hovermode='x unified',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12)
            )
            
            st.plotly_chart(fig_pct, use_container_width=True)
        
        # 资金流完整数据表格
        st.markdown('<h2 class="section-header">📋 资金流完整数据</h2>', unsafe_allow_html=True)
        
        # 准备显示数据
        display_df = df_fund.copy()
        
        # 格式化数值列
        numeric_cols = [
            '收盘价', '涨跌幅',
            '主力净流入-净额', '主力净流入-净占比',
            '超大单净流入-净额', '超大单净流入-净占比',
            '大单净流入-净额', '大单净流入-净占比',
            '中单净流入-净额', '中单净流入-净占比',
            '小单净流入-净额', '小单净流入-净占比'
        ]
        
        for col in numeric_cols:
            if col in display_df.columns:
                if '净额' in col:
                    # 净额转换为万元显示
                    display_df[col] = display_df[col].apply(lambda x: f"{x/10000:.2f}万" if pd.notna(x) else "N/A")
                elif '净占比' in col or '涨跌幅' in col:
                    # 百分比保留2位小数
                    display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
                elif '收盘价' in col:
                    # 价格保留2位小数
                    display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
        
        # 格式化日期
        if '日期' in display_df.columns:
            display_df['日期'] = display_df['日期'].dt.strftime('%Y-%m-%d')
        
        st.dataframe(display_df, use_container_width=True, height=400)
        
    except Exception as e:
        st.error(f"❌ 获取数据失败: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

