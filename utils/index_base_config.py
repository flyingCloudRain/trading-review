#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指数基础配置管理工具
从CSV文件读取所有指数的基本信息（代码和名称），作为基础配置
"""
import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
from services.stock_index_service import StockIndexService

# 配置文件路径
CONFIG_FILE = Path(__file__).parent.parent / "data" / "index_base_config.json"

def load_index_base_config() -> List[Dict[str, str]]:
    """
    加载指数基础配置
    
    Returns:
        List[Dict]: 指数基础配置列表，每个元素包含 'code' 和 'name'
    """
    if not CONFIG_FILE.exists():
        # 如果配置文件不存在，从CSV文件生成
        generate_base_config_from_csv()
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('indices', [])
    except (json.JSONDecodeError, IOError):
        return []

def save_index_base_config(indices: List[Dict[str, str]]) -> bool:
    """
    保存指数基础配置
    
    Args:
        indices: 指数配置列表，每个元素包含 'code' 和 'name'
    
    Returns:
        bool: 是否保存成功
    """
    try:
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'indices': indices,
            'total_count': len(indices),
            'updated_at': pd.Timestamp.now().isoformat()
        }
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
    except IOError:
        return False

def generate_base_config_from_csv(csv_file: Optional[Path] = None) -> List[Dict[str, str]]:
    """
    从CSV文件生成指数基础配置
    
    Args:
        csv_file: CSV文件路径，如果为None，使用默认路径
    
    Returns:
        List[Dict]: 指数基础配置列表
    """
    if csv_file is None:
        csv_file = Path(__file__).parent.parent / "data" / "stock_zh_index_spot_sina.csv"
    
    if not csv_file.exists():
        raise FileNotFoundError(f"CSV文件不存在: {csv_file}")
    
    # 读取CSV文件
    df = pd.read_csv(csv_file)
    
    # 提取代码和名称
    indices = []
    for _, row in df.iterrows():
        raw_code = str(row.get('代码', '')).strip()
        name = str(row.get('名称', '')).strip()
        
        if raw_code and name:
            # 标准化代码为6位格式
            code_6digit = StockIndexService.normalize_index_code(raw_code)
            
            indices.append({
                'code': code_6digit,
                'name': name,
                'raw_code': raw_code  # 保留原始代码用于显示
            })
    
    # 去重（基于code）
    seen_codes = set()
    unique_indices = []
    for idx in indices:
        if idx['code'] not in seen_codes:
            seen_codes.add(idx['code'])
            unique_indices.append(idx)
    
    # 按代码排序
    unique_indices.sort(key=lambda x: x['code'])
    
    # 保存到配置文件
    save_index_base_config(unique_indices)
    
    return unique_indices

def get_index_by_code(code: str) -> Optional[Dict[str, str]]:
    """
    根据代码获取指数信息
    
    Args:
        code: 指数代码（可以是原始格式或6位格式）
    
    Returns:
        Dict: 指数信息，如果未找到返回None
    """
    code_6digit = StockIndexService.normalize_index_code(code)
    indices = load_index_base_config()
    
    for idx in indices:
        if idx['code'] == code_6digit:
            return idx
    
    return None

def search_indices(keyword: str) -> List[Dict[str, str]]:
    """
    搜索指数（根据代码或名称）
    
    Args:
        keyword: 搜索关键词
    
    Returns:
        List[Dict]: 匹配的指数列表
    """
    if not keyword:
        return load_index_base_config()
    
    keyword_lower = keyword.lower()
    indices = load_index_base_config()
    
    matched = []
    for idx in indices:
        code = idx.get('code', '').lower()
        name = idx.get('name', '').lower()
        raw_code = idx.get('raw_code', '').lower()
        
        if (keyword_lower in code or 
            keyword_lower in name or 
            keyword_lower in raw_code):
            matched.append(idx)
    
    return matched

def get_index_name(code: str) -> str:
    """
    根据代码获取指数名称
    
    Args:
        code: 指数代码
    
    Returns:
        str: 指数名称，如果未找到返回代码本身
    """
    index_info = get_index_by_code(code)
    if index_info:
        return index_info['name']
    return code

