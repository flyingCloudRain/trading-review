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
from database.db import SessionLocal
from services.scheduler_execution_service import SchedulerExecutionService
from datetime import date, timedelta

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
        font-size: 1.5rem;
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
        font-size: 1.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #1f77b4;
    }
    /* 统一二级标题样式 - 无背景色 */
    .section-header {
        font-size: 1rem;
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
                    
                    # 方法3: 如果调度器未运行或无法获取，尝试从trigger计算下次执行时间
                    if next_run is None and hasattr(job, 'trigger'):
                        try:
                            # 使用trigger的get_next_fire_time方法计算下次执行时间
                            from apscheduler.triggers.cron import CronTrigger
                            if isinstance(job.trigger, CronTrigger):
                                # 计算下次执行时间（基于当前时间和trigger规则）
                                next_run = job.trigger.get_next_fire_time(None, now)
                        except Exception:
                            # 如果计算失败，尝试解析trigger信息
                            pass
                except Exception:
                    # 如果获取失败，next_run 保持为 None
                    pass
                
                if next_run:
                    # 确保next_run是datetime对象
                    if isinstance(next_run, datetime):
                        next_run_dt = next_run
                    else:
                        # 如果是其他类型，尝试转换
                        try:
                            next_run_dt = datetime.fromisoformat(str(next_run))
                            if next_run_dt.tzinfo is None:
                                # 如果没有时区信息，假设是UTC+8
                                next_run_dt = UTC8.localize(next_run_dt)
                        except:
                            next_run_dt = None
                    
                    if next_run_dt:
                        # 如果next_run_dt没有时区信息，添加UTC+8时区
                        if next_run_dt.tzinfo is None:
                            next_run_dt = UTC8.localize(next_run_dt)
                        # 如果next_run_dt有时区信息，转换为UTC+8
                        elif next_run_dt.tzinfo != UTC8:
                            next_run_dt = next_run_dt.astimezone(UTC8)
                        
                        next_run_str = next_run_dt.strftime("%Y-%m-%d %H:%M:%S")
                        time_until = next_run_dt - now
                        total_seconds = time_until.total_seconds()
                        
                        if total_seconds > 0:
                            days = int(total_seconds // 86400)
                            hours = int((total_seconds % 86400) // 3600)
                            minutes = int((total_seconds % 3600) // 60)
                            
                            if days > 0:
                                time_str = f"{days}天{hours}小时{minutes}分钟"
                            elif hours > 0:
                                time_str = f"{hours}小时{minutes}分钟"
                            else:
                                time_str = f"{minutes}分钟"
                            
                            status_prefix = "" if is_running else "（调度器未运行，此为预计时间）"
                            st.markdown(f"**下次执行时间**: {next_run_str} {status_prefix}")
                            st.markdown(f"**距离执行**: 还有 {time_str}")
                        else:
                            st.markdown(f"**下次执行时间**: {next_run_str} (即将执行或已过期)")
                    else:
                        if is_running:
                            st.markdown("**下次执行时间**: 未安排")
                        else:
                            st.markdown("**下次执行时间**: 未安排（调度器未运行）")
                else:
                    # 如果无法获取执行时间，尝试显示trigger信息
                    if hasattr(job, 'trigger'):
                        trigger_str = str(job.trigger)
                        # 尝试从trigger字符串中提取时间信息
                        if 'hour=15' in trigger_str and 'minute=10' in trigger_str:
                            # 计算今天的15:10或明天的15:10
                            today_1510 = now.replace(hour=15, minute=10, second=0, microsecond=0)
                            if today_1510 > now:
                                next_run_dt = today_1510
                            else:
                                from datetime import timedelta
                                next_run_dt = today_1510 + timedelta(days=1)
                            
                            next_run_str = next_run_dt.strftime("%Y-%m-%d %H:%M:%S")
                            time_until = next_run_dt - now
                            total_seconds = time_until.total_seconds()
                            
                            if total_seconds > 0:
                                days = int(total_seconds // 86400)
                                hours = int((total_seconds % 86400) // 3600)
                                minutes = int((total_seconds % 3600) // 60)
                                
                                if days > 0:
                                    time_str = f"{days}天{hours}小时{minutes}分钟"
                                elif hours > 0:
                                    time_str = f"{hours}小时{minutes}分钟"
                                else:
                                    time_str = f"{minutes}分钟"
                                
                                status_prefix = "" if is_running else "（调度器未运行，此为预计时间）"
                                st.markdown(f"**下次执行时间**: {next_run_str} {status_prefix}")
                                st.markdown(f"**距离执行**: 还有 {time_str}")
                            else:
                                st.markdown(f"**下次执行时间**: {next_run_str} (即将执行)")
                        else:
                            if is_running:
                                st.markdown("**下次执行时间**: 未安排")
                            else:
                                st.markdown("**下次执行时间**: 未安排（调度器未运行）")
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
                                            # 1. 保存行业板块数据
                                            try:
                                                industry_count = SectorHistoryService.save_today_sectors(db, sector_type='industry')
                                                results['sectors'] = industry_count
                                                excel_file = append_sectors_to_excel()
                                            except Exception as e:
                                                results['sectors'] = f"失败: {str(e)}"
                                            
                                            # 1.1 保存概念板块数据
                                            try:
                                                concept_count = SectorHistoryService.save_today_sectors(db, sector_type='concept')
                                                if 'sectors' in results and isinstance(results['sectors'], int):
                                                    results['sectors'] = f"行业:{results['sectors']}, 概念:{concept_count}"
                                                elif 'sectors' in results:
                                                    results['sectors'] = f"{results['sectors']}, 概念:{concept_count}"
                                                else:
                                                    results['sectors'] = f"概念:{concept_count}"
                                            except Exception as e:
                                                if 'sectors' in results:
                                                    results['sectors'] = f"{results['sectors']}, 概念失败: {str(e)}"
                                                else:
                                                    results['sectors'] = f"概念失败: {str(e)}"
                                            
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
st.markdown("### 📜 执行历史（从数据库查询）")

# 日期筛选
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    start_date = st.date_input(
        "开始日期",
        value=get_utc8_date() - timedelta(days=7),
        max_value=get_utc8_date(),
        help="查询执行历史的开始日期"
    )
with col2:
    end_date = st.date_input(
        "结束日期",
        value=get_utc8_date(),
        max_value=get_utc8_date(),
        help="查询执行历史的结束日期"
    )
with col3:
    limit = st.number_input(
        "显示条数",
        min_value=10,
        max_value=100,
        value=50,
        step=10,
        help="最多显示的执行记录条数"
    )

# 任务筛选
job_ids = ['save_daily_data', 'save_realtime_fund_flow_1510']
selected_job_id = st.selectbox(
    "筛选任务",
    options=['全部'] + job_ids,
    help="选择要查看的任务，或查看全部任务"
)

# 查询执行历史
try:
    db = SessionLocal()
    try:
        if selected_job_id == '全部':
            # 查询日期范围内的所有执行记录
            executions = SchedulerExecutionService.get_executions_by_date_range(
                db, start_date, end_date
            )
        else:
            # 查询指定任务的执行记录
            executions = SchedulerExecutionService.get_executions_by_job_id(
                db, selected_job_id, limit=limit
            )
            # 按日期范围过滤
            executions = [e for e in executions if start_date <= e.execution_date <= end_date]
        
        # 限制显示条数
        executions = executions[:limit]
        
        if executions:
            # 转换为DataFrame
            history_data = []
            for exec in executions:
                # 状态显示
                if exec.status == 'success':
                    status_text = "✅ 成功"
                    status_color = "#28a745"
                elif exec.status == 'skipped':
                    status_text = "⏭️ 已跳过"
                    status_color = "#ffc107"
                elif exec.status == 'failed':
                    status_text = "❌ 失败"
                    status_color = "#dc3545"
                else:
                    status_text = exec.status
                    status_color = "#6c757d"
                
                # 构建详情信息
                details = []
                if exec.industry_sectors_count and exec.industry_sectors_count > 0:
                    details.append(f"行业板块:{exec.industry_sectors_count}")
                if exec.concept_sectors_count and exec.concept_sectors_count > 0:
                    details.append(f"概念板块:{exec.concept_sectors_count}")
                if exec.zt_pool_count and exec.zt_pool_count > 0:
                    details.append(f"涨停:{exec.zt_pool_count}")
                if exec.zbgc_pool_count and exec.zbgc_pool_count > 0:
                    details.append(f"炸板:{exec.zbgc_pool_count}")
                if exec.dtgc_pool_count and exec.dtgc_pool_count > 0:
                    details.append(f"跌停:{exec.dtgc_pool_count}")
                if exec.index_count and exec.index_count > 0:
                    details.append(f"指数:{exec.index_count}")
                
                detail_text = ", ".join(details) if details else "-"
                
                # 执行耗时
                duration_text = f"{exec.duration_seconds:.2f}秒" if exec.duration_seconds else "-"
                
                # 是否为交易日
                trading_day_text = "是" if exec.is_trading_day else "否" if exec.is_trading_day is False else "-"
                
                history_data.append({
                    "执行时间": exec.execution_time.strftime("%Y-%m-%d %H:%M:%S") if exec.execution_time else "-",
                    "执行日期": exec.execution_date.strftime("%Y-%m-%d") if exec.execution_date else "-",
                    "任务名称": exec.job_name,
                    "状态": status_text,
                    "耗时": duration_text,
                    "数据条数": detail_text,
                    "交易日": trading_day_text,
                })
            
            history_df = pd.DataFrame(history_data)
            
            # 显示统计信息
            total_count = len(executions)
            success_count = len([e for e in executions if e.status == 'success'])
            failed_count = len([e for e in executions if e.status == 'failed'])
            skipped_count = len([e for e in executions if e.status == 'skipped'])
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("总执行次数", total_count)
            with col2:
                st.metric("成功", success_count, delta=f"{success_count/total_count*100:.1f}%" if total_count > 0 else None)
            with col3:
                st.metric("失败", failed_count, delta=f"{failed_count/total_count*100:.1f}%" if total_count > 0 else None, delta_color="inverse")
            with col4:
                st.metric("跳过", skipped_count, delta=f"{skipped_count/total_count*100:.1f}%" if total_count > 0 else None)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 显示详细表格
            st.dataframe(history_df, use_container_width=True, hide_index=True)
            
            # 查看详细信息
            st.markdown("#### 📋 详细信息")
            selected_index = st.selectbox(
                "选择要查看的记录",
                options=range(len(executions)),
                format_func=lambda x: f"{executions[x].execution_time.strftime('%Y-%m-%d %H:%M:%S')} - {executions[x].job_name} - {executions[x].status}" if executions[x].execution_time else f"记录 {x}",
                help="选择一条记录查看详细信息"
            )
            
            if selected_index is not None and selected_index < len(executions):
                exec = executions[selected_index]
                with st.expander(f"查看详细信息 - {exec.job_name}", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**基本信息**")
                        st.write(f"- 任务ID: `{exec.job_id}`")
                        st.write(f"- 任务名称: {exec.job_name}")
                        st.write(f"- 执行日期: {exec.execution_date}")
                        st.write(f"- 执行时间: {exec.execution_time.strftime('%Y-%m-%d %H:%M:%S') if exec.execution_time else '-'}")
                        st.write(f"- 执行状态: {exec.status}")
                        st.write(f"- 执行耗时: {exec.duration_seconds:.2f}秒" if exec.duration_seconds else "- 执行耗时: -")
                        st.write(f"- 是否为交易日: {'是' if exec.is_trading_day else '否' if exec.is_trading_day is False else '-'}")
                    
                    with col2:
                        st.markdown("**数据统计**")
                        st.write(f"- 行业板块: {exec.industry_sectors_count or 0} 条")
                        st.write(f"- 概念板块: {exec.concept_sectors_count or 0} 条")
                        st.write(f"- 涨停股票: {exec.zt_pool_count or 0} 条")
                        st.write(f"- 炸板股票: {exec.zbgc_pool_count or 0} 条")
                        st.write(f"- 跌停股票: {exec.dtgc_pool_count or 0} 条")
                        st.write(f"- 指数数据: {exec.index_count or 0} 条")
                    
                    if exec.notes:
                        st.markdown("**备注**")
                        st.write(exec.notes)
                    
                    if exec.error_message:
                        st.markdown("**错误信息**")
                        st.error(exec.error_message)
                        if exec.error_traceback:
                            with st.expander("查看错误堆栈"):
                                st.code(exec.error_traceback, language='python')
        else:
            st.info(f"📝 在 {start_date} 至 {end_date} 期间暂无执行历史记录")
            
    except Exception as e:
        st.error(f"❌ 查询执行历史失败: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
    finally:
        db.close()
except Exception as e:
    st.error(f"❌ 数据库连接失败: {str(e)}")
    st.info("💡 提示：请确保数据库配置正确且已初始化")

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

