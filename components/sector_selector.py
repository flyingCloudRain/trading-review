#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
板块选择器组件（优化版UI）
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.focused_sectors import get_focused_sectors

def render_sector_selector(df: pd.DataFrame, default_selected: list = None, max_display: int = 20, use_focused_as_default: bool = True):
    """
    渲染板块选择器（优化版UI）
    
    Args:
        df: 包含板块数据的DataFrame
        default_selected: 默认选中的板块列表
        max_display: 最大显示数量（用于性能优化）
        use_focused_as_default: 是否使用重点关注板块作为默认值（默认True）
    
    Returns:
        list: 选中的板块列表
    """
    if df.empty or 'name' not in df.columns:
        return []
    
    all_sectors = sorted(df['name'].unique().tolist())
    total_count = len(all_sectors)
    
    # 初始化session_state用于管理选择状态
    key = 'sector_selected_' + str(id(df))
    if key not in st.session_state:
        if use_focused_as_default:
            # 优先使用重点关注板块作为默认值
            focused_sectors = get_focused_sectors()
            # 过滤出在当前数据中存在的重点关注板块
            available_focused = [s for s in focused_sectors if s in all_sectors]
            
            if available_focused:
                st.session_state[key] = available_focused
            elif default_selected is not None:
                st.session_state[key] = default_selected
            else:
                st.session_state[key] = []
        else:
            # 不使用重点关注板块，直接使用传入的default_selected或空列表
            if default_selected is not None:
                st.session_state[key] = default_selected
            else:
                st.session_state[key] = []
    
    # 直接使用所有板块（已移除搜索功能）
    filtered_sectors = all_sectors
    
    # 多选下拉框
    current_selected = st.session_state[key]
    
    # 在过滤结果中显示已选择的板块
    filtered_selected = [s for s in current_selected if s in filtered_sectors]
    
    selected_in_filter = st.multiselect(
        "📋 选择板块（可多选）",
        options=filtered_sectors,
        default=filtered_selected,  # 默认显示已选择的板块，如果为空则显示为空
        help=f"共 {len(filtered_sectors)} 个板块可选，当前已选择 {len(current_selected)} 个。未选择时显示全部板块。",
        label_visibility="visible"
    )
    
    # 更新选择状态
    st.session_state[key] = selected_in_filter
    
    # 性能提示
    selected_count = len(st.session_state[key])
    if selected_count > max_display:
        st.warning(
            f"⚠️ **性能提示**: 已选择 {selected_count} 个板块，建议选择不超过 {max_display} 个以保持最佳性能。"
        )
    
    # 显示已选择的板块列表（可展开，仅在选择了板块时显示）
    if selected_count > 0:
        with st.expander(f"📋 已选择的板块列表 ({selected_count})", expanded=False):
            if selected_count <= 20:
                # 少于20个时，单列显示
                for i, sector in enumerate(sorted(st.session_state[key]), 1):
                    st.text(f"{i}. {sector}")
            else:
                # 多于20个时，分三列显示
                col_list1, col_list2, col_list3 = st.columns(3)
                sorted_selected = sorted(st.session_state[key])
                third = len(sorted_selected) // 3
                with col_list1:
                    for i, sector in enumerate(sorted_selected[:third], 1):
                        st.text(f"{i}. {sector}")
                with col_list2:
                    for i, sector in enumerate(sorted_selected[third:2*third], third + 1):
                        st.text(f"{i}. {sector}")
                with col_list3:
                    for i, sector in enumerate(sorted_selected[2*third:], 2*third + 1):
                        st.text(f"{i}. {sector}")
    
    # 如果未选择任何板块，返回全部板块（默认显示全部）
    if selected_count == 0:
        return all_sectors
    else:
        return st.session_state[key]
