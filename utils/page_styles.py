#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一页面样式工具
提供统一的CSS样式定义，确保所有页面样式一致
"""
import streamlit as st

def get_common_styles():
    """
    获取通用样式CSS
    
    Returns:
        str: CSS样式字符串
    """
    return """
    <style>
    /* ==================== 标题样式 ==================== */
    /* 主标题样式 */
    .main-header,
    h1.main-header {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        color: #1f77b4 !important;
        margin-top: 1.4rem !important;
        margin-bottom: 0.2rem !important;
        padding-bottom: 0.4rem !important;
        border-bottom: 3px solid #1f77b4 !important;
        line-height: 1.5 !important;
        overflow: visible !important;
        text-overflow: clip !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        width: 100% !important;
        max-width: 100% !important;
    }
    
    /* 章节标题样式 */
    .section-header,
    h2.section-header {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #2c3e50 !important;
        margin-top: 0.3rem !important;
        margin-bottom: 0.4rem !important;
        padding-top: 0.4rem !important;
        padding-bottom: 0.4rem !important;
        border-bottom: 2px solid #e0e0e0 !important;
        background: transparent !important;
        line-height: 1.4 !important;
    }
    /* 减少章节标题之间的间距（当连续出现时） */
    .section-header + .section-header,
    h2.section-header + h2.section-header {
        margin-top: 0.2rem !important;
    }
    /* 减少章节标题前的内容间距 */
    .stMetric + .section-header,
    .stDataFrame + .section-header,
    [data-testid="stDataFrame"] + .section-header,
    .element-container:has(.stMetric) + .section-header,
    .stPlotlyChart + .section-header,
    [data-testid="stPlotlyChart"] + .section-header {
        margin-top: 0.2rem !important;
    }
    /* 减少Metric组件容器的底部间距 */
    .element-container:has(.stMetric) {
        margin-bottom: 0.3rem !important;
    }
    /* 减少列容器后的章节标题间距 */
    [data-testid="column"] + .section-header,
    [data-testid="stHorizontalBlock"] + .section-header,
    .stColumns + .section-header {
        margin-top: 0.2rem !important;
    }
    
    /* ==================== 组件样式 ==================== */
    /* Metric卡片样式 */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Streamlit组件基础样式 */
    .stDataFrame {
        font-size: 0.9rem !important;
        margin-bottom: 0.2rem !important;
    }
    
    /* Metric组件样式 - 清晰优化 */
    .stMetric {
        background-color: transparent !important;
        padding: 0.3rem 0 !important;
        margin: 0 !important;
        border: none !important;
    }
    .stMetric > div {
        background-color: transparent !important;
        padding: 0.3rem 0.3rem !important;
        margin: 0 !important;
        border-radius: 0 !important;
        transition: all 0.2s ease !important;
        border: none !important;
    }
    .stMetric:hover > div {
        box-shadow: none !important;
    }
    /* Metric标签容器 - 确保帮助图标和文字同一行 */
    .stMetric > div > div:first-child {
        display: flex !important;
        align-items: center !important;
        gap: 0.15rem !important;
        flex-wrap: nowrap !important;
    }
    /* Metric标签样式 - 清晰易读 */
    .stMetric label {
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        line-height: 1.3 !important;
        margin-bottom: 0.2rem !important;
        padding: 0 !important;
        color: #495057 !important;
        letter-spacing: 0.01em !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 0.15rem !important;
        opacity: 0.9 !important;
        white-space: nowrap !important;
    }
    /* Metric帮助图标 - 与文字同一行 */
    .stMetric [data-testid="stTooltipIcon"],
    .stMetric [data-testid="stTooltipIconButton"],
    .stMetric label svg,
    .stMetric label button {
        display: inline-flex !important;
        align-items: center !important;
        vertical-align: middle !important;
        margin: 0 !important;
        padding: 0 !important;
        flex-shrink: 0 !important;
        line-height: 1 !important;
    }
    /* Metric数值样式 - 突出显示 */
    .stMetric [data-testid="stMetricValue"] {
        font-size: 1.35rem !important;
        font-weight: 700 !important;
        line-height: 1.2 !important;
        margin-top: 0.1rem !important;
        padding: 0 !important;
        color: #212529 !important;
        letter-spacing: -0.02em !important;
    }
    /* Metric Delta样式 - 清晰区分 */
    .stMetric [data-testid="stMetricDelta"] {
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        line-height: 1.2 !important;
        margin-top: 0.15rem !important;
        padding: 0 !important;
        letter-spacing: 0.01em !important;
    }
    
    /* ==================== 表单组件样式 ==================== */
    /* 按钮样式优化 */
    .stButton > button {
        border-radius: 6px;
        transition: all 0.3s ease;
        font-weight: 500;
        margin-bottom: 0.2rem !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    /* 按钮容器间距 */
    .stButton {
        margin-bottom: 0.2rem !important;
    }
    
    /* 输入框样式优化 */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stDateInput > div > div > input {
        border-radius: 6px;
        border: 1px solid #e0e0e0;
        transition: border-color 0.3s ease;
    }
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stDateInput > div > div > input:focus {
        border-color: #1f77b4;
        box-shadow: 0 0 0 2px rgba(31, 119, 180, 0.1);
    }
    /* 表单组件容器间距 */
    .stTextInput,
    .stSelectbox,
    .stDateInput,
    .stRadio,
    .stCheckbox {
        margin-bottom: 0.2rem !important;
    }
    
    /* 涨跌幅颜色优化 */
    div[data-testid="stMetricDelta"] {
        font-weight: 700 !important;
        font-size: 1.1em !important;
    }
    div[data-testid="stMetricDelta"] svg[data-testid="stMetricDeltaIcon-Up"],
    div[data-testid="stMetricDelta"]:has(> svg[data-testid="stMetricDeltaIcon-Up"]) {
        color: #dc2626 !important;
        fill: #dc2626 !important;
    }
    div[data-testid="stMetricDelta"] svg[data-testid="stMetricDeltaIcon-Down"],
    div[data-testid="stMetricDelta"]:has(> svg[data-testid="stMetricDeltaIcon-Down"]) {
        color: #059669 !important;
        fill: #059669 !important;
    }
    
    /* ==================== 容器布局优化 ==================== */
    /* 主容器和主块容器 - 统一内边距 */
    .main .block-container,
    [data-testid="stMainBlockContainer"] {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 100% !important;
    }
    /* 应用视图容器 */
    [data-testid="stAppViewContainer"] {
        padding: 0.25rem !important;
    }
    /* 元素容器间距 */
    .element-container {
        margin-bottom: 0.2rem !important;
    }
    /* Markdown 容器间距 */
    .stMarkdown {
        margin-bottom: 0.2rem !important;
    }
    /* ==================== 文本样式 ==================== */
    /* 段落样式 - 统一所有段落样式 */
    p,
    .stMarkdown p,
    [data-testid="stMarkdownContainer"] p {
        font-size: 1rem !important;
        line-height: 1.6 !important;
        margin-top: 0.2rem !important;
        margin-bottom: 0.2rem !important;
        padding: 0.2rem 0 !important;
        color: #212529 !important;
        word-wrap: break-word !important;
    }
    /* 连续段落之间的间距 */
    p + p {
        margin-top: 0.2rem !important;
    }
    /* 标签页和展开器内容间距 */
    [data-testid="stTabs"] [data-testid="stVerticalBlock"] {
        gap: 0.2rem !important;
    }
    [data-testid="stExpander"] .element-container {
        margin-bottom: 0.2rem !important;
    }
    /* 警告和信息提示框间距 */
    .stAlert,
    [data-testid="stAlert"] {
        margin-bottom: 0.2rem !important;
    }
    /* ==================== 布局 Gap 优化 ==================== */
    /* 统一设置所有布局容器的 gap 为 0.2rem */
    /* Streamlit 水平布局块（columns 容器） */
    [data-testid="stHorizontalBlock"],
    .stHorizontalBlock > div[class*="st-emotion-cache"] {
        gap: 0.2rem !important;
    }
    /* Streamlit 内部 emotion-cache 容器 */
    .st-emotion-cache-wfksaw,
    [class*="st-emotion-cache"][class*="e1wguzas"],
    [class*="st-emotion-cache"][class*="tn0cau"],
    div[class*="st-emotion-cache"][style*="flex"] {
        gap: 0.2rem !important;
    }
    /* 所有 flex 布局容器 */
    div[style*="display: flex"][style*="gap"],
    div[style*="flex-flow: column"],
    div[style*="flex-flow:column"],
    div[style*="gap"] {
        gap: 0.2rem !important;
    }
    
    /* ==================== 列布局优化 ==================== */
    /* 列容器内边距 */
    [data-testid="column"] {
        padding-left: 0.2rem !important;
        padding-right: 0.2rem !important;
    }
    /* 列容器之间的间距 */
    [data-testid="column"] + [data-testid="column"] {
        margin-left: 0.2rem !important;
    }
    /* 列内组件间距优化 */
    [data-testid="column"] .stMetric,
    [data-testid="column"] .stButton,
    [data-testid="column"] .stTextInput,
    [data-testid="column"] .stSelectbox {
        padding-left: 0.2rem !important;
        padding-right: 0.2rem !important;
    }
    
    /* ==================== 表格样式优化 ==================== */
    .stDataFrame table {
        border-collapse: collapse;
    }
    .stDataFrame th {
        background-color: #f8f9fa;
        font-weight: 600;
        padding: 0.75rem;
    }
    .stDataFrame td {
        padding: 0.5rem 0.75rem;
    }
    .stDataFrame tr:hover {
        background-color: #f8f9fa;
    }
    
    /* ==================== 图表容器间距 ==================== */
    [data-testid="stPlotlyChart"],
    .stPlotlyChart {
        margin-bottom: 0.2rem !important;
    }
    
    /* ==================== 通用工具样式 ==================== */
    /* 隐藏元素 */
    .hide {
        display: none !important;
    }
    /* 文本对齐 */
    .text-center {
        text-align: center !important;
    }
    .text-left {
        text-align: left !important;
    }
    .text-right {
        text-align: right !important;
    }
    /* 间距工具类 */
    .mb-0 { margin-bottom: 0 !important; }
    .mb-1 { margin-bottom: 0.2rem !important; }
    .mt-0 { margin-top: 0 !important; }
    .mt-1 { margin-top: 0.2rem !important; }
    
    /* ==================== 响应式设计 ==================== */
    @media (max-width: 768px) {
        /* 移动端标题样式 */
        .main-header,
        h1.main-header {
            font-size: 1.2rem !important;
            margin-top: 1rem !important;
        }
        .section-header,
        h2.section-header {
            font-size: 1rem !important;
        }
        /* 移动端容器内边距 */
        .main .block-container,
        [data-testid="stMainBlockContainer"] {
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
        }
        /* 移动端列间距 */
        [data-testid="column"] {
            padding-left: 0.1rem !important;
            padding-right: 0.1rem !important;
        }
        /* 移动端 Metric 组件 */
        .stMetric [data-testid="stMetricValue"] {
            font-size: 1.2rem !important;
        }
        .stMetric label {
            font-size: 0.75rem !important;
        }
    }
    </style>
    """

def get_metric_delta_script():
    """
    获取涨跌幅颜色动态设置脚本
    
    Returns:
        str: JavaScript代码字符串
    """
    return """
    <script>
    // 动态设置涨跌幅颜色
    (function() {
        function updateMetricDeltaColors() {
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
        }
        // 初始执行
        updateMetricDeltaColors();
        // 延迟执行（等待Streamlit渲染完成）
        setTimeout(updateMetricDeltaColors, 200);
        setTimeout(updateMetricDeltaColors, 500);
    })();
    </script>
    """

def apply_common_styles(additional_styles=""):
    """
    应用通用样式到当前页面
    
    Args:
        additional_styles: 可选的额外样式CSS字符串，用于页面特定的样式
    """
    styles = get_common_styles()
    script = get_metric_delta_script()
    st.markdown(styles + additional_styles + script, unsafe_allow_html=True)

def get_dashboard_specific_styles():
    """
    获取仪表盘页面特定的样式（用于实时和历史仪表盘）
    
    Returns:
        str: CSS样式字符串
    """
    return """
    <style>
    /* 仪表盘特定样式 */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem;
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
        font-size: 1.5rem;
        font-weight: bold;
    }
    .stRadio > div {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        padding: 1rem;
        border-radius: 12px;
        border: 2px solid #e9ecef;
        margin-bottom: 1rem;
    }
    .dashboard-type-info {
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    .dashboard-type-info.realtime {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(59, 130, 246, 0.08) 100%);
        border-left: 4px solid #3b82f6;
        color: #1e40af;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
    }
    .dashboard-type-info.history {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(139, 92, 246, 0.08) 100%);
        border-left: 4px solid #8b5cf6;
        color: #6b21a8;
        box-shadow: 0 2px 8px rgba(139, 92, 246, 0.2);
    }
    .data-source-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }
    .data-source-badge.realtime {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
    }
    .data-source-badge.database {
        background: linear-gradient(135deg, #8b5cf6, #7c3aed);
        color: white;
    }
    </style>
    """

def get_calendar_specific_styles():
    """
    获取复盘日历页面特定的样式
    
    Returns:
        str: CSS样式字符串
    """
    return """
    <style>
    /* 日历特定样式 */
    .calendar-container {
        background: transparent;
        padding: 0;
        margin: 0.2rem ;
    }
    .calendar-weekday {
        text-align: center;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 0.5rem 0.1rem;
        color: #495057;
        margin-bottom: 0.1rem;
    }
    .calendar-day-cell {
        border-radius: 4px;
        padding: 0.2rem;
        cursor: pointer;
        position: relative;
        margin: 0.1rem;
        display: flex;
        flex-direction: column;
        overflow: hidden;

    }
    .day-number {
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.2rem;
        text-align: right;
        color: #212529;
    }
    .selected .day-number {
        color: white;
        font-weight: 700;
    }
    .day-info {
        font-size: 0.7rem;
        line-height: 1;
    }
    .group-label {
        font-size: 0.6rem;
        font-weight: 600;
        color: #6b7280;
        text-align: center;
        margin-bottom: 0.2rem;
        padding: 0.1rem 0.2rem;
        background: transparent;
        display: inline-block;
        width: 100%;
    }
    .index-group {
        margin-bottom: 0.3rem;
        padding-bottom: 0.2rem;
    }
    .sector-group {
        margin-top: 0.3rem;
        padding-top: 0.3rem;
        border-top: 1px solid rgba(0, 0, 0, 0.1);
        position: relative;
    }
    .sector-group::before {
        display: none;
    }
    .index-badge {
        display: block;
        padding: 0.15rem 0.25rem;
        border-radius: 3px;
        font-size: 0.7rem;
        font-weight: 500;
        margin: 0.1rem 0;
        text-align: center;
        width: 100%;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        position: relative;
        border: none;
    }
    .index-badge.positive {
        background: rgba(239, 68, 68, 0.1);
        color: #dc2626;
    }
    .index-badge.negative {
        background: rgba(16, 185, 129, 0.1);
        color: #059669;
    }
    .sector-badge {
        display: block;
        padding: 0.15rem 0.25rem;
        border-radius: 3px;
        font-size: 0.7rem;
        font-weight: 500;
        margin: 0.1rem 0;
        text-align: center;
        width: 100%;
        background: rgba(102, 126, 234, 0.1);
        color: #4338ca;
        border: none;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .selected .index-badge.positive,
    .selected .index-badge.negative,
    .selected .sector-badge {
        background: rgba(255, 255, 255, 0.25);
        color: white;
        font-weight: 600;
    }
    .selected .group-label {
        color: rgba(255, 255, 255, 0.9);
        font-weight: 700;
        background: transparent;
    }
    .selected .sector-group {
        border-top-color: rgba(255, 255, 255, 0.25);
    }
    .today-indicator {
        position: absolute;
        top: 0.3rem;
        right: 0.3rem;
        width: 0.5rem;
        height: 0.5rem;
        background: #ef4444;
        border-radius: 50%;
    }
    .empty-day {
        color: #adb5bd;
        background: #f8f9fa;
        border-color: #e9ecef;
        opacity: 0.5;
    }
    .day-button-wrapper {
        margin-bottom: 0.2rem;
    }
    button[key^="day_btn_"] {
        display: none !important;
    }
    button[kind="primary"] {
        background: #1f77b4 !important;
        color: white !important;
        border: none !important;
    }
    button[kind="secondary"] {
        background: #f0f7ff !important;
        color: #1f77b4 !important;
        border: 1px solid #b3d9ff !important;
    }
    button[kind="tertiary"] {
        background: #ffffff !important;
        color: #6c757d !important;
        border: 1px solid #dee2e6 !important;
    }
    [data-testid="column"] {
        padding-left: 0.15rem !important;
        padding-right: 0.15rem !important;
    }
    div[data-testid="column"] > div {
        box-shadow: none !important;
    }
    div[data-testid="column"] button {
        margin-bottom: 0.3rem !important;
    }
    div[data-testid="column"] .stMarkdown {
        margin-top: 0.2rem !important;
        margin-bottom: 0.2rem !important;
    }
    .index-group + .sector-group {
        margin-top: 0.3rem !important;
    }
    .empty-day-cell {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        opacity: 0.5;
    }
    </style>
    """

def get_scheduler_specific_styles():
    """
    获取定时任务管理页面特定的样式
    
    Returns:
        str: CSS样式字符串
    """
    return """
    <style>
    /* 定时任务管理特定样式 */
    .status-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        margin-bottom: 1rem;
    }
    .status-running {
        border-color: #28a745;
    }
    .status-stopped {
        border-color: #dc3545;
    }
    .job-card {
        background: #ffffff;
        padding: 1.2rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .result-success {
        color: #28a745;
        font-weight: bold;
    }
    .result-error {
        color: #dc3545;
        font-weight: bold;
    }
    </style>
    """

