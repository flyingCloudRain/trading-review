#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接模块（统一入口）
使用 Supabase PostgreSQL 数据库
"""
from .db_supabase import (
    Base,
    engine,
    SessionLocal,
    init_db,
    get_db
)

__all__ = ['Base', 'engine', 'SessionLocal', 'init_db', 'get_db']

