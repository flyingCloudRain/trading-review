#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易日志页面 - 记录和管理交易复盘
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import sys
from datetime import date, datetime, timedelta

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 尝试导入数据库模块
try:
    from database.db import SessionLocal
    from services.trading_review_service import TradingReviewService
    from models.trading_review import TradingReview
    from sqlalchemy import func
    from utils.time_utils import get_utc8_date
    from utils.trading_reasons import (
        get_trading_reasons,
        save_trading_reasons,
        add_trading_reason,
        remove_trading_reason,
        update_trading_reason
    )
    DB_AVAILABLE = True
except (ValueError, RuntimeError) as e:
    DB_AVAILABLE = False
    DB_ERROR = str(e)
except Exception as e:
    DB_AVAILABLE = False
    DB_ERROR = f"数据库连接错误: {str(e)}"

st.set_page_config(
    page_title="交易日志",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 统一标题样式
# 应用统一样式
from utils.page_styles import apply_common_styles
apply_common_styles()

st.markdown('<h1 class="main-header">📝 交易日志</h1>', unsafe_allow_html=True)

# 检查数据库配置
if not DB_AVAILABLE:
    st.error(f"❌ 数据库连接失败: {DB_ERROR}")
    st.info("💡 请检查数据库配置，详细说明请查看 SUPABASE_SETUP.md")
    st.stop()

# 初始化数据库（确保表结构是最新的）
try:
    from database.db import init_db
    if 'trading_reviews_db_initialized' not in st.session_state:
        init_db()
        st.session_state.trading_reviews_db_initialized = True
except Exception as e:
    # 如果初始化失败，记录错误但不阻止应用运行
    st.warning(f"⚠️ 数据库初始化警告: {str(e)}")

# 初始化session state
if 'refresh_logs' not in st.session_state:
    st.session_state.refresh_logs = False
if 'form_reset_counter' not in st.session_state:
    st.session_state.form_reset_counter = 0

# 使用标签页组织功能
tab1, tab2, tab3, tab4 = st.tabs(["📋 交易记录", "➕ 添加记录", "📊 统计分析", "⚙️ 交易原因管理"])

# ==================== 标签页1: 交易记录列表 ====================
with tab1:
    db = SessionLocal()
    try:
        # 获取所有交易记录
        all_reviews = TradingReviewService.get_all_reviews(db)
        
        if not all_reviews:
            st.info("📝 暂无交易记录，请在「添加记录」标签页中添加第一条交易记录")
        else:
            # 筛选选项
            st.markdown('<h2 class="section-header">筛选条件</h2>', unsafe_allow_html=True)
            col_filter1, col_filter2, col_filter3, col_filter4 = st.columns(4)
            
            with col_filter1:
                # 日期筛选
                dates = sorted(set([r.date for r in all_reviews]), reverse=True)
                selected_date_filter = st.selectbox(
                    "📅 选择日期",
                    options=['全部'] + dates,
                    help="按日期筛选交易记录"
                )
            
            with col_filter2:
                # 市场筛选
                markets = sorted(set([r.market for r in all_reviews if hasattr(r, 'market') and r.market]))
                selected_market = st.selectbox(
                    "🌍 选择市场",
                    options=['全部'] + markets if markets else ['全部'],
                    help="按市场筛选交易记录"
                )
            
            with col_filter3:
                # 操作类型筛选
                operations = sorted(set([r.operation for r in all_reviews]))
                selected_operation = st.selectbox(
                    "🔄 操作类型",
                    options=['全部', '买入', '卖出'],
                    format_func=lambda x: {'全部': '全部', '买入': '买入 (buy)', '卖出': '卖出 (sell)'}.get(x, x),
                    help="按操作类型筛选"
                )
            
            with col_filter4:
                # 股票代码/名称搜索
                search_term = st.text_input(
                    "🔍 搜索股票",
                    placeholder="输入股票代码或名称...",
                    help="按股票代码或名称搜索"
                )
            
            # 应用筛选
            filtered_reviews = all_reviews
            if selected_date_filter != '全部':
                filtered_reviews = [r for r in filtered_reviews if r.date == selected_date_filter]
            
            if selected_market != '全部':
                filtered_reviews = [r for r in filtered_reviews if hasattr(r, 'market') and r.market == selected_market]
            
            if selected_operation != '全部':
                op_map = {'买入': 'buy', '卖出': 'sell'}
                filtered_reviews = [r for r in filtered_reviews if r.operation == op_map[selected_operation]]
            
            if search_term and search_term.strip():
                search_lower = search_term.strip().lower()
                filtered_reviews = [
                    r for r in filtered_reviews
                    if search_lower in r.stock_code.lower() or search_lower in r.stock_name.lower()
                ]
            
            # 显示统计信息
            st.markdown('<h2 class="section-header">交易记录列表</h2>', unsafe_allow_html=True)
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            with col_stat1:
                st.metric("总记录数", len(all_reviews))
            with col_stat2:
                st.metric("筛选后记录数", len(filtered_reviews))
            with col_stat3:
                buy_count = len([r for r in filtered_reviews if r.operation == 'buy'])
                sell_count = len([r for r in filtered_reviews if r.operation == 'sell'])
                st.metric("买入/卖出", f"{buy_count} / {sell_count}")
            
            # 显示交易记录表格
            if filtered_reviews:
                # 初始化session state
                if 'action_record_id' not in st.session_state:
                    st.session_state.action_record_id = None
                if 'action_type' not in st.session_state:
                    st.session_state.action_type = None
                
                # 准备数据并显示表格（保持原始数据类型以便编辑）
                records_data = []
                for review in filtered_reviews:
                    # 处理日期：确保是date对象
                    if isinstance(review.date, str):
                        try:
                            review_date = datetime.strptime(review.date, '%Y-%m-%d').date()
                        except:
                            review_date = review.date
                    else:
                        review_date = review.date
                    
                    record_dict = {
                        'ID': review.id,
                        '日期': review_date,
                        '市场': getattr(review, 'market', 'A股'),
                        '股票代码': review.stock_code or "",
                        '股票名称': review.stock_name or "",
                        '操作': '买入' if review.operation == 'buy' else '卖出',
                        '价格': float(review.price) if review.price is not None else None,
                        '数量': int(review.quantity) if review.quantity is not None else None,
                        '总金额': float(review.total_amount) if review.total_amount is not None else None,
                        '盈亏': float(review.profit) if review.profit is not None else None,
                        '盈亏比例': f"{review.profit_percent:.2f}%" if review.profit_percent is not None else "",
                    }
                    # 买入时显示止盈止损
                    if review.operation == 'buy':
                        record_dict['止盈价'] = float(review.take_profit_price) if review.take_profit_price is not None else None
                        record_dict['止损价'] = float(review.stop_loss_price) if review.stop_loss_price is not None else None
                    else:
                        record_dict['止盈价'] = None
                        record_dict['止损价'] = None
                    
                    # 添加关联信息
                    relation_info = ""
                    if review.parent_id:
                        relation_info = f"↗️ 关联买入#{review.parent_id}"
                    elif review.operation == 'buy':
                        # 查找关联的卖出记录数量
                        children_count = len([r for r in filtered_reviews if getattr(r, 'parent_id', None) == review.id])
                        if children_count > 0:
                            relation_info = f"↘️ {children_count}笔卖出"
                    
                    record_dict.update({
                        '交易原因': review.reason or "",
                        '复盘总结': review.review or "",
                        '关联': relation_info,
                        '创建时间': review.created_at.strftime('%Y-%m-%d %H:%M:%S') if review.created_at else '-'
                    })
                    records_data.append(record_dict)
                
                df_records = pd.DataFrame(records_data)
                
                # 保存原始数据用于比较
                if 'original_df_records' not in st.session_state:
                    st.session_state.original_df_records = df_records.copy()
                
                # 使用 data_editor 支持行选择和直接编辑
                try:
                    # 定义可编辑的列（某些列如ID、创建时间等不应编辑）
                    column_config = {
                        "ID": st.column_config.NumberColumn("ID", disabled=True),
                        "日期": st.column_config.DateColumn("日期", format="YYYY-MM-DD"),
                        "市场": st.column_config.SelectboxColumn("市场", options=['A股', '美股']),
                        "股票代码": st.column_config.TextColumn("股票代码"),
                        "股票名称": st.column_config.TextColumn("股票名称"),
                        "操作": st.column_config.SelectboxColumn("操作", options=['买入', '卖出']),
                        "价格": st.column_config.NumberColumn("价格", min_value=0.01, step=0.01, format="%.2f"),
                        "数量": st.column_config.NumberColumn("数量", min_value=1, step=100),
                        "总金额": st.column_config.NumberColumn("总金额", min_value=0, step=0.01, format="%.2f"),
                        "盈亏": st.column_config.NumberColumn("盈亏", step=0.01, format="%.2f"),
                        "盈亏比例": st.column_config.TextColumn("盈亏比例"),
                        "止盈价": st.column_config.NumberColumn("止盈价", min_value=0.01, step=0.01, format="%.2f"),
                        "止损价": st.column_config.NumberColumn("止损价", min_value=0.01, step=0.01, format="%.2f"),
                        "交易原因": st.column_config.TextColumn("交易原因"),
                        "复盘总结": st.column_config.TextColumn("复盘总结"),
                        "关联": st.column_config.TextColumn("关联", disabled=True),
                        "创建时间": st.column_config.TextColumn("创建时间", disabled=True),
                    }
                    
                    edited_df = st.data_editor(
                        df_records,
                        use_container_width=True,
                        height=400,
                        hide_index=True,
                        column_config=column_config,
                        on_select="rerun",  # 选择时自动刷新
                        selection_mode="single-row",  # 单选模式
                        num_rows="fixed",  # 固定行数，不允许添加/删除行
                        key="records_dataframe_editor"
                    )
                    
                    # 检测数据变化并保存
                    if not edited_df.equals(st.session_state.original_df_records):
                        # 找出被修改的行
                        for idx, row in edited_df.iterrows():
                            original_row = st.session_state.original_df_records.iloc[idx]
                            
                            # 检查是否有变化
                            if not row.equals(original_row):
                                if idx < len(filtered_reviews):
                                    review = filtered_reviews[idx]
                                    
                                    # 准备更新数据
                                    update_data = {}
                                    
                                    # 处理日期
                                    if pd.notna(row.get('日期')) and str(row['日期']) != str(original_row.get('日期')):
                                        if isinstance(row['日期'], str):
                                            update_data['date'] = row['日期']
                                        else:
                                            update_data['date'] = row['日期'].strftime('%Y-%m-%d')
                                    
                                    # 处理市场
                                    if row.get('市场') != original_row.get('市场'):
                                        update_data['market'] = row['市场']
                                    
                                    # 处理股票代码和名称
                                    if row.get('股票代码') != original_row.get('股票代码'):
                                        update_data['stockCode'] = str(row['股票代码']) if pd.notna(row.get('股票代码')) else ""
                                    if row.get('股票名称') != original_row.get('股票名称'):
                                        update_data['stockName'] = str(row['股票名称']) if pd.notna(row.get('股票名称')) else ""
                                    
                                    # 处理操作类型
                                    if row.get('操作') != original_row.get('操作'):
                                        update_data['operation'] = 'buy' if row['操作'] == '买入' else 'sell'
                                    
                                    # 处理价格和数量
                                    if pd.notna(row.get('价格')) and row.get('价格') != original_row.get('价格'):
                                        try:
                                            update_data['price'] = float(row['价格'])
                                        except (ValueError, TypeError):
                                            pass
                                    
                                    if pd.notna(row.get('数量')) and row.get('数量') != original_row.get('数量'):
                                        try:
                                            update_data['quantity'] = int(row['数量'])
                                        except (ValueError, TypeError):
                                            pass
                                    
                                    # 处理总金额（如果价格和数量都更新了，会自动计算）
                                    if 'price' in update_data and 'quantity' in update_data:
                                        update_data['totalAmount'] = update_data['price'] * update_data['quantity']
                                    elif pd.notna(row.get('总金额')) and row.get('总金额') != original_row.get('总金额'):
                                        try:
                                            update_data['totalAmount'] = float(row['总金额'])
                                        except (ValueError, TypeError):
                                            pass
                                    
                                    # 处理盈亏
                                    if pd.notna(row.get('盈亏')) and row.get('盈亏') != original_row.get('盈亏'):
                                        try:
                                            update_data['profit'] = float(row['盈亏'])
                                        except (ValueError, TypeError):
                                            pass
                                    
                                    # 处理盈亏比例
                                    if row.get('盈亏比例') != original_row.get('盈亏比例'):
                                        profit_percent_str = str(row['盈亏比例']).replace('%', '').strip()
                                        try:
                                            update_data['profitPercent'] = float(profit_percent_str)
                                        except (ValueError, TypeError):
                                            pass
                                    
                                    # 处理止盈止损
                                    if pd.notna(row.get('止盈价')) and row.get('止盈价') != original_row.get('止盈价'):
                                        try:
                                            update_data['takeProfitPrice'] = float(row['止盈价'])
                                        except (ValueError, TypeError):
                                            pass
                                    
                                    if pd.notna(row.get('止损价')) and row.get('止损价') != original_row.get('止损价'):
                                        try:
                                            update_data['stopLossPrice'] = float(row['止损价'])
                                        except (ValueError, TypeError):
                                            pass
                                    
                                    # 处理交易原因和复盘总结
                                    if row.get('交易原因') != original_row.get('交易原因'):
                                        update_data['reason'] = str(row['交易原因']) if pd.notna(row.get('交易原因')) else None
                                    
                                    if row.get('复盘总结') != original_row.get('复盘总结'):
                                        update_data['review'] = str(row['复盘总结']) if pd.notna(row.get('复盘总结')) and str(row['复盘总结']).strip() else None
                                    
                                    # 如果有更新，保存到数据库
                                    if update_data:
                                        try:
                                            updated_review = TradingReviewService.update_review(db, review.id, update_data)
                                            if updated_review:
                                                st.success(f"✅ 已更新记录: **{review.stock_name}** (ID: {review.id})")
                                                st.session_state.original_df_records = edited_df.copy()
                                                st.rerun()
                                            else:
                                                st.error(f"❌ 更新失败: **{review.stock_name}** (ID: {review.id})")
                                        except Exception as e:
                                            st.error(f"❌ 更新失败: {str(e)}")
                    
                    # 获取选中的行
                    if 'records_dataframe_editor' in st.session_state:
                        selection = st.session_state.records_dataframe_editor.get('selection', {})
                        selected_rows = selection.get('rows', [])
                        if selected_rows:
                            # 获取选中的行索引
                            selected_row_index = selected_rows[0]
                            if selected_row_index < len(filtered_reviews):
                                selected_review = filtered_reviews[selected_row_index]
                                # 自动设置操作记录
                                st.session_state.action_record_id = selected_review.id
                                st.session_state.action_type = "view"
                                
                except Exception as e:
                    # 如果 data_editor 不支持或出错，使用普通 dataframe
                    st.dataframe(
                    df_records,
                    use_container_width=True,
                    height=400,
                    hide_index=True
                )
                    st.caption("💡 提示：点击表格下方的按钮可快速操作记录")
                    if st.session_state.get('debug_mode', False):
                        st.error(f"Data editor error: {str(e)}")
                
                # 在表格下方显示操作按钮区域
                st.markdown("#### 🔧 快速操作")
                st.caption("💡 提示：点击下方按钮可快速查看、编辑或删除对应记录")
                
                # 使用网格布局显示操作按钮（每行3条记录）
                num_cols = 3
                for i in range(0, len(filtered_reviews), num_cols):
                    cols = st.columns(num_cols)
                    for j, col in enumerate(cols):
                        if i + j < len(filtered_reviews):
                            review = filtered_reviews[i + j]
                            with col:
                                st.markdown(f"**{review.stock_name}** ({review.date})")
                                col_btn1, col_btn2, col_btn3 = st.columns(3)
                                with col_btn1:
                                    if st.button("📄", key=f"view_{review.id}", help="查看详情", use_container_width=True):
                                        st.session_state.action_record_id = review.id
                                        st.session_state.action_type = "view"
                                        st.rerun()
                                with col_btn2:
                                    if st.button("✏️", key=f"edit_{review.id}", help="编辑记录", use_container_width=True):
                                        st.session_state.action_record_id = review.id
                                        st.session_state.action_type = "edit"
                                        st.rerun()
                                with col_btn3:
                                    if st.button("🗑️", key=f"delete_{review.id}", help="删除记录", use_container_width=True):
                                        st.session_state.action_record_id = review.id
                                        st.session_state.action_type = "delete"
                                        st.rerun()
                
                # 详细操作区域 - 根据按钮点击显示
                if st.session_state.get('action_record_id') and st.session_state.get('action_type'):
                    st.markdownst.markdown('<h2 class="section-header">记录操作</h2>', unsafe_allow_html=True)
                    selected_id = st.session_state.action_record_id
                    action_type = st.session_state.action_type
                    
                    # 显示当前操作的记录信息
                    current_review = next((r for r in filtered_reviews if r.id == selected_id), None)
                    if current_review:
                        st.info(f"📋 当前操作记录: **{current_review.stock_name}** ({current_review.date}) - {'买入' if current_review.operation == 'buy' else '卖出'}")
                        
                        # 添加返回按钮
                        if st.button("← 返回列表", key="back_to_list"):
                            st.session_state.action_record_id = None
                            st.session_state.action_type = None
                            st.rerun()
                        
                        # 根据操作类型显示对应内容
                        if action_type == "view":
                            # 查看详情
                            selected_review = current_review
                        elif action_type == "edit":
                            # 编辑记录
                            selected_review = current_review
                        elif action_type == "delete":
                            # 删除记录
                            selected_review = current_review
                    else:
                        st.warning("⚠️ 未找到选中的记录")
                        selected_id = None
                else:
                    # 如果没有选中操作，使用原来的选择框方式
                    st.markdown('<h2 class="section-header">记录操作</h2>', unsafe_allow_html=True)
                    review_ids = [r.id for r in filtered_reviews]
                    selected_id = st.selectbox(
                        "📋 选择要操作的记录",
                        options=review_ids,
                        format_func=lambda x: f"{next((r.stock_name for r in filtered_reviews if r.id == x), '')} ({next((r.date for r in filtered_reviews if r.id == x), '')}) - {next(('买入' if r.operation == 'buy' else '卖出' for r in filtered_reviews if r.id == x), '')}",
                        help="选择要查看、编辑或删除的交易记录",
                        key="selected_review_id"
                    )
                    action_type = "view"  # 默认查看
                    
                    if selected_id:
                        selected_review = next((r for r in filtered_reviews if r.id == selected_id), None)
                        if selected_review:
                            # 根据操作类型显示对应的标签页
                            op_tab1, op_tab2, op_tab3 = st.tabs(["📄 查看详情", "✏️ 编辑记录", "🗑️ 删除记录"])
                            view_tab, edit_tab, delete_tab = op_tab1, op_tab2, op_tab3
                        
                        # 标签页1: 查看详情
                        with view_tab:
                    
                            # 显示记录基本信息卡片
                            col_info1, col_info2, col_info3, col_info4 = st.columns(4)
                            with col_info1:
                                # 使用自定义HTML显示日期
                                date_str = str(selected_review.date) if selected_review.date else "-"
                                st.markdown(f"""
                                    <div style="padding: 1rem; background-color: #f0f2f6; border-radius: 0.5rem;">
                                        <div style="font-size: 0.875rem; color: #666; margin-bottom: 0.25rem;">📅 交易日期</div>
                                        <div style="font-size: 1.25rem; font-weight: 600; color: #1f2937;">{date_str}</div>
                                    </div>
                                """, unsafe_allow_html=True)
                            with col_info2:
                                operation_text = '买入' if selected_review.operation == 'buy' else '卖出'
                                st.markdown(f"""
                                    <div style="padding: 1rem; background-color: #f0f2f6; border-radius: 0.5rem;">
                                        <div style="font-size: 0.875rem; color: #666; margin-bottom: 0.25rem;">📊 操作类型</div>
                                        <div style="font-size: 1.25rem; font-weight: 600; color: #1f2937;">{operation_text}</div>
                                    </div>
                                """, unsafe_allow_html=True)
                            with col_info3:
                                if selected_review.total_amount is not None:
                                    st.metric("💰 成交总额", float(selected_review.total_amount), delta=None, help="单位：元")
                                else:
                                    st.markdown(f"""
                                        <div style="padding: 1rem; background-color: #f0f2f6; border-radius: 0.5rem;">
                                            <div style="font-size: 0.875rem; color: #666; margin-bottom: 0.25rem;">💰 成交总额</div>
                                            <div style="font-size: 1.25rem; font-weight: 600; color: #1f2937;">-</div>
                                        </div>
                                    """, unsafe_allow_html=True)
                            with col_info4:
                                if selected_review.profit is not None:
                                    profit_value = float(selected_review.profit)
                                    profit_delta = f"{selected_review.profit_percent:.2f}%" if selected_review.profit_percent is not None else None
                                    profit_color = "normal" if profit_value >= 0 else "inverse"
                                    st.metric("📈 盈亏金额", profit_value, delta=profit_delta, delta_color=profit_color)
                                else:
                                    st.markdown(f"""
                                        <div style="padding: 1rem; background-color: #f0f2f6; border-radius: 0.5rem;">
                                            <div style="font-size: 0.875rem; color: #666; margin-bottom: 0.25rem;">📈 盈亏金额</div>
                                            <div style="font-size: 1.25rem; font-weight: 600; color: #1f2937;">-</div>
                                        </div>
                                    """, unsafe_allow_html=True)
                            
                            # 详细信息
                            st.markdown("#### 📋 详细信息")
                            col_detail1, col_detail2 = st.columns(2)
                            
                            with col_detail1:
                                st.write(f"**市场:** {getattr(selected_review, 'market', 'A股')}")
                                st.write(f"**股票代码:** {selected_review.stock_code}")
                                st.write(f"**股票名称:** {selected_review.stock_name}")
                                st.write(f"**交易原因:** {selected_review.reason}")
                                st.write(f"**成交价格:** {selected_review.price:.2f}元" if selected_review.price is not None else "**成交价格:** -")
                                st.write(f"**成交数量:** {selected_review.quantity}" if selected_review.quantity is not None else "**成交数量:** -")
                            
                            with col_detail2:
                                if selected_review.operation == 'buy':
                                    st.write(f"**止盈价格:** {selected_review.take_profit_price:.2f}元" if selected_review.take_profit_price is not None else "**止盈价格:** -")
                                    st.write(f"**止损价格:** {selected_review.stop_loss_price:.2f}元" if selected_review.stop_loss_price is not None else "**止损价格:** -")
                                st.write(f"**创建时间:** {selected_review.created_at.strftime('%Y-%m-%d %H:%M:%S') if selected_review.created_at else '-'}")
                                st.write(f"**更新时间:** {selected_review.updated_at.strftime('%Y-%m-%d %H:%M:%S') if selected_review.updated_at else '-'}")
                            
                            if selected_review.review:
                                st.markdown("#### 📝 复盘总结")
                                st.text_area("", value=selected_review.review, height=100, disabled=True, key=f"view_review_{selected_id}")
                        
                        # 标签页2: 编辑记录
                        with edit_tab:
                            st.info("💡 修改以下信息后点击「保存修改」按钮保存更改")
                            with st.form(f"edit_review_{selected_id}"):
                                # 处理日期：可能是字符串或date对象
                                if isinstance(selected_review.date, str):
                                    edit_date_value = datetime.strptime(selected_review.date, '%Y-%m-%d').date()
                                else:
                                    edit_date_value = selected_review.date
                                
                                # 市场和日期放在同一行
                                col_edit_date_market1, col_edit_date_market2 = st.columns(2)
                                with col_edit_date_market1:
                                    edit_date = st.date_input(
                                        "📅 交易日期",
                                        value=edit_date_value,
                                        max_value=get_utc8_date(),
                                        key=f"edit_date_{selected_id}"
                                    )
                                with col_edit_date_market2:
                                    edit_market = st.selectbox(
                                        "🌍 市场",
                                        options=['A股', '美股'],
                                        index=0 if getattr(selected_review, 'market', 'A股') == 'A股' else 1,
                                        key=f"edit_market_{selected_id}"
                                    )
                                    
                                    # 股票代码和股票名称放在同一行
                                    col_edit_stock1, col_edit_stock2 = st.columns(2)
                                    with col_edit_stock1:
                                        edit_stock_code = st.text_input(
                                            "股票代码",
                                            value=selected_review.stock_code,
                                            key=f"edit_stock_code_{selected_id}"
                                        )
                                    with col_edit_stock2:
                                        edit_stock_name = st.text_input(
                                            "股票名称",
                                            value=selected_review.stock_name,
                                            key=f"edit_stock_name_{selected_id}"
                                        )
                                    
                                    edit_operation = st.selectbox(
                                        "🔄 操作类型",
                                        options=['buy', 'sell'],
                                        index=0 if selected_review.operation == 'buy' else 1,
                                        format_func=lambda x: '买入' if x == 'buy' else '卖出',
                                        key=f"edit_operation_{selected_id}"
                                    )
                                    
                                    # 交易原因（紧跟在操作类型后面）
                                    edit_trading_reasons = get_trading_reasons()
                                    # 如果当前原因不在列表中，添加到选项
                                    if selected_review.reason not in edit_trading_reasons:
                                        edit_trading_reasons = [selected_review.reason] + edit_trading_reasons
                                    
                                    edit_reason = st.selectbox(
                                        "💭 交易原因",
                                        options=edit_trading_reasons,
                                        index=edit_trading_reasons.index(selected_review.reason) if selected_review.reason in edit_trading_reasons else 0,
                                        help="选择本次交易的原因，可在「交易原因管理」标签页中添加新的原因",
                                        key=f"edit_reason_{selected_id}"
                                    )
                                    
                                    col_edit1, col_edit2 = st.columns(2)
                                    with col_edit1:
                                        # 成交价格和成交数量放在同一行
                                        col_edit_price_qty1, col_edit_price_qty2 = st.columns(2)
                                        with col_edit_price_qty1:
                                            edit_price = st.number_input(
                                                "成交价格",
                                                min_value=0.01,
                                                value=float(selected_review.price) if selected_review.price is not None else None,
                                                step=0.01,
                                                format="%.2f",
                                                help="成交价格（必填）",
                                                key=f"edit_price_{selected_id}"
                                            )
                                        with col_edit_price_qty2:
                                            edit_quantity = st.number_input(
                                                "成交数量",
                                                min_value=1,
                                                value=int(selected_review.quantity) if selected_review.quantity is not None else None,
                                                step=100,
                                                help="成交数量（必填）",
                                                key=f"edit_quantity_{selected_id}"
                                            )
                                    
                                    with col_edit2:
                                        # 自动计算总金额（如果价格和数量都提供了）
                                        if edit_price is not None and edit_quantity is not None and edit_price > 0 and edit_quantity > 0:
                                            edit_calculated_total = float(edit_price * edit_quantity)
                                            st.info(f"💡 成交总额（自动计算）：**{edit_calculated_total:.2f}** 元")
                                        else:
                                            edit_calculated_total = selected_review.total_amount if selected_review.total_amount is not None else None
                                            if edit_calculated_total is not None:
                                                st.info(f"💡 成交总额：**{edit_calculated_total:.2f}** 元")
                                            else:
                                                st.info("💡 成交总额：请填写成交价格和成交数量后自动计算")
                                        
                                        edit_total_amount = edit_calculated_total
                                        
                                        edit_profit = st.number_input(
                                            "📊 盈亏金额",
                                            value=float(selected_review.profit) if selected_review.profit is not None else None,
                                            step=0.01,
                                            format="%.2f",
                                            key=f"edit_profit_{selected_id}"
                                        )
                                    
                                    edit_profit_percent = st.number_input(
                                        "📈 盈亏比例 (%)",
                                        value=float(selected_review.profit_percent) if selected_review.profit_percent is not None else None,
                                        step=0.01,
                                        format="%.2f",
                                        key=f"edit_profit_percent_{selected_id}"
                                    )
                                    
                                    # 止盈止损信息（买入时显示）
                                if edit_operation == 'buy':
                                        st.markdown("---")
                                        st.markdown("#### 🎯 止盈止损设置")
                                        col_edit_tp_sl1, col_edit_tp_sl2 = st.columns(2)
                                        with col_edit_tp_sl1:
                                            edit_take_profit_price = st.number_input(
                                                "🔼 止盈价格",
                                                min_value=0.01,
                                                value=float(selected_review.take_profit_price) if selected_review.take_profit_price is not None else None,
                                                step=0.01,
                                                format="%.2f",
                                                help="止盈价格（可选）",
                                                key=f"edit_take_profit_price_{selected_id}"
                                            )
                                        with col_edit_tp_sl2:
                                            edit_stop_loss_price = st.number_input(
                                                "🔽 止损价格",
                                                min_value=0.01,
                                                value=float(selected_review.stop_loss_price) if selected_review.stop_loss_price is not None else None,
                                                step=0.01,
                                                format="%.2f",
                                                help="止损价格（可选）",
                                                key=f"edit_stop_loss_price_{selected_id}"
                                            )
                                        
                                        # 显示止盈止损比例提示
                                        if edit_price and edit_price > 0:
                                            if edit_take_profit_price:
                                                tp_percent = ((edit_take_profit_price - edit_price) / edit_price) * 100
                                                st.info(f"💡 止盈价格 {edit_take_profit_price:.2f} 元，相对于买入价 {edit_price:.2f} 元，涨幅 {tp_percent:+.2f}%")
                                            if edit_stop_loss_price:
                                                sl_percent = ((edit_stop_loss_price - edit_price) / edit_price) * 100
                                                st.info(f"💡 止损价格 {edit_stop_loss_price:.2f} 元，相对于买入价 {edit_price:.2f} 元，跌幅 {sl_percent:+.2f}%")
                                else:
                                        edit_take_profit_price = None
                                        edit_stop_loss_price = None
                                
                                # 复盘总结（无论操作类型如何都显示）
                                edit_review = st.text_area(
                                    "📝 复盘总结",
                                    value=selected_review.review,
                                    height=150,
                                    key=f"edit_review_text_{selected_id}"
                                )
                                    
                                col_submit1, col_submit2 = st.columns([1, 1])
                                with col_submit1:
                                    edit_submitted = st.form_submit_button("✅ 保存修改", type="primary", use_container_width=True)
                                with col_submit2:
                                    edit_cancel = st.form_submit_button("❌ 取消", use_container_width=True)
                                    
                                if edit_submitted and not edit_cancel:
                                        # 安全地处理可能为None的值
                                        edit_stock_code_trimmed = (edit_stock_code.strip() if edit_stock_code and isinstance(edit_stock_code, str) else "") or ""
                                        edit_stock_name_trimmed = (edit_stock_name.strip() if edit_stock_name and isinstance(edit_stock_name, str) else "") or ""
                                        
                                        # 股票代码和名称不能同时为空
                                        if not edit_stock_code_trimmed and not edit_stock_name_trimmed:
                                            st.error("❌ 股票代码和股票名称不能同时为空，请至少填写其中一项")
                                            st.info("💡 提示：请至少填写股票代码或股票名称中的一项")
                                        elif not edit_reason:
                                            st.error("❌ 请选择交易原因")
                                        elif edit_price is None or edit_price <= 0:
                                            st.error("❌ 请输入成交价格（必须大于0）")
                                        elif edit_quantity is None or edit_quantity <= 0:
                                            st.error("❌ 请输入成交数量（必须大于0）")
                                        else:
                                            # 自动计算总金额
                                            edit_final_total_amount = float(edit_price * edit_quantity)
                                            
                                            update_data = {
                                                'date': edit_date.strftime('%Y-%m-%d'),
                                                'market': edit_market,
                                                'stockCode': edit_stock_code_trimmed or "",
                                                'stockName': edit_stock_name_trimmed or "",
                                                'operation': edit_operation,
                                                'price': float(edit_price),
                                                'quantity': int(edit_quantity),
                                                'totalAmount': edit_final_total_amount,
                                                'reason': edit_reason,
                                                'review': edit_review.strip() if edit_review and edit_review.strip() else None,
                                                'profit': float(edit_profit) if edit_profit is not None else None,
                                                'profitPercent': float(edit_profit_percent) if edit_profit_percent is not None else None,
                                                'takeProfitPrice': float(edit_take_profit_price) if edit_take_profit_price is not None else None,
                                                'stopLossPrice': float(edit_stop_loss_price) if edit_stop_loss_price is not None else None,
                                            }
                                            
                                            try:
                                                updated_review = TradingReviewService.update_review(db, selected_id, update_data)
                                                if updated_review:
                                                    # 显示 toast 提示
                                                    st.toast("✅ 记录已更新", icon="✨")
                                                    st.success("✅ 记录已更新")
                                                    st.rerun()
                                                else:
                                                    st.error("❌ 更新失败")
                                            except ValueError as e:
                                                st.error(f"❌ 数据验证失败: {str(e)}")
                                            except Exception as e:
                                                st.error(f"❌ 更新失败: {str(e)}")
                
                        # 标签页3: 删除记录
                        with delete_tab:
                            st.warning("⚠️ **危险操作：删除记录后无法恢复，请谨慎操作！**")
                            
                            # 显示要删除的记录信息
                            st.markdown("#### 📋 将要删除的记录信息")
                            col_del1, col_del2 = st.columns(2)
                            
                            with col_del1:
                                st.write(f"**交易日期:** {selected_review.date}")
                                st.write(f"**股票代码:** {selected_review.stock_code}")
                                st.write(f"**股票名称:** {selected_review.stock_name}")
                                st.write(f"**操作类型:** {'买入' if selected_review.operation == 'buy' else '卖出'}")
                            
                            with col_del2:
                                st.write(f"**成交价格:** {selected_review.price:.2f}元" if selected_review.price else "-")
                                st.write(f"**成交数量:** {selected_review.quantity}" if selected_review.quantity else "-")
                                st.write(f"**成交总额:** {selected_review.total_amount:.2f}元" if selected_review.total_amount else "-")
                                st.write(f"**交易原因:** {selected_review.reason}")
                            
                            # 二次确认
                            st.markdown("---")
                            confirm_text = st.text_input(
                                "🔒 安全确认：请输入股票名称以确认删除",
                                placeholder=f"请输入: {selected_review.stock_name}",
                                key=f"delete_confirm_{selected_id}",
                                help="请输入完整的股票名称以确认删除操作"
                            )
                            
                            col_del_btn1, col_del_btn2 = st.columns([1, 1])
                            with col_del_btn1:
                                delete_confirmed = st.button(
                                    "🗑️ 确认删除",
                                    type="primary",
                                    disabled=confirm_text != selected_review.stock_name,
                                    use_container_width=True,
                                    key=f"delete_btn_{selected_id}"
                                )
                            with col_del_btn2:
                                delete_cancel = st.button(
                                    "❌ 取消",
                                    use_container_width=True,
                                    key=f"delete_cancel_{selected_id}"
                                )
                            
                            if delete_confirmed and confirm_text == selected_review.stock_name:
                                try:
                                    success = TradingReviewService.delete_review(db, selected_id)
                                    if success:
                                        st.toast("✅ 记录已删除", icon="🗑️")
                                        st.success("✅ 记录已删除")
                                        st.rerun()
                                    else:
                                        st.error("❌ 删除失败")
                                except Exception as e:
                                    st.error(f"❌ 删除失败: {str(e)}")
                            elif delete_confirmed and confirm_text != selected_review.stock_name:
                                st.error("❌ 输入的股票名称不匹配，请重新输入")
            else:
                st.info("🔍 没有找到匹配的交易记录")
    finally:
        db.close()

# ==================== 标签页2: 添加记录 ====================
with tab2:
    st.markdown('<h2 class="section-header">添加交易记录</h2>', unsafe_allow_html=True)
    
    # 检查是否需要清除表单（通过增加key后缀来强制重置）
    form_reset_counter = st.session_state.get('form_reset_counter', 0)
    form_key_suffix = f"_{form_reset_counter}" if form_reset_counter > 0 else ""
    
    with st.form("add_trading_review", clear_on_submit=False):
        col_form1, col_form2 = st.columns(2)
        
        with col_form1:
            # 基本信息
            # 日期和市场放在同一行
            col_date_market1, col_date_market2 = st.columns(2)
            with col_date_market1:
                trading_date = st.date_input(
                    "📅 交易日期",
                value=get_utc8_date(),
                max_value=get_utc8_date(),
                    help="选择交易日期",
                    key=f"add_trading_date{form_key_suffix}"
            )
            with col_date_market2:
                market = st.selectbox(
                    "🌍 市场",
                options=['A股', '美股'],
                    help="选择交易市场",
                    key=f"add_market{form_key_suffix}"
            )
            # 股票代码和股票名称放在同一行
            col_stock1, col_stock2 = st.columns(2)
            with col_stock1:
                stock_code = st.text_input(
                    "股票代码",
                    value="",
                    placeholder="例如: 000001" if market == 'A股' else "例如: AAPL",
                    help="输入股票代码",
                    key=f"add_stock_code{form_key_suffix}"
                )
            with col_stock2:
                stock_name = st.text_input(
                    "股票名称",
                    value="",
                    placeholder="例如: 平安银行" if market == 'A股' else "例如: Apple Inc.",
                    help="输入股票名称",
                    key=f"add_stock_name{form_key_suffix}"
                )
            
            # 操作类型和交易原因放在同一行
            col_op_reason1, col_op_reason2 = st.columns(2)
            with col_op_reason1:
                operation = st.selectbox(
                    "操作类型",
                    options=['buy', 'sell'],
                    format_func=lambda x: '买入' if x == 'buy' else '卖出',
                    help="选择买入或卖出",
                    key=f"add_operation{form_key_suffix}"
                )
            with col_op_reason2:
                # 交易原因
                trading_reasons = get_trading_reasons()
                reason = st.selectbox(
                    "交易原因",
                    options=trading_reasons,
                    help="选择本次交易的原因，可在「交易原因管理」标签页中添加新的原因",
                    key=f"add_reason{form_key_suffix}"
                )
            
            # 如果是卖出操作，显示可关联的买入记录选择
            if operation == 'sell' and stock_code and stock_code.strip():
                db_temp = SessionLocal()
                try:
                    # 查找同一只股票的买入记录
                    buy_records = db_temp.query(TradingReview).filter(
                        TradingReview.operation == 'buy',
                        TradingReview.stock_code == stock_code.strip()
                    ).order_by(TradingReview.date.desc(), TradingReview.created_at.desc()).all()
                    
                    if buy_records:
                        # 计算每个买入记录的剩余可卖出数量
                        buy_options = []
                        buy_options_dict = {}
                        
                        for buy_record in buy_records:
                            # 计算已卖出数量
                            sold_quantity = db_temp.query(func.sum(TradingReview.quantity)).filter(
                                TradingReview.parent_id == buy_record.id,
                                TradingReview.operation == 'sell'
                            ).scalar() or 0
                            
                            remaining = buy_record.quantity - sold_quantity
                            
                            if remaining > 0:
                                option_text = f"买入#{buy_record.id} - {buy_record.date} | {buy_record.price:.2f}元 × {buy_record.quantity}股 | 剩余{remaining}股"
                                buy_options.append(option_text)
                                buy_options_dict[option_text] = buy_record.id
                        
                        if buy_options:
                            st.markdown("#### 🔗 关联买入记录（可选）")
                            st.caption("💡 选择要关联的买入记录，系统将自动计算盈亏。如果不选择，系统会自动匹配最早的未完全卖出的买入记录。")
                            
                            selected_buy_option = st.selectbox(
                                "选择关联的买入记录",
                                options=["自动匹配（推荐）"] + buy_options,
                                help="选择要关联的买入记录，或选择'自动匹配'让系统自动选择",
                                key=f"add_parent_buy{form_key_suffix}"
                            )
                            
                            # 将选中的买入记录ID存储到session_state，以便在提交时使用
                            if selected_buy_option != "自动匹配（推荐）" and selected_buy_option in buy_options_dict:
                                st.session_state[f'selected_parent_id{form_key_suffix}'] = buy_options_dict[selected_buy_option]
                            else:
                                st.session_state[f'selected_parent_id{form_key_suffix}'] = None
                                
                                # 显示选中买入记录的详细信息
                                selected_buy = next((r for r in buy_records if r.id == selected_parent_id), None)
                                if selected_buy:
                                    sold_qty = db_temp.query(func.sum(TradingReview.quantity)).filter(
                                        TradingReview.parent_id == selected_buy.id,
                                        TradingReview.operation == 'sell'
                                    ).scalar() or 0
                                    remaining_qty = selected_buy.quantity - sold_qty
                                    
                                    st.info(f"""
                                    **选中的买入记录：**
                                    - 买入日期：{selected_buy.date}
                                    - 买入价格：{selected_buy.price:.2f} 元
                                    - 买入数量：{selected_buy.quantity} 股
                                    - 已卖出：{sold_qty} 股
                                    - 剩余可卖：{remaining_qty} 股
                                    """)
                finally:
                    db_temp.close()
        
        with col_form2:
            # 交易信息
            # 成交价格和成交数量放在同一行
            col_price_qty1, col_price_qty2 = st.columns(2)
            with col_price_qty1:
                price = st.number_input(
                    "成交价格",
                    min_value=0.01,
                    value=None,
                    step=0.01,
                    format="%.2f",
                    help="输入成交价格（元，必填）",
                    key=f"add_price{form_key_suffix}"
                )
            with col_price_qty2:
                quantity = st.number_input(
                    "成交数量",
                    min_value=1,
                    value=None,
                    step=100,
                    help="输入成交数量（股，必填）",
                    key=f"add_quantity{form_key_suffix}"
                )
            
            # 自动计算总金额（如果价格和数量都提供了）
            if price is not None and quantity is not None and price > 0 and quantity > 0:
                calculated_total = float(price * quantity)
                st.info(f"成交总额（自动计算）：**{calculated_total:.2f}** 元 = {price:.2f} × {quantity}")
                total_amount = calculated_total
            else:
                st.info("成交总额：请填写成交价格和成交数量后自动计算")
                total_amount = None
            
            # 盈亏信息（可选）
            col_profit1, col_profit2 = st.columns(2)
            with col_profit1:
                profit = st.number_input(
                    "盈亏金额",
                    value=None,
                    step=0.01,
                    format="%.2f",
                    help="盈亏金额（可选，卖出时填写）",
                    key=f"add_profit{form_key_suffix}"
                )
            with col_profit2:
                profit_percent = st.number_input(
                    "盈亏比例 (%)",
                    value=None,
                    step=0.01,
                    format="%.2f",
                    help="盈亏比例（可选，卖出时填写）",
                    key=f"add_profit_percent{form_key_suffix}"
                )
        
        # 止盈止损信息（买入时填写）
        if operation == 'buy':
            col_tp_sl1, col_tp_sl2 = st.columns(2)
            with col_tp_sl1:
                take_profit_price = st.number_input(
                    "止盈价格",
                    min_value=0.01,
                    value=None,
                    step=0.01,
                    format="%.2f",
                    help="止盈价格（可选，买入时建议设置）",
                    key=f"add_take_profit_price{form_key_suffix}"
                )
            with col_tp_sl2:
                stop_loss_price = st.number_input(
                    "止损价格",
                    min_value=0.01,
                    value=None,
                    step=0.01,
                    format="%.2f",
                    help="止损价格（可选，买入时建议设置）",
                    key=f"add_stop_loss_price{form_key_suffix}"
                )
            
            # 显示止盈止损比例提示
            if price and price > 0:
                if take_profit_price:
                    tp_percent = ((take_profit_price - price) / price) * 100
                    st.info(f"止盈价格 {take_profit_price:.2f} 元，相对于买入价 {price:.2f} 元，涨幅 {tp_percent:+.2f}%")
                if stop_loss_price:
                    sl_percent = ((stop_loss_price - price) / price) * 100
                    st.info(f"止损价格 {stop_loss_price:.2f} 元，相对于买入价 {price:.2f} 元，跌幅 {sl_percent:+.2f}%")
        else:
            take_profit_price = None
            stop_loss_price = None
        
        # 复盘总结
        review = st.text_area(
            "复盘总结",
            value="",
            placeholder="请输入复盘总结，例如：交易执行情况、市场表现、经验教训等...",
            height=150,
            help="对本次交易进行复盘总结",
            key=f"add_review{form_key_suffix}"
        )
        
        # 提交按钮
        submitted = st.form_submit_button("提交记录", type="primary", use_container_width=True)
        
        if submitted:
            # 验证必填字段
            # Streamlit的text_input返回空字符串""而不是None
            # 简化处理：直接转换为字符串并去除空格
            stock_code_trimmed = (str(stock_code).strip() if stock_code is not None and stock_code != "" else "")
            stock_name_trimmed = (str(stock_name).strip() if stock_name is not None and stock_name != "" else "")
            
            # 股票代码和名称不能同时为空
            if not stock_code_trimmed and not stock_name_trimmed:
                # 显示调试信息帮助定位问题
                st.error("股票代码和股票名称不能同时为空，请至少填写其中一项")
                st.info("提示：请至少填写股票代码或股票名称中的一项")
                # 显示调试信息（帮助用户理解问题）
                with st.expander("调试信息（点击查看）", expanded=True):
                    st.write(f"**股票代码原始值:** `{repr(stock_code)}`")
                    st.write(f"**股票代码类型:** `{type(stock_code)}`")
                    st.write(f"**股票代码处理后:** `{repr(stock_code_trimmed)}`")
                    st.write(f"**股票代码长度:** {len(stock_code_trimmed) if stock_code_trimmed else 0}")
                    st.write(f"**股票名称原始值:** `{repr(stock_name)}`")
                    st.write(f"**股票名称类型:** `{type(stock_name)}`")
                    st.write(f"**股票名称处理后:** `{repr(stock_name_trimmed)}`")
                    st.write(f"**股票名称长度:** {len(stock_name_trimmed) if stock_name_trimmed else 0}")
                    st.write(f"**股票代码是否为空:** {not stock_code_trimmed}")
                    st.write(f"**股票名称是否为空:** {not stock_name_trimmed}")
                    st.write(f"**两者都为空:** {not stock_code_trimmed and not stock_name_trimmed}")
            elif not reason:
                st.error("请选择交易原因")
            elif price is None or price <= 0:
                st.error("请输入成交价格（必须大于0）")
            elif quantity is None or quantity <= 0:
                st.error("请输入成交数量（必须大于0）")
            else:
                # 自动计算总金额
                final_total_amount = float(price * quantity)
                
                # 准备数据
                review_data = {
                    'date': trading_date.strftime('%Y-%m-%d'),
                    'market': market,
                    'stockCode': stock_code_trimmed or "",
                    'stockName': stock_name_trimmed or "",
                    'operation': operation,
                    'price': float(price),
                    'quantity': int(quantity),
                    'totalAmount': final_total_amount,
                    'reason': reason,
                    'review': review.strip() if review and review.strip() else None,
                    'profit': float(profit) if profit is not None else None,
                    'profitPercent': float(profit_percent) if profit_percent is not None else None,
                    'takeProfitPrice': float(take_profit_price) if take_profit_price is not None else None,
                    'stopLossPrice': float(stop_loss_price) if stop_loss_price is not None else None,
                }
                
                # 如果选择了关联的买入记录，添加到数据中
                if operation == 'sell':
                    selected_parent_id = st.session_state.get(f'selected_parent_id{form_key_suffix}', None)
                    if selected_parent_id:
                        review_data['parentId'] = selected_parent_id
                        # 清除session_state中的值
                        if f'selected_parent_id{form_key_suffix}' in st.session_state:
                            del st.session_state[f'selected_parent_id{form_key_suffix}']
                
                # 保存到数据库
                db = SessionLocal()
                try:
                    created_review = TradingReviewService.create_review(db, review_data)
                    # 显示 toast 提示
                    st.toast(f"交易记录已添加！记录ID: {created_review.id}")
                    st.success(f"交易记录已添加！记录ID: {created_review.id}")
                    st.info("记录已保存，可在「交易记录」标签页查看")
                    # 增加表单重置计数器，通过改变key来强制重置表单字段
                    st.session_state.form_reset_counter = st.session_state.get('form_reset_counter', 0) + 1
                    # 刷新页面以清除表单
                    st.rerun()
                except ValueError as e:
                    st.error(f"数据验证失败: {str(e)}")
                except Exception as e:
                    st.error(f"保存失败: {str(e)}")
                finally:
                    db.close()
        

# ==================== 标签页3: 统计分析 ====================
with tab3:
    st.markdown('<h2 class="section-header">交易统计分析</h2>', unsafe_allow_html=True)
    
    db = SessionLocal()
    try:
        # 获取统计信息
        stats = TradingReviewService.get_statistics(db)
        all_reviews = TradingReviewService.get_all_reviews(db)
        
        if not all_reviews:
            st.info("📊 暂无交易记录，无法进行统计分析")
        else:
            # 总体统计
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            
            with col_stat1:
                st.metric("总记录数", stats['totalRecords'])
            
            with col_stat2:
                total_profit = stats['totalProfit']
                profit_color = "normal" if total_profit >= 0 else "inverse"
                st.metric("总盈亏", f"{total_profit:.2f}元", delta_color=profit_color)
            
            with col_stat3:
                win_count = stats['winCount']
                loss_count = stats['lossCount']
                total_trades = win_count + loss_count
                win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0
                st.metric("胜率", f"{win_rate:.1f}%", delta=f"{win_count}胜/{loss_count}负")
            
            with col_stat4:
                st.metric("盈利次数", win_count)
            
            # 详细统计
            st.markdown('<h2 class="section-header">详细统计</h2>', unsafe_allow_html=True)
            
            # 按日期统计
            if all_reviews:
                date_stats = {}
                for review in all_reviews:
                    if review.date not in date_stats:
                        date_stats[review.date] = {'buy': 0, 'sell': 0, 'profit': 0}
                    date_stats[review.date][review.operation] += 1
                    if review.profit is not None:
                        date_stats[review.date]['profit'] += review.profit
                
                df_date_stats = pd.DataFrame([
                    {
                        '日期': date_key,
                        '买入次数': date_stat['buy'],
                        '卖出次数': date_stat['sell'],
                        '当日盈亏': f"{date_stat['profit']:.2f}"
                    }
                    for date_key, date_stat in sorted(date_stats.items(), reverse=True)
                ])
                
                st.subheader("📅 按日期统计")
                st.dataframe(df_date_stats, use_container_width=True, hide_index=True)
            
            # 按股票统计
            if all_reviews:
                stock_stats = {}
                for review in all_reviews:
                    key = f"{review.stock_code} ({review.stock_name})"
                    if key not in stock_stats:
                        stock_stats[key] = {'buy': 0, 'sell': 0, 'profit': 0, 'total_amount': 0}
                    stock_stats[key][review.operation] += 1
                    stock_stats[key]['total_amount'] += review.total_amount
                    if review.profit is not None:
                        stock_stats[key]['profit'] += review.profit
                
                df_stock_stats = pd.DataFrame([
                    {
                        '股票': stock,
                        '买入次数': stats['buy'],
                        '卖出次数': stats['sell'],
                        '总盈亏': f"{stats['profit']:.2f}",
                        '总成交额': f"{stats['total_amount']:.2f}"
                    }
                    for stock, stats in sorted(stock_stats.items(), key=lambda x: x[1]['profit'], reverse=True)
                ])
                
                st.subheader("📊 按股票统计")
                st.dataframe(df_stock_stats, use_container_width=True, hide_index=True)
    finally:
        db.close()

# ==================== 标签页4: 交易原因管理 ====================
with tab4:
    # 添加自定义CSS样式
    st.markdown("""
        <style>
        .reason-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 0.75rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .reason-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        .reason-card-content {
            background: white;
            padding: 1.25rem;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .reason-number {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 0.9rem;
            margin-right: 1rem;
            flex-shrink: 0;
        }
        .reason-text {
            flex: 1;
            font-size: 1.1rem;
            font-weight: 500;
            color: #2c3e50;
            margin-right: 1rem;
        }
        .reason-actions {
            display: flex;
            gap: 0.5rem;
        }
        .empty-state {
            text-align: center;
            padding: 3rem 1rem;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 10px;
            margin: 2rem 0;
        }
        .empty-state-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
        .empty-state-text {
            font-size: 1.2rem;
            color: #6b7280;
            margin-top: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h2 class="section-header">交易原因管理</h2>', unsafe_allow_html=True)
    
    # 获取当前交易原因列表
    current_reasons = get_trading_reasons()
    
    # 美化提示信息
    st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); 
                    padding: 1rem; 
                    border-radius: 8px; 
                    margin-bottom: 2rem;">
            <p style="margin: 0; color: #4b5563; font-size: 0.95rem;">
                💡 <strong>使用说明：</strong>在这里可以管理交易原因列表。添加、编辑或删除交易原因后，在添加或编辑交易记录时就可以使用这些原因。
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # 显示当前交易原因列表
    st.markdown('<h2 class="section-header">当前交易原因列表</h2>', unsafe_allow_html=True)
    
    if current_reasons:
        # 统计信息和搜索
        col_stat1, col_stat2, col_stat3 = st.columns([1, 1, 2])
        with col_stat1:
            st.metric("📊 总数", len(current_reasons))
        
        with col_stat2:
            # 搜索功能
            search_reason = st.text_input(
                "🔍 搜索原因",
                placeholder="输入关键词...",
                help="快速查找交易原因",
                key="search_reason_input"
            )
        
        # 过滤交易原因
        filtered_reasons = current_reasons
        if search_reason and search_reason.strip():
            search_lower = search_reason.strip().lower()
            filtered_reasons = [r for r in current_reasons if search_lower in r.lower()]
        
        if filtered_reasons:
            # 使用网格布局显示交易原因卡片（每行2个）
            num_reasons = len(filtered_reasons)
            for row_start in range(0, num_reasons, 2):
                cols = st.columns(2)
                for col_idx, col in enumerate(cols):
                    reason_idx = row_start + col_idx
                    if reason_idx < num_reasons:
                        reason = filtered_reasons[reason_idx]
                        original_idx = current_reasons.index(reason)
                        # 使用reason作为唯一标识符，避免索引冲突
                        reason_key = reason.replace(" ", "_").replace("/", "_")
                        
                        with col:
                            # 卡片式布局
                            st.markdown(f"""
                                <div class="reason-card">
                                    <div class="reason-card-content">
                                        <div class="reason-number">{original_idx + 1}</div>
                                        <div class="reason-text">{reason}</div>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # 操作按钮
                            col_edit, col_delete = st.columns(2)
                            with col_edit:
                                if st.button("✏️ 编辑", key=f"edit_reason_{reason_key}", use_container_width=True):
                                    st.session_state[f'editing_reason_{reason_key}'] = True
                                    st.session_state[f'editing_reason_value_{reason_key}'] = reason
                                    st.rerun()
                            
                            with col_delete:
                                if st.button("🗑️ 删除", key=f"delete_reason_{reason_key}", use_container_width=True, type="secondary"):
                                    if remove_trading_reason(reason):
                                        st.success(f"✅ 已删除 '{reason}'")
                                        st.rerun()
                                    else:
                                        st.error("❌ 删除失败")
                            
                            # 编辑表单
                            if st.session_state.get(f'editing_reason_{reason_key}', False):
                                with st.expander(f"✏️ 编辑: {reason}", expanded=True):
                                    new_reason = st.text_input(
                                        "新的交易原因",
                                        value=st.session_state.get(f'editing_reason_value_{reason_key}', reason),
                                        key=f"new_reason_input_{reason_key}"
                                    )
                                    col_edit_btn1, col_edit_btn2 = st.columns(2)
                                    with col_edit_btn1:
                                        if st.button("✅ 保存", key=f"save_reason_{reason_key}", use_container_width=True, type="primary"):
                                            if new_reason and new_reason.strip():
                                                if update_trading_reason(reason, new_reason.strip()):
                                                    st.success(f"✅ 已更新为 '{new_reason.strip()}'")
                                                    st.session_state[f'editing_reason_{reason_key}'] = False
                                                    st.rerun()
                                                else:
                                                    st.error("❌ 更新失败")
                                            else:
                                                st.error("❌ 交易原因不能为空")
                                    with col_edit_btn2:
                                        if st.button("❌ 取消", key=f"cancel_reason_{reason_key}", use_container_width=True):
                                            st.session_state[f'editing_reason_{reason_key}'] = False
                                            st.rerun()
            
            if search_reason and search_reason.strip() and len(filtered_reasons) < len(current_reasons):
                st.info(f"🔍 找到 {len(filtered_reasons)} 个匹配的交易原因（共 {len(current_reasons)} 个）")
        else:
            st.warning(f"🔍 未找到包含「{search_reason}」的交易原因")
    else:
        # 美化空状态
        st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">📝</div>
                <h3 style="color: #4b5563; margin: 0.5rem 0;">当前没有交易原因</h3>
                <p class="empty-state-text">请添加第一个交易原因</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 添加新交易原因
    st.markdown('<h2 class="section-header">添加新交易原因</h2>', unsafe_allow_html=True)
    
    with st.form("add_trading_reason_form"):
        new_reason_input = st.text_input(
            "💭 交易原因",
            placeholder="例如：技术面突破、基本面改善等...",
            help="输入新的交易原因"
        )
        
        col_add_btn1, col_add_btn2 = st.columns([1, 3])
        with col_add_btn1:
            add_submitted = st.form_submit_button("➕ 添加", type="primary", use_container_width=True)
        
        if add_submitted:
            if not new_reason_input or not new_reason_input.strip():
                st.error("❌ 请输入交易原因")
            else:
                if add_trading_reason(new_reason_input.strip()):
                    st.success(f"✅ 已添加交易原因: '{new_reason_input.strip()}'")
                    st.rerun()
                else:
                    st.error("❌ 添加失败，可能该原因已存在")
    
    # 批量操作
    st.markdown("---")
    with st.expander("📦 批量操作", expanded=False):
        st.markdown("### 批量导入交易原因")
        batch_reasons_text = st.text_area(
            "输入多个交易原因（每行一个）",
            placeholder="技术面突破\n基本面改善\n消息面利好\n...",
            height=150,
            help="每行输入一个交易原因，系统会自动去重"
        )
        
        if st.button("📥 批量导入", type="primary", use_container_width=True):
            if batch_reasons_text and batch_reasons_text.strip():
                reasons_list = [r.strip() for r in batch_reasons_text.strip().split('\n') if r.strip()]
                if reasons_list:
                    # 合并到现有列表
                    existing_reasons = get_trading_reasons()
                    all_reasons = list(set(existing_reasons + reasons_list))
                    if save_trading_reasons(all_reasons):
                        st.success(f"✅ 成功导入 {len(reasons_list)} 个交易原因（已去重）")
                        st.rerun()
                    else:
                        st.error("❌ 批量导入失败")
                else:
                    st.warning("⚠️ 没有有效的交易原因")
            else:
                st.error("❌ 请输入交易原因")

# 说明信息
st.markdown("---")
st.info("""
💡 **使用说明：**
- **交易记录：** 查看、筛选和搜索所有交易记录，支持按日期、操作类型和股票筛选
- **添加记录：** 记录新的交易，包括买入和卖出，支持填写盈亏信息
- **统计分析：** 查看交易统计信息，包括总盈亏、胜率、按日期和股票的统计
- **交易原因管理：** 管理交易原因列表，可以添加、编辑、删除交易原因，支持批量导入
- **注意事项：** 卖出时建议填写盈亏金额和盈亏比例，以便进行准确的统计分析
""")

