#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时任务执行记录模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, Date
from sqlalchemy.sql import func
from database.db import Base

class SchedulerExecution(Base):
    """定时任务执行记录模型"""
    __tablename__ = 'scheduler_execution'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(100), nullable=False, index=True, comment='任务ID')
    job_name = Column(String(200), nullable=False, comment='任务名称')
    execution_date = Column(Date, nullable=False, index=True, comment='执行日期')
    execution_time = Column(DateTime, nullable=False, index=True, comment='执行时间')
    status = Column(String(20), nullable=False, index=True, comment='执行状态: success/failed/skipped')
    duration_seconds = Column(Float, nullable=True, comment='执行耗时（秒）')
    
    # 数据保存统计
    industry_sectors_count = Column(Integer, nullable=True, default=0, comment='行业板块数据条数')
    concept_sectors_count = Column(Integer, nullable=True, default=0, comment='概念板块数据条数')
    zt_pool_count = Column(Integer, nullable=True, default=0, comment='涨停股票池数据条数')
    zbgc_pool_count = Column(Integer, nullable=True, default=0, comment='炸板股票池数据条数')
    dtgc_pool_count = Column(Integer, nullable=True, default=0, comment='跌停股票池数据条数')
    index_count = Column(Integer, nullable=True, default=0, comment='指数数据条数')
    
    # 错误信息
    error_message = Column(Text, nullable=True, comment='错误信息')
    error_traceback = Column(Text, nullable=True, comment='错误堆栈')
    
    # 其他信息
    is_trading_day = Column(Boolean, nullable=True, comment='是否为交易日')
    notes = Column(Text, nullable=True, comment='备注信息')
    
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'jobId': self.job_id,
            'jobName': self.job_name,
            'executionDate': self.execution_date.strftime('%Y-%m-%d') if self.execution_date else None,
            'executionTime': self.execution_time.isoformat() if self.execution_time else None,
            'status': self.status,
            'durationSeconds': self.duration_seconds,
            'industrySectorsCount': self.industry_sectors_count,
            'conceptSectorsCount': self.concept_sectors_count,
            'ztPoolCount': self.zt_pool_count,
            'zbgcPoolCount': self.zbgc_pool_count,
            'dtgcPoolCount': self.dtgc_pool_count,
            'indexCount': self.index_count,
            'errorMessage': self.error_message,
            'errorTraceback': self.error_traceback,
            'isTradingDay': self.is_trading_day,
            'notes': self.notes,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }

