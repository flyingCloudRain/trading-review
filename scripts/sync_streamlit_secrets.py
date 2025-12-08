#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同步本地 .env 配置到 Streamlit Cloud Secrets 格式
"""
import os
from pathlib import Path
from dotenv import load_dotenv

def load_env_file():
    """加载 .env 文件"""
    env_path = Path(__file__).parent.parent / '.env'
    if not env_path.exists():
        print(f"❌ 未找到 .env 文件: {env_path}")
        return None
    
    load_dotenv(env_path)
    return env_path

def generate_streamlit_secrets():
    """生成 Streamlit Cloud Secrets 配置"""
    env_path = load_env_file()
    if not env_path:
        return
    
    print("=" * 60)
    print("📋 Streamlit Cloud Secrets 配置（基于本地 .env）")
    print("=" * 60)
    print()
    print("请将以下内容复制到 Streamlit Cloud 的 Secrets 配置中：")
    print()
    print("-" * 60)
    print()
    
    # 必需配置
    project_ref = os.getenv('SUPABASE_PROJECT_REF', '')
    db_password = os.getenv('SUPABASE_DB_PASSWORD', '')
    
    # 可选配置
    supabase_url = os.getenv('SUPABASE_URL', '')
    anon_key = os.getenv('SUPABASE_ANON_KEY', '')
    
    # 生成 TOML 格式配置
    config_lines = [
        "# Streamlit Cloud Secrets 配置",
        "# 从本地 .env 文件同步",
        "",
        "# 必需配置",
        f'SUPABASE_PROJECT_REF = "{project_ref}"',
        f'SUPABASE_DB_PASSWORD = "{db_password}"',
        "",
        "# 可选配置",
    ]
    
    if supabase_url:
        config_lines.append(f'SUPABASE_URL = "{supabase_url}"')
    if anon_key:
        config_lines.append(f'SUPABASE_ANON_KEY = "{anon_key}"')
    
    config_text = '\n'.join(config_lines)
    print(config_text)
    print()
    print("-" * 60)
    print()
    
    # 验证配置
    if not project_ref or not db_password:
        print("⚠️  警告：缺少必需配置（SUPABASE_PROJECT_REF 或 SUPABASE_DB_PASSWORD）")
    else:
        print("✅ 配置验证通过")
    
    print()
    print("=" * 60)
    print("📝 使用说明：")
    print("=" * 60)
    print("1. 复制上面的配置内容")
    print("2. 访问 Streamlit Cloud: https://share.streamlit.io/")
    print("3. 进入应用设置 → Secrets")
    print("4. 粘贴配置内容")
    print("5. 点击 Save 保存")
    print("6. 应用会自动重新部署")
    print()

if __name__ == '__main__':
    generate_streamlit_secrets()

