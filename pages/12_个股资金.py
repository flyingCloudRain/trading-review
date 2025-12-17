#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
个股资金页面 - 显示个股资金流数据（完整版）
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
from datetime import date, datetime, timedelta

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 尝试导入数据库模块
try:
    from database.db import SessionLocal
    from services.stock_fund_flow_history_service import StockFundFlowHistoryService
    from utils.time_utils import get_utc8_date
    from utils.focused_stocks import get_focused_stocks
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

# 应用统一样式
from utils.page_styles import apply_common_styles
apply_common_styles()

st.markdown('<h1 class="main-header">💰 个股资金流分析</h1>', unsafe_allow_html=True)

# 检查数据库配置
if not DB_AVAILABLE:
    st.error(f"❌ 数据库连接失败: {DB_ERROR}")
    st.info("请检查数据库配置，详细说明请查看 SUPABASE_SETUP.md")
    st.stop()

col_query1, col_query2, col_query3 = st.columns([2, 2, 2])

with col_query1:
    today = get_utc8_date()
    selected_date = st.date_input(
        "📅 选择日期",
        value=today,
        max_value=today,
        help="选择要查看的日期"
    )

with col_query2:
    # 获取关注股票列表
    focused_stocks = get_focused_stocks()
    filter_option = st.selectbox(
        "🔎 数据筛选",
        options=['全部数据', '仅关注股票', '仅交易过的股票'],
        index=0,
        help="选择要显示的数据范围"
    )

with col_query3:
    sort_option = st.selectbox(
        "📊 排序方式",
        options=[
            '净额降序', '净额升序',
            '流入资金降序', '流入资金升序',
            '流出资金降序', '流出资金升序',
            '涨跌幅降序', '涨跌幅升序',
            '成交额降序', '成交额升序'
        ],
        index=0,
        help="选择数据排序方式"
    )

# 股票代码/名称搜索
stock_search = st.text_input(
    "🔍 股票搜索",
    placeholder="输入股票代码（如：000001）或股票名称（如：平安银行）",
    help="可以输入股票代码或股票名称进行搜索，支持模糊匹配"
)

