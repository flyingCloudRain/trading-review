#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图表工具函数
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from chart_config.chart_config import (
    CHANGE_PERCENT_COLOR_SCALE,
    CHANGE_PERCENT_COLOR_SCALE_REVERSE,
    POSITIVE_COLOR_SCALE,
    NEGATIVE_COLOR_SCALE,
    CHART_CONFIG,
    LAYOUT_CONFIG
)
from utils.time_utils import filter_trading_days

def create_sector_trend_chart(
    df: pd.DataFrame,
    sectors: list,
    date_col: str = 'date',
    value_col: str = 'changePercent',
    title: str = '板块涨跌幅趋势'
) -> go.Figure:
    """
    创建板块趋势折线图
    
    Args:
        df: 数据DataFrame
        sectors: 要显示的板块列表
        date_col: 日期列名
        value_col: 数值列名
        title: 图表标题
    
    Returns:
        Plotly图表对象
    """
    if df.empty:
        return go.Figure()
    
    # 筛选选中的板块
    filtered_df = df[df['name'].isin(sectors)].copy() if 'name' in df.columns else df.copy()
    
    if filtered_df.empty:
        return go.Figure()
    
    # 确保日期是datetime类型
    if not pd.api.types.is_datetime64_any_dtype(filtered_df[date_col]):
        filtered_df[date_col] = pd.to_datetime(filtered_df[date_col])
    
    # 过滤非交易日
    filtered_df = filter_trading_days(filtered_df, date_column=date_col)
    
    if filtered_df.empty:
        return go.Figure()
    
    # filter_trading_days 会将date列转换为date对象，需要重新转换为datetime才能使用.dt访问器
    if not pd.api.types.is_datetime64_any_dtype(filtered_df[date_col]):
        filtered_df[date_col] = pd.to_datetime(filtered_df[date_col])
    
    # 排序数据
    filtered_df = filtered_df.sort_values([date_col, 'name'])
    
    # 将日期转换为字符串格式，用于X轴显示（避免非交易日空白）
    filtered_df['date_str'] = filtered_df[date_col].dt.strftime('%Y-%m-%d')
    
    # 根据value_col设置不同的标签
    y_label_map = {
        'changePercent': '涨跌幅(%)',
        'netInflow': '净流入(亿元)',
        'net_inflow': '净流入(亿元)'
    }
    y_label = y_label_map.get(value_col, value_col)
    
    # 使用统一的配色方案
    from chart_config.chart_config import MULTI_LINE_COLORS, LINE_CHART_CONFIG
    
    # 获取唯一的板块名称
    unique_sectors = filtered_df['name'].unique() if 'name' in filtered_df.columns else []
    
    # 创建颜色映射
    color_map = {}
    for i, sector in enumerate(unique_sectors):
        color_map[sector] = MULTI_LINE_COLORS[i % len(MULTI_LINE_COLORS)]
    
    # 使用 go.Figure 和 go.Scatter 来创建图表，以便更好地控制 X 轴
    fig = go.Figure()
    
    # 为每个板块添加一条折线
    for sector in unique_sectors:
        sector_data = filtered_df[filtered_df['name'] == sector].copy()
        if not sector_data.empty:
            fig.add_trace(go.Scatter(
                x=sector_data['date_str'],
                y=sector_data[value_col],
                mode='lines+markers',
                name=sector,
                line=dict(
                    color=color_map[sector],
                    width=LINE_CHART_CONFIG.get('line_width', 2),
                    shape='spline'  # 平滑曲线
                ),
                marker=dict(
                    color=color_map[sector],
                    size=LINE_CHART_CONFIG.get('marker_size', 5),
                    line=dict(
                        width=LINE_CHART_CONFIG.get('marker_line_width', 1),
                        color=LINE_CHART_CONFIG.get('marker_line_color', 'white')
                    )
                ),
                hovertemplate=f'<b>{sector}</b><br>日期: %{{x}}<br>{y_label}: %{{y:.2f}}<extra></extra>'
            ))
    
    # 添加零线 - 优化样式
    fig.add_hline(
        y=0, 
        line_dash="dash", 
        line_color='#6b7280', 
        opacity=0.5, 
        line_width=2,
        annotation_text="零线",
        annotation_position="right",
        annotation_font_size=10,
        annotation_font_color='#6b7280'
    )
    
    # 更新布局 - 优化样式
    fig.update_layout(
        height=500,  # 增加图表高度
        plot_bgcolor='rgba(0,0,0,0)',  # 透明背景
        paper_bgcolor='rgba(0,0,0,0)',  # 透明背景
        font=dict(
            family='Arial, sans-serif',
            size=12,
            color='#2c3e50'
        ),
        title=dict(
            font=dict(size=20, color='#2c3e50', family='Arial, sans-serif'),
            x=0.5,
            xanchor='center',
            pad=dict(b=20)
        ),
        xaxis=dict(
            title=dict(
                font=dict(size=14, color='#2c3e50', family='Arial, sans-serif'),
                text='日期'
            ),
            gridcolor='rgba(128, 128, 128, 0.15)',
            gridwidth=1,
            showgrid=True,
            tickfont=dict(size=11, color='#6b7280'),
            linecolor='rgba(128, 128, 128, 0.3)',
            linewidth=1,
            type='category',  # 使用分类类型，避免非交易日空白
            tickangle=-45  # 倾斜角度，避免日期重叠
        ),
        yaxis=dict(
            title=dict(
                font=dict(size=14, color='#2c3e50', family='Arial, sans-serif'),
                text=y_label
            ),
            gridcolor='rgba(128, 128, 128, 0.15)',
            gridwidth=1,
            showgrid=True,
            tickfont=dict(size=11, color='#6b7280'),
            linecolor='rgba(128, 128, 128, 0.3)',
            linewidth=1
        ),
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color='#2c3e50'),
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='rgba(128, 128, 128, 0.2)',
            borderwidth=1
        ),
        margin=dict(l=60, r=30, t=80, b=60)
    )
    
    # 设置X轴日期格式，只显示日期（不显示时间）
    fig.update_xaxes(
        tickformat='%Y-%m-%d',  # 只显示日期格式：YYYY-MM-DD
        dtick='D1'  # 每天一个刻度
    )
    
    # 优化线条样式
    fig.update_traces(
        line_width=3,  # 增加线条宽度，更清晰
        marker_size=6,  # 标记点大小
        marker_line_width=1.5,  # 标记点边框宽度
        marker_line_color='white',  # 标记点边框颜色
        mode='lines+markers',  # 显示线条和标记点
        hovertemplate='<b>%{fullData.name}</b><br>日期: %{x}<br>' + y_label + ': %{y:.2f}<extra></extra>'
    )
    
    return fig

