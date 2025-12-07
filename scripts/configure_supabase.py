#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速配置Supabase连接
"""
import os
from pathlib import Path

# Supabase项目信息
SUPABASE_URL = "https://uvtmbjgndhcmlupridss.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2dG1iamduZGhjbWx1cHJpZHNzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM0MDA2MjksImV4cCI6MjA3ODk3NjYyOX0.KCu_julbsWVNtfVQKWZIefJKVMdqsBoHL8o44DwxbRY"
PROJECT_REF = "uvtmbjgndhcmlupridss"

def create_env_file():
    """创建或更新.env文件"""
    env_file = Path('.env')
    
    # 读取现有.env文件（如果存在）
    existing_content = ""
    if env_file.exists():
        existing_content = env_file.read_text(encoding='utf-8')
    
    # 检查是否已有Supabase配置
    if 'SUPABASE_URL' in existing_content:
        print("⚠️  .env文件中已存在Supabase配置")
        response = input("是否要更新？(y/n): ")
        if response.lower() != 'y':
            print("已取消")
            return
    
    # 准备Supabase配置
    supabase_config = f"""
# Supabase配置
SUPABASE_URL={SUPABASE_URL}
SUPABASE_ANON_KEY={SUPABASE_ANON_KEY}
SUPABASE_DB_PASSWORD=请从Supabase Dashboard获取（Settings -> Database -> Database password）
SUPABASE_PROJECT_REF={PROJECT_REF}
"""
    
    # 合并配置
    if 'SUPABASE_URL' in existing_content:
        # 更新现有配置
        lines = existing_content.split('\n')
        new_lines = []
        skip_until_empty = False
        
        for line in lines:
            if line.startswith('# Supabase配置'):
                skip_until_empty = True
                new_lines.append(supabase_config.strip())
            elif skip_until_empty:
                if line.strip() == '':
                    skip_until_empty = False
                    new_lines.append(line)
                continue
            else:
                new_lines.append(line)
        
        new_content = '\n'.join(new_lines)
    else:
        # 追加新配置
        new_content = existing_content.rstrip() + '\n' + supabase_config
    
    # 写入文件
    env_file.write_text(new_content, encoding='utf-8')
    print(f"✅ 已更新 .env 文件")
    print(f"\n📝 请补充以下信息到 .env 文件：")
    print(f"   1. SUPABASE_DB_PASSWORD - 从 Supabase Dashboard -> Settings -> Database -> Database password 获取")
    print(f"\n💡 提示：")
    print(f"   - 访问: {SUPABASE_URL.replace('https://', 'https://app.')}")
    print(f"   - 或访问: https://supabase.com/dashboard/project/{PROJECT_REF}")

def main():
    print("=" * 60)
    print("Supabase配置助手")
    print("=" * 60)
    print(f"\n项目URL: {SUPABASE_URL}")
    print(f"项目引用ID: {PROJECT_REF}")
    print(f"Anon Key: 已配置")
    print("\n正在配置...")
    
    create_env_file()
    
    print("\n" + "=" * 60)
    print("下一步：")
    print("1. 获取 SUPABASE_DB_PASSWORD")
    print("2. 更新 .env 文件")
    print("3. 运行测试: python3 scripts/test_supabase_connection.py")
    print("=" * 60)

if __name__ == '__main__':
    main()

