#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图表配置
"""
import plotly.colors as pc

# 颜色方案
COLOR_SCALE = {
    'positive': '#00ff00',  # 绿色 - 上涨
    'negative': '#ff0000',  # 红色 - 下跌
    'neutral': '#808080'    # 灰色 - 平盘
}

# Plotly颜色方案
COLOR_PALETTE = pc.qualitative.Set3  # 12色方案
COLOR_PALETTE_10 = pc.qualitative.Set1  # 10色方案

# 涨跌幅颜色映射
CHANGE_PERCENT_COLOR_SCALE = 'RdYlGn'  # 红-黄-绿
CHANGE_PERCENT_COLOR_SCALE_REVERSE = 'RdYlGn_r'  # 绿-黄-红（反向）

# 统一颜色方案
# 涨幅和净流入：使用相同的绿色系，确保颜色一致
POSITIVE_COLOR_SCALE = 'Greens'  # 绿色系 - 用于涨幅和净流入（统一色系）

# 跌幅和净流出：使用相同的红色系
NEGATIVE_COLOR_SCALE = 'Reds'    # 红色系 - 用于跌幅和净流出（统一色系）

# 图表尺寸配置
CHART_CONFIG = {
    'height': 400,  # 标准图表高度
    'width': '100%',  # 自适应宽度
    'margin': dict(l=50, r=50, t=50, b=50),  # 边距
    'template': 'plotly_white',  # 图表模板
}

# 图表布局配置
LAYOUT_CONFIG = {
    'hovermode': 'x unified',  # 悬停模式
    'showlegend': True,  # 显示图例
    'legend': dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    'xaxis': dict(
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray'
    ),
    'yaxis': dict(
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray'
    ),
}

# 数据采样配置
SAMPLING_CONFIG = {
    'max_points': 1000,  # 最大数据点数
    'auto_sample': True,  # 自动采样
}

# 折线图统一配置
LINE_CHART_CONFIG = {
    'line_width': 3,  # 线条宽度
    'marker_size': 8,  # 标记大小
    'marker_line_width': 2,  # 标记边框宽度
    'marker_line_color': 'white',  # 标记边框颜色
    'fill_opacity': 0.15,  # 填充透明度
    'grid_color': '#e8e8e8',  # 网格线颜色
    'grid_width': 1,  # 网格线宽度
    'zero_line_color': '#999999',  # 零线颜色
    'zero_line_width': 2,  # 零线宽度
    'zero_line_opacity': 0.5,  # 零线透明度
    'font_family': 'Arial, sans-serif',  # 字体
    'font_size': 12,  # 字体大小
    'title_font_size': 18,  # 标题字体大小
    'axis_title_font_size': 14,  # 坐标轴标题字体大小
    'plot_bgcolor': 'rgba(0,0,0,0)',  # 图表背景色 - 透明，跟随系统主题
    'paper_bgcolor': 'rgba(0,0,0,0)',  # 纸张背景色 - 透明，跟随系统主题
    'height': 450,  # 图表高度
}

# 折线图配色方案
LINE_CHART_COLORS = {
    'primary': '#2563eb',  # 主色 - 蓝色
    'success': '#10b981',  # 成功色 - 绿色
    'warning': '#f59e0b',  # 警告色 - 橙色
    'danger': '#ef4444',  # 危险色 - 红色
    'info': '#3b82f6',  # 信息色 - 浅蓝色
    'purple': '#8b5cf6',  # 紫色
    'pink': '#ec4899',  # 粉色
    'teal': '#14b8a6',  # 青色
}

# 多线条配色方案（用于多条折线图）
MULTI_LINE_COLORS = [
    '#2563eb',  # 蓝色
    '#f59e0b',  # 橙色
    '#10b981',  # 绿色
    '#ef4444',  # 红色
    '#8b5cf6',  # 紫色
    '#ec4899',  # 粉色
    '#14b8a6',  # 青色
    '#f97316',  # 深橙色
    '#06b6d4',  # 天蓝色
    '#84cc16',  # 黄绿色
    '#a855f7',  # 紫罗兰
    '#f43f5e',  # 玫瑰红
    '#0ea5e9',  # 亮蓝色
    '#22c55e',  # 亮绿色
    '#eab308',  # 黄色
    '#6366f1',  # 靛蓝色
    '#d946ef',  # 紫红色
    '#64748b',  # 石板灰
    '#fbbf24',  # 琥珀色
    '#34d399',  # 翠绿色
]

