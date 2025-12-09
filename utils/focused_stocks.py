#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
关注股票管理工具
"""
import json
import os
from pathlib import Path
from typing import List

# 配置文件路径
CONFIG_FILE = Path(__file__).parent.parent / "data" / "focused_stocks.json"

def get_focused_stocks() -> List[str]:
    """
    获取关注股票列表（股票代码列表）
    
    Returns:
        List[str]: 关注股票代码列表
    """
    if not CONFIG_FILE.exists():
        # 如果文件不存在，创建默认配置
        default_stocks = []
        save_focused_stocks(default_stocks)
        return default_stocks
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('stocks', [])
    except (json.JSONDecodeError, IOError):
        # 如果文件损坏，返回空列表
        return []

def save_focused_stocks(stocks: List[str]) -> bool:
    """
    保存关注股票列表
    
    Args:
        stocks: 股票代码列表
    
    Returns:
        bool: 是否保存成功
    """
    try:
        # 确保目录存在
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'stocks': stocks,
            'updated_at': str(Path(__file__).stat().st_mtime)
        }
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except IOError:
        return False

def add_focused_stock(stock_code: str) -> bool:
    """
    添加关注股票
    
    Args:
        stock_code: 股票代码
    
    Returns:
        bool: 是否添加成功
    """
    stocks = get_focused_stocks()
    if stock_code not in stocks:
        stocks.append(stock_code)
        return save_focused_stocks(stocks)
    return True

def remove_focused_stock(stock_code: str) -> bool:
    """
    移除关注股票
    
    Args:
        stock_code: 股票代码
    
    Returns:
        bool: 是否移除成功
    """
    stocks = get_focused_stocks()
    if stock_code in stocks:
        stocks.remove(stock_code)
        return save_focused_stocks(stocks)
    return True