def create_ranking_bar_chart(
    df: pd.DataFrame,
    value_col: str = 'changePercent',
    name_col: str = 'name',
    top_n: int = 10,
    ascending: bool = False,
    title: str = None
) -> go.Figure:
    """
    创建排名柱状图
    
    Args:
        df: 数据DataFrame
        value_col: 排序的数值列
        name_col: 名称列
        top_n: 显示前N名
        ascending: 是否升序
        title: 图表标题
    """
    if df.empty:
        return go.Figure()
    
    # 排序并取前N名
    # 确保从大到小排列：
    # - ascending=False: 使用 nlargest，取最大的N个值，然后按降序排列
    # - ascending=True: 使用 nsmallest，取最小的N个值（跌幅/净流出），然后按绝对值从大到小排序
    if not ascending:
        # 涨幅/净流入：取最大的N个值，然后按降序排列（值从大到小）
        sorted_df = df.nlargest(top_n, value_col).sort_values(value_col, ascending=False)
    else:
        # 跌幅/净流出：取最小的N个值（绝对值最大的负数），然后按绝对值从大到小排序
        smallest_df = df.nsmallest(top_n, value_col)
        # 创建临时列用于排序（按绝对值降序）
        smallest_df = smallest_df.copy()
        smallest_df['_abs_sort'] = smallest_df[value_col].abs()
        sorted_df = smallest_df.sort_values('_abs_sort', ascending=False).drop('_abs_sort', axis=1)
    
    # 确定颜色方案 - 统一色系
    # 涨幅使用红色系，跌幅使用绿色系
    # 净流入使用橙色系，净流出使用蓝色系
    if value_col == 'changePercent':
        # 涨幅（ascending=False）使用红色系，跌幅（ascending=True）使用绿色系
        color_scale = NEGATIVE_COLOR_SCALE if not ascending else POSITIVE_COLOR_SCALE
    elif value_col == 'netInflow':
        # 净流入（ascending=False，显示最大的正数）使用橙色系
        # 净流出（ascending=True，显示最小的负数）使用蓝色系
        color_scale = 'Oranges' if not ascending else 'Blues'
    else:
        color_scale = 'Blues'
    
    # 设置标签
    labels_dict = {
        value_col: value_col,
        name_col: '板块'
    }
    if value_col == 'netInflow':
        labels_dict[value_col] = '净流入(亿元)'
    
    # 对于横向柱状图，值大的应该在顶部（从上到下显示）
    # Plotly横向柱状图Y轴从下往上显示，需要反转数据框顺序
    # 数据框已经是降序（值大的在前），反转后值大的会在顶部
    display_df = sorted_df.copy()
    display_df = display_df.iloc[::-1].reset_index(drop=True)  # 反转数据框，让值大的在顶部
    
    fig = px.bar(
        display_df,
        x=value_col,
        y=name_col,
        orientation='h',
        title=title or f'{value_col}排名 TOP {top_n}',
        labels=labels_dict,
        color=value_col,
        color_continuous_scale=color_scale
    )
    
    # 设置图表高度
    fig.update_layout(height=CHART_CONFIG['height'])
    
    return fig

