#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据加载工具（带缓存）
"""
import streamlit as st
import pandas as pd
from database.db import SessionLocal
from services.sector_history_service import SectorHistoryService
from services.zt_pool_history_service import ZtPoolHistoryService
from services.zbgc_pool_history_service import ZbgcPoolHistoryService
from services.dtgc_pool_history_service import DtgcPoolHistoryService
from datetime import date

@st.cache_data(ttl=300)  # 缓存5分钟
def load_sector_data(
    start_date: date,
    end_date: date,
    sector_names: list = None
) -> pd.DataFrame:
    """
    加载板块数据（带缓存）
    
    Args:
        start_date: 开始日期
        end_date: 结束日期
        sector_names: 板块名称列表（可选）
    
    Returns:
        包含板块数据的DataFrame
    """
    db = SessionLocal()
    try:
        if start_date == end_date:
            sectors = SectorHistoryService.get_sectors_by_date(db, start_date)
        else:
            sectors = SectorHistoryService.get_sectors_by_date_range(db, start_date, end_date)
        
        df = pd.DataFrame(sectors)
        
        if sector_names and not df.empty and 'name' in df.columns:
            df = df[df['name'].isin(sector_names)]
        
        return df
    except Exception as e:
        error_msg = f"加载板块数据失败: {str(e)}"
        st.error(error_msg)
        # 清除缓存以便重试
        load_sector_data.clear()
        return pd.DataFrame()
    finally:
        db.close()

@st.cache_data(ttl=300)
def load_sector_data_by_date(target_date: date) -> pd.DataFrame:
    """加载指定日期的板块数据"""
    db = SessionLocal()
    try:
        sectors = SectorHistoryService.get_sectors_by_date(db, target_date)
        return pd.DataFrame(sectors)
    except Exception as e:
        error_msg = f"加载板块数据失败: {str(e)}"
        st.error(error_msg)
        # 清除缓存以便重试
        load_sector_data_by_date.clear()
        return pd.DataFrame()
    finally:
        db.close()

@st.cache_data(ttl=600)  # 缓存10分钟
def get_available_dates() -> list:
    """获取所有有数据的日期列表"""
    db = SessionLocal()
    try:
        dates = SectorHistoryService.get_all_dates(db)
        return [d.strftime('%Y-%m-%d') for d in dates]
    except Exception as e:
        st.error(f"获取日期列表失败: {str(e)}")
        return []
    finally:
        db.close()

@st.cache_data(ttl=300)
def load_zt_pool_data(target_date: date) -> pd.DataFrame:
    """加载指定日期的涨停股票池数据"""
    db = SessionLocal()
    try:
        stocks = ZtPoolHistoryService.get_zt_pool_by_date(db, target_date)
        return pd.DataFrame(stocks)
    except Exception as e:
        st.error(f"加载涨停股票数据失败: {str(e)}")
        return pd.DataFrame()
    finally:
        db.close()

@st.cache_data(ttl=300)
def load_zbgc_pool_data(target_date: date) -> pd.DataFrame:
    """加载指定日期的炸板股票池数据"""
    db = SessionLocal()
    try:
        stocks = ZbgcPoolHistoryService.get_zbgc_pool_by_date(db, target_date)
        return pd.DataFrame(stocks)
    except Exception as e:
        st.error(f"加载炸板股票数据失败: {str(e)}")
        return pd.DataFrame()
    finally:
        db.close()

@st.cache_data(ttl=300)
def load_dtgc_pool_data(target_date: date) -> pd.DataFrame:
    """加载指定日期的跌停股票池数据"""
    db = SessionLocal()
    try:
        stocks = DtgcPoolHistoryService.get_dtgc_pool_by_date(db, target_date)
        return pd.DataFrame(stocks)
    except Exception as e:
        st.error(f"加载跌停股票数据失败: {str(e)}")
        return pd.DataFrame()
    finally:
        db.close()

