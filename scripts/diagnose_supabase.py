#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase连接诊断工具
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

def diagnose_config():
    """诊断配置"""
    print("=" * 60)
    print("Supabase配置诊断")
    print("=" * 60)
    
    # 检查环境变量
    config_items = {
        'SUPABASE_URL': os.environ.get('SUPABASE_URL'),
        'SUPABASE_ANON_KEY': os.environ.get('SUPABASE_ANON_KEY'),
        'SUPABASE_DB_PASSWORD': os.environ.get('SUPABASE_DB_PASSWORD'),
        'SUPABASE_PROJECT_REF': os.environ.get('SUPABASE_PROJECT_REF'),
    }
    
    print("\n📋 配置检查:")
    all_ok = True
    for key, value in config_items.items():
        if value:
            if 'KEY' in key or 'PASSWORD' in key:
                # 隐藏敏感信息
                display_value = value[:20] + '...' if len(value) > 20 else '***'
                status = "✅"
            else:
                display_value = value
                status = "✅"
            print(f"   {status} {key}: {display_value}")
        else:
            print(f"   ❌ {key}: 未配置")
            all_ok = False
    
    # 检查密码格式
    password = config_items['SUPABASE_DB_PASSWORD']
    if password:
        print(f"\n🔍 密码格式检查:")
        print(f"   长度: {len(password)} 字符")
        if password.startswith('"') or password.startswith("'"):
            print(f"   ⚠️  密码可能包含引号，请检查.env文件")
        if ' ' in password:
            print(f"   ⚠️  密码包含空格")
        if password == '请从Supabase Dashboard获取（Settings -> Database -> Database password）':
            print(f"   ❌ 密码还是占位符，请填入实际密码")
            all_ok = False
    
    return all_ok, config_items

def test_connection_with_details(config_items):
    """详细测试连接"""
    print(f"\n🔍 连接测试:")
    
    # 构建连接URL
    project_ref = config_items['SUPABASE_PROJECT_REF']
    password = config_items['SUPABASE_DB_PASSWORD']
    user = 'postgres'
    
    if not project_ref or not password:
        print("   ❌ 缺少必要配置")
        return False
    
    # 显示连接信息（隐藏密码）
    print(f"   主机: db.{project_ref}.supabase.co")
    print(f"   端口: 5432")
    print(f"   用户: {user}")
    print(f"   数据库: postgres")
    
    # 尝试连接
    try:
        from sqlalchemy import create_engine, text
        
        # 构建连接URL
        database_url = f"postgresql://{user}:{password}@db.{project_ref}.supabase.co:5432/postgres"
        
        print(f"\n   正在连接...")
        engine = create_engine(database_url, pool_pre_ping=True, connect_args={'connect_timeout': 10})
        
        with engine.connect() as conn:
            # 测试基本连接
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"   ✅ 连接成功！")
            print(f"   PostgreSQL版本: {version[:50]}...")
            
            # 检查表
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result]
            if tables:
                print(f"   ✅ 已创建的表: {', '.join(tables)}")
            else:
                print(f"   ⚠️  尚未创建表，请执行 scripts/supabase_setup.sql")
            
            return True
            
    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ 连接失败")
        
        if 'password authentication failed' in error_msg:
            print(f"\n   💡 密码认证失败，可能的原因：")
            print(f"      1. 数据库密码不正确")
            print(f"      2. .env文件中的密码格式有问题（可能有引号或空格）")
            print(f"      3. 密码需要重置")
            print(f"\n   🔧 解决方法：")
            print(f"      1. 检查Supabase Dashboard -> Settings -> Database")
            print(f"      2. 如果忘记密码，可以重置数据库密码")
            print(f"      3. 确保.env文件中密码没有引号，例如：")
            print(f"         SUPABASE_DB_PASSWORD=your_password_here")
            print(f"         而不是：")
            print(f"         SUPABASE_DB_PASSWORD=\"your_password_here\"")
        elif 'could not resolve hostname' in error_msg or 'timeout' in error_msg.lower():
            print(f"   💡 网络连接问题，请检查网络")
        else:
            print(f"   错误详情: {error_msg[:200]}")
        
        return False

def main():
    all_ok, config_items = diagnose_config()
    
    if all_ok:
        print(f"\n{'='*60}")
        test_connection_with_details(config_items)
    else:
        print(f"\n{'='*60}")
        print("❌ 配置不完整，请先完成配置")
        print(f"\n💡 获取配置信息：")
        print(f"   访问: https://supabase.com/dashboard/project/{config_items.get('SUPABASE_PROJECT_REF', 'your-project')}")
        print(f"   1. Settings -> API -> anon public key")
        print(f"   2. Settings -> Database -> Database password")
        print(f"   3. Settings -> General -> Reference ID")
    
    print(f"\n{'='*60}")

if __name__ == '__main__':
    main()

