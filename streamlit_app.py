#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股交易复盘系统 - Streamlit可视化应用
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.db import SessionLocal
from services.sector_history_service import SectorHistoryService
from utils.time_utils import get_utc8_date_str

# 页面配置
st.set_page_config(
    page_title="A股交易复盘系统",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 标题
st.title("📈 A股交易复盘系统 - 数据可视化")

# 提示：此文件已不再使用，请使用 pages 目录下的多页面应用
st.info("💡 请使用左侧导航栏访问各个页面功能")

# 侧边栏已移除，使用多页面应用（pages目录）
# 以下代码已废弃，保留仅用于兼容性
"""
# 板块信息可视化
if page == "板块信息":
    st.header("📊 板块信息可视化")
    
    # 数据源选择
    data_source = st.radio("数据来源", ["数据库", "Excel文件"], horizontal=True)
    
    if data_source == "数据库":
        try:
            db = SessionLocal()
            dates = SectorHistoryService.get_all_dates(db)
            db.close()
            
            if dates:
                selected_date = st.selectbox(
                    "选择日期",
                    options=[d.strftime('%Y-%m-%d') for d in dates],
                    index=0
                )
                
                db = SessionLocal()
                sectors = SectorHistoryService.get_sectors_by_date(
                    db, datetime.strptime(selected_date, '%Y-%m-%d').date()
                )
                db.close()
                
                df = pd.DataFrame(sectors)
            else:
                st.warning("数据库中没有板块历史数据")
                df = pd.DataFrame()
        except Exception as e:
            st.error(f"读取数据库失败: {str(e)}")
            df = pd.DataFrame()
    else:
        # 从Excel读取
        excel_file = Path('data/板块信息历史.xlsx')
        if excel_file.exists():
            try:
                df = pd.read_excel(excel_file, sheet_name='板块信息')
                # 选择最新日期的数据
                if len(df) > 0:
                    latest_date = df['日期'].max()
                    df = df[df['日期'] == latest_date]
                    st.info(f"显示日期: {latest_date}")
            except Exception as e:
                st.error(f"读取Excel失败: {str(e)}")
                df = pd.DataFrame()
        else:
            st.warning("Excel文件不存在")
            df = pd.DataFrame()
    
    if not df.empty:
        # 创建两列布局
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 涨跌幅排名（TOP 10）")
            top10 = df.nlargest(10, 'changePercent' if 'changePercent' in df.columns else '涨跌幅(%)')
            y_col = 'changePercent' if 'changePercent' in df.columns else '涨跌幅(%)'
            name_col = 'name' if 'name' in df.columns else '板块'
            
            fig_bar = px.bar(
                top10,
                x=name_col,
                y=y_col,
                title="涨跌幅TOP 10",
                labels={y_col: '涨跌幅(%)', name_col: '板块'},
                color=y_col,
                color_continuous_scale='RdYlGn'
            )
            fig_bar.update_layout(height=400)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            st.subheader("📉 涨跌幅排名（BOTTOM 10）")
            bottom10 = df.nsmallest(10, y_col)
            
            fig_bar2 = px.bar(
                bottom10,
                x=name_col,
                y=y_col,
                title="涨跌幅BOTTOM 10",
                labels={y_col: '涨跌幅(%)', name_col: '板块'},
                color=y_col,
                color_continuous_scale='RdYlGn_r'
            )
            fig_bar2.update_layout(height=400)
            st.plotly_chart(fig_bar2, use_container_width=True)
        
        # 涨跌幅分布
        st.subheader("📊 涨跌幅分布")
        fig_hist = px.histogram(
            df,
            x=y_col,
            nbins=30,
            title="涨跌幅分布直方图",
            labels={y_col: '涨跌幅(%)', 'count': '板块数量'}
        )
        st.plotly_chart(fig_hist, use_container_width=True)
        
        # 数据表格
        st.subheader("📋 完整数据")
        st.dataframe(df, use_container_width=True, height=400)

# 涨停股票可视化
elif page == "涨停股票":
    st.header("📈 涨停股票可视化")
    
    excel_file = Path('data/涨停股票池.xlsx')
    if excel_file.exists():
        try:
            df = pd.read_excel(excel_file, sheet_name='涨停股票')
            
            if len(df) > 0:
                # 选择最新日期的数据
                latest_date = df['日期'].max()
                df_latest = df[df['日期'] == latest_date].copy()
                
                st.info(f"显示日期: {latest_date}，共 {len(df_latest)} 只涨停股票")
                
                # 统计信息
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("涨停股票数", len(df_latest))
                with col2:
                    st.metric("平均涨跌幅", f"{df_latest['涨跌幅(%)'].mean():.2f}%")
                with col3:
                    st.metric("总成交额", f"{df_latest['成交额(亿元)'].sum():.2f}亿元")
                with col4:
                    st.metric("平均连板数", f"{df_latest['连板数'].mean():.1f}")
                
                # 连板数分布
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("📊 连板数分布")
                    fig_pie = px.pie(
                        df_latest,
                        names='连板数',
                        title="连板数分布",
                        hole=0.4
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with col2:
                    st.subheader("📊 行业分布（TOP 10）")
                    industry_count = df_latest['所属行业'].value_counts().head(10)
                    fig_bar = px.bar(
                        x=industry_count.index,
                        y=industry_count.values,
                        title="行业分布",
                        labels={'x': '行业', 'y': '股票数量'}
                    )
                    fig_bar.update_xaxes(tickangle=45)
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                # 成交额TOP 10
                st.subheader("💰 成交额TOP 10")
                top_turnover = df_latest.nlargest(10, '成交额(亿元)')
                fig_bar = px.bar(
                    top_turnover,
                    x='名称',
                    y='成交额(亿元)',
                    title="成交额TOP 10",
                    labels={'名称': '股票名称', '成交额(亿元)': '成交额(亿元)'}
                )
                fig_bar.update_xaxes(tickangle=45)
                st.plotly_chart(fig_bar, use_container_width=True)
                
                # 数据表格
                st.subheader("📋 完整数据")
                st.dataframe(df_latest, use_container_width=True, height=400)
            else:
                st.warning("Excel文件中没有数据")
        except Exception as e:
            st.error(f"读取Excel失败: {str(e)}")
    else:
        st.warning("涨停股票池Excel文件不存在")

# 炸板股票可视化
elif page == "炸板股票":
    st.header("💥 炸板股票可视化")
    
    excel_file = Path('data/炸板股票池.xlsx')
    if excel_file.exists():
        try:
            df = pd.read_excel(excel_file, sheet_name='炸板股票')
            
            if len(df) > 0:
                latest_date = df['日期'].max()
                df_latest = df[df['日期'] == latest_date].copy()
                
                st.info(f"显示日期: {latest_date}，共 {len(df_latest)} 只炸板股票")
                
                # 统计信息
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("炸板股票数", len(df_latest))
                with col2:
                    st.metric("平均涨跌幅", f"{df_latest['涨跌幅(%)'].mean():.2f}%")
                with col3:
                    st.metric("总成交额", f"{df_latest['成交额(亿元)'].sum():.2f}亿元")
                
                # 炸板次数分布
                st.subheader("💥 炸板次数分布")
                explosion_count = df_latest['炸板次数'].value_counts().sort_index()
                fig_bar = px.bar(
                    x=explosion_count.index,
                    y=explosion_count.values,
                    title="炸板次数分布",
                    labels={'x': '炸板次数', 'y': '股票数量'}
                )
                st.plotly_chart(fig_bar, use_container_width=True)
                
                # 数据表格
                st.subheader("📋 完整数据")
                st.dataframe(df_latest, use_container_width=True, height=400)
            else:
                st.warning("Excel文件中没有数据")
        except Exception as e:
            st.error(f"读取Excel失败: {str(e)}")
    else:
        st.warning("炸板股票池Excel文件不存在")

# 跌停股票可视化
elif page == "跌停股票":
    st.header("📉 跌停股票可视化")
    
    excel_file = Path('data/跌停股票池.xlsx')
    if excel_file.exists():
        try:
            df = pd.read_excel(excel_file, sheet_name='跌停股票')
            
            if len(df) > 0:
                latest_date = df['日期'].max()
                df_latest = df[df['日期'] == latest_date].copy()
                
                st.info(f"显示日期: {latest_date}，共 {len(df_latest)} 只跌停股票")
                
                # 统计信息
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("跌停股票数", len(df_latest))
                with col2:
                    st.metric("平均涨跌幅", f"{df_latest['涨跌幅(%)'].mean():.2f}%")
                with col3:
                    st.metric("总成交额", f"{df_latest['成交额(亿元)'].sum():.2f}亿元")
                
                # 连续跌停分布
                st.subheader("📉 连续跌停分布")
                limit_down_count = df_latest['连续跌停'].value_counts().sort_index()
                fig_bar = px.bar(
                    x=limit_down_count.index,
                    y=limit_down_count.values,
                    title="连续跌停分布",
                    labels={'x': '连续跌停数', 'y': '股票数量'}
                )
                st.plotly_chart(fig_bar, use_container_width=True)
                
                # 数据表格
                st.subheader("📋 完整数据")
                st.dataframe(df_latest, use_container_width=True, height=400)
            else:
                st.warning("Excel文件中没有数据")
        except Exception as e:
            st.error(f"读取Excel失败: {str(e)}")
    else:
        st.warning("跌停股票池Excel文件不存在")

# 板块异动可视化
elif page == "板块异动":
    st.header("🔔 板块异动可视化")
    
    excel_file = Path('data/板块异动.xlsx')
    if excel_file.exists():
        try:
            df = pd.read_excel(excel_file, sheet_name='板块异动')
            
            if len(df) > 0:
                latest_date = df['日期'].max()
                df_latest = df[df['日期'] == latest_date].copy()
                
                st.info(f"显示日期: {latest_date}，共 {len(df_latest)} 个板块异动")
                
                # 异动总次数TOP 20
                st.subheader("🔔 板块异动总次数TOP 20")
                top_changes = df_latest.nlargest(20, '板块异动总次数')
                fig_bar = px.bar(
                    top_changes,
                    x='板块名称',
                    y='板块异动总次数',
                    title="板块异动总次数TOP 20",
                    labels={'板块名称': '板块', '板块异动总次数': '异动次数'},
                    color='涨跌幅(%)',
                    color_continuous_scale='RdYlGn'
                )
                fig_bar.update_xaxes(tickangle=45)
                st.plotly_chart(fig_bar, use_container_width=True)
                
                # 数据表格
                st.subheader("📋 完整数据")
                st.dataframe(df_latest, use_container_width=True, height=400)
            else:
                st.warning("Excel文件中没有数据")
        except Exception as e:
            st.error(f"读取Excel失败: {str(e)}")
    else:
        st.warning("板块异动Excel文件不存在")

# 交易复盘可视化
elif page == "交易复盘":
    st.header("📝 交易复盘可视化")
    
    try:
        from services.trading_review_service import TradingReviewService
        
        db = SessionLocal()
        # 获取所有记录
        reviews = TradingReviewService.get_all_reviews(db)
        db.close()
        
        if reviews:
            df = pd.DataFrame([r.to_dict() for r in reviews])
            
            # 统计信息
            db = SessionLocal()
            stats = TradingReviewService.get_statistics(db)
            db.close()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("总记录数", stats['totalRecords'])
            with col2:
                st.metric("总盈亏", f"{stats['totalProfit']:.2f}元")
            with col3:
                st.metric("盈利次数", stats['winCount'])
            with col4:
                st.metric("亏损次数", stats['lossCount'])
            
            # 盈亏分布
            if 'profit' in df.columns and df['profit'].notna().any():
                st.subheader("💰 盈亏分布")
                profit_df = df[df['profit'].notna()]
                fig_hist = px.histogram(
                    profit_df,
                    x='profit',
                    nbins=30,
                    title="盈亏分布直方图",
                    labels={'profit': '盈亏金额(元)', 'count': '交易次数'}
                )
                st.plotly_chart(fig_hist, use_container_width=True)
            
            # 数据表格
            st.subheader("📋 完整数据")
            st.dataframe(df, use_container_width=True, height=400)
        else:
            st.info("暂无交易复盘记录")
    except Exception as e:
        st.error(f"读取数据失败: {str(e)}")
"""
# 页脚已移除

