#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase配置示例
请复制此文件内容到 .env 文件中，并填入你的Supabase项目信息
"""
import os
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 项目根目录
BASE_DIR = Path(__file__).parent

# 数据目录
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)

class SupabaseConfig:
    """Supabase配置"""
    
    # Supabase项目URL（从Supabase Dashboard获取）
    SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
    
    # Supabase API密钥（anon key: 用于客户端，受RLS保护）
    SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY', '')
    
    # 数据库连接信息
    # 从Supabase Dashboard -> Settings -> Database 获取密码
    SUPABASE_DB_PASSWORD = os.environ.get('SUPABASE_DB_PASSWORD', '')
    
    # 项目引用（用于构建数据库URL，从Settings -> General获取）
    SUPABASE_PROJECT_REF = os.environ.get('SUPABASE_PROJECT_REF', '')
    
    # 固定值（Supabase标准配置）
    _DB_USER = 'postgres'
    _DB_NAME = 'postgres'
    _DB_PORT = '5432'
    
    @classmethod
    def get_database_url(cls) -> str:
        """
        获取PostgreSQL数据库连接URL
        使用项目引用构建连接URL
        """
        if not cls.SUPABASE_PROJECT_REF or not cls.SUPABASE_DB_PASSWORD:
            raise ValueError("请配置 SUPABASE_PROJECT_REF 和 SUPABASE_DB_PASSWORD")
        
        # 对用户名和密码进行URL编码，防止特殊字符导致解析错误
        encoded_user = quote_plus(cls._DB_USER)
        encoded_password = quote_plus(cls.SUPABASE_DB_PASSWORD)
        
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

