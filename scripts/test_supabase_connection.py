#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Supabase连接
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_supabase_client():
    """测试Supabase客户端连接"""
    try:
        from supabase import create_client
        from config_supabase import SupabaseConfig
        
        print("🔍 测试Supabase客户端连接...")
        
        if not SupabaseConfig.validate():
            print("❌ 配置不完整，请检查 .env 文件")
            return False
        
        # 创建客户端
        supabase = create_client(
            SupabaseConfig.SUPABASE_URL,
            SupabaseConfig.SUPABASE_ANON_KEY
        )
        
        # 测试查询
        print("📡 测试API连接...")
        response = supabase.table('sector_history').select('id', count='exact').limit(1).execute()
        
        print(f"✅ Supabase客户端连接成功！")
        print(f"   URL: {SupabaseConfig.SUPABASE_URL}")
        print(f"   表 sector_history 记录数: {response.count if hasattr(response, 'count') else 'N/A'}")
        return True
        
    except ImportError:
        print("❌ 请先安装supabase: pip install supabase")
        return False
    except Exception as e:
        print(f"❌ Supabase客户端连接失败: {str(e)}")
        return False

def test_database_connection():
    """测试PostgreSQL数据库连接"""
    try:
        from sqlalchemy import create_engine, text
        from config_supabase import SupabaseConfig
        
        print("\n🔍 测试PostgreSQL数据库连接...")
        
        database_url = SupabaseConfig.get_database_url()
        print(f"   连接URL: postgresql://***@{SupabaseConfig.SUPABASE_PROJECT_REF or 'host'}.supabase.co")
        
        # 创建引擎
        engine = create_engine(database_url, pool_pre_ping=True)
        
        # 测试连接
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ PostgreSQL数据库连接成功！")
            print(f"   版本: {version[:50]}...")
            
            # 测试表是否存在
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result]
            print(f"   已创建的表: {', '.join(tables) if tables else '无'}")
            
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL数据库连接失败: {str(e)}")
        print("   请检查:")
        print("   1. 数据库密码是否正确")
        print("   2. 项目引用是否正确")
        print("   3. 网络连接是否正常")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("Supabase连接测试")
    print("=" * 60)
    
    # 测试客户端连接
    client_ok = test_supabase_client()
    
    # 测试数据库连接
    db_ok = test_database_connection()
    
    print("\n" + "=" * 60)
    if client_ok and db_ok:
        print("✅ 所有连接测试通过！")
        print("\n💡 下一步:")
        print("   1. 执行SQL脚本创建表: scripts/supabase_setup.sql")
        print("   2. 迁移数据: python3 scripts/migrate_to_supabase.py")
        print("   3. 更新应用配置使用Supabase")
    else:
        print("❌ 部分连接测试失败，请检查配置")
    print("=" * 60)

if __name__ == '__main__':
    main()

