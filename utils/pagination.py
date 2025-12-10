#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据表格分页工具
提供通用的分页功能，用于在Streamlit中显示大量数据
"""
import streamlit as st
import pandas as pd
from typing import Optional


def paginate_dataframe(
    df: pd.DataFrame,
    page_size: int = 50,
    key_prefix: str = "pagination",
    show_info: bool = True
) -> pd.DataFrame:
    """
    对DataFrame进行分页显示
    
    Args:
        df: 要分页的DataFrame
        page_size: 每页显示的行数，默认50
        key_prefix: 用于session_state的唯一前缀
        show_info: 是否显示分页信息（当前页/总页数等）
    
    Returns:
        当前页的DataFrame
    """
    if df.empty:
        return df
    
    total_rows = len(df)
    total_pages = (total_rows + page_size - 1) // page_size  # 向上取整
    
    # 初始化session_state
    page_key = f"{key_prefix}_page"
    if page_key not in st.session_state:
        st.session_state[page_key] = 1
    
    current_page = st.session_state[page_key]
    
    # 确保当前页在有效范围内
    if current_page < 1:
        current_page = 1
    elif current_page > total_pages:
        current_page = total_pages
    
    # 显示分页控件
    if show_info and total_pages > 1:
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
        
        with col1:
            if st.button("◀◀ 首页", key=f"{key_prefix}_first", disabled=(current_page == 1)):
                st.session_state[page_key] = 1
                st.rerun()
        
        with col2:
            if st.button("◀ 上一页", key=f"{key_prefix}_prev", disabled=(current_page == 1)):
                st.session_state[page_key] = current_page - 1
                st.rerun()
        
        with col3:
            # 显示当前页信息
            page_input = st.number_input(
                f"第 {current_page} 页 / 共 {total_pages} 页",
                min_value=1,
                max_value=total_pages,
                value=current_page,
                key=f"{key_prefix}_input",
                label_visibility="collapsed"
            )
            if page_input != current_page:
                st.session_state[page_key] = int(page_input)
                st.rerun()
        
        with col4:
            if st.button("下一页 ▶", key=f"{key_prefix}_next", disabled=(current_page == total_pages)):
                st.session_state[page_key] = current_page + 1
                st.rerun()
        
        with col5:
            if st.button("末页 ▶▶", key=f"{key_prefix}_last", disabled=(current_page == total_pages)):
                st.session_state[page_key] = total_pages
                st.rerun()
        
        # 显示数据统计信息
        start_idx = (current_page - 1) * page_size
        end_idx = min(start_idx + page_size, total_rows)
        st.caption(f"📊 显示第 {start_idx + 1} - {end_idx} 行，共 {total_rows} 行数据")
    
    # 计算当前页的数据范围
    start_idx = (current_page - 1) * page_size
    end_idx = start_idx + page_size
    
    # 返回当前页的数据
    return df.iloc[start_idx:end_idx]


def paginate_dataframe_with_size_selector(
    df: pd.DataFrame,
    default_page_size: int = 50,
    page_size_options: list = [20, 50, 100, 200, 500],
    key_prefix: str = "pagination",
    show_info: bool = True
):
    """
    带页面大小选择器的分页功能
    注意：此函数只返回分页后的数据，不显示控件。
    需要在显示数据表格后调用 show_pagination_controls 来显示分页控件。
    
    Args:
        df: 要分页的DataFrame
        default_page_size: 默认每页显示的行数
        page_size_options: 可选的页面大小选项
        key_prefix: 用于session_state的唯一前缀
        show_info: 是否显示分页信息（用于后续显示控件）
    
    Returns:
        (当前页的DataFrame, 当前页面大小)
    """
    if df.empty:
        return df, default_page_size
    
    # 获取或初始化页面大小
    page_size_key = f"{key_prefix}_page_size"
    if page_size_key not in st.session_state:
        st.session_state[page_size_key] = default_page_size
    
    # 从session_state获取当前页面大小（可能已被show_pagination_controls更新）
    page_size = st.session_state[page_size_key]
    
    # 确保页面大小在有效范围内
    if page_size not in page_size_options:
        page_size = default_page_size
        st.session_state[page_size_key] = page_size
    
    # 计算分页
    total_rows = len(df)
    total_pages = (total_rows + page_size - 1) // page_size if page_size > 0 else 1
    
    # 初始化或获取当前页码
    page_key = f"{key_prefix}_page"
    if page_key not in st.session_state:
        st.session_state[page_key] = 1
    
    current_page = st.session_state[page_key]
    
    # 确保当前页在有效范围内
    if current_page < 1:
        current_page = 1
        st.session_state[page_key] = current_page
    elif current_page > total_pages and total_pages > 0:
        current_page = total_pages
        st.session_state[page_key] = current_page
    
    # 计算当前页的数据范围
    start_idx = (current_page - 1) * page_size
    end_idx = min(start_idx + page_size, total_rows)
    
    # 确保索引有效
    if start_idx < 0:
        start_idx = 0
    if end_idx > total_rows:
        end_idx = total_rows
    
    # 返回当前页的数据（使用copy避免SettingWithCopyWarning）
    if start_idx >= end_idx or start_idx >= total_rows:
        return pd.DataFrame(columns=df.columns), page_size
    
    return df.iloc[start_idx:end_idx].copy(), page_size


def show_pagination_controls(
    df: pd.DataFrame,
    page_size: int,
    key_prefix: str = "pagination",
    show_info: bool = True
):
    """
    显示分页控件（页面大小选择器和翻页按钮）
    应该在显示数据表格后调用此函数
    
    Args:
        df: 完整的DataFrame（未分页的）
        page_size: 当前每页显示的行数（初始值）
        key_prefix: 用于session_state的唯一前缀
        show_info: 是否显示分页信息
    """
    if df.empty:
        return
    
    # 页面大小选择器
    page_size_key = f"{key_prefix}_page_size"
    if page_size_key not in st.session_state:
        st.session_state[page_size_key] = page_size
    
    page_size_options = [20, 50, 100, 200, 500]
    
    col_size, _ = st.columns([1, 4])
    with col_size:
        current_page_size = st.selectbox(
            "每页显示行数",
            options=page_size_options,
            index=page_size_options.index(st.session_state[page_size_key]) if st.session_state[page_size_key] in page_size_options else 0,
            key=f"{key_prefix}_size_selector"
        )
        if current_page_size != st.session_state[page_size_key]:
            st.session_state[page_size_key] = current_page_size
            # 重置到第一页
            page_key = f"{key_prefix}_page"
            st.session_state[page_key] = 1
            st.rerun()
    
    # 使用当前选择的页面大小
    current_page_size = st.session_state[page_size_key]
    
    total_rows = len(df)
    # 更新总页数（基于当前的页面大小）
    total_pages = (total_rows + current_page_size - 1) // current_page_size if current_page_size > 0 else 1
    
    # 获取当前页
    page_key = f"{key_prefix}_page"
    if page_key not in st.session_state:
        st.session_state[page_key] = 1
    
    current_page = st.session_state[page_key]
    if current_page > total_pages:
        current_page = total_pages
        st.session_state[page_key] = current_page
    
    # 显示分页控件
    if show_info:
        # 如果有多页，显示完整的翻页控件
        if total_pages > 1:
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
            
            with col1:
                if st.button("◀◀ 首页", key=f"{key_prefix}_first", disabled=(current_page == 1)):
                    st.session_state[page_key] = 1
                    st.rerun()
            
            with col2:
                if st.button("◀ 上一页", key=f"{key_prefix}_prev", disabled=(current_page == 1)):
                    st.session_state[page_key] = current_page - 1
                    st.rerun()
            
            with col3:
                # 显示当前页信息
                page_input = st.number_input(
                    f"第 {current_page} 页 / 共 {total_pages} 页",
                    min_value=1,
                    max_value=total_pages,
                    value=current_page,
                    key=f"{key_prefix}_input",
                    label_visibility="collapsed"
                )
                if page_input != current_page:
                    st.session_state[page_key] = int(page_input)
                    st.rerun()
            
            with col4:
                if st.button("下一页 ▶", key=f"{key_prefix}_next", disabled=(current_page == total_pages)):
                    st.session_state[page_key] = current_page + 1
                    st.rerun()
            
            with col5:
                if st.button("末页 ▶▶", key=f"{key_prefix}_last", disabled=(current_page == total_pages)):
                    st.session_state[page_key] = total_pages
                    st.rerun()
        else:
            # 如果只有一页，只显示页码信息
            st.markdown(f"<div style='text-align: center; color: #6b7280; font-size: 0.9rem; margin: 0.5rem 0;'>第 {current_page} 页 / 共 {total_pages} 页</div>", unsafe_allow_html=True)
        
        # 显示数据统计信息（使用当前选择的页面大小）
        start_idx = (current_page - 1) * current_page_size
        end_idx = min(start_idx + current_page_size, total_rows)
        st.caption(f"📊 显示第 {start_idx + 1} - {end_idx} 行，共 {total_rows} 行数据")

