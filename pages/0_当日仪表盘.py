#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
仪表盘页面 - 综合展示指定日期的所有关键数据
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
from pathlib import Path
import sys

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.db import SessionLocal
from services.sector_history_service import SectorHistoryService
from services.zt_pool_history_service import ZtPoolHistoryService
from services.dtgc_pool_history_service import DtgcPoolHistoryService
from services.zbgc_pool_history_service import ZbgcPoolHistoryService
from services.index_history_service import IndexHistoryService
from utils.time_utils import get_data_date, get_utc8_date
from utils.focused_indices import get_focused_indices

st.set_page_config(
    page_title="仪表盘",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 页面样式 - 统一标题样式
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
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }
    /* 优化指数涨跌幅颜色 - 加深颜色，提升视觉效果 */
    div[data-testid="stMetricDelta"] {
        font-weight: 700 !important;
        font-size: 1.1em !important;
    }
    /* 上涨颜色 - 深红色 (#dc2626) - 使用属性选择器 */
    div[data-testid="stMetricDelta"] svg[data-testid="stMetricDeltaIcon-Up"],
    div[data-testid="stMetricDelta"]:has(> svg[data-testid="stMetricDeltaIcon-Up"]) {
        color: #dc2626 !important;
        fill: #dc2626 !important;
    }
    /* 下跌颜色 - 深绿色 (#059669) */
    div[data-testid="stMetricDelta"] svg[data-testid="stMetricDeltaIcon-Down"],
    div[data-testid="stMetricDelta"]:has(> svg[data-testid="stMetricDeltaIcon-Down"]) {
        color: #059669 !important;
        fill: #059669 !important;
    }
    </style>
    <script>
    // 动态设置涨跌幅颜色，确保颜色加深
    setTimeout(function() {
        document.querySelectorAll('div[data-testid="stMetricDelta"]').forEach(function(el) {
            var text = el.textContent || el.innerText;
            var svg = el.querySelector('svg');
            if (text && text.includes('+')) {
                el.style.color = '#dc2626';
                el.style.fontWeight = '700';
                if (svg) {
                    svg.style.color = '#dc2626';
                    svg.style.fill = '#dc2626';
                }
            } else if (text && text.includes('-')) {
                el.style.color = '#059669';
                el.style.fontWeight = '700';
                if (svg) {
                    svg.style.color = '#059669';
                    svg.style.fill = '#059669';
                }
            }
        });
    }, 200);
    </script>
