#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase配置
支持从 Streamlit secrets 或环境变量读取配置
"""
import os
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv

# 加载环境变量（本地开发使用）
load_dotenv()

# 项目根目录
BASE_DIR = Path(__file__).parent

# 数据目录
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)

def _get_config_value(key: str, default: str = '') -> str:
    """
    获取配置值，优先级：
    1. Streamlit secrets（如果在 Streamlit 环境中）
    2. 环境变量（os.environ）
    
    Args:
        key: 配置键名
        default: 默认值
    
    Returns:
        配置值
    """
    # 尝试从 Streamlit secrets 读取（Streamlit Cloud 或本地 Streamlit）
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except (ImportError, RuntimeError, AttributeError):
        # 不在 Streamlit 环境中，或 secrets 不可用
        pass
    
    # 从环境变量读取（本地开发或非 Streamlit 环境）
    return os.environ.get(key, default)

class SupabaseConfig:
    """Supabase配置"""
    
    # 数据库连接 URI（完整连接字符串，优先使用）
    # 从 Supabase Dashboard -> Settings -> Database -> Connection string 获取
    # 格式：postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres
    DATABASE_URL = _get_config_value('DATABASE_URL', '')
    
    # 连接池 URI（推荐使用，可以避免 IPv6 问题）
    # 从 Supabase Dashboard -> Settings -> Database -> Connection Pooler URL 获取
    # 格式：postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres?pgbouncer=true
    DATABASE_POOLER_URL = _get_config_value('DATABASE_POOLER_URL', '')
    
    # Supabase项目URL（从Supabase Dashboard获取）
    SUPABASE_URL = _get_config_value('SUPABASE_URL', '')
    
    # Supabase API密钥（anon key: 用于客户端，受RLS保护）
    SUPABASE_ANON_KEY = _get_config_value('SUPABASE_ANON_KEY', '')
    
    # 数据库连接信息
    # 从Supabase Dashboard -> Settings -> Database 获取密码
    SUPABASE_DB_PASSWORD = _get_config_value('SUPABASE_DB_PASSWORD', '')
    
    # 项目引用（用于构建数据库URL，从Settings -> General获取）
    SUPABASE_PROJECT_REF = _get_config_value('SUPABASE_PROJECT_REF', '')
    
    # 固定值（Supabase标准配置）
    _DB_USER = 'postgres'
    _DB_NAME = 'postgres'
    _DB_PORT = '5432'
    
    @classmethod
    def _clean_connection_url(cls, url: str) -> str:
        """
        清理连接 URL，移除 psycopg2 不支持的参数
        
        Args:
            url: 原始连接 URL
        
        Returns:
            清理后的连接 URL
        """
        from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
        
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        # 移除 pgbouncer 参数（psycopg2 不支持）
        if 'pgbouncer' in query_params:
            del query_params['pgbouncer']
        
        # 重新构建查询字符串
        new_query = urlencode(query_params, doseq=True) if query_params else ''
        
        # 重新构建 URL
        cleaned_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
        
        return cleaned_url
    
    @classmethod
    def get_database_url(cls, use_pooler: bool = True) -> str:
        """
        获取PostgreSQL数据库连接URL
        
        优先级：
        1. DATABASE_POOLER_URL（如果 use_pooler=True）- 连接池 URI，推荐使用
        2. DATABASE_URL - 完整连接字符串 URI
        3. 使用 SUPABASE_PROJECT_REF 和 SUPABASE_DB_PASSWORD 构建 Session Pooler
        
        Args:
            use_pooler: 是否优先使用连接池（推荐，可以避免 IPv6 问题）
        """
        # 优先级 1: 如果提供了连接池 URI 且 use_pooler=True，优先使用
        if use_pooler and cls.DATABASE_POOLER_URL:
            # 清理 URL，移除 pgbouncer 参数
            return cls._clean_connection_url(cls.DATABASE_POOLER_URL)
        
        # 优先级 2: 如果提供了完整连接 URI，直接使用
        if cls.DATABASE_URL:
            # 清理 URL，移除 pgbouncer 参数（如果有）
            return cls._clean_connection_url(cls.DATABASE_URL)
        
        # 优先级 3: 使用项目引用和密码构建 Session Pooler（推荐，避免 IPv6 问题）
        if not cls.SUPABASE_PROJECT_REF or not cls.SUPABASE_DB_PASSWORD:
            raise ValueError(
                "请配置以下任一方式：\n"
                "1. DATABASE_URL 或 DATABASE_POOLER_URL（推荐，从 Supabase Dashboard 复制）\n"
                "2. SUPABASE_PROJECT_REF 和 SUPABASE_DB_PASSWORD"
            )
        
        # 对用户名和密码进行URL编码，防止特殊字符导致解析错误
        encoded_user = quote_plus(cls._DB_USER)
        encoded_password = quote_plus(cls.SUPABASE_DB_PASSWORD)
        
        if use_pooler:
            # 使用 Session Pooler（推荐）：端口 5432，避免 IPv6 问题，更好的性能
            # 格式：postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-1-[region].pooler.supabase.com:5432/postgres
            # 注意：区域需要根据实际项目配置，这里使用 ap-southeast-1 作为默认值
            # 如果区域不同，建议直接使用 DATABASE_POOLER_URL 配置
            pooler_host = f"aws-1-ap-southeast-1.pooler.supabase.com"
            return f"postgresql://{encoded_user}.{cls.SUPABASE_PROJECT_REF}:{encoded_password}@{pooler_host}:{cls._DB_PORT}/{cls._DB_NAME}"
        else:
            # 标准连接（可能有 IPv6 问题）
            return f"postgresql://{encoded_user}:{encoded_password}@db.{cls.SUPABASE_PROJECT_REF}.supabase.co:{cls._DB_PORT}/{cls._DB_NAME}"
    
    @classmethod
    def validate(cls) -> bool:
        """验证配置是否完整"""
        required = [
            cls.SUPABASE_URL,
            cls.SUPABASE_ANON_KEY,
            cls.SUPABASE_DB_PASSWORD,
            cls.SUPABASE_PROJECT_REF,
        ]
        return all(required)

