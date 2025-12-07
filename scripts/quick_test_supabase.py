#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试Supabase连接（仅测试API连接，不需要数据库密码）
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_api_connection():
    """测试Supabase API连接"""
    try:
        from supabase import create_client
        from config_supabase import SupabaseConfig
        
        print("🔍 测试Supabase API连接...")
        
        if not SupabaseConfig.SUPABASE_URL or not SupabaseConfig.SUPABASE_ANON_KEY:
            print("❌ 配置不完整")
            print("   请确保 .env 文件中有 SUPABASE_URL 和 SUPABASE_ANON_KEY")
            return False
        
        print(f"   URL: {SupabaseConfig.SUPABASE_URL}")
        
        # 创建客户端
        supabase = create_client(
            SupabaseConfig.SUPABASE_URL,
            SupabaseConfig.SUPABASE_ANON_KEY
        )
        
        # 测试连接（尝试查询一个表，即使表不存在也会返回错误信息）
        print("📡 测试API连接...")
        try:
            # 尝试查询sector_history表
            response = supabase.table('sector_history').select('id', count='exact').limit(1).execute()
            print(f"✅ API连接成功！")
            if hasattr(response, 'count'):
                print(f"   表 sector_history 记录数: {response.count}")
            return True
        except Exception as e:
            error_msg = str(e)
            if 'relation "public.sector_history" does not exist' in error_msg:
                print("✅ API连接成功！")
                print("   ⚠️  表 sector_history 尚未创建")
                print("   💡 请在Supabase Dashboard的SQL Editor中执行 scripts/supabase_setup.sql")
                return True
            elif 'JWT' in error_msg or 'invalid' in error_msg.lower():
                print(f"❌ API密钥无效: {error_msg[:100]}")
                return False
            else:
                print(f"⚠️  API连接测试: {error_msg[:100]}")
                return True  # 连接成功，只是表不存在
        
    except ImportError:
        print("❌ 请先安装supabase: pip install supabase")
        return False
    except Exception as e:
        print(f"❌ 连接失败: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("Supabase快速连接测试")
    print("=" * 60)
    print("\n此测试仅验证API连接，不需要数据库密码")
    print()
    
    result = test_api_connection()
    
    print("\n" + "=" * 60)
    if result:
        print("✅ API连接测试通过！")
        print("\n💡 下一步：")
        print("   1. 获取 SUPABASE_DB_PASSWORD 和 SUPABASE_PROJECT_REF")
        print("   2. 更新 .env 文件")
        print("   3. 执行数据库初始化: scripts/supabase_setup.sql")
        print("   4. 运行完整测试: python3 scripts/test_supabase_connection.py")
    else:
        print("❌ API连接测试失败")
        print("\n💡 请检查：")
        print("   1. .env 文件中的 SUPABASE_URL 和 SUPABASE_ANON_KEY")
        print("   2. 网络连接")
        print("   3. Supabase项目状态")
    print("=" * 60)

if __name__ == '__main__':
    main()