""", unsafe_allow_html=True)

# 页面标题
st.markdown('<h1 class="main-header">📊 仪表盘</h1>', unsafe_allow_html=True)

# 日期选择
today = get_utc8_date()
default_date = get_data_date()  # 默认使用数据日期（自动判断）

selected_date = st.date_input(
    "📅 选择日期",
    value=default_date,
    max_value=today,
    label_visibility="visible",
    help="选择要查看的日期，默认显示最新可用数据"
)

# 处理日期
if selected_date is None:
    selected_date = default_date

data_date = selected_date

# 加载数据
@st.cache_data(ttl=300)  # 缓存5分钟
def load_daily_data(target_date: date):
    """加载指定日期的所有数据"""
    db = SessionLocal()
    try:
        # 行业板块数据
        industry_sectors = SectorHistoryService.get_sectors_by_date(db, target_date, 'industry')
        
        # 概念板块数据
        concept_sectors = SectorHistoryService.get_sectors_by_date(db, target_date, 'concept')
        
        # 涨停股票池
        zt_pool = ZtPoolHistoryService.get_zt_pool_by_date(db, target_date)
        
        # 跌停股票池
        dt_pool = DtgcPoolHistoryService.get_dtgc_pool_by_date(db, target_date)
        
        # 炸板股票池
        zb_pool = ZbgcPoolHistoryService.get_zbgc_pool_by_date(db, target_date)
        
        # 指数数据
        indices = IndexHistoryService.get_indices_by_date(db, target_date)
        
        return {
            'industry_sectors': industry_sectors,
            'concept_sectors': concept_sectors,
            'zt_pool': zt_pool,
            'dt_pool': dt_pool,
            'zb_pool': zb_pool,
            'indices': indices
        }
    finally:
        db.close()

# 加载数据
try:
    data = load_daily_data(data_date)
    
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
        # 显示诊断信息
        st.warning("⚠️ 数据诊断信息：")
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
        
        st.info("💡 提示：如果数据应该存在但显示为空，请点击「🔄 清除缓存」按钮清除缓存后重试")
        
        # 如果是今天或最近的日期，自动获取数据
        if data_date == today or (today - data_date).days <= 1:
            # 使用 session state 防止重复获取
            fetch_key = f"auto_fetch_{data_date}"
            if fetch_key not in st.session_state:
                st.session_state[fetch_key] = True
                
                with st.spinner("🔄 检测到没有数据，正在自动获取数据，请稍候..."):
                    try:
                        from services.sector_history_service import SectorHistoryService
                        from services.zt_pool_history_service import ZtPoolHistoryService
                        from services.zbgc_pool_history_service import ZbgcPoolHistoryService
                        from services.dtgc_pool_history_service import DtgcPoolHistoryService
                        from services.index_history_service import IndexHistoryService
                        from utils.excel_export import append_sectors_to_excel
                        from tasks.sector_scheduler import SectorScheduler
                        
                        # 检查是否为交易日（仅对今天的数据）
                        if data_date == today:
                            scheduler = SectorScheduler()
                            if not scheduler._is_trading_day(today):
                                st.warning(f"⚠️ 今日 ({today}) 不是交易日，无法获取数据")
                                st.info("💡 请选择其他日期查看历史数据")
                                st.stop()
                        
                        db = SessionLocal()
                        results = {}
                        
                        try:
                            # 1. 保存行业板块数据
                            try:
                                industry_count = SectorHistoryService.save_today_sectors(db, sector_type='industry')
                                results['sectors'] = industry_count
                                excel_file = append_sectors_to_excel()
                            except Exception as e:
                                results['sectors'] = f"失败: {str(e)}"
                                st.warning(f"⚠️ 保存行业板块数据失败: {str(e)}")
                            
                            # 1.1 保存概念板块数据
                            try:
                                concept_count = SectorHistoryService.save_today_sectors(db, sector_type='concept')
                                if 'sectors' in results and isinstance(results['sectors'], int):
                                    results['sectors'] = f"行业:{results['sectors']}, 概念:{concept_count}"
                                elif 'sectors' in results:
                                    results['sectors'] = f"{results['sectors']}, 概念:{concept_count}"
                                else:
                                    results['sectors'] = f"概念:{concept_count}"
                            except Exception as e:
                                if 'sectors' in results:
                                    results['sectors'] = f"{results['sectors']}, 概念失败: {str(e)}"
                                else:
                                    results['sectors'] = f"概念失败: {str(e)}"
                                st.warning(f"⚠️ 保存概念板块数据失败: {str(e)}")
                            
                            # 2. 保存涨停股票池数据
                            try:
                                zt_count = ZtPoolHistoryService.save_today_zt_pool(db)
                                results['zt_pool'] = zt_count
                            except Exception as e:
                                results['zt_pool'] = f"失败: {str(e)}"
                                st.warning(f"⚠️ 保存涨停股票数据失败: {str(e)}")
                            
                            # 3. 保存炸板股票池数据
                            try:
                                zbgc_count = ZbgcPoolHistoryService.save_today_zbgc_pool(db)
                                results['zbgc_pool'] = zbgc_count
                            except Exception as e:
                                results['zbgc_pool'] = f"失败: {str(e)}"
                                st.warning(f"⚠️ 保存炸板股票数据失败: {str(e)}")
                            
                            # 4. 保存跌停股票池数据
                            try:
                                dtgc_count = DtgcPoolHistoryService.save_today_dtgc_pool(db)
                                results['dtgc_pool'] = dtgc_count
                            except Exception as e:
                                results['dtgc_pool'] = f"失败: {str(e)}"
                                st.warning(f"⚠️ 保存跌停股票数据失败: {str(e)}")
                            
                            # 5. 保存指数数据
                            try:
                                index_count = IndexHistoryService.save_today_indices(db)
                                results['indices'] = index_count
                            except Exception as e:
                                results['indices'] = f"失败: {str(e)}"
                                st.warning(f"⚠️ 保存指数数据失败: {str(e)}")
                            
                            # 清除缓存，重新加载数据
                            load_daily_data.clear()
                            
                        finally:
                            db.close()
                        
                        # 刷新页面以重新加载数据
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ 自动获取数据失败: {str(e)}")
                        st.info("💡 请稍后重试，或前往定时任务管理页面手动执行")
                        # 清除标记，允许重试
                        if fetch_key in st.session_state:
                            del st.session_state[fetch_key]
                        st.stop()
            else:
                # 已经尝试过获取，但数据仍然为空
                st.error(f"❌ {data_date} 没有数据，自动获取失败")
                st.info("💡 请稍后重试，或前往定时任务管理页面手动执行")
                # 清除标记，允许重试
                if fetch_key in st.session_state:
                    del st.session_state[fetch_key]
                st.stop()
        else:
            # 历史日期没有数据，直接提示
            st.error(f"❌ {data_date} 没有数据，请选择其他日期")
            st.info("💡 提示：如果数据应该存在但显示为空，请点击「🔄 清除缓存」按钮清除缓存后重试")
        st.stop()
    
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
    
    # 显示市场概况卡片（4列布局）
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
    
    with col4:
        st.markdown("#### 📋 数据概览")
        st.metric(
            "🏢 行业板块",
            f"{len(industry_sectors) if industry_sectors else 0}",
            help="行业板块数量"
        )
        st.metric(
            "💡 概念板块",
            f"{len(concept_sectors) if concept_sectors else 0}",
            help="概念板块数量"
        )
        st.metric(
            "⭐ 重点指数",
            f"{index_total}",
            help="重点指数数量"
        )
        st.metric(
            "📅 数据日期",
            f"{data_date}",
            help="当前显示的数据日期"
        )
    
    st.markdown("---")
    
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
                delta=f"{index_up - index_down}" if index_up > index_down else None,
                help="重点指数中上涨的数量"
            )
        
        with col2:
            st.metric(
                "📉 下跌指数",
                f"{index_down}",
                delta=f"{index_down - index_up}" if index_down > index_up else None,
                delta_color="inverse",
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
        df_focused_indices = df_focused_indices.sort_values('sort_order', ascending=True)
        
        # 准备表格数据
        df_display = df_focused_indices[['name', 'code', 'currentPrice', 'changePercent', 'change']].copy()
        df_display.columns = ['指数名称', '指数代码', '最新价', '涨跌幅(%)', '涨跌额']
        
        # 保存原始涨跌幅用于样式判断
        change_percent_values = df_focused_indices['changePercent'].values
        
        # 格式化数值
        df_display['最新价'] = df_display['最新价'].apply(lambda x: f"{x:.2f}")
        df_display['涨跌幅(%)'] = df_display['涨跌幅(%)'].apply(lambda x: f"{x:+.2f}%")
        df_display['涨跌额'] = df_display['涨跌额'].apply(lambda x: f"{x:+.2f}")
        
        # 定义样式函数：上涨用深红色背景，下跌用深绿色背景
        def apply_cell_style(df):
            """对涨跌幅列应用背景色：上涨深红色，下跌深绿色，加深颜色优化视觉效果"""
            styles = pd.DataFrame('', index=df.index, columns=df.columns)
            # 只对涨跌幅列应用样式
            for idx in df.index:
                change_pct = change_percent_values[idx]
                if change_pct > 0:
                    # 上涨：深红色背景 (#dc2626)，白色文字，加粗
                    styles.loc[idx, '涨跌幅(%)'] = 'background-color: #dc2626; color: #ffffff; font-weight: 700;'
                elif change_pct < 0:
                    # 下跌：深绿色背景 (#059669)，白色文字，加粗
                    styles.loc[idx, '涨跌幅(%)'] = 'background-color: #059669; color: #ffffff; font-weight: 700;'
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
                help="所选日期的行业板块资金净流入总额"
            )
        
        with col4:
            st.metric(
                "💸 资金净流出",
                f"{industry_net_outflow:.2f}亿元",
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
        
        col1, col2, col3 = st.columns(3)
        
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
                help="所选日期的概念板块资金净流入总额"
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
            
            # 资金净流入TOP 10
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
    
    # ========== 数据更新时间 ==========
    st.markdown("---")
    st.caption(f"📅 数据日期: {data_date}")

except Exception as e:
    st.error(f"❌ 加载数据失败: {str(e)}")
    import traceback
    st.code(traceback.format_exc())