# ==================== 数据查询 ====================
db = SessionLocal()
try:
    # 获取选中日期的所有股票资金流数据
    fund_flows = StockFundFlowHistoryService.get_fund_flow_by_date(db, selected_date)
    
    if not fund_flows:
        st.warning(f"📭 {selected_date} 暂无资金流数据")
        st.info("💡 提示：可以点击下方的'刷新今日数据'按钮获取最新数据")
    else:
        # 转换为DataFrame
        df_data = []
        for ff in fund_flows:
            df_data.append({
                '股票代码': ff['stockCode'],
                '股票简称': ff.get('stockName') or '-',
                '最新价': ff.get('latestPrice'),
                '涨跌幅(%)': ff.get('changePercent'),
                '换手率(%)': ff.get('turnoverRate'),
                '流入资金(元)': ff.get('inflow'),
                '流出资金(元)': ff.get('outflow'),
                '净额(元)': ff.get('netAmount'),
                '成交额(元)': ff.get('turnover'),
            })
        
        df = pd.DataFrame(df_data)
        
        # ==================== 数据筛选 ====================
        # 按筛选选项过滤
        if filter_option == '仅关注股票':
            if focused_stocks:
                df = df[df['股票代码'].isin(focused_stocks)]
            else:
                st.warning("⚠️ 没有关注股票，请先添加关注股票")
                df = pd.DataFrame()
        elif filter_option == '仅交易过的股票':
            from services.trading_review_service import TradingReviewService
            all_reviews = TradingReviewService.get_all_reviews(db)
            traded_stocks = list(set([r.stock_code for r in all_reviews if r.stock_code]))
            if traded_stocks:
                df = df[df['股票代码'].isin(traded_stocks)]
            else:
                st.warning("⚠️ 没有交易过的股票")
                df = pd.DataFrame()
        
        # 股票代码/名称搜索
        if stock_search:
            search_term = stock_search.strip()
            # 判断是代码还是名称
            if search_term.isdigit():
                # 如果是纯数字，按代码搜索（补齐6位）
                search_code = search_term.zfill(6)
                df = df[df['股票代码'].str.contains(search_code, na=False)]
            else:
                # 如果是非数字，按名称搜索（支持模糊匹配）
                df = df[df['股票简称'].str.contains(search_term, na=False, case=False)]
        
        if not df.empty:
            # ==================== 数据排序 ====================
            # 保存原始数值用于排序（格式化前）
            df['_净额_原始'] = df['净额(元)']
            df['_流入_原始'] = df['流入资金(元)']
            df['_流出_原始'] = df['流出资金(元)']
            df['_涨跌幅_原始'] = df['涨跌幅(%)']
            df['_成交额_原始'] = df['成交额(元)']
            
            if '净额降序' in sort_option:
                df = df.sort_values('_净额_原始', ascending=False, na_position='last')
            elif '净额升序' in sort_option:
                df = df.sort_values('_净额_原始', ascending=True, na_position='last')
            elif '流入资金降序' in sort_option:
                df = df.sort_values('_流入_原始', ascending=False, na_position='last')
            elif '流入资金升序' in sort_option:
                df = df.sort_values('_流入_原始', ascending=True, na_position='last')
            elif '流出资金降序' in sort_option:
                df = df.sort_values('_流出_原始', ascending=False, na_position='last')
            elif '流出资金升序' in sort_option:
                df = df.sort_values('_流出_原始', ascending=True, na_position='last')
            elif '涨跌幅降序' in sort_option:
                df = df.sort_values('_涨跌幅_原始', ascending=False, na_position='last')
            elif '涨跌幅升序' in sort_option:
                df = df.sort_values('_涨跌幅_原始', ascending=True, na_position='last')
            elif '成交额降序' in sort_option:
                df = df.sort_values('_成交额_原始', ascending=False, na_position='last')
            elif '成交额升序' in sort_option:
                df = df.sort_values('_成交额_原始', ascending=True, na_position='last')
            
            # ==================== 统计信息 ====================
            st.markdown('<h2 class="section-header">📊 统计信息</h2>', unsafe_allow_html=True)
            
            # 计算统计数据
            total_count = len(df)
            total_inflow = df['_流入_原始'].sum() if df['_流入_原始'].notna().any() else 0
            total_outflow = df['_流出_原始'].sum() if df['_流出_原始'].notna().any() else 0
            total_net = df['_净额_原始'].sum() if df['_净额_原始'].notna().any() else 0
            total_turnover = df['_成交额_原始'].sum() if df['_成交额_原始'].notna().any() else 0
            
            # 格式化函数
            def format_amount(val):
                if pd.isna(val) or val is None or val == 0:
                    return "0"
                abs_val = abs(val)
                if abs_val >= 100000000:
                    return f"{val/100000000:.2f}亿"
                elif abs_val >= 10000:
                    return f"{val/10000:.2f}万"
                else:
                    return f"{val:.2f}"
            
            # 显示统计卡片
            col_stat1, col_stat2, col_stat3, col_stat4, col_stat5 = st.columns(5)
            
            with col_stat1:
                st.metric("📈 总记录数", f"{total_count:,}")
            
            with col_stat2:
                st.metric("💰 总流入", format_amount(total_inflow))
            
            with col_stat3:
                st.metric("💸 总流出", format_amount(total_outflow))
            
            with col_stat4:
                net_color = "normal" if total_net >= 0 else "inverse"
                st.metric("📊 净流入", format_amount(total_net), delta=None)
            
            with col_stat5:
                st.metric("💵 总成交额", format_amount(total_turnover))
            
            
            # 准备图表数据（取前20名）
            df_chart = df.head(20).copy()
            
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                # 净流入TOP 20
                if df_chart['_净额_原始'].notna().any():
                    df_chart_sorted = df_chart.sort_values('_净额_原始', ascending=True, na_position='last')
                    fig_net = px.bar(
                        df_chart_sorted,
                        x='_净额_原始',
                        y='股票简称',
                        orientation='h',
                        labels={'_净额_原始': '净流入(元)', '股票简称': '股票名称'},
                        title="净流入TOP 20",
                        color='_净额_原始',
                        color_continuous_scale='RdYlGn',
                        text='_净额_原始'
                    )
                    fig_net.update_traces(
                        texttemplate='%{text:,.0f}',
                        textposition='outside',
                        hovertemplate='<b>%{y}</b><br>净流入: %{x:,.0f}元<extra></extra>'
                    )
                    fig_net.update_layout(
                        height=600,
                        showlegend=False,
                        coloraxis_showscale=False,
                        yaxis={'categoryorder': 'total ascending'},
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig_net, use_container_width=True)
            
            with col_chart2:
                # 流入流出对比
                if df_chart['_流入_原始'].notna().any() and df_chart['_流出_原始'].notna().any():
                    df_compare = df_chart[['股票简称', '_流入_原始', '_流出_原始']].copy()
                    df_compare = df_compare.sort_values('_流入_原始', ascending=True, na_position='last')
                    
                    fig_compare = go.Figure()
                    
                    fig_compare.add_trace(go.Bar(
                        name='流入',
                        x=df_compare['_流入_原始'],
                        y=df_compare['股票简称'],
                        orientation='h',
                        marker_color='#2ca02c',
                        text=df_compare['_流入_原始'],
                        texttemplate='%{text:,.0f}',
                        textposition='outside'
                    ))
                    
                    fig_compare.add_trace(go.Bar(
                        name='流出',
                        x=-df_compare['_流出_原始'],
                        y=df_compare['股票简称'],
                        orientation='h',
                        marker_color='#d62728',
                        text=df_compare['_流出_原始'],
                        texttemplate='%{text:,.0f}',
                        textposition='outside'
                    ))
                    
                    fig_compare.update_layout(
                        title="流入流出对比（TOP 20）",
                        barmode='overlay',
                        height=600,
                        xaxis_title="金额(元)",
                        yaxis_title="股票名称",
                        yaxis={'categoryorder': 'total ascending'},
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        hovermode='y unified'
                    )
                    st.plotly_chart(fig_compare, use_container_width=True)
            
            # ==================== 数据表格 ====================
            st.markdown('<h2 class="section-header">📋 详细数据</h2>', unsafe_allow_html=True)
            
            # 格式化显示数据
            df_display = df.copy()
            
            # 格式化金额
            for col in ['流入资金(元)', '流出资金(元)', '净额(元)', '成交额(元)']:
                if col in df_display.columns:
                    df_display[col] = df_display[col].apply(format_amount)
            
            # 格式化百分比
            def format_percent(val):
                if pd.isna(val) or val is None:
                    return "-"
                return f"{val:.2f}%"
            
            for col in ['涨跌幅(%)', '换手率(%)']:
                if col in df_display.columns:
                    df_display[col] = df_display[col].apply(format_percent)
            
            # 格式化价格
            def format_price(val):
                if pd.isna(val) or val is None:
                    return "-"
                return f"{val:.2f}"
            
            if '最新价' in df_display.columns:
                df_display['最新价'] = df_display['最新价'].apply(format_price)
            
            # 删除辅助列
            df_display = df_display.drop(columns=[col for col in df_display.columns if col.startswith('_')])
            
            # 显示前20条记录
            df_display = df_display.head(20)
            st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True,
                height=600
            )
            
            # 导出功能
            st.markdown("---")
            col_export1, col_export2 = st.columns([1, 4])
            with col_export1:
                # 准备导出数据（使用原始数值）
                df_export = df.copy()
                df_export = df_export.drop(columns=[col for col in df_export.columns if col.startswith('_')])
                csv = df_export.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 导出CSV",
                    data=csv,
                    file_name=f"个股资金流_{selected_date}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        else:
            st.info(f"📭 {selected_date} 没有符合条件的数据")

