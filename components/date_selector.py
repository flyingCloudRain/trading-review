#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日期选择器组件
"""
import streamlit as st
from datetime import date, timedelta
from utils.time_utils import get_utc8_date

def render_date_selector():
    """
    渲染日期选择器
    
    Returns:
        tuple: (start_date, end_date) 日期范围
    """
    col1, col2 = st.columns(2)
    
    with col1:
        date_type = st.radio(
            "选择方式",
            ["单日", "日期范围"],
            horizontal=True
        )
    
    today = get_utc8_date()
    
    if date_type == "单日":
        selected_date = st.date_input(
            "选择日期",
            value=today,
            max_value=today
        )
        return selected_date, selected_date
    else:
        with col2:
            date_range = st.date_input(
                "选择日期范围",
                value=(today - timedelta(days=7), today),
                max_value=today
            )
            if len(date_range) == 2:
                return date_range[0], date_range[1]
            return today - timedelta(days=7), today

