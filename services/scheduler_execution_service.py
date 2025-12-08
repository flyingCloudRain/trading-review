#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时任务执行记录服务
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from datetime import date, datetime
from models.scheduler_execution import SchedulerExecution


class SchedulerExecutionService:
    """定时任务执行记录服务"""
    
    @staticmethod
    def create_execution(
        db: Session,
        job_id: str,
        job_name: str,
        execution_date: date,
        execution_time: datetime,
        status: str,
        duration_seconds: Optional[float] = None,
        industry_sectors_count: Optional[int] = None,
        concept_sectors_count: Optional[int] = None,
        zt_pool_count: Optional[int] = None,
        zbgc_pool_count: Optional[int] = None,
        dtgc_pool_count: Optional[int] = None,
        index_count: Optional[int] = None,
        error_message: Optional[str] = None,
        error_traceback: Optional[str] = None,
        is_trading_day: Optional[bool] = None,
        notes: Optional[str] = None
    ) -> SchedulerExecution:
        """
        创建执行记录
        
        Args:
            db: 数据库会话
            job_id: 任务ID
            job_name: 任务名称
            execution_date: 执行日期
            execution_time: 执行时间
            status: 执行状态 (success/failed/skipped)
            duration_seconds: 执行耗时（秒）
            industry_sectors_count: 行业板块数据条数
            concept_sectors_count: 概念板块数据条数
            zt_pool_count: 涨停股票池数据条数
            zbgc_pool_count: 炸板股票池数据条数
            dtgc_pool_count: 跌停股票池数据条数
            index_count: 指数数据条数
            error_message: 错误信息
            error_traceback: 错误堆栈
            is_trading_day: 是否为交易日
            notes: 备注信息
            
        Returns:
            创建的执行记录对象
        """
        execution = SchedulerExecution(
            job_id=job_id,
            job_name=job_name,
            execution_date=execution_date,
            execution_time=execution_time,
            status=status,
            duration_seconds=duration_seconds,
            industry_sectors_count=industry_sectors_count or 0,
            concept_sectors_count=concept_sectors_count or 0,
            zt_pool_count=zt_pool_count or 0,
            zbgc_pool_count=zbgc_pool_count or 0,
            dtgc_pool_count=dtgc_pool_count or 0,
            index_count=index_count or 0,
            error_message=error_message,
            error_traceback=error_traceback,
            is_trading_day=is_trading_day,
            notes=notes
        )
        
        db.add(execution)
        db.commit()
        db.refresh(execution)
        return execution
    
    @staticmethod
    def get_executions_by_date(db: Session, target_date: date) -> List[SchedulerExecution]:
        """获取指定日期的所有执行记录"""
        return db.query(SchedulerExecution).filter(
            SchedulerExecution.execution_date == target_date
        ).order_by(desc(SchedulerExecution.execution_time)).all()
    
    @staticmethod
    def get_executions_by_job_id(db: Session, job_id: str, limit: int = 100) -> List[SchedulerExecution]:
        """获取指定任务ID的执行记录（最近N条）"""
        return db.query(SchedulerExecution).filter(
            SchedulerExecution.job_id == job_id
        ).order_by(desc(SchedulerExecution.execution_time)).limit(limit).all()
    
    @staticmethod
    def get_recent_executions(db: Session, limit: int = 50) -> List[SchedulerExecution]:
        """获取最近的执行记录"""
        return db.query(SchedulerExecution).order_by(
            desc(SchedulerExecution.execution_time)
        ).limit(limit).all()
    
    @staticmethod
    def get_executions_by_date_range(
        db: Session,
        start_date: date,
        end_date: date
    ) -> List[SchedulerExecution]:
        """获取日期范围内的执行记录"""
        return db.query(SchedulerExecution).filter(
            and_(
                SchedulerExecution.execution_date >= start_date,
                SchedulerExecution.execution_date <= end_date
            )
        ).order_by(desc(SchedulerExecution.execution_time)).all()
    
    @staticmethod
    def get_execution_statistics(db: Session, start_date: date, end_date: date) -> Dict:
        """获取执行统计信息"""
        executions = SchedulerExecutionService.get_executions_by_date_range(
            db, start_date, end_date
        )
        
        total = len(executions)
        success = len([e for e in executions if e.status == 'success'])
        failed = len([e for e in executions if e.status == 'failed'])
        skipped = len([e for e in executions if e.status == 'skipped'])
        
        return {
            'total': total,
            'success': success,
            'failed': failed,
            'skipped': skipped,
            'success_rate': (success / total * 100) if total > 0 else 0,
        }

