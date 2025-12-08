#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
关注管理页面 - 合并关注板块和关注指数管理
"""
import streamlit as st
from pathlib import Path
import sys

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.focused_sectors import (
    get_focused_sectors,
    save_focused_sectors,
    add_focused_sector,
    remove_focused_sector
)
from utils.focused_indices import (
    get_focused_indices,
    save_focused_indices,
    add_focused_index,
    remove_focused_index
)
from utils.data_loader import load_sector_data
from services.stock_index_service import StockIndexService
from utils.index_base_config import (
    load_index_base_config,
    get_index_name,
    search_indices
)
from utils.time_utils import get_utc8_date
from datetime import timedelta

st.set_page_config(
    page_title="关注管理",
    page_icon="⭐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 统一标题样式
st.markdown("""
    <style>
    /* 统一主标题样式 */
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

st.markdown('<h1 class="main-header">⭐ 关注管理</h1>', unsafe_allow_html=True)

# 使用标签页组织两个功能
tab1, tab2 = st.tabs(["📊 关注板块管理", "📈 关注指数管理"])

# ==================== 标签页1: 关注板块管理 ====================
with tab1:
    # 获取当前重点关注板块
    focused_sectors = get_focused_sectors()
    
    # 初始化过滤后的板块列表
    filtered_focused = focused_sectors.copy() if focused_sectors else []
    
    # 显示当前重点关注板块
    st.subheader("📋 当前重点关注板块")
    
    if focused_sectors:
        # 统计信息 - 使用原生组件
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.metric("重点关注板块数", len(focused_sectors))
        
        # 搜索功能
        search_term = st.text_input(
            "🔍 搜索板块",
            placeholder="输入板块名称...",
            help="快速查找重点关注板块",
            key="search_focused_sectors"
        )
        
        # 过滤板块
        if search_term:
            filtered_focused = [s for s in focused_sectors if search_term.lower() in s.lower()]
        else:
            filtered_focused = focused_sectors.copy()
        
        if filtered_focused:
            # 板块列表显示 - 简洁设计
            for i, sector in enumerate(filtered_focused):
                col_name, col_btn = st.columns([5, 1])
                
                with col_name:
                    st.write(f"{i+1}. {sector}")
                
                with col_btn:
                    if st.button("删除", key=f"delete_sector_{sector}_{i}", use_container_width=True, 
                               help=f"删除 {sector}", type="secondary"):
                        if remove_focused_sector(sector):
                            st.success(f"✅ 已移除 '{sector}'")
                            st.rerun()
                        else:
                            st.error("❌ 移除失败")
        else:
            st.info(f"未找到包含 '{search_term}' 的重点关注板块")
    else:
        st.info("⭐ 当前没有设置重点关注板块。添加后，它们将在板块信息和板块趋势分析页面中默认选中。")
    
    st.markdown("---")
    
    # 获取所有可用板块
    try:
        today = get_utc8_date()
        df = load_sector_data(today - timedelta(days=14), today)
        all_sectors = sorted(df['name'].unique().tolist()) if not df.empty else []
        
        if all_sectors:
            # 过滤掉已经是重点关注板块的
            available_sectors = [s for s in all_sectors if s not in focused_sectors]
            
            if available_sectors:
                # 搜索可用板块
                search_available = st.text_input(
                    "🔍 搜索可用板块",
                    placeholder="输入板块名称...",
                    key="search_available_sectors",
                    help="快速查找要添加的板块"
                )
                
                if search_available:
                    filtered_available = [s for s in available_sectors if search_available.lower() in s.lower()]
                else:
                    filtered_available = available_sectors
                
                if filtered_available:
                    col_add1, col_add2, col_add3 = st.columns([3, 1, 1])
                    
                    with col_add1:
                        selected_sector = st.selectbox(
                            "选择要添加的板块",
                            options=filtered_available,
                            help=f"共 {len(filtered_available)} 个可用板块（已过滤 {len(available_sectors) - len(filtered_available)} 个）",
                            key="select_sector"
                        )
                    
                    with col_add2:
                        if st.button("➕ 添加", use_container_width=True, type="primary", key="add_sector"):
                            if add_focused_sector(selected_sector):
                                st.success(f"✅ 已添加 '{selected_sector}'")
                                st.rerun()
                            else:
                                st.error("❌ 添加失败")
                    
                    with col_add3:
                        if st.button("📦 批量", use_container_width=True, key="batch_add_sector_btn"):
                            st.info("💡 在下方多选框中选择多个板块，然后点击批量添加")
                    
                    # 批量添加功能
                    with st.expander("📦 批量添加板块", expanded=False):
                        multi_selected = st.multiselect(
                            "选择要批量添加的板块（可多选）",
                            options=filtered_available,
                            help="选择多个板块后，点击批量添加按钮",
                            key="multi_select_sectors"
                        )
                        
                        if multi_selected:
                            if st.button(f"✅ 批量添加 ({len(multi_selected)} 个)", use_container_width=True, type="primary", key="batch_add_sectors"):
                                success_count = 0
                                for sector in multi_selected:
                                    if add_focused_sector(sector):
                                        success_count += 1
                                if success_count > 0:
                                    st.success(f"✅ 成功添加 {success_count} 个板块")
                                    st.rerun()
                                else:
                                    st.error("❌ 批量添加失败")
                else:
                    st.info(f"未找到包含 '{search_available}' 的可用板块")
            else:
                st.info("✨ 所有可用板块都已经是重点关注板块了")
        else:
            st.warning("⚠️ 无法获取板块列表，请确保数据库中有数据")
    except Exception as e:
        st.error(f"❌ 获取板块列表失败: {str(e)}")

# ==================== 标签页2: 关注指数管理 ====================
with tab2:
    # 获取当前关注指数
    focused_indices = get_focused_indices()
    
    # 初始化过滤后的指数列表
    filtered_focused = focused_indices.copy() if focused_indices else []
    
    # 显示当前关注指数
    st.subheader("📋 当前关注指数")
    
    if focused_indices:
        # 统计信息 - 使用原生组件
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.metric("关注指数数", len(focused_indices))
        
        # 搜索功能
        search_term = st.text_input(
            "🔍 搜索指数",
            placeholder="输入指数代码或名称...",
            help="快速查找关注指数",
            key="search_focused_indices"
        )
        
        # 获取指数详细信息用于显示（从基础配置获取）
        index_dict = {}
        try:
            # 从基础配置加载所有指数信息
            base_indices = load_index_base_config()
            for idx in base_indices:
                code_6digit = idx.get('code', '')
                name = idx.get('name', '')
                if code_6digit:
                    index_dict[code_6digit] = name
        except Exception as e:
            # 如果基础配置加载失败，使用预定义映射
            default_index_names = {
                '000001': '上证指数',
                '000016': '上证50',
                '000300': '沪深300',
                '000688': '科创50',
                '000852': '中证1000',
                '000905': '中证500',
                '000985': '中证全指',
                '399006': '创业板指',
                '399106': '深证综合指数',
            }
            for code, name in default_index_names.items():
                from services.stock_index_service import StockIndexService
                code_6digit = StockIndexService.normalize_index_code(code)
                index_dict[code_6digit] = name
        
        # 过滤指数
        if search_term:
            filtered_focused = []
            for code in focused_indices:
                name = index_dict.get(code, '')
                if search_term.lower() in code.lower() or search_term.lower() in name.lower():
                    filtered_focused.append(code)
        else:
            filtered_focused = focused_indices.copy()
        
        if filtered_focused:
            # 指数列表显示 - 简洁设计
            for i, index_code in enumerate(filtered_focused):
                # 将关注指数代码标准化为6位格式，用于查找名称
                from services.stock_index_service import StockIndexService
                code_6digit = StockIndexService.normalize_index_code(index_code)
                index_name = index_dict.get(code_6digit, index_code)
                
                # 如果名称还是代码，说明没找到，尝试使用原始代码查找
                if index_name == index_code or index_name == code_6digit:
                    index_name = index_dict.get(index_code, index_code)
                
                col_name, col_btn = st.columns([5, 1])
                
                with col_name:
                    st.write(f"{i+1}. {index_name}（{index_code}）")
                
                with col_btn:
                    if st.button("删除", key=f"delete_index_{index_code}_{i}", use_container_width=True, 
                               help=f"删除 {index_name}", type="secondary"):
                        if remove_focused_index(index_code):
                            st.success(f"✅ 已移除 '{index_name}'")
                            st.rerun()
                        else:
                            st.error("❌ 移除失败")
        else:
            st.info(f"未找到包含 '{search_term}' 的关注指数")
    else:
        st.info("⭐ 当前没有设置关注指数。添加后，它们将在指数信息页面中默认显示。")
    
    st.markdown("---")
    
    # 从基础配置获取所有可用指数
    st.subheader("➕ 添加关注指数")
    
    try:
        with st.spinner("🔄 正在加载指数基础配置..."):
            # 从基础配置加载所有指数
            base_indices = load_index_base_config()
        
        if base_indices:
            # 获取已关注的指数代码（标准化为6位格式）
            from services.stock_index_service import StockIndexService
            focused_codes_6digit = set()
            for code in focused_indices:
                code_6digit = StockIndexService.normalize_index_code(code)
                focused_codes_6digit.add(code_6digit)
            
            # 过滤出未关注的指数
            available_indices = [
                idx for idx in base_indices 
                if idx['code'] not in focused_codes_6digit
            ]
            
            if available_indices:
                st.info(f"📊 基础配置中共有 {len(base_indices)} 个指数，其中 {len(available_indices)} 个可添加")
                
                # 创建显示选项（指数名称（指数代码）格式）
                display_options = []
                code_to_index = {}
                
                # 添加所有可用指数
                for idx in available_indices:
                    display_text = f"{idx['name']}（{idx['code']}）"
                    display_options.append(display_text)
                    code_to_index[display_text] = idx['code']
                
                col_add1, col_add2, col_add3 = st.columns([3, 1, 1])
                
                with col_add1:
                    # 初始化 session_state
                    if 'index_search_input' not in st.session_state:
                        st.session_state.index_search_input = "请输入需要添加的指数或名称"
                    
                    # 添加 CSS 和 JavaScript 来实现在输入框获得焦点时自动清除提示文案
                    st.markdown("""
                    <style>
                    /* 为搜索输入框添加样式 */
                    div[data-testid*="textInput"] input {
                        color: #262730;
                    }
                    div[data-testid*="textInput"] input::placeholder {
                        color: #9ca3af;
                    }
                    </style>
                    <script>
                    // 等待 Streamlit 组件加载完成
                    function setupAutoClearPlaceholder() {
                        // 查找所有文本输入框
                        const inputs = document.querySelectorAll('input[data-testid*="textInput"]');
                        inputs.forEach((input, index) => {
                            // 检查是否是我们要处理的输入框（通过 placeholder 或位置判断）
                            if (input.placeholder && input.placeholder.includes('请输入需要添加的指数')) {
                                // 如果当前值是提示文案，在获得焦点时清除
                                if (input.value === input.placeholder || input.value === '请输入需要添加的指数或名称') {
                                    input.addEventListener('focus', function() {
                                        if (this.value === '请输入需要添加的指数或名称' || this.value === this.placeholder) {
                                            this.value = '';
                                            this.style.color = '#262730';
                                        }
                                    }, { once: true });
                                    
                                    // 失去焦点时，如果为空则恢复提示文案
                                    input.addEventListener('blur', function() {
                                        if (this.value === '') {
                                            this.value = '请输入需要添加的指数或名称';
                                            this.style.color = '#9ca3af';
                                        }
                                    });
                                }
                            }
                        });
                    }
                    
                    // 页面加载后执行
                    if (document.readyState === 'loading') {
                        document.addEventListener('DOMContentLoaded', setupAutoClearPlaceholder);
                    } else {
                        setupAutoClearPlaceholder();
                    }
                    
                    // Streamlit 页面更新后也执行（使用 MutationObserver）
                    const observer = new MutationObserver(setupAutoClearPlaceholder);
                    observer.observe(document.body, { childList: true, subtree: true });
                    </script>
                    """, unsafe_allow_html=True)
                    
                    # 创建搜索输入框
                    # 如果当前值是提示文案，使用空字符串，否则使用实际值
                    current_value = st.session_state.index_search_input
                    if current_value == "请输入需要添加的指数或名称":
                        input_value = ""
                    else:
                        input_value = current_value
                    
                    search_input = st.text_input(
                        "🔍 搜索指数",
                        value=input_value,
                        placeholder="请输入需要添加的指数或名称",
                        help=f"共 {len(available_indices)} 个可用指数，输入关键词快速查找（点击输入框自动清除提示）",
                        key="index_search_input_widget"
                    )
                    
                    # 更新 session_state（如果输入框为空，保持提示文案）
                    if search_input:
                        st.session_state.index_search_input = search_input
                    else:
                        # 如果输入框为空，检查是否应该显示提示文案
                        # 这里我们保持为空，让 placeholder 显示
                        st.session_state.index_search_input = ""
                    
                    # 根据搜索关键词过滤选项
                    if search_input and search_input.strip():
                        filtered_options = [
                            opt for opt in display_options
                            if search_input.lower() in opt.lower()
                        ]
                    else:
                        filtered_options = display_options
                    
                    # 添加默认提示选项（如果没有搜索或搜索为空）
                    if not search_input or not search_input.strip():
                        default_option = "请输入需要添加的指数或名称"
                        if default_option not in filtered_options:
                            filtered_options.insert(0, default_option)
                            code_to_index[default_option] = None
                    elif not filtered_options:
                        filtered_options = ["未找到匹配的指数"]
                        code_to_index["未找到匹配的指数"] = None
                    
                    selected_display = st.selectbox(
                        "选择要添加的指数",
                        options=filtered_options,
                        help=f"共 {len(available_indices)} 个可用指数",
                        key="select_index"
                    )
                    selected_code = code_to_index.get(selected_display)
                    
                    with col_add2:
                        if st.button("➕ 添加", use_container_width=True, type="primary", key="add_index"):
                            if selected_code is None:
                                st.warning("⚠️ 请先选择要添加的指数")
                            else:
                                # 添加时使用原始格式的代码（从基础配置中获取）
                                if add_focused_index(selected_code):
                                    index_name = get_index_name(selected_code)
                                    st.success(f"✅ 已添加 '{index_name}（{selected_code}）'")
                                    st.rerun()
                                else:
                                    st.error("❌ 添加失败")
                    
                    with col_add3:
                        if st.button("📦 批量", use_container_width=True, key="batch_add_index_btn"):
                            st.info("💡 在下方多选框中选择多个指数，然后点击批量添加")
                    
                    # 批量添加功能
                    with st.expander("📦 批量添加指数", expanded=False):
                        # 批量添加时不包含默认选项
                        batch_options = [opt for opt in display_options if opt != default_option]
                        multi_selected_display = st.multiselect(
                            "选择要批量添加的指数（可多选）",
                            options=batch_options,
                            help="选择多个指数后，点击批量添加按钮",
                            key="multi_select_indices"
                        )
                        
                        if multi_selected_display:
                            multi_selected_codes = [code_to_index[disp] for disp in multi_selected_display if code_to_index.get(disp) is not None]
                            if multi_selected_codes:
                                if st.button(f"✅ 批量添加 ({len(multi_selected_codes)} 个)", use_container_width=True, type="primary", key="batch_add_indices"):
                                    success_count = 0
                                    for code in multi_selected_codes:
                                        if add_focused_index(code):
                                            success_count += 1
                                    if success_count > 0:
                                        st.success(f"✅ 成功添加 {success_count} 个指数")
                                        st.rerun()
                                    else:
                                        st.error("❌ 批量添加失败")
                            else:
                                st.warning("⚠️ 请选择有效的指数")
            else:
                st.info("✨ 所有基础配置中的指数都已经是关注指数了")
        else:
            st.warning("⚠️ 基础配置为空，请先运行脚本生成基础配置")
            st.info("💡 运行命令: `python scripts/generate_index_base_config.py`")
    except Exception as e:
        st.error(f"❌ 加载指数基础配置失败: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

# 说明信息 - 简洁设计
st.markdown("---")
st.info("""
💡 **使用说明：**
- **关注板块：** 添加后，将在板块信息和板块趋势分析页面中默认选中
- **关注指数：** 添加后，将在指数信息页面中默认显示
- 可通过搜索功能快速查找，支持单个和批量添加
""")

