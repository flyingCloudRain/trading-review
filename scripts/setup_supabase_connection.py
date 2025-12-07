#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase连接设置和测试脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def print_instructions():
    """打印设置说明"""
    print("=" * 60)
    print("Supabase连接设置指南")
    print("=" * 60)
    print("\n1. 获取Supabase项目信息")
    print("   访问: https://supabase.com/dashboard")
    print("   选择你的项目")
    print("\n2. 获取以下信息:")
    print("   - Project URL (Settings -> API -> Project URL)")
    print("   - Anon Key (Settings -> API -> anon public)")
    print("   - Database Password (Settings -> Database -> Database password)")
    print("   - Project Reference (Settings -> General -> Reference ID)")
    print("\n3. 创建 .env 文件（在项目根目录）")
    print("   添加以下配置:")
    print("\n   # Supabase配置")
    print("   SUPABASE_URL=https://your-project.supabase.co")
    print("   SUPABASE_ANON_KEY=your-anon-key")
    print("   SUPABASE_DB_PASSWORD=your-database-password")
    print("   SUPABASE_PROJECT_REF=your-project-ref")
    print("\n4. 测试连接")
    print("   运行: python3 scripts/test_supabase_connection.py")
    print("=" * 60)

def create_env_template():
    """创建.env模板文件"""
    env_template = """# Supabase配置
# 从Supabase Dashboard获取以下信息

# Project URL (Settings -> API -> Project URL)
SUPABASE_URL=https://your-project.supabase.co

# Anon Key (Settings -> API -> anon public)
SUPABASE_ANON_KEY=your-anon-key-here

# Database Password (Settings -> Database -> Database password)
SUPABASE_DB_PASSWORD=your-database-password-here

# Project Reference (Settings -> General -> Reference ID)
SUPABASE_PROJECT_REF=your-project-ref-here
"""
    
    env_file = Path('.env.supabase.template')
    env_file.write_text(env_template, encoding='utf-8')
    print(f"\n✅ 已创建模板文件: {env_file}")
    print("   请复制内容到 .env 文件并填入实际值")

if __name__ == '__main__':
    print_instructions()
    create_env_template()

