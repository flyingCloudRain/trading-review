#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重点关注板块管理工具
"""
import json
import os
from pathlib import Path
from typing import List, Set

# 配置文件路径
CONFIG_FILE = Path(__file__).parent.parent / "data" / "focused_sectors.json"

def get_focused_sectors() -> List[str]:
    """
    获取重点关注板块列表
    
    Returns:
        List[str]: 重点关注板块名称列表
    """
    if not CONFIG_FILE.exists():
        # 如果文件不存在，创建默认配置
        default_sectors = []
        save_focused_sectors(default_sectors)
        return default_sectors
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('sectors', [])
    except (json.JSONDecodeError, IOError):
        # 如果文件损坏，返回空列表
        return []

def save_focused_sectors(sectors: List[str]) -> bool:
    """
    保存重点关注板块列表
    
    Args:
        sectors: 板块名称列表
    
    Returns:
        bool: 是否保存成功
    """
    try:
        # 确保目录存在
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # 去重并排序
        unique_sectors = sorted(list(set(sectors)))
        
        data = {
            'sectors': unique_sectors,
            'updated_at': str(Path(__file__).stat().st_mtime) if CONFIG_FILE.exists() else None
        }
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
    except IOError:
        return False

def add_focused_sector(sector_name: str) -> bool:
    """
    添加重点关注板块
    
    Args:
        sector_name: 板块名称
    
    Returns:
        bool: 是否添加成功
    """
    sectors = get_focused_sectors()
    if sector_name not in sectors:
        sectors.append(sector_name)
        return save_focused_sectors(sectors)
    return True

def remove_focused_sector(sector_name: str) -> bool:
    """
    移除重点关注板块
    
    Args:
        sector_name: 板块名称
    
    Returns:
        bool: 是否移除成功
    """
    sectors = get_focused_sectors()
    if sector_name in sectors:
        sectors.remove(sector_name)
        return save_focused_sectors(sectors)
    return True

def is_focused_sector(sector_name: str) -> bool:
    """
    检查是否为重点关注板块
    
    Args:
        sector_name: 板块名称
    
    Returns:
        bool: 是否为重点关注板块
    """
    return sector_name in get_focused_sectors()

