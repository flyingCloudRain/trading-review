#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
关注指数管理工具
"""
import json
import os
from pathlib import Path
from typing import List, Set

# 配置文件路径
CONFIG_FILE = Path(__file__).parent.parent / "data" / "focused_indices.json"

def get_focused_indices() -> List[str]:
    """
    获取关注指数列表（指数代码列表）
    
    Returns:
        List[str]: 关注指数代码列表
    """
    if not CONFIG_FILE.exists():
        # 如果文件不存在，创建默认配置
        default_indices = []
        save_focused_indices(default_indices)
        return default_indices
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('indices', [])
    except (json.JSONDecodeError, IOError):
        # 如果文件损坏，返回空列表
        return []

def save_focused_indices(indices: List[str]) -> bool:
    """
    保存关注指数列表
    
    Args:
        indices: 指数代码列表
    
    Returns:
        bool: 是否保存成功
    """
    try:
        # 确保目录存在
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # 去重并排序
        unique_indices = sorted(list(set(indices)))
        
        data = {
            'indices': unique_indices,
            'updated_at': str(Path(__file__).stat().st_mtime) if CONFIG_FILE.exists() else None
        }
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
    except IOError:
        return False

def add_focused_index(index_code: str) -> bool:
    """
    添加关注指数
    
    Args:
        index_code: 指数代码
    
    Returns:
        bool: 是否添加成功
    """
    indices = get_focused_indices()
    if index_code not in indices:
        indices.append(index_code)
        return save_focused_indices(indices)
    return True

def remove_focused_index(index_code: str) -> bool:
    """
    移除关注指数
    
    Args:
        index_code: 指数代码
    
    Returns:
        bool: 是否移除成功
    """
    indices = get_focused_indices()
    if index_code in indices:
        indices.remove(index_code)
        return save_focused_indices(indices)
    return True

def is_focused_index(index_code: str) -> bool:
    """
    检查是否为关注指数
    
    Args:
        index_code: 指数代码
    
    Returns:
        bool: 是否为关注指数
    """
    return index_code in get_focused_indices()

