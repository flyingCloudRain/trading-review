#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
时间工具模块 - 统一使用UTC+8时区（北京时间）
"""
from datetime import datetime, date
import pytz

# 定义UTC+8时区（北京时间）
UTC8 = pytz.timezone('Asia/Shanghai')

def get_utc8_now() -> datetime:
    """
    获取当前UTC+8时区时间
    :return: UTC+8时区的当前时间
    """
    return datetime.now(UTC8)

def get_utc8_date_str() -> str:
    """
    获取当前UTC+8时区的日期字符串（YYYY-MM-DD）
    :return: 日期字符串
    """
    return get_utc8_now().strftime('%Y-%m-%d')

def get_utc8_time_str() -> str:
    """
    获取当前UTC+8时区的时间字符串（HH:MM:SS）
    :return: 时间字符串
    """
    return get_utc8_now().strftime('%H:%M:%S')

def get_utc8_datetime_str() -> str:
    """
    获取当前UTC+8时区的完整日期时间字符串（YYYY-MM-DD HH:MM:SS）
    :return: 日期时间字符串
    """
    return get_utc8_now().strftime('%Y-%m-%d %H:%M:%S')

def get_utc8_timestamp_str() -> str:
    """
    获取当前UTC+8时区的时间戳字符串（YYYYMMDD_HHMMSS）
    :return: 时间戳字符串
    """
    return get_utc8_now().strftime('%Y%m%d_%H%M%S')

def get_utc8_date_compact_str() -> str:
    """
    获取当前UTC+8时区的紧凑日期字符串（YYYYMMDD）
    :return: 日期字符串
    """
    return get_utc8_now().strftime('%Y%m%d')

def get_utc8_date() -> date:
    """
    获取当前UTC+8时区的日期对象
    :return: date对象
    """
    return get_utc8_now().date()

def is_trading_time() -> bool:
    """
    判断当前时间是否在交易时间内（9:30-15:00，北京时间）
    :return: True表示在交易时间内，False表示不在
    """
    now = get_utc8_now()
    current_time = now.time()
    
    # 交易时间：9:30-11:30, 13:00-15:00
    morning_start = datetime.strptime('09:30:00', '%H:%M:%S').time()
    morning_end = datetime.strptime('11:30:00', '%H:%M:%S').time()
    afternoon_start = datetime.strptime('13:00:00', '%H:%M:%S').time()
    afternoon_end = datetime.strptime('15:00:00', '%H:%M:%S').time()
    
    # 判断是否在交易时间内
    is_morning = morning_start <= current_time <= morning_end
    is_afternoon = afternoon_start <= current_time <= afternoon_end
    
    return is_morning or is_afternoon

def get_last_trading_day() -> date:
    """
    获取上一个交易日（使用akshare交易日历）
    注意：如果当前不在交易时间内，返回小于今天的最大交易日
    :return: 上一个交易日的date对象
    """
    try:
        import akshare as ak
        import pandas as pd
        from datetime import timedelta
        
        # 获取交易日历
        trade_dates = ak.tool_trade_date_hist_sina()
        
        if trade_dates is not None and not trade_dates.empty:
            # 将日期列转换为date对象
            trade_dates['date'] = pd.to_datetime(trade_dates['trade_date']).dt.date
            # 按日期降序排序
            trade_dates = trade_dates.sort_values('date', ascending=False)
            
            # 获取当前日期
            today = get_utc8_date()
            
            # 找到小于今天的最大交易日（不包括今天）
            last_trading_day = None
            for trade_date in trade_dates['date']:
                if trade_date < today:
                    last_trading_day = trade_date
                    break
            
            if last_trading_day:
                return last_trading_day
        
        # 如果无法获取交易日历，返回昨天（简单处理）
        return get_utc8_date() - timedelta(days=1)
        
    except Exception as e:
        # 如果出错，返回昨天（简单处理）
        from datetime import timedelta
        return get_utc8_date() - timedelta(days=1)

def get_data_date() -> date:
    """
    获取应该使用的数据日期
    - 如果在交易时间内，使用当前日期
    - 如果不在交易时间内，使用上一个交易日
    :return: 应该使用的数据日期
    """
    if is_trading_time():
        return get_utc8_date()
    else:
        return get_last_trading_day()

