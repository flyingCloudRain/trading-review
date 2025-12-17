#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
复盘日历页面 - 显示每日重要指数变化和上涨top3概念板块
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import sys
from datetime import date, datetime, timedelta
import calendar

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 尝试导入数据库模块
try:
    from database.db import SessionLocal
    from services.index_history_service import IndexHistoryService
    from services.sector_history_service import SectorHistoryService
    from services.stock_index_service import StockIndexService
    from utils.time_utils import get_utc8_date, get_data_date
    from utils.focused_indices import get_focused_indices
    DB_AVAILABLE = True
except (ValueError, RuntimeError) as e:
    DB_AVAILABLE = False
    DB_ERROR = str(e)
except Exception as e:
    DB_AVAILABLE = False
    DB_ERROR = f"数据库连接错误: {str(e)}"

st.set_page_config(
    page_title="复盘日历",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 应用统一样式（包含日历特定样式）
from utils.page_styles import apply_common_styles, get_calendar_specific_styles
apply_common_styles(additional_styles=get_calendar_specific_styles())

st.markdown('<h1 class="main-header">复盘日历</h1>', unsafe_allow_html=True)

# 检查数据库配置
if not DB_AVAILABLE:
    st.error(f"数据库连接失败: {DB_ERROR}")
    st.info("请检查数据库配置，详细说明请查看 SUPABASE_SETUP.md")
    st.stop()

# 获取有数据的日期范围
db = SessionLocal()
try:
    from services.sector_history_service import SectorHistoryService
    all_dates = SectorHistoryService.get_all_dates(db)
    if all_dates:
        min_date = min(all_dates)
        max_date = max(all_dates)
    else:
        min_date = get_utc8_date() - timedelta(days=30)
        max_date = get_utc8_date()
except:
    min_date = get_utc8_date() - timedelta(days=30)
    max_date = get_utc8_date()
finally:
    db.close()

# 日期选择
col_date1, col_date2 = st.columns([2, 3])
with col_date1:
    # 生成可选的月份列表（最近6个月）
    month_options = []
    current = max_date
    for i in range(6):
        month_options.append((current.year, current.month))
        # 往前推一个月
        if current.month == 1:
            current = date(current.year - 1, 12, 1)
        else:
            current = date(current.year, current.month - 1, 1)
    
    selected_month = st.selectbox(
        "选择月份",
        options=month_options,
        format_func=lambda x: f"{x[0]}年{x[1]}月",
        help="选择要查看的月份",
        index=0
    )
    year, month = selected_month

# 获取该月的所有日期
first_day = date(year, month, 1)
if month == 12:
    last_day = date(year + 1, 1, 1) - timedelta(days=1)
else:
    last_day = date(year, month + 1, 1) - timedelta(days=1)

# 获取该月有数据的日期
db = SessionLocal()
try:
    month_dates = [d for d in all_dates if first_day <= d <= last_day]
except:
    month_dates = []
finally:
    db.close()

# 获取关注指数
focused_indices = get_focused_indices()
if not focused_indices:
    # 如果没有关注指数，使用默认的重要指数
    focused_indices = ['000001', '000300', '399006', '000688', '000852', '000905']

# 获取指数名称映射
index_name_map = {}
try:
    from utils.index_base_config import load_index_base_config, get_index_name
    base_indices = load_index_base_config()
    for idx in base_indices:
        index_name_map[idx['code']] = idx['name']
except:
    # 默认映射
    default_names = {
        '000001': '上证指数',
        '000300': '沪深300',
        '399006': '创业板指',
        '000688': '科创50',
        '000852': '中证1000',
        '000905': '中证500',
    }
    index_name_map = default_names

# 日历显示
col_cal_header1, col_cal_header2 = st.columns([3, 1])
with col_cal_header1:
    st.markdown('<h2 class="section-header">日历视图</h2>', unsafe_allow_html=True)
# 获取选中日期的详细信息
selected_date = st.session_state.get('selected_calendar_date', None)
today = get_utc8_date()

# 生成日历
cal = calendar.monthcalendar(year, month)
weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

# 显示星期标题
cols = st.columns(7)
for i, weekday in enumerate(weekdays):
    with cols[i]:
        st.markdown(f"<div class='calendar-weekday'>{weekday}</div>", unsafe_allow_html=True)

# 批量加载当月所有日期的数据（优化性能）
@st.cache_data(ttl=300)  # 缓存5分钟
def load_month_data(year, month, month_dates, focused_indices):
    """批量加载整月的数据"""
    if not month_dates:
        return {}
    
    db = SessionLocal()
    try:
        month_data = {}
        for current_date in month_dates:
            try:
                # 获取所有关注的指数数据
                indices_data = IndexHistoryService.get_indices_by_date(db, current_date)
                focused_indices_data = [idx for idx in indices_data if idx.get('code') in focused_indices]
                
                # 获取top3板块
                sectors_data = SectorHistoryService.get_sectors_by_date(db, current_date, 'concept')
                up_sectors = [s for s in sectors_data if s.get('changePercent', 0) > 0]
                top3_sectors = sorted(up_sectors, key=lambda x: x.get('changePercent', 0), reverse=True)[:3]
                
                month_data[current_date] = {
                    'indices': focused_indices_data,
                    'top3_sectors': top3_sectors
                }
            except Exception:
                pass
        return month_data
    finally:
        db.close()

# 加载当月数据
month_data_cache = load_month_data(year, month, month_dates, focused_indices)

# 显示日历
st.markdown('<div class="calendar-container">', unsafe_allow_html=True)
for week in cal:
    cols = st.columns(7)
    for i, day in enumerate(week):
        with cols[i]:
            if day == 0:
                st.markdown("<div style='min-height: 10px;'></div>", unsafe_allow_html=True)
            else:
                current_date = date(year, month, day)
                has_data = current_date in month_dates
                is_selected = selected_date == current_date if selected_date else False
                is_today = current_date == today
                
                # 从缓存获取数据
                day_summary = month_data_cache.get(current_date)
                
                # 日期文本显示
                day_label = str(day)
                
                # 使用文本显示日期（不再使用按钮）
                cell_class = "calendar-day-cell"
                if has_data:
                    cell_class += " has-data"
                if is_selected:
                    cell_class += " selected"
                if is_today:
                    cell_class += " today"
                
                # 显示日期文本（不再使用按钮形式）
                day_html = f'<div class="{cell_class}"><div class="day-number">{day_label}</div>'
                st.markdown(day_html, unsafe_allow_html=True)
                

                
                # 显示数据（在日期文本下方）
                if day_summary:
                    # 指数组 - 显示所有关注的指数（简化显示）
                    indices_html = '<div class="index-group">'
                    if day_summary['indices']:
                        for idx in day_summary['indices']:
                            change = idx.get('changePercent', 0)
                            code = idx.get('code', '')
                            name = index_name_map.get(code, code)
                            if len(name) > 3:
                                name = name[:3]
                            badge_class = "index-badge positive" if change > 0 else "index-badge negative"
                            arrow = "↑" if change > 0 else "↓"
                            indices_html += f'<div class="{badge_class}">{name}{arrow}{abs(change):.1f}%</div>'
                    indices_html += '</div>'
                    st.markdown(indices_html, unsafe_allow_html=True)
                    
                    # 板块组 - 显示top3板块（简化显示）
                    sectors_html = '<div class="sector-group">'
                    if day_summary['top3_sectors']:
                        for i, sector in enumerate(day_summary['top3_sectors'], 1):
                            sector_name = sector.get('name', '')
                            if len(sector_name) > 3:
                                sector_name = sector_name[:3]
                            change = sector.get('changePercent', 0)
                            sectors_html += f'<div class="sector-badge">{i}.{sector_name}+{change:.1f}%</div>'
                    sectors_html += '</div></div>'
                    st.markdown(sectors_html, unsafe_allow_html=True)
                else:
                    # 如果没有数据，也要关闭 div
                    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# 显示选中日期的详细信息
if selected_date:
    st.markdown("---")
    st.markdown(f'<h2 class="section-header">{selected_date} 复盘详情</h2>', unsafe_allow_html=True)
    
    db = SessionLocal()
    try:
        # 获取指数数据
        indices_data = IndexHistoryService.get_indices_by_date(db, selected_date)
        focused_indices_data = [idx for idx in indices_data if idx.get('code') in focused_indices]
        
        # 获取概念板块数据
        sectors_data = SectorHistoryService.get_sectors_by_date(db, selected_date, 'concept')
        up_sectors = [s for s in sectors_data if s.get('changePercent', 0) > 0]
        top3_sectors = sorted(up_sectors, key=lambda x: x.get('changePercent', 0), reverse=True)[:3]
        
        # 显示重要指数变化
        if focused_indices_data:
            st.markdown("### 重要指数变化")
            indices_df_data = []
            for idx in focused_indices_data:
                code = idx.get('code', '')
                name = index_name_map.get(code, code)
                indices_df_data.append({
                    '指数名称': name,
                    '指数代码': code,
                    '最新价': f"{idx.get('currentPrice', 0):.2f}",
                    '涨跌幅': f"{idx.get('changePercent', 0):+.2f}%",
                    '涨跌额': f"{idx.get('change', 0):+.2f}",
                    '成交量': f"{idx.get('volume', 0):.2f}",
                    '成交额': f"{idx.get('amount', 0):.2f}",
                })
            
            indices_df = pd.DataFrame(indices_df_data)
            # 根据涨跌幅着色
            def color_change(val):
                if isinstance(val, str) and '%' in val:
                    try:
                        num = float(val.replace('%', '').replace('+', ''))
                        if num > 0:
                            return 'color: #ef4444; font-weight: 600;'
                        elif num < 0:
                            return 'color: #10b981; font-weight: 600;'
                    except:
                        pass
                return ''
            
            styled_df = indices_df.style.applymap(color_change, subset=['涨跌幅'])
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
        else:
            st.info("该日期暂无指数数据")
        
        # 显示上涨top3概念板块
        if top3_sectors:
            st.markdown("### 上涨TOP3概念板块")
            sectors_df_data = []
            for i, sector in enumerate(top3_sectors, 1):
                sectors_df_data.append({
                    '排名': i,
                    '板块名称': sector.get('name', ''),
                    '涨跌幅': f"{sector.get('changePercent', 0):+.2f}%",
                    '总成交量(万手)': f"{sector.get('totalVolume', 0):.2f}",
                    '总成交额(亿元)': f"{sector.get('totalAmount', 0):.2f}",
                    '净流入(亿元)': f"{sector.get('netInflow', 0):.2f}",
                })
            
            sectors_df = pd.DataFrame(sectors_df_data)
            styled_df = sectors_df.style.applymap(color_change, subset=['涨跌幅'])
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
        else:
            st.info("该日期暂无概念板块数据")
            
    except Exception as e:
        st.error(f"获取数据失败: {str(e)}")
    finally:
        db.close()
else:
    st.info("请点击日历中的日期查看详细复盘信息")

