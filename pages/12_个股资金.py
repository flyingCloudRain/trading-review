#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
个股资金页面 - 显示个股资金流数据
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import sys
from datetime import date, datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 尝试导入数据库模块
try:
    from database.db import SessionLocal
    from services.stock_fund_flow_history_service import StockFundFlowHistoryService
    from utils.time_utils import get_utc8_date
    from utils.focused_stocks import get_focused_stocks
    import akshare as ak
    DB_AVAILABLE = True
except (ValueError, RuntimeError) as e:
    DB_AVAILABLE = False
    DB_ERROR = str(e)
except Exception as e:
    DB_AVAILABLE = False
    DB_ERROR = f"数据库连接错误: {str(e)}"

st.set_page_config(
    page_title="个股资金",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 统一标题样式
st.markdown("""
    <style>
    .main-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
    }
    .section-header {
        font-size: 1rem;
        font-weight: 600;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        background: transparent;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">个股资金</h1>', unsafe_allow_html=True)

# 检查数据库配置
if not DB_AVAILABLE:
    st.error(f"数据库连接失败: {DB_ERROR}")
    st.info("请检查数据库配置，详细说明请查看 SUPABASE_SETUP.md")
    st.stop()

# ==================== 资金流数据 ====================
st.markdown('<h2 class="section-header">个股资金流数据</h2>', unsafe_allow_html=True)

# 日期选择
today = get_utc8_date()
selected_date = st.date_input(
    "选择日期",
    value=today,
    max_value=today,
    help="选择要查看的日期"
)

# 获取关注股票列表（用于筛选，如果有的话）
focused_stocks = get_focused_stocks()

# 如果有关注股票，提供筛选选项
if focused_stocks:
    filter_option = st.radio(
        "数据筛选",
        options=['全部数据', '仅关注股票'],
        index=0,
        horizontal=True,
        help="选择要显示的数据范围"
    )
else:
    filter_option = '全部数据'

# 显示资金流数据
db = SessionLocal()
try:
    # 获取选中日期的所有股票资金流数据
    fund_flows = StockFundFlowHistoryService.get_fund_flow_by_date(db, selected_date)
    
    if not fund_flows:
        st.info(f"{selected_date} 暂无资金流数据")
    else:
        # 转换为DataFrame
        df_data = []
        for ff in fund_flows:
            # 根据筛选选项决定是否包含
            if filter_option == '全部数据' or ff['stockCode'] in focused_stocks:
                df_data.append({
                    '股票代码': ff['stockCode'],
                    '股票简称': ff.get('stockName', '-'),
                    '最新价': ff.get('latestPrice'),
                    '涨跌幅(%)': ff.get('changePercent'),
                    '换手率(%)': ff.get('turnoverRate'),
                    '流入资金(元)': ff.get('inflow'),
                    '流出资金(元)': ff.get('outflow'),
                    '净额(元)': ff.get('netAmount'),
                    '成交额(元)': ff.get('turnover'),
                })
        
        if df_data:
            df = pd.DataFrame(df_data)
            
            # 格式化显示
            def format_amount(val):
                if pd.isna(val) or val is None:
                    return "-"
                if abs(val) >= 100000000:
                    return f"{val/100000000:.2f}亿"
                elif abs(val) >= 10000:
                    return f"{val/10000:.2f}万"
                else:
                    return f"{val:.2f}"
            
            # 格式化百分比
            def format_percent(val):
                if pd.isna(val) or val is None:
                    return "-"
                return f"{val:.2f}%"
            
            # 格式化价格
            def format_price(val):
                if pd.isna(val) or val is None:
                    return "-"
                return f"{val:.2f}"
            
            # 应用格式化
            for col in ['流入资金(元)', '流出资金(元)', '净额(元)', '成交额(元)']:
                if col in df.columns:
                    df[col] = df[col].apply(format_amount)
            
            for col in ['涨跌幅(%)', '换手率(%)']:
                if col in df.columns:
                    df[col] = df[col].apply(format_percent)
            
            if '最新价' in df.columns:
                df['最新价'] = df['最新价'].apply(format_price)
            
            # 显示统计信息
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            with col_stat1:
                st.metric("总记录数", len(df_data))
            with col_stat2:
                if filter_option == '全部数据':
                    st.metric("筛选", "全部数据")
                else:
                    filtered_count = len([d for d in df_data if d['股票代码'] in focused_stocks])
                    st.metric("筛选", f"关注股票 ({filtered_count} 只)")
            with col_stat3:
                # 计算净流入总额
                total_net = sum([d['净额(元)'] for d in df_data if d['净额(元)'] and isinstance(d['净额(元)'], (int, float))])
                if total_net >= 100000000:
                    net_display = f"{total_net/100000000:.2f}亿"
                elif total_net >= 10000:
                    net_display = f"{total_net/10000:.2f}万"
                else:
                    net_display = f"{total_net:.2f}"
                st.metric("净流入总额", net_display)
            
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            if filter_option == '全部数据':
                st.info(f"{selected_date} 暂无资金流数据")
            else:
                st.info(f"{selected_date} 暂无关注股票的资金流数据")

finally:
    db.close()

# 手动刷新按钮
st.markdown("---")
col_refresh1, col_refresh2 = st.columns([1, 3])
with col_refresh1:
    if st.button("刷新今日数据", type="primary", use_container_width=True):
        with st.spinner("正在刷新资金流数据..."):
            db = SessionLocal()
            try:
                from services.stock_fund_flow_history_service import StockFundFlowHistoryService
                # 获取所有需要刷新的股票（关注股票 + 交易过的股票）
                from services.trading_review_service import TradingReviewService
                all_reviews = TradingReviewService.get_all_reviews(db)
                traded_stocks = list(set([r.stock_code for r in all_reviews if r.stock_code]))
                all_stocks = list(set(focused_stocks + traded_stocks))
                
                if all_stocks:
                    results = StockFundFlowHistoryService.save_multiple_stocks_fund_flow(
                        db=db,
                        stock_codes=all_stocks,
                        target_date=today
                    )
                    success_count = sum(1 for success in results.values() if success)
                    st.success(f"成功刷新 {success_count}/{len(all_stocks)} 只股票的资金流数据")
                else:
                    st.warning("没有需要刷新的股票，请先添加关注股票或进行交易")
                st.rerun()
            except Exception as e:
                st.error(f"刷新失败: {str(e)}")
            finally:
                db.close()

