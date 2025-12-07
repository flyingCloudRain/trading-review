#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指数信息查询页面
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 尝试导入数据库模块，如果失败则显示配置提示
try:
    from database.db import SessionLocal
    from services.index_history_service import IndexHistoryService
    from utils.time_utils import get_utc8_date, get_data_date
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
        st.info("💡 提示：指数数据会在交易日15:10自动保存到数据库")
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
    
    # 涨跌幅TOP 10
    if '涨跌幅(%)' in df_display.columns and len(df_display) > 0:
        st.markdown('<h2 class="section-header">📊 涨跌幅排行</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📈 涨幅TOP 10")
            # 直接使用已合并的"指数名称（指数代码）"列
            top_gainers = df_display.nlargest(10, '涨跌幅(%)')[['指数名称（指数代码）', '涨跌幅(%)', '最新价']].copy()
            top_gainers = top_gainers.sort_values('涨跌幅(%)', ascending=False)
            
            # 创建横向柱状图
            fig_gainers = px.bar(
                top_gainers,
                x='涨跌幅(%)',
                y='指数名称（指数代码）',
                orientation='h',
                text='涨跌幅(%)',
                color='涨跌幅(%)',
                color_continuous_scale='Reds',
                labels={'涨跌幅(%)': '涨跌幅(%)', '指数名称（指数代码）': '指数名称（指数代码）'},
                title='涨幅TOP 10'
            )
            fig_gainers.update_traces(
                texttemplate='%{text:.2f}%',
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>涨跌幅: %{x:.2f}%<extra></extra>'
            )
            fig_gainers.update_layout(
                height=400,
                showlegend=False,
                coloraxis_showscale=False,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig_gainers, use_container_width=True)
        
        with col2:
            st.markdown("#### 📉 跌幅TOP 10")
            # 直接使用已合并的"指数名称（指数代码）"列
            top_losers = df_display.nsmallest(10, '涨跌幅(%)')[['指数名称（指数代码）', '涨跌幅(%)', '最新价']].copy()
            top_losers = top_losers.sort_values('涨跌幅(%)', ascending=True)
            
            # 创建横向柱状图
            fig_losers = px.bar(
                top_losers,
                x='涨跌幅(%)',
                y='指数名称（指数代码）',
                orientation='h',
                text='涨跌幅(%)',
                color='涨跌幅(%)',
                color_continuous_scale='Greens',
                labels={'涨跌幅(%)': '涨跌幅(%)', '指数名称（指数代码）': '指数名称（指数代码）'},
                title='跌幅TOP 10'
            )
            fig_losers.update_traces(
                texttemplate='%{text:.2f}%',
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>涨跌幅: %{x:.2f}%<extra></extra>'
            )
            fig_losers.update_layout(
                height=400,
                showlegend=False,
                coloraxis_showscale=False,
                yaxis={'categoryorder': 'total descending'}
            )
            st.plotly_chart(fig_losers, use_container_width=True)
    
    # 完整数据表格
    st.markdown('<h2 class="section-header">📋 完整数据</h2>', unsafe_allow_html=True)
    
    # 显示数据表格（显示全部数据，不限制高度）
    st.dataframe(df_display, use_container_width=True)
    
    # 下载按钮
    csv = df_display.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 下载CSV",
        data=csv,
        file_name="指数信息.csv",
        mime="text/csv",
        key="download_index"
    )

except Exception as e:
    st.error(f"❌ 加载数据失败: {str(e)}")
    import traceback
    st.code(traceback.format_exc())

