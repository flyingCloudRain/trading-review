#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KPI指标卡片组件（美化版）
"""
import streamlit as st

def render_kpi_cards(metrics: list):
    """
    渲染KPI指标卡片（美化版）
    
    Args:
        metrics: [(label, value, delta), ...] 格式的指标列表
                delta为可选，如果提供则显示变化值
    """
    if not metrics:
        return
    
    # 添加自定义样式
    st.markdown("""
        <style>
        .kpi-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        .metric-container {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)
    
    cols = st.columns(len(metrics))
    for i, metric in enumerate(metrics):
        with cols[i]:
            if len(metric) == 3:
                label, value, delta = metric
                st.metric(label, value, delta)
            else:
                label, value = metric
                st.metric(label, value)

