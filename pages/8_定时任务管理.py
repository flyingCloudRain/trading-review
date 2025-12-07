#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时任务管理页面 - 查看定时任务状态，手动执行任务
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import sys
from datetime import datetime
import traceback

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tasks.sector_scheduler import get_scheduler
from utils.time_utils import UTC8, get_utc8_date

st.set_page_config(
    page_title="定时任务管理",
    page_icon="⏰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 页面样式
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
""", unsafe_allow_html=True)

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

# 页面标题
st.markdown('<h1 class="main-header">⏰ 定时任务管理</h1>', unsafe_allow_html=True)

# 获取调度器实例
try:
    scheduler_obj = get_scheduler()
    scheduler = scheduler_obj.scheduler
    
    # 如果调度器未启动，尝试启动（但不强制，因为可能在其他地方管理）
    if not scheduler.running:
        # 只在用户明确要求时启动，这里只显示状态
        pass
except Exception as e:
    st.error(f"❌ 无法获取调度器实例: {str(e)}")
    st.info("💡 提示：如果 Flask 应用正在运行，调度器应该已经启动。Streamlit 应用可以查看状态，但建议通过 Flask 应用管理调度器。")
    st.stop()

# 调度器状态
st.markdown("### 📊 调度器状态")
col1, col2, col3 = st.columns(3)

is_running = scheduler.running
status_color = "🟢" if is_running else "🔴"
status_text = "运行中" if is_running else "已停止"

with col1:
    st.metric("调度器状态", f"{status_color} {status_text}")

with col2:
    job_count = len(scheduler.get_jobs())
    st.metric("任务数量", job_count)

with col3:
    now = datetime.now(UTC8)
    st.metric("当前时间", now.strftime("%H:%M:%S"))

# 任务列表
st.markdown("---")
st.markdown("### 📋 定时任务列表")

if job_count == 0:
    st.warning("⚠️ 当前没有配置的定时任务")
else:
    jobs = scheduler.get_jobs()
    
    for job in jobs:
        with st.container():
            st.markdown(f'<div class="job-card">', unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**任务名称**: {job.name}")
                st.markdown(f"**任务ID**: `{job.id}`")
                
                # 下次执行时间
                next_run = None
                try:
                    # 方法1: 从调度器重新获取job对象（更可靠）
                    if is_running:
                        job_from_scheduler = scheduler.get_job(job.id)
                        if job_from_scheduler:
                            next_run = getattr(job_from_scheduler, 'next_run_time', None)
                    
                    # 方法2: 如果方法1失败，尝试直接从job对象获取
                    if next_run is None:
                        next_run = getattr(job, 'next_run_time', None)
                except Exception:
                    # 如果获取失败，next_run 保持为 None
                    pass
                
                if next_run:
                    next_run_str = next_run.strftime("%Y-%m-%d %H:%M:%S")
                    time_until = next_run - now
                    hours = int(time_until.total_seconds() // 3600)
                    minutes = int((time_until.total_seconds() % 3600) // 60)
                    
                    if time_until.total_seconds() > 0:
                        st.markdown(f"**下次执行时间**: {next_run_str} (还有 {hours}小时{minutes}分钟)")
                    else:
                        st.markdown(f"**下次执行时间**: {next_run_str} (即将执行)")
                else:
                    if is_running:
                        st.markdown("**下次执行时间**: 未安排")
                    else:
                        st.markdown("**下次执行时间**: 未安排（调度器未运行）")
                
                # 触发器信息
                if hasattr(job.trigger, 'fields'):
                    trigger_info = []
                    for field in job.trigger.fields:
                        trigger_info.append(f"{field.name}={field}")
                    st.markdown(f"**触发规则**: {', '.join(trigger_info)}")
                else:
                    st.markdown(f"**触发规则**: {str(job.trigger)}")
            
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                # 强制执行选项（仅对 save_daily_data 任务）
                force_execution = False
                if job.id == 'save_daily_data':
                    force_execution = st.checkbox("强制执行", key=f"force_{job.id}", 
                                                  help="跳过交易日检查，强制执行任务")
                
                # 手动执行按钮
                if st.button(f"▶️ 立即执行", key=f"run_{job.id}", use_container_width=True):
                    with st.spinner("正在执行任务，请稍候..."):
                        try:
                            # 执行任务
                            if job.id == 'save_daily_data':
                                # 使用 run_scheduler_task 中的函数
                                results = {}
                                try:
                                    # 检查是否为交易日（除非强制执行）
                                    if not force_execution:
                                        today = get_utc8_date()
                                        if not scheduler_obj._is_trading_day(today):
                                            st.warning(f"⚠️ 今日 ({today}) 不是交易日，任务已跳过")
                                            st.info('💡 如需强制执行，请勾选上方的"强制执行"选项')
                                            # 保存跳过记录
                                            execution_key = f"execution_{job.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                                            st.session_state[execution_key] = {
                                                'job_id': job.id,
                                                'job_name': job.name,
                                                'execution_time': datetime.now(UTC8).strftime("%Y-%m-%d %H:%M:%S"),
                                                'status': 'skipped',
                                                'reason': f'今日 ({today}) 不是交易日'
                                            }
                                            # 不继续执行，但继续显示页面
                                            continue_execution = False
                                        else:
                                            continue_execution = True
                                    else:
                                        continue_execution = True
                                    
                                    if not continue_execution:
                                        # 跳过执行，但继续显示页面
                                        pass
                                    else:
                                        # 获取数据库会话
                                        from database.db import SessionLocal
                                        from services.sector_history_service import SectorHistoryService
                                        from services.zt_pool_history_service import ZtPoolHistoryService
                                        from services.zbgc_pool_history_service import ZbgcPoolHistoryService
                                        from services.dtgc_pool_history_service import DtgcPoolHistoryService
                                        from services.index_history_service import IndexHistoryService
                                        from utils.excel_export import append_sectors_to_excel
                                        
                                        db = SessionLocal()
                                        try:
                                            # 1. 保存板块数据
                                            try:
                                                saved_count = SectorHistoryService.save_today_sectors(db)
                                                results['sectors'] = saved_count
                                                excel_file = append_sectors_to_excel()
                                            except Exception as e:
                                                results['sectors'] = f"失败: {str(e)}"
                                            
                                            # 2. 保存涨停股票池数据
                                            try:
                                                zt_count = ZtPoolHistoryService.save_today_zt_pool(db)
                                                results['zt_pool'] = zt_count
                                            except Exception as e:
                                                results['zt_pool'] = f"失败: {str(e)}"
                                            
                                            # 3. 保存炸板股票池数据
                                            try:
                                                zbgc_count = ZbgcPoolHistoryService.save_today_zbgc_pool(db)
                                                results['zbgc_pool'] = zbgc_count
                                            except Exception as e:
                                                results['zbgc_pool'] = f"失败: {str(e)}"
                                            
                                            # 4. 保存跌停股票池数据
                                            try:
                                                dtgc_count = DtgcPoolHistoryService.save_today_dtgc_pool(db)
                                                results['dtgc_pool'] = dtgc_count
                                            except Exception as e:
                                                results['dtgc_pool'] = f"失败: {str(e)}"
                                            
                                            # 5. 保存指数数据
                                            try:
                                                index_count = IndexHistoryService.save_today_indices(db)
                                                results['indices'] = index_count
                                            except Exception as e:
                                                results['indices'] = f"失败: {str(e)}"
                                            
                                        finally:
                                            db.close()
                                        
                                        # 显示执行结果
                                        st.success("✅ 任务执行完成！")
                                        
                                        # 结果详情
                                        st.markdown("#### 📊 执行结果")
                                        result_df = pd.DataFrame([
                                            {"数据类型": "板块数据", "结果": results.get('sectors', '未执行')},
                                            {"数据类型": "涨停股票池", "结果": results.get('zt_pool', '未执行')},
                                            {"数据类型": "炸板股票池", "结果": results.get('zbgc_pool', '未执行')},
                                            {"数据类型": "跌停股票池", "结果": results.get('dtgc_pool', '未执行')},
                                            {"数据类型": "指数数据", "结果": results.get('indices', '未执行')},
                                        ])
                                        st.dataframe(result_df, use_container_width=True, hide_index=True)
                                        
                                        # 保存执行结果到 session state
                                        execution_key = f"execution_{job.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                                        st.session_state[execution_key] = {
                                            'job_id': job.id,
                                            'job_name': job.name,
                                            'execution_time': datetime.now(UTC8).strftime("%Y-%m-%d %H:%M:%S"),
                                            'results': results,
                                            'status': 'success'
                                        }
                                    
                                except Exception as e:
                                    error_msg = str(e)
                                    st.error(f"❌ 任务执行失败: {error_msg}")
                                    st.code(traceback.format_exc())
                                    
                                    # 保存失败结果
                                    execution_key = f"execution_{job.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                                    st.session_state[execution_key] = {
                                        'job_id': job.id,
                                        'job_name': job.name,
                                        'execution_time': datetime.now(UTC8).strftime("%Y-%m-%d %H:%M:%S"),
                                        'error': error_msg,
                                        'status': 'error'
                                    }
                            else:
                                # 对于其他任务，直接运行
                                job.func()
                                st.success("✅ 任务执行完成！")
                                
                        except Exception as e:
                            st.error(f"❌ 任务执行失败: {str(e)}")
                            st.code(traceback.format_exc())
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

# 执行历史
st.markdown("---")
st.markdown("### 📜 执行历史")

# 从 session state 获取执行历史
execution_history = []
for key in st.session_state.keys():
    if key.startswith('execution_'):
        execution_history.append(st.session_state[key])

if execution_history:
    # 按执行时间倒序排列
    execution_history.sort(key=lambda x: x.get('execution_time', ''), reverse=True)
    
    # 只显示最近10条
    recent_history = execution_history[:10]
    
    history_data = []
    for hist in recent_history:
        status = hist.get('status', 'unknown')
        if status == 'success':
            status_text = "✅ 成功"
            detail = str(hist.get('results', ''))
        elif status == 'skipped':
            status_text = "⏭️ 已跳过"
            detail = hist.get('reason', '')
        else:
            status_text = "❌ 失败"
            detail = hist.get('error', '')
        
        history_data.append({
            "执行时间": hist.get('execution_time', ''),
            "任务名称": hist.get('job_name', ''),
            "状态": status_text,
            "详情": detail
        })
    
    history_df = pd.DataFrame(history_data)
    st.dataframe(history_df, use_container_width=True, hide_index=True)
    
    # 清除历史按钮
    if st.button("🗑️ 清除执行历史"):
        keys_to_remove = [key for key in st.session_state.keys() if key.startswith('execution_')]
        for key in keys_to_remove:
            del st.session_state[key]
        st.rerun()
else:
    st.info("📝 暂无执行历史记录")

# 调度器控制
st.markdown("---")
st.markdown("### ⚙️ 调度器控制")

col1, col2 = st.columns(2)

with col1:
    if is_running:
        if st.button("⏸️ 停止调度器", type="primary", use_container_width=True):
            try:
                scheduler.shutdown()
                st.success("✅ 调度器已停止")
                st.rerun()
            except Exception as e:
                st.error(f"❌ 停止调度器失败: {str(e)}")
                st.warning("⚠️ 注意：如果调度器是在 Flask 应用中启动的，建议通过停止 Flask 应用来停止调度器。")
    else:
        if st.button("▶️ 启动调度器", type="primary", use_container_width=True):
            try:
                scheduler.start()
                st.success("✅ 调度器已启动")
                st.rerun()
            except Exception as e:
                st.error(f"❌ 启动调度器失败: {str(e)}")
                st.info("💡 提示：如果 Flask 应用正在运行，调度器应该已经启动。建议通过 Flask 应用管理调度器。")

with col2:
    if st.button("🔄 刷新状态", use_container_width=True):
        st.rerun()

# 说明信息
st.markdown("---")
with st.expander("ℹ️ 使用说明"):
    st.markdown("""
    ### 功能说明
    
    1. **调度器状态**: 显示定时任务调度器的运行状态
    2. **任务列表**: 显示所有配置的定时任务及其详细信息
    3. **手动执行**: 点击"立即执行"按钮可以手动触发任务执行
    4. **执行历史**: 查看最近的任务执行记录和结果
    5. **调度器控制**: 可以启动或停止调度器
    
    ### 注意事项
    
    - 定时任务会在每日 15:10（北京时间）自动执行
    - 手动执行会跳过交易日检查（除非是交易日）
    - 执行结果会保存在会话中，刷新页面后会保留
    - 如果调度器未运行，定时任务不会自动执行
    """)

