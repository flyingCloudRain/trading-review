#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
部署前检查脚本
检查项目是否准备好部署到 Streamlit Cloud
"""
import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """检查文件是否存在"""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} (不存在)")
        return False

def check_requirements():
    """检查 requirements.txt"""
    if not check_file_exists("requirements.txt", "requirements.txt"):
        return False
    
    # 检查关键依赖
    required_packages = [
        "streamlit",
        "pandas",
        "sqlalchemy",
        "plotly",
        "akshare"
    ]
    
    with open("requirements.txt", "r") as f:
        content = f.read()
        missing = []
        for package in required_packages:
            if package.lower() not in content.lower():
                missing.append(package)
        
        if missing:
            print(f"⚠️  缺少依赖: {', '.join(missing)}")
            return False
        else:
            print("✅ 所有关键依赖都在 requirements.txt 中")
            return True

def check_streamlit_app():
    """检查 streamlit_app.py"""
    return check_file_exists("streamlit_app.py", "streamlit_app.py")

def check_gitignore():
    """检查 .gitignore"""
    if not check_file_exists(".gitignore", ".gitignore"):
        return False
    
    # 检查是否排除了敏感文件
    sensitive_files = [".env", "secrets.toml", "*.db"]
    with open(".gitignore", "r") as f:
        content = f.read()
        missing = []
        for file in sensitive_files:
            if file not in content:
                missing.append(file)
        
        if missing:
            print(f"⚠️  .gitignore 可能缺少: {', '.join(missing)}")
            return False
        else:
            print("✅ .gitignore 配置正确")
            return True

def check_pages_directory():
    """检查 pages 目录"""
    if Path("pages").exists() and Path("pages").is_dir():
        page_files = list(Path("pages").glob("*.py"))
        if page_files:
            print(f"✅ pages 目录存在，包含 {len(page_files)} 个页面文件")
            return True
        else:
            print("⚠️  pages 目录存在但为空")
            return False
    else:
        print("⚠️  pages 目录不存在")
        return False

def check_config_files():
    """检查配置文件"""
    configs = [
        ("config.py", "config.py"),
        (".streamlit/config.toml", "Streamlit 配置文件"),
    ]
    
    all_exist = True
    for filepath, desc in configs:
        if not check_file_exists(filepath, desc):
            all_exist = False
    
    return all_exist

def main():
    """主检查函数"""
    print("=" * 60)
    print("🔍 Streamlit Cloud 部署前检查")
    print("=" * 60)
    print()
    
    checks = [
        ("requirements.txt", check_requirements),
        ("streamlit_app.py", check_streamlit_app),
        (".gitignore", check_gitignore),
        ("pages 目录", check_pages_directory),
        ("配置文件", check_config_files),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n📋 检查: {name}")
        print("-" * 60)
        result = check_func()
        results.append((name, result))
    
    print()
    print("=" * 60)
    print("📊 检查结果汇总")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {status}: {name}")
        if not result:
            all_passed = False
    
    print()
    if all_passed:
        print("✅ 所有检查通过！可以部署到 Streamlit Cloud")
        print()
        print("下一步：")
        print("1. 将代码推送到 GitHub")
        print("2. 访问 https://share.streamlit.io/")
        print("3. 创建新应用并连接 GitHub 仓库")
        print("4. 配置 Secrets（环境变量）")
        print("5. 部署应用")
        print()
        print("详细步骤请查看: STREAMLIT_CLOUD_DEPLOY.md")
        return 0
    else:
        print("❌ 部分检查未通过，请修复后重试")
        return 1

if __name__ == "__main__":
    sys.exit(main())

