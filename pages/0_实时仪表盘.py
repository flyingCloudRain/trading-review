#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时仪表盘页面 - 从akshare接口获取最新实时数据
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
from pathlib import Path
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import akshare as ak
import time

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.db import SessionLocal
from services.sector_history_service import SectorHistoryService
from services.sector_service import SectorService
from services.concept_service import ConceptService
from services.zt_pool_history_service import ZtPoolHistoryService
from services.zt_pool_service import ZtPoolService
from services.dtgc_pool_history_service import DtgcPoolHistoryService
from services.dtgc_service import DtgcService
from services.zbgc_pool_history_service import ZbgcPoolHistoryService
from services.zbgc_service import ZbgcService
from services.index_history_service import IndexHistoryService
from services.stock_index_service import StockIndexService
from utils.time_utils import get_data_date, get_utc8_date, get_utc8_date_compact_str
from utils.focused_indices import get_focused_indices

st.set_page_config(
    page_title="实时仪表盘",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 应用统一样式（包含仪表盘特定样式）
from utils.page_styles import apply_common_styles, get_dashboard_specific_styles
apply_common_styles(additional_styles=get_dashboard_specific_styles())

# 页面标题
st.markdown('<h1 class="main-header">⚡ 实时仪表盘</h1>', unsafe_allow_html=True)

# 实时仪表盘：固定使用最新数据日期
today = get_utc8_date()
data_date = today

# 加载数据 - 实时仪表盘使用akshare接口（并行优化）
@st.cache_data(ttl=60)  # 实时数据缓存1分钟
def load_realtime_data():
    """从akshare接口并行加载实时数据，提升查询效率"""
    date_str = get_utc8_date_compact_str()
    results = {
        'industry_sectors': [],
        'concept_sectors': [],
        'zt_pool': [],
        'dt_pool': [],
        'zb_pool': [],
        'indices': [],
        'source': 'realtime',
        'errors': {}
    }
    
    # 定义并行任务函数
    def fetch_industry_sectors():
        try:
            return ('industry_sectors', SectorService.get_industry_summary(), None)
        except Exception as e:
            return ('industry_sectors', [], str(e))
    
    def fetch_concept_sectors():
        try:
            return ('concept_sectors', ConceptService.get_concept_summary(), None)
        except Exception as e:
            return ('concept_sectors', [], str(e))
    
    def fetch_zt_pool():
        try:
            return ('zt_pool', ZtPoolService.get_zt_pool(date=date_str), None)
        except Exception as e:
            return ('zt_pool', [], str(e))
    
    def fetch_dt_pool():
        try:
            return ('dt_pool', DtgcService.get_dtgc_pool(date=date_str), None)
        except Exception as e:
            return ('dt_pool', [], str(e))
    
    def fetch_zb_pool():
        try:
            return ('zb_pool', ZbgcService.get_zbgc_pool(date=date_str), None)
        except Exception as e:
            return ('zb_pool', [], str(e))
    
    def fetch_indices():
        try:
            return ('indices', StockIndexService.get_index_spot_sina(), None)
        except Exception as e:
            return ('indices', [], str(e))
    
    # 并行执行所有数据获取任务
    tasks = [
        fetch_industry_sectors,
        fetch_concept_sectors,
        fetch_zt_pool,
        fetch_dt_pool,
        fetch_zb_pool,
        fetch_indices
    ]
    
    try:
        with ThreadPoolExecutor(max_workers=6) as executor:
            # 提交所有任务
            future_to_task = {executor.submit(task): task for task in tasks}
            
            # 收集结果
            for future in as_completed(future_to_task):
                try:
                    result = future.result()
                    key, value, error = result
                    results[key] = value if value is not None else []
                    if error:
                        results['errors'][key] = error
                except Exception as e:
                    # 处理任务执行异常
                    task_name = future_to_task[future].__name__
                    results['errors'][task_name] = str(e)
        
        # 如果有错误，记录但不阻止返回
        if results['errors']:
            error_msg = "; ".join([f"{k}: {v}" for k, v in results['errors'].items()])
            results['error'] = f"部分数据获取失败: {error_msg}"
        
        return results
    except Exception as e:
        return {
            'industry_sectors': [],
            'concept_sectors': [],
            'zt_pool': [],
            'dt_pool': [],
            'zb_pool': [],
            'indices': [],
            'source': 'realtime',
            'error': str(e)
        }


# 加载实时数据
try:
    # 实时仪表盘：从akshare接口获取数据
    with st.spinner("⚡ 正在从实时接口获取最新数据..."):
        data = load_realtime_data()
        if 'error' in data:
            st.error(f"❌ 获取实时数据失败: {data['error']}")
            st.info("💡 提示：实时数据获取失败，可能是网络问题或API接口异常。请稍后重试。")
            st.stop()
            return
    
    industry_sectors = data['industry_sectors']
    concept_sectors = data['concept_sectors']
    zt_pool = data['zt_pool']
    dt_pool = data['dt_pool']
    zb_pool = data['zb_pool']
    indices = data['indices']
    
    # 合并所有板块数据（用于兼容旧代码）
    sectors = (industry_sectors or []) + (concept_sectors or [])
    
    # 检查数据是否为空（显示详细诊断信息）
    if not industry_sectors and not concept_sectors and not zt_pool and not dt_pool and not zb_pool and not indices:
        # 检查是否为交易日
        from tasks.sector_scheduler import SectorScheduler
        scheduler = SectorScheduler()
        is_trading = scheduler._is_trading_day(data_date)
        
        # 显示诊断信息
        st.warning(f"⚠️ {data_date} 暂无数据")
        
        # 显示详细诊断信息
        with st.expander("📊 查看数据诊断信息"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"- 行业板块数据: {len(industry_sectors) if industry_sectors else 0} 条")
                st.write(f"- 概念板块数据: {len(concept_sectors) if concept_sectors else 0} 条")
                st.write(f"- 涨停股票池: {len(zt_pool) if zt_pool else 0} 条")
                st.write(f"- 跌停股票池: {len(dt_pool) if dt_pool else 0} 条")
            with col2:
                st.write(f"- 炸板股票池: {len(zb_pool) if zb_pool else 0} 条")
                st.write(f"- 指数数据: {len(indices) if indices else 0} 条")
                st.write(f"- 查询日期: {data_date}")
                st.write(f"- 是否为交易日: {'是' if is_trading else '否'}")
        
        # 根据情况提供不同的提示
        if data_date == today:
            if not is_trading:
                st.info("💡 今天不是交易日，无法获取实时数据。请选择其他日期查看历史数据。")
        else:
            if not is_trading:
                st.info("💡 该日期不是交易日，无法获取数据。请选择其他交易日查看数据。")
                st.stop()
        
    # ========== 创建Tab页 ==========
    tab_overview, tab_zt, tab_fund = st.tabs(["📊 市场概况", "📊 股票池", "💰 个股资金流"])
    
    # Tab 1: 市场概况
    with tab_overview:
        # ========== 市场概况 ==========
        st.markdown('<h2 class="section-header">📊 市场概况</h2>', unsafe_allow_html=True)
    
    # 先计算重点关注指数数据（用于后续统计）
    focused_indices_codes = get_focused_indices()
    focused_indices_data = []
    
    if focused_indices_codes and indices:
        from services.stock_index_service import StockIndexService
        
        # 标准化关注指数代码为6位格式
        focused_codes_6digit = set()
        for focused_code in focused_indices_codes:
            code_6digit = StockIndexService.normalize_index_code(focused_code)
            focused_codes_6digit.add(code_6digit)
        
        # 匹配重点关注指数
        matched_codes = set()
        for idx in indices:
            db_code = idx.get('code', '')
            db_code_6digit = StockIndexService.normalize_index_code(db_code)
            
            if db_code_6digit in focused_codes_6digit:
                if db_code_6digit not in matched_codes:
                    focused_indices_data.append(idx)
                    matched_codes.add(db_code_6digit)
    
    # 计算重点指数总数
    index_total = len(focused_indices_data) if focused_indices_data else 0
    
    # 如果指数数据为空，显示提示信息（但不阻止页面继续显示其他数据）
    if not indices:
        st.warning(f"⚠️ {data_date} 暂无指数数据")
        # 检查是否为交易日
        from tasks.sector_scheduler import SectorScheduler
        scheduler = SectorScheduler()
        is_trading = scheduler._is_trading_day(data_date)
        
        if not is_trading:
            st.info("💡 提示：该日期不是交易日，无法获取指数数据。请选择其他交易日查看数据。")
    
    # 获取主要指数数据（上证指数、深证指数、创业板指）
    main_indices = {}
    main_index_codes = {
        '000001': '上证指数',
        '399106': '深证综指',
        '399006': '创业板指'
    }
    
    if indices:
        from services.stock_index_service import StockIndexService
        
        for idx in indices:
            db_code = idx.get('code', '')
            db_code_6digit = StockIndexService.normalize_index_code(db_code)
            
            # 尝试多种匹配方式
            matched_code = None
            if db_code_6digit in main_index_codes:
                matched_code = db_code_6digit
            elif db_code in main_index_codes:
                matched_code = db_code
            elif db_code.startswith('sz') or db_code.startswith('sh'):
                code_without_prefix = db_code[2:]
                if code_without_prefix in main_index_codes:
                    matched_code = code_without_prefix
            
            if matched_code:
                main_indices[matched_code] = {
                    'name': main_index_codes[matched_code],
                    'changePercent': idx.get('changePercent', 0),
                    'currentPrice': idx.get('currentPrice', 0)
                }
    
    # 如果数据库中没有找到某些指数，尝试从API实时获取
    missing_codes = [code for code in main_index_codes.keys() if code not in main_indices]
    if missing_codes:
        try:
            from services.stock_index_service import StockIndexService
            # 尝试从API获取缺失的指数（优先使用sina接口，数据更完整）
            try:
                all_indices = StockIndexService.get_index_spot_sina()
                for idx in all_indices:
                    db_code = idx.get('code', '')
                    db_code_6digit = StockIndexService.normalize_index_code(db_code)
                    
                    if db_code_6digit in missing_codes:
                        main_indices[db_code_6digit] = {
                            'name': main_index_codes[db_code_6digit],
                            'changePercent': idx.get('changePercent', 0),
                            'currentPrice': idx.get('currentPrice', 0)
                        }
                        missing_codes.remove(db_code_6digit)
                        if not missing_codes:
                            break
            except Exception as e:
                # 如果sina接口失败，尝试使用em接口作为备用
                try:
                    all_indices = StockIndexService.get_index_spot()
                    for idx in all_indices:
                        db_code = idx.get('code', '')
                        db_code_6digit = StockIndexService.normalize_index_code(db_code)
                        
                        if db_code_6digit in missing_codes:
                            main_indices[db_code_6digit] = {
                                'name': main_index_codes[db_code_6digit],
                                'changePercent': idx.get('changePercent', 0),
                                'currentPrice': idx.get('currentPrice', 0)
                            }
                            missing_codes.remove(db_code_6digit)
                            if not missing_codes:
                                break
                except Exception:
                    # API获取失败，忽略
                    pass
        except Exception:
            # 导入失败，忽略
            pass
    
    # 计算行业板块统计
    industry_up = len([s for s in industry_sectors if s.get('changePercent', 0) > 0]) if industry_sectors else 0
    industry_down = len([s for s in industry_sectors if s.get('changePercent', 0) < 0]) if industry_sectors else 0
    industry_net_inflow = sum([s.get('netInflow', 0) for s in industry_sectors if s.get('netInflow', 0) > 0]) if industry_sectors else 0
    industry_net_outflow = abs(sum([s.get('netInflow', 0) for s in industry_sectors if s.get('netInflow', 0) < 0])) if industry_sectors else 0
    
    # 计算概念板块统计
    concept_up = len([s for s in concept_sectors if s.get('changePercent', 0) > 0]) if concept_sectors else 0
    concept_down = len([s for s in concept_sectors if s.get('changePercent', 0) < 0]) if concept_sectors else 0
    concept_net_inflow = sum([s.get('netInflow', 0) for s in concept_sectors if s.get('netInflow', 0) > 0]) if concept_sectors else 0
    concept_net_outflow = abs(sum([s.get('netInflow', 0) for s in concept_sectors if s.get('netInflow', 0) < 0])) if concept_sectors else 0
    
    # 合并统计（用于兼容旧代码）
    sector_up = industry_up + concept_up
    sector_down = industry_down + concept_down
    sector_net_inflow = industry_net_inflow + concept_net_inflow
    sector_net_outflow = industry_net_outflow + concept_net_outflow
    
    # 股票池统计
    zt_count = len(zt_pool) if zt_pool else 0
    zb_count = len(zb_pool) if zb_pool else 0
    dt_count = len(dt_pool) if dt_pool else 0
    
        # 显示市场概况卡片（4列布局：主要指数、行业板块、概念板块、股票池）
        col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("#### 📈 主要指数")
        # 上证指数
        if '000001' in main_indices:
            idx = main_indices['000001']
            change_color = "🔴" if idx['changePercent'] < 0 else "🟢" if idx['changePercent'] > 0 else "⚪"
            st.metric(
                f"{change_color} {idx['name']}",
                f"{idx['currentPrice']:.2f}",
                delta=f"{idx['changePercent']:+.2f}%",
                delta_color="inverse" if idx['changePercent'] < 0 else "normal"
            )
        else:
            st.info("上证指数: 暂无数据")
        
        # 深证综指
        if '399106' in main_indices:
            idx = main_indices['399106']
            change_color = "🔴" if idx['changePercent'] < 0 else "🟢" if idx['changePercent'] > 0 else "⚪"
            st.metric(
                f"{change_color} {idx['name']}",
                f"{idx['currentPrice']:.2f}",
                delta=f"{idx['changePercent']:+.2f}%",
                delta_color="inverse" if idx['changePercent'] < 0 else "normal"
            )
        else:
            st.info("深证综指: 暂无数据")
        
        # 创业板指
        if '399006' in main_indices:
            idx = main_indices['399006']
            change_color = "🔴" if idx['changePercent'] < 0 else "🟢" if idx['changePercent'] > 0 else "⚪"
            st.metric(
                f"{change_color} {idx['name']}",
                f"{idx['currentPrice']:.2f}",
                delta=f"{idx['changePercent']:+.2f}%",
                delta_color="inverse" if idx['changePercent'] < 0 else "normal"
            )
        else:
            st.info("创业板指: 暂无数据")
    
    with col2:
        st.markdown("#### 🏢 行业板块统计")
        st.metric(
            "📈 上涨板块",
            f"{industry_up}",
            help="上涨行业板块数量"
        )
        st.metric(
            "📉 下跌板块",
            f"{industry_down}",
            help="下跌行业板块数量"
        )
        st.metric(
            "💰 资金净流入",
            f"{industry_net_inflow:.2f}亿元",
            help="行业板块资金净流入总额"
        )
        st.metric(
            "💸 资金净流出",
            f"{industry_net_outflow:.2f}亿元",
            help="行业板块资金净流出总额"
        )
    
    with col3:
            st.markdown("#### 💡 概念板块统计")
            st.metric(
                "📈 上涨概念",
                f"{concept_up}",
                help="上涨概念板块数量"
            )
            st.metric(
                "📉 下跌概念",
                f"{concept_down}",
                help="下跌概念板块数量"
            )
            st.metric(
                "💰 资金净流入",
                f"{concept_net_inflow:.2f}亿元",
                help="概念板块资金净流入总额"
            )
            st.metric(
                "💸 资金净流出",
                f"{concept_net_outflow:.2f}亿元",
                help="概念板块资金净流出总额"
            )
        
        with col4:
        st.markdown("#### 📊 股票池统计")
        st.metric(
            "📈 涨停股票",
            f"{zt_count}",
            help="涨停股票数量"
        )
        st.metric(
            "💥 炸板股票",
            f"{zb_count}",
            help="炸板股票数量"
        )
        st.metric(
            "📉 跌停股票",
            f"{dt_count}",
            help="跌停股票数量"
        )
    
    # 只统计重点关注指数（focused_indices_data 已在市场概况部分计算）
    index_up = len([i for i in focused_indices_data if i.get('changePercent', 0) > 0]) if focused_indices_data else 0
    index_down = len([i for i in focused_indices_data if i.get('changePercent', 0) < 0]) if focused_indices_data else 0
    
    # ========== 指数统计（重点关注指数） ==========
    if focused_indices_data:
        st.markdown('<h2 class="section-header">📊 重点指数统计</h2>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "📈 上涨指数",
                f"{index_up}",
                help="重点指数中上涨的数量"
            )
        
        with col2:
            st.metric(
                "📉 下跌指数",
                f"{index_down}",
                help="重点指数中下跌的数量"
            )
        
        with col3:
            flat_count = index_total - index_up - index_down
            st.metric(
                "➡️ 平盘指数",
                f"{flat_count}",
                help="重点指数中平盘的数量"
            )
        
        # 重点指数涨跌幅表格
        df_focused_indices = pd.DataFrame(focused_indices_data)
        
        # 定义显示顺序：上证指数、深证指数、创业板
        display_order = {
            '000001': 1,  # 上证指数
            '399106': 2,  # 深证综指（深证指数）
            '399006': 3,  # 创业板指
            '000016': 4,  # 上证50
            '000300': 5,  # 沪深300
            '000852': 6,  # 中证1000
            '000905': 7,  # 中证500
        }
        
        # 添加排序字段
        df_focused_indices['sort_order'] = df_focused_indices['code'].map(
            lambda x: display_order.get(x, 999)  # 未定义的指数排在最后
        )
        
        # 按显示顺序排序
        df_focused_indices = df_focused_indices.sort_values('sort_order', ascending=True).reset_index(drop=True)
        
        # 准备表格数据
        df_display = df_focused_indices[['name', 'code', 'currentPrice', 'changePercent', 'change']].copy()
        df_display.columns = ['指数名称', '指数代码', '最新价', '涨跌幅(%)', '涨跌额']
        
        # 保存原始涨跌幅用于样式判断（重置索引后，位置索引与DataFrame索引一致）
        change_percent_values = df_focused_indices['changePercent'].values
        
        # 格式化数值
        df_display['最新价'] = df_display['最新价'].apply(lambda x: f"{x:.2f}")
        df_display['涨跌幅(%)'] = df_display['涨跌幅(%)'].apply(lambda x: f"{x:+.2f}%")
        df_display['涨跌额'] = df_display['涨跌额'].apply(lambda x: f"{x:+.2f}")
        
        # 定义样式函数：上涨用红色背景，下跌用绿色背景（整行）
        def apply_cell_style(df):
            """对整行应用背景色：上涨红色背景，下跌绿色背景"""
            styles = pd.DataFrame('', index=df.index, columns=df.columns)
            # 对整行应用样式
            for idx in df.index:
                # 使用位置索引获取涨跌幅值（因为已经重置了索引）
                change_pct = change_percent_values[idx]
                if change_pct > 0:
                    # 上涨：红色背景 (#ef4444)，白色文字
                    for col in df.columns:
                        styles.loc[idx, col] = 'background-color: #ef4444; color: #ffffff;'
                elif change_pct < 0:
                    # 下跌：绿色背景 (#10b981)，白色文字
                    for col in df.columns:
                        styles.loc[idx, col] = 'background-color: #10b981; color: #ffffff;'
            return styles
        
        # 使用pandas Styler应用样式
        styled_df = df_display.style.apply(apply_cell_style, axis=None)
        
        # 显示样式化的表格
        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True
        )
    elif focused_indices_codes:
        st.markdown('<h2 class="section-header">📊 重点指数统计</h2>', unsafe_allow_html=True)
        st.warning("⚠️ 当前日期没有重点指数的数据")
    else:
        st.markdown('<h2 class="section-header">📊 重点指数统计</h2>', unsafe_allow_html=True)
        st.info("💡 当前未设置重点指数，请在「关注管理」页面添加关注指数")
    
    # ========== 板块数据统计 ==========
    # 行业板块数据统计
    if industry_sectors:
        st.markdown('<h2 class="section-header">🏢 行业板块数据统计</h2>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # 计算上涨板块占比
            industry_total = len(industry_sectors) if industry_sectors else 0
            industry_up_ratio = (industry_up / industry_total * 100) if industry_total > 0 else 0
            st.metric(
                "📈 上涨板块",
                f"{industry_up}",
                delta=f"{industry_up_ratio:.1f}%" if industry_total > 0 else None,
                help="所选日期的上涨行业板块数量及占比"
            )
        
        with col2:
            # 计算下跌板块占比
            industry_down_ratio = (industry_down / industry_total * 100) if industry_total > 0 else 0
            st.metric(
                "📉 下跌板块",
                f"{industry_down}",
                delta=f"{industry_down_ratio:.1f}%" if industry_total > 0 else None,
                delta_color="inverse",
                help="所选日期的下跌行业板块数量及占比"
            )
        
        with col3:
            st.metric(
                "💰 资金净流入",
                f"{industry_net_inflow:.2f}亿元",
                    delta="",  # 添加空delta以保持高度一致
                help="所选日期的行业板块资金净流入总额"
            )
        
        with col4:
            st.metric(
                "💸 资金净流出",
                f"{industry_net_outflow:.2f}亿元",
                    delta="",  # 添加空delta以保持高度一致
                delta_color="inverse",
                help="所选日期的行业板块资金净流出总额"
            )
        
        # 行业板块涨跌幅TOP 10
        if len(industry_sectors) > 0:
            df_industry = pd.DataFrame(industry_sectors)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 涨幅TOP 10
                top_up = df_industry.nlargest(10, 'changePercent')[['name', 'changePercent']]
                if not top_up.empty:
                    fig_up = px.bar(
                        top_up,
                        x='changePercent',
                        y='name',
                        orientation='h',
                        color='changePercent',
                        color_continuous_scale='Reds',
                        title='📈 行业板块涨幅TOP 10',
                        labels={'changePercent': '涨跌幅(%)', 'name': '板块名称'}
                    )
                    fig_up.update_layout(
                        yaxis={'categoryorder': 'total ascending'},
                        height=400,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        showlegend=False
                    )
                    st.plotly_chart(fig_up, use_container_width=True)
            
            with col2:
                # 跌幅TOP 10
                top_down = df_industry.nsmallest(10, 'changePercent')[['name', 'changePercent']]
                if not top_down.empty:
                    # 取绝对值用于排序，但显示原值
                    top_down_sorted = top_down.copy()
                    top_down_sorted['_abs_sort'] = top_down_sorted['changePercent'].abs()
                    top_down_sorted = top_down_sorted.nlargest(10, '_abs_sort')
                    
                    fig_down = px.bar(
                        top_down_sorted,
                        x='changePercent',
                        y='name',
                        orientation='h',
                        color='changePercent',
                        color_continuous_scale='Greens',
                        title='📉 行业板块跌幅TOP 10',
                        labels={'changePercent': '涨跌幅(%)', 'name': '板块名称'}
                    )
                    fig_down.update_layout(
                        yaxis={'categoryorder': 'total ascending'},
                        height=400,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        showlegend=False
                    )
                    st.plotly_chart(fig_down, use_container_width=True)
    
            # 资金净流入/流出TOP 10
            col3, col4 = st.columns(2)
            
            with col3:
                # 资金净流入TOP 10
                if 'netInflow' in df_industry.columns:
                    top_inflow = df_industry.nlargest(10, 'netInflow')[['name', 'netInflow']]
                    if not top_inflow.empty:
                        fig_inflow = px.bar(
                            top_inflow,
                            x='netInflow',
                            y='name',
                            orientation='h',
                            color='netInflow',
                            color_continuous_scale='Oranges',
                            title='💰 行业板块资金净流入TOP 10',
                            labels={'netInflow': '净流入(亿元)', 'name': '板块名称'}
                        )
                        fig_inflow.update_layout(
                            yaxis={'categoryorder': 'total ascending'},
                            height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                            showlegend=False
                        )
                        st.plotly_chart(fig_inflow, use_container_width=True)
            
            with col4:
                # 资金净流出TOP 10（取绝对值最大的）
                if 'netInflow' in df_industry.columns:
                    # 筛选净流出的板块（netInflow < 0）
                    outflow_sectors = df_industry[df_industry['netInflow'] < 0].copy()
                    if not outflow_sectors.empty:
                        outflow_sectors['abs_netInflow'] = outflow_sectors['netInflow'].abs()
                        top_outflow = outflow_sectors.nlargest(10, 'abs_netInflow')[['name', 'netInflow']]
                        if not top_outflow.empty:
                            fig_outflow = px.bar(
                                top_outflow,
                                x='netInflow',
                                y='name',
                                orientation='h',
                                color='netInflow',
                                color_continuous_scale='Blues',
                                title='💸 行业板块资金净流出TOP 10',
                                labels={'netInflow': '净流出(亿元)', 'name': '板块名称'}
                            )
                            fig_outflow.update_layout(
                                yaxis={'categoryorder': 'total ascending'},
                                height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                                showlegend=False
                            )
                            st.plotly_chart(fig_outflow, use_container_width=True)
    
    # 概念板块数据统计
    if concept_sectors:
        st.markdown('<h2 class="section-header">💡 概念板块数据统计</h2>', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                # 计算上涨概念占比
                concept_total = len(concept_sectors) if concept_sectors else 0
                concept_up_ratio = (concept_up / concept_total * 100) if concept_total > 0 else 0
                st.metric(
                    "📈 上涨概念",
                    f"{concept_up}",
                    delta=f"{concept_up_ratio:.1f}%" if concept_total > 0 else None,
                    help="所选日期的上涨概念板块数量及占比"
                )
            
            with col2:
                # 计算下跌概念占比
                concept_down_ratio = (concept_down / concept_total * 100) if concept_total > 0 else 0
                st.metric(
                    "📉 下跌概念",
                    f"{concept_down}",
                    delta=f"{concept_down_ratio:.1f}%" if concept_total > 0 else None,
                    delta_color="inverse",
                    help="所选日期的下跌概念板块数量及占比"
                )
            
            with col3:
                st.metric(
                    "💰 资金净流入",
                    f"{concept_net_inflow:.2f}亿元",
                    delta="",  # 添加空delta以保持高度一致
                    help="所选日期的概念板块资金净流入总额"
                )
            
            with col4:
                st.metric(
                    "💸 资金净流出",
                    f"{concept_net_outflow:.2f}亿元",
                    delta="",  # 添加空delta以保持高度一致
                    delta_color="inverse",
                    help="所选日期的概念板块资金净流出总额"
                )
        
        # 概念板块涨跌幅TOP 10
        if len(concept_sectors) > 0:
            df_concept = pd.DataFrame(concept_sectors)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 涨幅TOP 10
                top_up = df_concept.nlargest(10, 'changePercent')[['name', 'changePercent']]
                if not top_up.empty:
                    fig_up = px.bar(
                        top_up,
                        x='changePercent',
                        y='name',
                        orientation='h',
                        color='changePercent',
                        color_continuous_scale='Reds',
                        title='📈 概念板块涨幅TOP 10',
                        labels={'changePercent': '涨跌幅(%)', 'name': '概念名称'}
                    )
                    fig_up.update_layout(
                        yaxis={'categoryorder': 'total ascending'},
                        height=400,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        showlegend=False
                    )
                    st.plotly_chart(fig_up, use_container_width=True)
            
            with col2:
                # 跌幅TOP 10
                top_down = df_concept.nsmallest(10, 'changePercent')[['name', 'changePercent']]
                if not top_down.empty:
                    # 取绝对值用于排序，但显示原值
                    top_down_sorted = top_down.copy()
                    top_down_sorted['_abs_sort'] = top_down_sorted['changePercent'].abs()
                    top_down_sorted = top_down_sorted.nlargest(10, '_abs_sort')
                    
                    fig_down = px.bar(
                        top_down_sorted,
                        x='changePercent',
                        y='name',
                        orientation='h',
                        color='changePercent',
                        color_continuous_scale='Greens',
                        title='📉 概念板块跌幅TOP 10',
                        labels={'changePercent': '涨跌幅(%)', 'name': '概念名称'}
                    )
                    fig_down.update_layout(
                        yaxis={'categoryorder': 'total ascending'},
                        height=400,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        showlegend=False
                    )
                    st.plotly_chart(fig_down, use_container_width=True)
            
                # 资金净流入/流出TOP 10
            col3, col4 = st.columns(2)
            
            with col3:
                # 资金净流入TOP 10
                if 'netInflow' in df_concept.columns:
                    top_inflow = df_concept.nlargest(10, 'netInflow')[['name', 'netInflow']]
                    if not top_inflow.empty:
                        fig_inflow = px.bar(
                            top_inflow,
                            x='netInflow',
                            y='name',
                            orientation='h',
                            color='netInflow',
                            color_continuous_scale='Oranges',
                            title='💰 概念板块资金净流入TOP 10',
                            labels={'netInflow': '净流入(亿元)', 'name': '概念名称'}
                        )
                        fig_inflow.update_layout(
                            yaxis={'categoryorder': 'total ascending'},
                            height=400,
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            showlegend=False
                        )
                        st.plotly_chart(fig_inflow, use_container_width=True)
            
            with col4:
                # 资金净流出TOP 10（取绝对值最大的）
                if 'netInflow' in df_concept.columns:
                    # 筛选净流出的板块（netInflow < 0）
                    outflow_concepts = df_concept[df_concept['netInflow'] < 0].copy()
                    if not outflow_concepts.empty:
                        outflow_concepts['abs_netInflow'] = outflow_concepts['netInflow'].abs()
                        top_outflow = outflow_concepts.nlargest(10, 'abs_netInflow')[['name', 'netInflow']]
                        if not top_outflow.empty:
                            fig_outflow = px.bar(
                                top_outflow,
                                x='netInflow',
                                y='name',
                                orientation='h',
                                color='netInflow',
                                color_continuous_scale='Blues',
                                title='💸 概念板块资金净流出TOP 10',
                                labels={'netInflow': '净流出(亿元)', 'name': '概念名称'}
                            )
                            fig_outflow.update_layout(
                                yaxis={'categoryorder': 'total ascending'},
                                height=400,
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                showlegend=False
                            )
                            st.plotly_chart(fig_outflow, use_container_width=True)
    
    # Tab 2: 股票池（包括股票池统计和当日涨停股票详情）
    with tab_zt:
    # ========== 股票池统计 ==========
    st.markdown('<h2 class="section-header">📊 股票池统计</h2>', unsafe_allow_html=True)
    # 显示KPI卡片（统计数据已在市场概况部分计算）
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📈 涨停股票",
            f"{zt_count}",
            help="所选日期的涨停股票数量"
        )
    
    with col2:
        st.metric(
            "📉 跌停股票",
            f"{dt_count}",
            help="所选日期的跌停股票数量"
        )
    
    with col3:
        st.metric(
            "💥 炸板股票",
            f"{zb_count}",
            help="所选日期的炸板股票数量"
        )
    
    with col4:
        # 计算连板率（连板数>1的股票数 / 涨停股票总数）
        if zt_pool and zt_count > 0:
            df_zt = pd.DataFrame(zt_pool)
            if 'continuousBoards' in df_zt.columns:
                # 连板数大于1的股票数
                continuous_count = len(df_zt[df_zt['continuousBoards'] > 1])
                # 连板率 = 连板股票数 / 涨停股票总数 * 100%
                continuous_rate = (continuous_count / zt_count) * 100 if zt_count > 0 else 0
                st.metric(
                    "🔗 连板率",
                    f"{continuous_rate:.1f}%",
                    delta=f"{continuous_count}/{zt_count}",
                    help=f"连板股票数（连板数>1）占涨停股票总数的比例，共{continuous_count}只连板股票"
                )
            else:
                st.metric(
                    "🔗 连板率",
                    "N/A",
                    help="暂无连板数据"
                )
        else:
            st.metric(
                "🔗 连板率",
                "0%",
                help="暂无涨停股票数据"
            )
    
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
                                showgrid=True,
                                tickangle=-45  # 倾斜角度，避免日期重叠
                            ),
                            yaxis=dict(
                                title=dict(text="涨停股票数", font=dict(size=LINE_CHART_CONFIG['axis_title_font_size'])),
                                gridcolor=LINE_CHART_CONFIG['grid_color'],
                                gridwidth=LINE_CHART_CONFIG['grid_width'],
                                showgrid=True
                            ),
                            height=LINE_CHART_CONFIG['height'],
                            hovermode='x unified',
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1
                            )
                        )
                        
                        st.plotly_chart(fig_trend, use_container_width=True)
                else:
                    st.info("暂无趋势数据")
            else:
                st.info("暂无最近1个月的涨停股票数据")
        except Exception as e:
            db_trend.close()
            st.warning(f"⚠️ 获取趋势数据失败: {str(e)}")
    except Exception as e:
        st.warning(f"⚠️ 获取趋势数据失败: {str(e)}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if zt_pool:
            df_zt = pd.DataFrame(zt_pool)
            # 连板数统计
            if 'continuousBoards' in df_zt.columns:
                board_count = df_zt['continuousBoards'].value_counts().sort_index()
                fig_zt = px.bar(
                    x=board_count.index,
                    y=board_count.values,
                    title='📈 涨停股票连板数分布',
                    labels={'x': '连板数', 'y': '股票数量'},
                    color=board_count.values,
                    color_continuous_scale='Oranges'
                )
                fig_zt.update_layout(
                    height=300,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    showlegend=False,
                    coloraxis_showscale=False
                )
                st.plotly_chart(fig_zt, use_container_width=True)
            
            # 行业分布统计
            if 'industry' in df_zt.columns:
                # 统计行业分布 - 显示全部行业
                industry_count = df_zt['industry'].value_counts()  # 显示全部行业
                if not industry_count.empty:
                    # 转换为DataFrame用于绘图
                    df_industry = pd.DataFrame({
                        'industry': industry_count.index,
                        'count': industry_count.values
                    })
                    
                    # 使用横向柱状图展示行业分布
                    fig_industry = px.bar(
                        df_industry,
                        x='count',
                        y='industry',
                        orientation='h',
                        color='count',
                        color_continuous_scale='Oranges',
                        title='📊 涨停股票行业分布',
                        labels={'count': '股票数量', 'industry': '行业名称'}
                    )
                    fig_industry.update_traces(
                        text=df_industry['count'],
                        textposition='outside',
                        hovertemplate='<b>%{y}</b><br>数量: %{x}<extra></extra>'
                    )
                    # 根据行业数量动态调整高度
                    num_industries = len(df_industry)
                    chart_height = max(400, min(800, num_industries * 25))
                    fig_industry.update_layout(
                        yaxis={'categoryorder': 'total ascending'},
                        height=chart_height,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        showlegend=False
                    )
                    st.plotly_chart(fig_industry, use_container_width=True)
        else:
            st.info("📈 暂无涨停股票数据")
    
    with col2:
        if dt_pool:
            df_dt = pd.DataFrame(dt_pool)
            # 连续跌停数统计
            if 'continuousLimitDown' in df_dt.columns:
                limit_down_count = df_dt['continuousLimitDown'].value_counts().sort_index()
                fig_dt = px.bar(
                    x=limit_down_count.index,
                    y=limit_down_count.values,
                    title='📉 跌停股票连续跌停数分布',
                    labels={'x': '连续跌停数', 'y': '股票数量'},
                    color=limit_down_count.values,
                    color_continuous_scale='Reds'
                )
                fig_dt.update_layout(
                    height=300,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    showlegend=False,
                    coloraxis_showscale=False,
                    xaxis=dict(
                        tickformat='d',  # 使用整数格式
                        dtick=1  # 每个刻度间隔为1
                    )
                )
                st.plotly_chart(fig_dt, use_container_width=True)
            
            # 行业分布统计
            if 'industry' in df_dt.columns:
                # 统计行业分布
                industry_count = df_dt['industry'].value_counts().head(10)  # 取前10个行业
                if not industry_count.empty:
                    # 转换为DataFrame用于绘图
                    df_industry = pd.DataFrame({
                        'industry': industry_count.index,
                        'count': industry_count.values
                    })
                    
                    # 使用横向柱状图展示行业分布
                    fig_industry = px.bar(
                        df_industry,
                        x='count',
                        y='industry',
                        orientation='h',
                        color='count',
                        color_continuous_scale='Reds',
                        title='📊 跌停股票行业分布（TOP 10）',
                        labels={'count': '股票数量', 'industry': '行业名称'}
                    )
                    fig_industry.update_traces(
                        text=df_industry['count'],
                        textposition='outside',
                        hovertemplate='<b>%{y}</b><br>数量: %{x}<extra></extra>'
                    )
                    fig_industry.update_layout(
                        yaxis={'categoryorder': 'total ascending'},
                        height=400,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        showlegend=False
                    )
                    st.plotly_chart(fig_industry, use_container_width=True)
        else:
            st.info("📉 暂无跌停股票数据")
    
    with col3:
        if zb_pool:
            df_zb = pd.DataFrame(zb_pool)
            # 炸板次数统计
            if 'explosionCount' in df_zb.columns:
                explosion_count = df_zb['explosionCount'].value_counts().sort_index()
                fig_zb = px.bar(
                    x=explosion_count.index,
                    y=explosion_count.values,
                    title='💥 炸板股票炸板次数分布',
                    labels={'x': '炸板次数', 'y': '股票数量'},
                    color=explosion_count.values,
                    color_continuous_scale='Oranges'
                )
                fig_zb.update_layout(
                    height=300,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    showlegend=False,
                    coloraxis_showscale=False
                )
                st.plotly_chart(fig_zb, use_container_width=True)
        else:
            st.info("💥 暂无炸板股票数据")
    
        # ========== 当日涨停股票详情 ==========
        if zt_pool:
        st.markdown("---")
        st.markdown('<h2 class="section-header">📈 当日涨停股票详情</h2>', unsafe_allow_html=True)
        
        df_zt_display = pd.DataFrame(zt_pool)
        
        # 行业筛选功能
        selected_industry = None
        if 'industry' in df_zt_display.columns:
            # 获取所有唯一的行业列表（排除空值）
            industries = sorted([ind for ind in df_zt_display['industry'].unique() if pd.notna(ind) and str(ind).strip()])
            if industries:
                # 添加"全部"选项
                industry_options = ['全部'] + industries
                selected_industry = st.selectbox(
                    "🏢 筛选行业",
                    options=industry_options,
                    index=0,
                    help="选择要查看的行业，选择'全部'显示所有行业"
                )
                
                # 如果选择了具体行业，进行筛选
                if selected_industry != '全部':
                    df_zt_display = df_zt_display[df_zt_display['industry'] == selected_industry].copy()
                    if df_zt_display.empty:
                        st.info(f"📊 所选行业 '{selected_industry}' 暂无涨停股票数据")
                st.stop()
        
        # 准备显示的数据
        display_columns = []
        column_mapping = {}
        
        # 根据实际存在的列进行映射
        if 'code' in df_zt_display.columns:
            display_columns.append('code')
            column_mapping['code'] = '代码'
        if 'name' in df_zt_display.columns:
            display_columns.append('name')
            column_mapping['name'] = '名称'
        if 'changePercent' in df_zt_display.columns:
            display_columns.append('changePercent')
            column_mapping['changePercent'] = '涨跌幅(%)'
        if 'latestPrice' in df_zt_display.columns:
            display_columns.append('latestPrice')
            column_mapping['latestPrice'] = '最新价'
        if 'turnover' in df_zt_display.columns:
            display_columns.append('turnover')
            column_mapping['turnover'] = '成交额(亿元)'
        if 'circulatingMarketValue' in df_zt_display.columns:
            display_columns.append('circulatingMarketValue')
            column_mapping['circulatingMarketValue'] = '流通市值(亿元)'
        if 'turnoverRate' in df_zt_display.columns:
            display_columns.append('turnoverRate')
            column_mapping['turnoverRate'] = '换手率(%)'
        if 'sealingFunds' in df_zt_display.columns:
            display_columns.append('sealingFunds')
            column_mapping['sealingFunds'] = '封板资金(亿元)'
        if 'firstSealingTime' in df_zt_display.columns:
            display_columns.append('firstSealingTime')
            column_mapping['firstSealingTime'] = '首次封板时间'
        if 'lastSealingTime' in df_zt_display.columns:
            display_columns.append('lastSealingTime')
            column_mapping['lastSealingTime'] = '最后封板时间'
        if 'continuousBoards' in df_zt_display.columns:
            display_columns.append('continuousBoards')
            column_mapping['continuousBoards'] = '连板数'
        if 'industry' in df_zt_display.columns:
            display_columns.append('industry')
            column_mapping['industry'] = '所属行业'
        
        # 选择要显示的列
        df_display = df_zt_display[display_columns].copy() if display_columns else df_zt_display.copy()
        
        # 重命名列
        df_display = df_display.rename(columns=column_mapping)
        
        # 格式化数值列
        if '涨跌幅(%)' in df_display.columns:
            df_display['涨跌幅(%)'] = df_display['涨跌幅(%)'].apply(lambda x: f"{x:.2f}%")
        if '最新价' in df_display.columns:
            df_display['最新价'] = df_display['最新价'].apply(lambda x: f"{x:.2f}")
        if '成交额(亿元)' in df_display.columns:
            df_display['成交额(亿元)'] = df_display['成交额(亿元)'].apply(lambda x: f"{x:.2f}")
        if '流通市值(亿元)' in df_display.columns:
            df_display['流通市值(亿元)'] = df_display['流通市值(亿元)'].apply(lambda x: f"{x:.2f}")
        if '换手率(%)' in df_display.columns:
            df_display['换手率(%)'] = df_display['换手率(%)'].apply(lambda x: f"{x:.2f}%")
        if '封板资金(亿元)' in df_display.columns:
            df_display['封板资金(亿元)'] = df_display['封板资金(亿元)'].apply(lambda x: f"{x:.2f}")
        
        # 按连板数降序排序（如果有连板数列）
        if '连板数' in df_display.columns:
            df_display = df_display.sort_values('连板数', ascending=False)
        
            # 显示前20条记录
            df_display = df_display.head(20)
        st.dataframe(df_display, use_container_width=True, height=400)
        else:
            st.info("📈 暂无涨停股票数据")
    
    # Tab 3: 个股资金流（显示当日个股资金流入情况）
    with tab_fund:
        st.markdown('<h2 class="section-header">💰 个股资金流</h2>', unsafe_allow_html=True)
        
        # 搜索和筛选区域
        col_search1, col_search2 = st.columns([3, 1])
        
        with col_search1:
            # 股票代码搜索（可选）
            code_input = st.text_input(                "🔍 股票代码搜索（可选，留空显示全部）",
            value="",
                help="请输入6位股票代码进行筛选，留空则显示全部股票数据",
                placeholder="留空显示全部，或输入如：000001",
            key="fund_flow_stock_code"
                )
        
        with col_search2:
            # 排序选项
            sort_option = st.selectbox(
                "📊 排序方式",
                options=['净流入降序', '净流入升序', '流入资金降序', '流出资金降序', '成交额降序'],
                index=0,
                key="fund_flow_sort"
        )
        
        stock_code = None
        if code_input:
            code_input = code_input.strip()
            
            # 去除前缀
            if code_input.startswith('sh') or code_input.startswith('sz') or code_input.startswith('bj'):
                code_input = code_input[2:]
            
            # 验证是否为6位数字
            if code_input.isdigit() and len(code_input) == 6:
                stock_code = code_input
            elif code_input:
                st.error("❌ 请输入有效的6位股票代码")
        
        # 获取并显示资金流数据（无论是否输入股票代码都获取全部数据）
            try:
                # 获取即时资金流数据（带重试机制）
                with st.spinner("🔄 正在获取个股即时资金流数据..."):
                df_all_fund = None
                    max_retries = 3
                    retry_delay = 2
                    
                    for retry in range(max_retries):
                        try:
                        # 使用 stock_fund_flow_individual 接口获取所有股票的即时资金流数据
                        df_all_fund = ak.stock_fund_flow_individual(symbol="即时")
                            break  # 成功获取，跳出重试循环
                        except Exception as e:
                            if retry < max_retries - 1:
                                st.warning(f"⚠️ 获取即时资金流数据失败，{retry_delay}秒后重试... ({retry + 1}/{max_retries})")
                                time.sleep(retry_delay)
                                retry_delay *= 2  # 指数退避
                            else:
                                raise e
                
            if df_all_fund is None or df_all_fund.empty:
                st.warning(f"⚠️ 获取资金流数据失败")
                else:
                # 解析金额字符串（如 "7.60亿" -> 760000000）
                def parse_amount_str(amount_str):
                    """解析金额字符串，如 '7.60亿' -> 760000000, '16.31亿' -> 1631000000"""
                    if pd.isna(amount_str) or amount_str == '' or amount_str == '-':
                        return 0
                    try:
                        amount_str = str(amount_str).strip()
                        if '亿' in amount_str:
                            value = float(amount_str.replace('亿', ''))
                            return int(value * 100000000)
                        elif '万' in amount_str:
                            value = float(amount_str.replace('万', ''))
                            return int(value * 10000)
                        else:
                            return float(amount_str)
                    except:
                        return 0
                
                # 解析百分比字符串（如 "151.12%" -> 151.12）
                def parse_percent_str(percent_str):
                    """解析百分比字符串，如 '151.12%' -> 151.12"""
                    if pd.isna(percent_str) or percent_str == '' or percent_str == '-':
                        return 0
                    try:
                        percent_str = str(percent_str).strip().replace('%', '')
                        return float(percent_str)
                    except:
                        return 0
                
                # 处理数据：添加数值列用于排序
                df_display = df_all_fund.copy()
                
                # 如果输入了股票代码，进行筛选
                if stock_code:
                    stock_code_6digit = stock_code.zfill(6)
                    if '股票代码' in df_display.columns:
                        df_display = df_display[df_display['股票代码'].astype(str).str.zfill(6) == stock_code_6digit].copy()
                    else:
                        df_display = pd.DataFrame()
                    
                    if df_display.empty:
                        st.warning(f"⚠️ 未找到股票代码 {stock_code} 的资金流数据（该股票可能不在当前排行中）")            st.stop()
                
                # 添加数值列用于排序
                if '净额' in df_display.columns:
                    df_display['_净额数值'] = df_display['净额'].apply(parse_amount_str)
                if '流入资金' in df_display.columns:
                    df_display['_流入资金数值'] = df_display['流入资金'].apply(parse_amount_str)
                if '流出资金' in df_display.columns:
                    df_display['_流出资金数值'] = df_display['流出资金'].apply(parse_amount_str)
                if '成交额' in df_display.columns:
                    df_display['_成交额数值'] = df_display['成交额'].apply(parse_amount_str)
                
                # 根据排序选项排序
                if sort_option == '净流入降序' and '_净额数值' in df_display.columns:
                    df_display = df_display.sort_values('_净额数值', ascending=False)
                elif sort_option == '净流入升序' and '_净额数值' in df_display.columns:
                    df_display = df_display.sort_values('_净额数值', ascending=True)
                elif sort_option == '流入资金降序' and '_流入资金数值' in df_display.columns:
                    df_display = df_display.sort_values('_流入资金数值', ascending=False)
                elif sort_option == '流出资金降序' and '_流出资金数值' in df_display.columns:
                    df_display = df_display.sort_values('_流出资金数值', ascending=False)
                elif sort_option == '成交额降序' and '_成交额数值' in df_display.columns:
                    df_display = df_display.sort_values('_成交额数值', ascending=False)
                
                # 移除临时数值列
                df_display = df_display.drop(columns=[col for col in df_display.columns if col.startswith('_')], errors='ignore')
                
                # 统计信息
                total_count = len(df_display)
                if total_count > 0:
                    # 计算总净流入（需要重新解析）
                    total_net = sum([parse_amount_str(row.get('净额', 0)) for _, row in df_display.iterrows()])
                    total_inflow = sum([parse_amount_str(row.get('流入资金', 0)) for _, row in df_display.iterrows()])
                    total_outflow = sum([parse_amount_str(row.get('流出资金', 0)) for _, row in df_display.iterrows()])
                    
                    # 显示统计卡片
                    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                    
                    with col_stat1:
                        st.metric("📊 股票数量", f"{total_count}")
                    
                    with col_stat2:
                        st.metric(
                            "💰 总净流入",
                            f"{total_net/100000000:.2f}亿" if abs(total_net) >= 100000000 else f"{total_net/10000:.2f}万",
                            delta_color="normal" if total_net >= 0 else "inverse"
                        )
                    
                    with col_stat3:
                        st.metric(
                            "📈 总流入",
                            f"{total_inflow/100000000:.2f}亿" if abs(total_inflow) >= 100000000 else f"{total_inflow/10000:.2f}万"
                        )
                    
                    with col_stat4:
                        st.metric(
                            "📉 总流出",
                            f"{total_outflow/100000000:.2f}亿" if abs(total_outflow) >= 100000000 else f"{total_outflow/10000:.2f}万"
                        )
                
                # 显示数据表格（带分页）
                st.markdown("#### 📋 完整数据")
                
                # 选择要显示的列（排除序号列）
                display_columns = [col for col in df_display.columns if col != '序号']
                df_display = df_display[display_columns]
                
                # 显示前20条记录
                df_display = df_display.head(20)
                st.dataframe(df_display, use_container_width=True, height=400)
            except Exception as e:
                st.error(f"❌ 获取个股资金流数据失败: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
    # ========== 数据更新时间 ==========
    st.markdown("---")
    st.caption(f"📅 数据日期: {data_date}")

except Exception as e:
    st.error(f"❌ 加载数据失败: {str(e)}")
    import traceback
    st.code(traceback.format_exc())