def create_distribution_histogram(
    df: pd.DataFrame,
    value_col: str = 'changePercent',
    title: str = '涨跌幅分布',
    bins: int = 30
) -> go.Figure:
    """创建分布直方图 - 优化配色和显示"""
    if df.empty or value_col not in df.columns:
        return go.Figure()
    
    # 计算统计值
    mean_val = df[value_col].mean()
    median_val = df[value_col].median()
    std_val = df[value_col].std()
    
    # 根据涨跌使用不同颜色 - 创建颜色映射
    # 正值为红色，负值为绿色（符合之前的配色方案）
    df_with_color = df.copy()
    df_with_color['color'] = df_with_color[value_col].apply(
        lambda x: '#ef4444' if x >= 0 else '#10b981'
    )
    
    # 创建直方图，使用条件颜色
    fig = go.Figure()
    
    # 分别绘制正值和负值的柱状图
    positive_df = df[df[value_col] >= 0]
    negative_df = df[df[value_col] < 0]
    
    if not positive_df.empty:
        fig.add_trace(go.Histogram(
            x=positive_df[value_col],
            nbinsx=bins,
            name='上涨',
            marker_color='#ef4444',
            opacity=0.7,
            hovertemplate='涨跌幅: %{x:.2f}%<br>板块数: %{y}<extra></extra>'
        ))
    
    if not negative_df.empty:
        fig.add_trace(go.Histogram(
            x=negative_df[value_col],
            nbinsx=bins,
            name='下跌',
            marker_color='#10b981',
            opacity=0.7,
            hovertemplate='涨跌幅: %{x:.2f}%<br>板块数: %{y}<extra></extra>'
        ))
    
    # 添加均值线 - 红色虚线
    fig.add_vline(
        x=mean_val,
        line_dash="dash",
        line_color="#ef4444",
        line_width=3,
        annotation_text=f"均值: {mean_val:.2f}%",
        annotation_position="top right",
        annotation_font_size=13,
        annotation_font_color="#ef4444",
        annotation_bgcolor="rgba(239, 68, 68, 0.1)",
        annotation_borderpad=5
    )
    
    # 添加中位数线 - 绿色虚线
    fig.add_vline(
        x=median_val,
        line_dash="dash",
        line_color="#10b981",
        line_width=3,
        annotation_text=f"中位数: {median_val:.2f}%",
        annotation_position="top left",
        annotation_font_size=13,
        annotation_font_color="#10b981",
        annotation_bgcolor="rgba(16, 185, 129, 0.1)",
        annotation_borderpad=5
    )
    
    # 添加标准差区间（均值±1标准差）- 紫色半透明区域
    fig.add_vrect(
        x0=mean_val - std_val,
        x1=mean_val + std_val,
        fillcolor="rgba(102, 126, 234, 0.15)",
        layer="below",
        line_width=2,
        line_color="rgba(102, 126, 234, 0.5)",
        line_dash="dot",
        annotation_text=f"±1σ区间 ({mean_val-std_val:.2f}% ~ {mean_val+std_val:.2f}%)",
        annotation_position="top left",
        annotation_font_size=11,
        annotation_font_color="#667eea"
    )
    
    # 优化布局 - 背景色透明，跟随系统主题
    # 检测 Streamlit 主题（如果可用）
    try:
        import streamlit as st
        # 尝试获取 Streamlit 主题配置
        theme_config = st.get_option("theme.base")
        is_dark = theme_config == "dark"
    except:
        # 默认使用浅色主题
        is_dark = False
    
    # 根据主题设置颜色
    if is_dark:
        # 深色主题
        text_color = '#ffffff'
        grid_color = 'rgba(255, 255, 255, 0.1)'
        zero_line_color = 'rgba(255, 255, 255, 0.3)'
    else:
        # 浅色主题（默认）
        text_color = '#2c3e50'
        grid_color = 'rgba(128, 128, 128, 0.2)'
        zero_line_color = 'rgba(128, 128, 128, 0.5)'
    
    fig.update_layout(
        height=CHART_CONFIG['height'],
        plot_bgcolor='rgba(0,0,0,0)',  # 透明背景
        paper_bgcolor='rgba(0,0,0,0)',  # 透明背景
        font=dict(size=12, family="Arial, sans-serif", color=text_color),
        title=dict(
            text=title,
            font=dict(size=20, color=text_color, family="Arial, sans-serif"),
            x=0.5,
            xanchor='center',
            pad=dict(b=20)
        ),
        xaxis=dict(
            title=dict(text='涨跌幅(%)', font=dict(size=15, color=text_color)),
            gridcolor=grid_color,
            gridwidth=1,
            zeroline=True,
            zerolinecolor=zero_line_color,
            zerolinewidth=2
        ),
        yaxis=dict(
            title=dict(text='板块数量', font=dict(size=15, color=text_color)),
            gridcolor=grid_color,
            gridwidth=1
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12, color=text_color)
        ),
        hovermode='x unified',
        bargap=0.1
    )
    
    # 优化柱状图样式
    fig.update_traces(
        marker=dict(
            line=dict(width=1.5, color='white')
        )
    )
    
    return fig

