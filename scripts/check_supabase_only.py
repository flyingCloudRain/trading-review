#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库配置，确保全部使用 Supabase
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_database_config():
    """检查数据库配置"""
    print("=" * 60)
    print("🔍 检查数据库配置 - 确保全部使用 Supabase")
    print("=" * 60)
    print()
    
    # 1. 检查数据库连接模块
    print("📋 1. 检查数据库连接模块...")
    try:
        from database.db import engine, SessionLocal
        from database.db_supabase import engine as supabase_engine
        
        # 检查引擎 URL
        engine_url = str(engine.url)
        print(f"   ✅ 数据库引擎 URL: {engine_url[:50]}...")
        
        if 'sqlite' in engine_url.lower():
            print("   ❌ 错误：检测到 SQLite 连接！")
            print("   💡 应该使用 Supabase PostgreSQL")
            return False
        elif 'postgresql' in engine_url.lower() or 'supabase' in engine_url.lower():
            print("   ✅ 使用 Supabase PostgreSQL")
        else:
            print(f"   ⚠️  未知的数据库类型: {engine_url}")
            return False
    except Exception as e:
        print(f"   ❌ 检查失败: {str(e)}")
        return False
    
    print()
    
    # 2. 检查 Supabase 配置
    print("📋 2. 检查 Supabase 配置...")
    try:
        from config_supabase import SupabaseConfig
        
        has_project_ref = bool(SupabaseConfig.SUPABASE_PROJECT_REF)
        has_password = bool(SupabaseConfig.SUPABASE_DB_PASSWORD)
        has_url = bool(SupabaseConfig.SUPABASE_URL)
        has_anon_key = bool(SupabaseConfig.SUPABASE_ANON_KEY)
        
        print(f"   SUPABASE_PROJECT_REF: {'✅' if has_project_ref else '❌'}")
        print(f"   SUPABASE_DB_PASSWORD: {'✅' if has_password else '❌'}")
        print(f"   SUPABASE_URL: {'✅' if has_url else '⚠️  (可选)'}")
        print(f"   SUPABASE_ANON_KEY: {'✅' if has_anon_key else '⚠️  (可选)'}")
        
        if not has_project_ref or not has_password:
            print("   ❌ Supabase 配置不完整！")
            print("   💡 请配置 SUPABASE_PROJECT_REF 和 SUPABASE_DB_PASSWORD")
            return False
        
        print("   ✅ Supabase 配置完整")
    except Exception as e:
        print(f"   ❌ 检查失败: {str(e)}")
        return False
    
    print()
    
    # 3. 检查数据库连接
    print("📋 3. 测试数据库连接...")
    try:
        from sqlalchemy import text
        db = SessionLocal()
        try:
            # 尝试执行简单查询
            result = db.execute(text("SELECT 1"))
            result.fetchone()
            print("   ✅ 数据库连接成功")
        finally:
            db.close()
    except Exception as e:
        print(f"   ❌ 数据库连接失败: {str(e)}")
        print("   💡 请检查 Supabase 配置和网络连接")
        return False
    
    print()
    
    # 4. 检查所有导入
    print("📋 4. 检查数据库导入...")
    import os
    import subprocess
    
    # 检查是否有直接导入 SQLite 的代码
    try:
        result = subprocess.run(
            ['grep', '-r', '--include=*.py', 'sqlite3', str(project_root)],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # 排除文档和测试文件
        sqlite_imports = [
            line for line in result.stdout.split('\n')
            if line and 'scripts/check_database.py' not in line
            and 'docs/' not in line
            and 'test' not in line.lower()
        ]
        
        if sqlite_imports:
            print("   ⚠️  发现 SQLite 导入:")
            for line in sqlite_imports[:5]:  # 只显示前5个
                print(f"      {line}")
            if len(sqlite_imports) > 5:
                print(f"      ... 还有 {len(sqlite_imports) - 5} 个")
        else:
            print("   ✅ 没有发现直接使用 SQLite 的代码")
    except Exception as e:
        print(f"   ⚠️  无法检查 SQLite 导入: {str(e)}")
    
    print()
    
    # 5. 总结
    print("=" * 60)
    print("✅ 检查完成！")
    print("=" * 60)
    print()
    print("📝 总结:")
    print("   - 数据库连接：使用 Supabase PostgreSQL")
    print("   - 配置状态：已配置")
    print("   - 连接状态：正常")
    print()
    print("💡 如果发现问题，请检查:")
    print("   1. 环境变量配置（.env 或 Streamlit Cloud Secrets）")
    print("   2. Supabase 项目状态")
    print("   3. 网络连接")
    
    return True

if __name__ == "__main__":
    try:
        success = check_database_config()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 检查过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