finally:
    db.close()

# ==================== 操作按钮 ====================
st.markdown("---")
st.markdown('<h2 class="section-header">🔄 数据操作</h2>', unsafe_allow_html=True)

col_action1, col_action2, col_action3 = st.columns([1, 1, 2])

with col_action1:
    if st.button("🔄 刷新今日数据", type="primary", use_container_width=True):
        with st.spinner("正在刷新资金流数据..."):
            db = SessionLocal()
            try:
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
                    st.success(f"✅ 成功刷新 {success_count}/{len(all_stocks)} 只股票的资金流数据")
                else:
                    st.warning("⚠️ 没有需要刷新的股票，请先添加关注股票或进行交易")
                st.rerun()
            except Exception as e:
                st.error(f"❌ 刷新失败: {str(e)}")
            finally:
                db.close()

with col_action2:
    if st.button("🔄 刷新所有股票", use_container_width=True):
        with st.spinner("正在从接口获取所有股票的资金流数据，这可能需要几分钟..."):
            db = SessionLocal()
            try:
                results = StockFundFlowHistoryService.save_all_stocks_fund_flow_from_individual(
                    db=db,
                    target_date=today
                )
                st.success(f"✅ 成功保存 {results['success_count']}/{results['total_count']} 只股票的资金流数据")
                st.rerun()
            except Exception as e:
                st.error(f"❌ 刷新失败: {str(e)}")
            finally:
                db.close()

with col_action3:
    st.info("💡 **提示**: 刷新今日数据会更新关注股票和交易过的股票；刷新所有股票会从接口获取全部股票数据（约5000+只）")
