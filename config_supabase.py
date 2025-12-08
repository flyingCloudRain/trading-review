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
        清理连接 URL，移除 psycopg2 不支持的参数，并确保密码正确编码
        
        Args:
            url: 原始连接 URL（可能包含未编码的密码）
        
        Returns:
            清理后的连接 URL（密码已正确编码）
        """
        from urllib.parse import urlparse, urlunparse, parse_qs, urlencode, quote_plus
        import re
        
        # 如果 URL 中包含未编码的 @ 符号（在密码中），urlparse 可能无法正确解析
        # 我们需要手动处理这种情况
        # 格式：postgresql://[user]:[pass]@[host]:[port]/[path]?[query]
        
        if not url.startswith('postgresql://'):
            raise ValueError(f"Invalid URL format: {url}")
        
        # 尝试正常解析
        parsed = urlparse(url)
        
        # 检查解析是否成功：如果密码中有未编码的 @，hostname 可能包含 @ 符号
        # 或者 username/password 为 None 但 URL 中明显有认证信息
        needs_manual_parse = False
        if parsed.hostname and '@' in parsed.hostname:
            needs_manual_parse = True
        elif not parsed.username and not parsed.password and '@' in url:
            # URL 中有 @ 但没有解析出用户名密码，说明密码中有未编码的 @
            needs_manual_parse = True
        
        if needs_manual_parse:
            # 手动解析 URL
            url_without_scheme = url.replace('postgresql://', '')
            
            # 找到最后一个 @（应该是分隔认证和主机的 @）
            # 但密码中可能也有 @，所以我们需要找到正确的分隔符
            # 策略：从右往左找第一个 @，然后检查后面是否是有效的主机名格式
            last_at_index = url_without_scheme.rfind('@')
            if last_at_index == -1:
                raise ValueError(f"Invalid URL format: {url}")
            
            auth_part = url_without_scheme[:last_at_index]
            rest_part = url_without_scheme[last_at_index + 1:]
            
            # 分离用户名和密码（第一个冒号之后的所有内容都是密码）
            if ':' in auth_part:
                colon_index = auth_part.find(':')
                username = auth_part[:colon_index]
                password = auth_part[colon_index + 1:]
            else:
                username = auth_part
                password = ''
            
            # 编码用户名和密码
            encoded_username = quote_plus(username)
            encoded_password = quote_plus(password)
            
            # 分离主机和路径
            if '/' in rest_part:
                host_port, path_query = rest_part.split('/', 1)
                path = '/' + path_query
            else:
                host_port = rest_part
                path = '/'
            
            # 分离路径和查询
            if '?' in path:
                path, query = path.split('?', 1)
            else:
                query = ''
            
            # 分离主机和端口（从右往左找最后一个冒号）
            if ':' in host_port:
                last_colon_index = host_port.rfind(':')
                hostname = host_port[:last_colon_index]
                port_str = host_port[last_colon_index + 1:]
                try:
                    port = int(port_str)
                except ValueError:
                    # 如果无法转换为整数，说明冒号是 IPv6 地址的一部分
                    hostname = host_port
                    port = None
            else:
                hostname = host_port
                port = None
            
            # 重新构建 netloc
            if port:
                netloc = f"{encoded_username}:{encoded_password}@{hostname}:{port}"
            else:
                netloc = f"{encoded_username}:{encoded_password}@{hostname}"
            
            # 重新构建 URL
            cleaned_url = urlunparse((
                'postgresql',
                netloc,
                path,
                '',
                query,
                ''
            ))
            
            # 重新解析以进行后续处理
            parsed = urlparse(cleaned_url)
        else:
            # 正常解析成功，但需要确保密码正确编码
            if parsed.username or parsed.password:
                encoded_username = quote_plus(parsed.username) if parsed.username else ''
                encoded_password = quote_plus(parsed.password) if parsed.password else ''
                
                if encoded_username and encoded_password:
                    netloc = f"{encoded_username}:{encoded_password}@{parsed.hostname}"
                elif encoded_username:
                    netloc = f"{encoded_username}@{parsed.hostname}"
                else:
                    netloc = parsed.hostname
                
                if parsed.port:
                    netloc = f"{netloc}:{parsed.port}"
                
                cleaned_url = urlunparse((
                    parsed.scheme,
                    netloc,
                    parsed.path,
                    parsed.params,
                    parsed.query,
                    parsed.fragment
                ))
                
                parsed = urlparse(cleaned_url)
        
        # 处理查询参数
        query_params = parse_qs(parsed.query)
        
        # 移除 pgbouncer 参数（psycopg2 不支持）
        if 'pgbouncer' in query_params:
            del query_params['pgbouncer']
        
        # 重新构建查询字符串
        new_query = urlencode(query_params, doseq=True) if query_params else ''
        
        # 最终构建 URL
        final_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
        
        return final_url
    
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