def create_heatmap(
    df: pd.DataFrame,
    x_col: str = 'date',
    y_col: str = 'name',
    value_col: str = 'changePercent',
    title: str = '板块涨跌幅热力图'
) -> go.Figure:
    """创建热力图 - 优化显示"""
    if df.empty:
        return go.Figure()
    
    # 检查必要的列是否存在
    required_cols = [x_col, y_col, value_col]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"Warning: Missing columns in create_heatmap: {missing_cols}")
        return go.Figure()
    
    # 透视表
    try:
        # 确保日期是datetime类型
        df_copy = df.copy()
        if not pd.api.types.is_datetime64_any_dtype(df_copy[x_col]):
            df_copy[x_col] = pd.to_datetime(df_copy[x_col], errors='coerce')
        
        # 移除日期转换失败的行
        df_copy = df_copy.dropna(subset=[x_col])
        
        if df_copy.empty:
            print("Warning: All dates are invalid after conversion")
            return go.Figure()
        
        # 过滤非交易日
        df_copy = filter_trading_days(df_copy, date_column=x_col)
        
        if df_copy.empty:
            print("Warning: No trading days found after filtering")
            return go.Figure()
        
        # 按日期排序
        df_copy = df_copy.sort_values(by=[x_col, y_col])
        
        pivot_df = df_copy.pivot_table(
            index=y_col,
            columns=x_col,
            values=value_col,
            aggfunc='mean'
        )
        
        # 如果透视表为空，返回空图表
        if pivot_df.empty:
            print("Warning: Pivot table is empty")
            return go.Figure()
        
        fig = px.imshow(
            pivot_df,
            title=title,
            labels=dict(x='日期', y='板块', color='涨跌幅(%)'),
            color_continuous_scale='RdYlGn',  # 红-黄-绿配色，红色表示上涨，绿色表示下跌
            color_continuous_midpoint=0,  # 设置0值为中间点（黄色），确保上涨为红色，下跌为绿色
            aspect='auto',
            text_auto='.1f',  # 显示数值，保留1位小数
            textfont=dict(size=10, color='white')  # 数值文字样式
        )
        
        # 优化数值显示 - 根据背景色自动调整文字颜色
        fig.update_traces(
            texttemplate='%{text:.1f}%',
            textfont=dict(size=10),
            hovertemplate='<b>%{y}</b><br>日期: %{x}<br>涨跌幅: %{z:.2f}%<extra></extra>'
        )
        
        # 优化布局
        fig.update_layout(
            height=max(600, len(pivot_df) * 30),  # 根据板块数量动态调整高度，增加行高
            plot_bgcolor='rgba(0,0,0,0)',  # 透明背景
            paper_bgcolor='rgba(0,0,0,0)',  # 透明背景
            font=dict(size=12, family='Arial, sans-serif'),
            title=dict(
                font=dict(size=20, color='#2c3e50', family='Arial, sans-serif'),
                x=0.5,
                xanchor='center',
                pad=dict(b=25)
            ),
            xaxis=dict(
                title=dict(
                    font=dict(size=14, color='#2c3e50', family='Arial, sans-serif'),
                    text='日期'
                ),
                tickformat='%m-%d',  # 只显示月-日，更简洁
                tickfont=dict(size=11, color='#6b7280'),
                showgrid=True,
                gridcolor='rgba(128, 128, 128, 0.1)',
                gridwidth=1,
                side='bottom'
            ),
            yaxis=dict(
                title=dict(
                    font=dict(size=14, color='#2c3e50', family='Arial, sans-serif'),
                    text='板块'
                ),
                tickfont=dict(size=11, color='#6b7280'),
                showgrid=True,
                gridcolor='rgba(128, 128, 128, 0.1)',
                gridwidth=1
            ),
            coloraxis=dict(
                colorbar=dict(
                    title=dict(
                        text='涨跌幅(%)',
                        font=dict(size=12, color='#2c3e50')
                    ),
                    tickfont=dict(size=11, color='#6b7280'),
                    thickness=20,
                    len=0.6,
                    yanchor='middle',
                    y=0.5,
                    xanchor='left',
                    x=1.02
                )
            ),
            margin=dict(l=100, r=120, t=80, b=60)  # 优化边距
        )
        
        return fig
    except Exception as e:
        print(f"Error in create_heatmap: {str(e)}")
        import traceback
        traceback.print_exc()
        return go.Figure()

