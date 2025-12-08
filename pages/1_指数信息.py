#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指数信息查询页面
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 尝试导入数据库模块，如果失败则显示配置提示
try:
    from database.db import SessionLocal
    from services.index_history_service import IndexHistoryService
    from services.stock_index_service import StockIndexService
    from utils.time_utils import get_utc8_date, get_data_date, filter_trading_days
    from utils.focused_indices import get_focused_indices
    from datetime import date, timedelta
    DB_AVAILABLE = True
except (ValueError, RuntimeError) as e:
    DB_AVAILABLE = False
    DB_ERROR = str(e)
except Exception as e:
    DB_AVAILABLE = False
    DB_ERROR = f"数据库连接错误: {str(e)}"

st.set_page_config(
    page_title="指数信息",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 检查数据库配置
if not DB_AVAILABLE:
    st.error("❌ 数据库配置未完成")
    st.markdown("""
    ### 📋 请在 Streamlit Cloud Secrets 中配置以下环境变量：
    
    **必需配置：**
    - `SUPABASE_PROJECT_REF`: Supabase项目引用ID
    - `SUPABASE_DB_PASSWORD`: Supabase数据库密码
    
    **可选配置：**
    - `SUPABASE_URL`: Supabase项目URL
    - `SUPABASE_ANON_KEY`: Supabase匿名密钥
    
    ### 🔧 配置步骤：
    1. 进入 Streamlit Cloud 应用设置
    2. 点击 **"Secrets"** 标签
    3. 添加上述环境变量（使用 TOML 格式）
    4. 保存并重新部署应用
    
    ### 📝 示例 Secrets 配置：
    ```toml
    SUPABASE_PROJECT_REF = "your-project-ref"
    SUPABASE_DB_PASSWORD = "your-db-password"
    SUPABASE_URL = "https://your-project.supabase.co"
    SUPABASE_ANON_KEY = "your-anon-key"
    ```
    
    ### 📚 详细配置说明：
    请查看项目文档：`SUPABASE_SETUP.md`
    """)
    st.code(DB_ERROR, language="text")
    st.stop()

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
st.markdown('<h1 class="main-header">📊 指数信息</h1>', unsafe_allow_html=True)

# 日期选择 - 默认为数据日期（自动判断）
default_date = get_data_date()
selected_date = st.date_input(
    "📅 选择日期",
    value=default_date,
    max_value=get_utc8_date(),
    help="选择要查看的指数数据日期"
)

try:
    # 从数据库加载数据
    with st.spinner("🔄 正在从数据库加载指数数据..."):
        db = SessionLocal()
        try:
            indices = IndexHistoryService.get_indices_by_date(db, selected_date)
        except Exception as e:
            st.error(f"❌ 加载数据失败: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
            st.stop()
        finally:
            db.close()
    
    if not indices:
        st.warning(f"⚠️ {selected_date} 暂无指数数据")
        
        # 检查是否为交易日
        from tasks.sector_scheduler import SectorScheduler
        scheduler = SectorScheduler()
        is_trading = scheduler._is_trading_day(selected_date)
        
        if is_trading:
            st.info("💡 提示：指数数据会在交易日15:10自动保存到数据库。如果数据应该存在但显示为空，可以：\n1. 前往「定时任务管理」页面手动执行任务\n2. 点击「🔄 清除缓存」按钮清除缓存后重试")
        else:
            st.info("💡 提示：该日期不是交易日，无法获取指数数据。请选择其他交易日查看数据。")
        
        # 提供操作按钮
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 清除缓存", use_container_width=True, key="clear_cache_index"):
                # 清除缓存（如果有的话）
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
        
        st.stop()
    
    # 转换为DataFrame
    # to_dict() 方法已经将字段名转换为 camelCase 格式
    df = pd.DataFrame(indices)
    
    # 直接使用所有数据，不进行筛选
    df_display = df.copy()
    
    # 将名称和代码合并为"指数名称（指数代码）"格式
    if 'name' in df_display.columns and 'code' in df_display.columns:
        df_display['指数名称（指数代码）'] = df_display['name'] + '（' + df_display['code'] + '）'
        df_display = df_display.drop(columns=['code', 'name'])
    
    # 列名映射：英文转中文
    column_mapping = {
        'currentPrice': '最新价',
        'changePercent': '涨跌幅(%)',
        'change': '涨跌额',
        'volume': '成交量',
        'amount': '成交额',
        'open': '今开',
        'high': '最高',
        'low': '最低',
        'prevClose': '昨收',
        'amplitude': '振幅(%)',
        'volumeRatio': '量比'
    }
    # 重命名列
    df_display = df_display.rename(columns=column_mapping)
    
    # 确保"指数名称（指数代码）"列在最前面
    if '指数名称（指数代码）' in df_display.columns:
        cols = ['指数名称（指数代码）'] + [col for col in df_display.columns if col != '指数名称（指数代码）']
        df_display = df_display[cols]
    
    # 统计信息
    st.markdown('<h2 class="section-header">📈 指数统计</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_count = len(df_display)
        st.metric("📊 指数总数", total_count)
    
    with col2:
        up_count = len(df_display[df_display['涨跌幅(%)'] > 0]) if '涨跌幅(%)' in df_display.columns else 0
        st.metric("📈 上涨指数", up_count, delta=f"{up_count/total_count*100:.1f}%" if total_count > 0 else "0%")
    
    with col3:
        down_count = len(df_display[df_display['涨跌幅(%)'] < 0]) if '涨跌幅(%)' in df_display.columns else 0
        st.metric("📉 下跌指数", down_count, delta=f"{down_count/total_count*100:.1f}%" if total_count > 0 else "0%")
    
    with col4:
        flat_count = len(df_display[df_display['涨跌幅(%)'] == 0]) if '涨跌幅(%)' in df_display.columns else 0
        st.metric("➡️ 平盘指数", flat_count)
    
    # 重点指数统计
    focused_indices_codes = get_focused_indices()
    if focused_indices_codes:
        # 标准化关注指数代码为6位格式
        focused_codes_6digit = set()
        for focused_code in focused_indices_codes:
            code_6digit = StockIndexService.normalize_index_code(focused_code)
            focused_codes_6digit.add(code_6digit)
        
        # 从当前数据中筛选重点指数
        focused_indices_data = []
        matched_codes = set()
        for idx in indices:
            db_code = idx.get('code', '')
            db_code_6digit = StockIndexService.normalize_index_code(db_code)
            
            if db_code_6digit in focused_codes_6digit:
                if db_code_6digit not in matched_codes:
                    focused_indices_data.append(idx)
                    matched_codes.add(db_code_6digit)
        
        if focused_indices_data:
            st.markdown('<h2 class="section-header">📊 重点指数统计</h2>', unsafe_allow_html=True)
            
            # 计算统计
            index_total = len(focused_indices_data)
            index_up = len([i for i in focused_indices_data if i.get('changePercent', 0) > 0])
            index_down = len([i for i in focused_indices_data if i.get('changePercent', 0) < 0])
            index_flat = index_total - index_up - index_down
            
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
                st.metric(
                    "➡️ 平盘指数",
                    f"{index_flat}",
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
            df_focused_display = df_focused_indices[['name', 'code', 'currentPrice', 'changePercent', 'change']].copy()
            df_focused_display.columns = ['指数名称', '指数代码', '最新价', '涨跌幅(%)', '涨跌额']
            
            # 保存原始涨跌幅用于样式判断
            change_percent_values = df_focused_indices['changePercent'].values
            
            # 格式化数值
            df_focused_display['最新价'] = df_focused_display['最新价'].apply(lambda x: f"{x:.2f}")
            df_focused_display['涨跌幅(%)'] = df_focused_display['涨跌幅(%)'].apply(lambda x: f"{x:+.2f}%")
            df_focused_display['涨跌额'] = df_focused_display['涨跌额'].apply(lambda x: f"{x:+.2f}")
            
            # 定义样式函数：上涨用深红色背景，下跌用深绿色背景
            def apply_cell_style(df):
                """对涨跌幅列应用背景色：上涨深红色，下跌深绿色"""
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
            styled_df = df_focused_display.style.apply(apply_cell_style, axis=None)
            
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
    
    # 关注指数变化曲线图
    focused_indices_codes = get_focused_indices()
    if focused_indices_codes:
        st.markdown('<h2 class="section-header">📈 关注指数变化曲线</h2>', unsafe_allow_html=True)
        
        # 日期范围选择（最近1个月）
        trend_end_date = selected_date
        trend_start_date = trend_end_date - timedelta(days=29)  # 30天（包含今天）
        
        try:
            db_trend = SessionLocal()
            try:
                # 获取关注指数的历史数据
                focused_indices_data = {}
                
                # 标准化关注指数代码为6位格式
                focused_codes_6digit = set()
                for focused_code in focused_indices_codes:
                    code_6digit = StockIndexService.normalize_index_code(focused_code)
                    focused_codes_6digit.add(code_6digit)
                
                # 为每个关注指数获取历史数据
                for focused_code in focused_indices_codes:
                    code_6digit = StockIndexService.normalize_index_code(focused_code)
                    history_data = IndexHistoryService.get_index_by_code_and_date_range(
                        db_trend, code_6digit, trend_start_date, trend_end_date
                    )
                    
                    if history_data:
                        # 获取指数名称（从第一条数据中获取）
                        index_name = history_data[0].get('name', focused_code)
                        focused_indices_data[code_6digit] = {
                            'name': index_name,
                            'code': code_6digit,
                            'data': history_data
                        }
                
                db_trend.close()
                
                if focused_indices_data:
                    # 准备图表数据
                    from chart_config.chart_config import LINE_CHART_CONFIG, LINE_CHART_COLORS, MULTI_LINE_COLORS
                    import plotly.colors as pc
                    
                    # 使用更鲜明的配色方案，使颜色区分更明显
                    # 优先使用 MULTI_LINE_COLORS（更鲜明的颜色），如果不够则使用 Set1
                    color_palette = MULTI_LINE_COLORS if len(focused_indices_data) <= len(MULTI_LINE_COLORS) else pc.qualitative.Set1
                    
                    fig_trend = go.Figure()
                    
                    # 收集所有数据以确定 Y 轴范围
                    all_change_percents = []
                    all_dates = set()
                    
                    # 为每个关注指数添加一条折线
                    color_idx = 0
                    for code_6digit, index_info in focused_indices_data.items():
                        history_data = index_info['data']
                        index_name = index_info['name']
                        
                        # 转换为DataFrame
                        df_index = pd.DataFrame(history_data)
                        
                        if 'date' in df_index.columns and 'changePercent' in df_index.columns:
                            # 确保date列是datetime类型（从数据库返回的是字符串）
                            if not pd.api.types.is_datetime64_any_dtype(df_index['date']):
                                df_index['date'] = pd.to_datetime(df_index['date'])
                            
                            # 过滤非交易日（这个函数会将date列转换为date对象）
                            df_index = filter_trading_days(df_index, date_column='date')
                            
                            if not df_index.empty:
                                # filter_trading_days 会将date列转换为date对象，需要重新转换为datetime才能使用.dt访问器
                                if not pd.api.types.is_datetime64_any_dtype(df_index['date']):
                                    df_index['date'] = pd.to_datetime(df_index['date'])
                                
                                df_index = df_index.sort_values('date')
                                
                                # 将日期转换为字符串格式，用于X轴显示（避免非交易日空白）
                                df_index['date_str'] = df_index['date'].dt.strftime('%Y-%m-%d')
                                
                                # 收集数据用于确定范围
                                all_change_percents.extend(df_index['changePercent'].tolist())
                                all_dates.update(df_index['date_str'].tolist())
                                
                                # 选择颜色
                                color = color_palette[color_idx % len(color_palette)]
                                color_idx += 1
                                
                                # 添加折线（使用更鲜明的颜色和稍粗的线条）
                                fig_trend.add_trace(go.Scatter(
                                    x=df_index['date_str'],
                                    y=df_index['changePercent'],
                                    mode='lines+markers',
                                    name=f"{index_name}（{code_6digit}）",
                                    line=dict(
                                        color=color,
                                        width=2.5,  # 线条稍粗，使颜色更明显
                                        shape='spline'  # 平滑曲线
                                    ),
                                    marker=dict(
                                        color=color,
                                        size=5,  # 标记点稍大，使颜色更明显
                                        line=dict(
                                            width=1,
                                            color='white'
                                        )
                                    ),
                                    hovertemplate=f'<b>{index_name}</b><br>日期: %{{x}}<br>涨跌幅: %{{y:.2f}}%<extra></extra>'
                                ))
                    
                    # 确定 Y 轴范围（用于背景色矩形）
                    if all_change_percents:
                        y_min = min(all_change_percents) - 1  # 留一点边距
                        y_max = max(all_change_percents) + 1
                    else:
                        y_min = -5
                        y_max = 5
                    
                    # 添加背景色：0 以下绿色，0 以上红色
                    # 绿色背景（0 以下）
                    fig_trend.add_hrect(
                        y0=y_min,
                        y1=0,
                        fillcolor="rgba(0, 200, 0, 0.08)",  # 浅绿色，透明度 8%（更淡）
                        layer="below",
                        line_width=0,
                    )
                    
                    # 红色背景（0 以上）
                    fig_trend.add_hrect(
                        y0=0,
                        y1=y_max,
                        fillcolor="rgba(255, 0, 0, 0.08)",  # 浅红色，透明度 8%（更淡）
                        layer="below",
                        line_width=0,
                    )
                    
                    # 添加零线
                    fig_trend.add_hline(
                        y=0,
                        line_dash="dash",
                        line_color=LINE_CHART_CONFIG['zero_line_color'],
                        opacity=LINE_CHART_CONFIG['zero_line_opacity'],
                        line_width=LINE_CHART_CONFIG['zero_line_width'],
                        annotation_text="0%",
                        annotation_position="right",
                        annotation_font_size=12,
                        layer="above"  # 确保零线在背景色之上
                    )
                    
                    # 更新布局
                    fig_trend.update_layout(
                        title=dict(
                            text="关注指数涨跌幅变化趋势（最近1个月）",
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
                            title=dict(text="涨跌幅(%)", font=dict(size=LINE_CHART_CONFIG['axis_title_font_size'])),
                            gridcolor=LINE_CHART_CONFIG['grid_color'],
                            gridwidth=LINE_CHART_CONFIG['grid_width'],
                            showgrid=True
                        ),
                        height=LINE_CHART_CONFIG['height'],
                        hovermode='x unified',
                        showlegend=True,
                        legend=dict(
                            orientation="v",
                            yanchor="top",
                            y=1,
                            xanchor="left",
                            x=1.02
                        ),
                        plot_bgcolor=LINE_CHART_CONFIG['plot_bgcolor'],
                        paper_bgcolor=LINE_CHART_CONFIG['paper_bgcolor'],
                        font=dict(
                            family=LINE_CHART_CONFIG['font_family'],
                            size=LINE_CHART_CONFIG['font_size']
                        )
                    )
                    
                    st.plotly_chart(fig_trend, use_container_width=True)
                else:
                    st.info("📭 暂无关注指数的历史数据")
                    
            except Exception as e:
                if 'db_trend' in locals():
                    db_trend.close()
                st.warning(f"⚠️ 获取关注指数历史数据失败: {str(e)}")
        except Exception as e:
            st.warning(f"⚠️ 显示关注指数变化曲线失败: {str(e)}")
    else:
        st.markdown('<h2 class="section-header">📈 关注指数变化曲线</h2>', unsafe_allow_html=True)
        st.info("💡 当前未设置关注指数，请在「关注管理」页面添加关注指数后查看变化曲线")
    
    # 完整数据表格
    st.markdown('<h2 class="section-header">📋 完整数据</h2>', unsafe_allow_html=True)
    
    # 搜索功能
    search_term = st.text_input(
        "🔍 搜索指数",
        placeholder="输入指数名称或代码进行搜索...",
        help="支持搜索指数名称或代码，支持模糊匹配",
        key="search_index_data"
    )
    
    # 根据搜索词过滤数据
    df_filtered = df_display.copy()
    if search_term:
        search_term_lower = search_term.lower().strip()
        # 创建搜索掩码：匹配指数名称（指数代码）列
        if '指数名称（指数代码）' in df_filtered.columns:
            mask = df_filtered['指数名称（指数代码）'].astype(str).str.lower().str.contains(
                search_term_lower, na=False
            )
        else:
            # 如果没有合并列，尝试搜索所有文本列
            mask = pd.Series([False] * len(df_filtered))
            for col in df_filtered.columns:
                if df_filtered[col].dtype == 'object':  # 文本列
                    mask = mask | df_filtered[col].astype(str).str.lower().str.contains(
                        search_term_lower, na=False
                    )
        
        df_filtered = df_filtered[mask].copy()
        
        # 显示搜索结果统计
        if len(df_filtered) > 0:
            st.info(f"🔍 找到 {len(df_filtered)} 条匹配结果（共 {len(df_display)} 条数据）")
        else:
            st.warning(f"⚠️ 未找到包含 '{search_term}' 的指数数据")
    
    # 显示数据表格（显示过滤后的数据，不限制高度）
    if len(df_filtered) > 0:
        st.dataframe(df_filtered, use_container_width=True)
        
        # 下载按钮（下载过滤后的数据）
        csv = df_filtered.to_csv(index=False).encode('utf-8-sig')
        file_name = f"指数信息_{search_term.replace(' ', '_')}.csv" if search_term else "指数信息.csv"
        st.download_button(
            label="📥 下载CSV" + (f"（{len(df_filtered)}条）" if search_term else ""),
            data=csv,
            file_name=file_name,
            mime="text/csv",
            key="download_index"
    )
    else:
        if search_term:
            st.info("💡 请尝试使用其他关键词搜索，或清空搜索框查看全部数据")
        else:
            st.info("📭 暂无数据")

except Exception as e:
    st.error(f"❌ 加载数据失败: {str(e)}")
    import traceback
    st.code(traceback.format_exc())