def create_scatter_chart(
    df: pd.DataFrame,
    x_col: str = 'totalVolume',
    y_col: str = 'changePercent',
    size_col: str = 'totalAmount',
    color_col: str = 'changePercent',
    title: str = '涨跌幅 vs 成交量'
) -> go.Figure:
    """创建散点图（气泡图）"""
    if df.empty:
        return go.Figure()
    
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        size=size_col,
        color=color_col,
        hover_data=['name'] if 'name' in df.columns else [],
        title=title,
        labels={
            x_col: '总成交量(万手)',
            y_col: '涨跌幅(%)',
            size_col: '总成交额(亿元)',
            color_col: '涨跌幅(%)',
            'name': '板块'
        },
        color_continuous_scale=CHANGE_PERCENT_COLOR_SCALE
    )
    
    # 添加象限线
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    if x_col in df.columns:
        fig.add_vline(x=df[x_col].median(), line_dash="dash", line_color="gray", opacity=0.5)
    
    fig.update_layout(height=CHART_CONFIG['height'])
    return fig

def create_pie_chart(
    df: pd.DataFrame,
    names_col: str,
    values_col: str = None,
    title: str = '分布图',
    hole: float = 0.4
) -> go.Figure:
    """创建饼图"""
    if df.empty:
        return go.Figure()
    
    if values_col:
        fig = px.pie(
            df,
            names=names_col,
            values=values_col,
            title=title,
            hole=hole
        )
    else:
        # 如果只有names_col，计算计数
        value_counts = df[names_col].value_counts()
        fig = px.pie(
            values=value_counts.values,
            names=value_counts.index,
            title=title,
            hole=hole
        )
    
    fig.update_layout(height=CHART_CONFIG['height'])
    return fig

