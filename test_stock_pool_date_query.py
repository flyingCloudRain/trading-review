#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试股票池日期查询功能
测试涨停股票池、跌停股票池、炸板股票池的日期查询接口
"""
import requests
import json
from datetime import datetime, timedelta

# API基础URL
BASE_URL = "http://localhost:5000"

def test_zt_pool_date_query():
    """测试涨停股票池日期查询"""
    print("=" * 60)
    print("测试涨停股票池日期查询")
    print("=" * 60)
    
    # 测试1: 从数据库查询指定日期
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    url = f"{BASE_URL}/api/zt-pool?date={yesterday}"
    print(f"\n📡 测试1: 从数据库查询指定日期")
    print(f"URL: {url}")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ 成功获取 {data.get('count', 0)} 条数据")
                print(f"   数据来源: {data.get('source', 'unknown')}")
                print(f"   查询日期: {data.get('date', 'unknown')}")
            else:
                print(f"❌ 请求失败: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
    
    # 测试2: 查询历史数据（单日期）
    url = f"{BASE_URL}/api/zt-pool/history?date={yesterday}"
    print(f"\n📡 测试2: 查询历史数据（单日期）")
    print(f"URL: {url}")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ 成功获取 {data.get('count', 0)} 条数据")
            else:
                print(f"❌ 请求失败: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
    
    # 测试3: 查询历史数据（日期范围）
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    url = f"{BASE_URL}/api/zt-pool/history?start_date={start_date}&end_date={end_date}"
    print(f"\n📡 测试3: 查询历史数据（日期范围）")
    print(f"URL: {url}")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ 成功获取 {data.get('count', 0)} 条数据")
                print(f"   日期范围: {data.get('start_date')} 至 {data.get('end_date')}")
            else:
                print(f"❌ 请求失败: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")

def test_dt_pool_date_query():
    """测试跌停股票池日期查询"""
    print("\n" + "=" * 60)
    print("测试跌停股票池日期查询")
    print("=" * 60)
    
    # 测试1: 从数据库查询指定日期
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    url = f"{BASE_URL}/api/dt-pool?date={yesterday}"
    print(f"\n📡 测试1: 从数据库查询指定日期")
    print(f"URL: {url}")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ 成功获取 {data.get('count', 0)} 条数据")
                print(f"   数据来源: {data.get('source', 'unknown')}")
            else:
                print(f"❌ 请求失败: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
    
    # 测试2: 查询历史数据（日期范围）
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    url = f"{BASE_URL}/api/dt-pool/history?start_date={start_date}&end_date={end_date}"
    print(f"\n📡 测试2: 查询历史数据（日期范围）")
    print(f"URL: {url}")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ 成功获取 {data.get('count', 0)} 条数据")
            else:
                print(f"❌ 请求失败: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")

def test_zb_pool_date_query():
    """测试炸板股票池日期查询"""
    print("\n" + "=" * 60)
    print("测试炸板股票池日期查询")
    print("=" * 60)
    
    # 测试1: 从数据库查询指定日期
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    url = f"{BASE_URL}/api/zb-pool?date={yesterday}"
    print(f"\n📡 测试1: 从数据库查询指定日期")
    print(f"URL: {url}")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ 成功获取 {data.get('count', 0)} 条数据")
                print(f"   数据来源: {data.get('source', 'unknown')}")
            else:
                print(f"❌ 请求失败: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
    
    # 测试2: 查询历史数据（日期范围）
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    url = f"{BASE_URL}/api/zb-pool/history?start_date={start_date}&end_date={end_date}"
    print(f"\n📡 测试2: 查询历史数据（日期范围）")
    print(f"URL: {url}")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ 成功获取 {data.get('count', 0)} 条数据")
            else:
                print(f"❌ 请求失败: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")

def print_summary():
    """打印使用说明"""
    print("\n" + "=" * 60)
    print("📝 API接口使用说明")
    print("=" * 60)
    print("\n1. 涨停股票池 (zt-pool):")
    print("   - GET /api/zt-pool?date=YYYY-MM-DD")
    print("   - GET /api/zt-pool/history?date=YYYY-MM-DD")
    print("   - GET /api/zt-pool/history?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD")
    print("\n2. 跌停股票池 (dt-pool):")
    print("   - GET /api/dt-pool?date=YYYY-MM-DD")
    print("   - GET /api/dt-pool/history?date=YYYY-MM-DD")
    print("   - GET /api/dt-pool/history?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD")
    print("\n3. 炸板股票池 (zb-pool):")
    print("   - GET /api/zb-pool?date=YYYY-MM-DD")
    print("   - GET /api/zb-pool/history?date=YYYY-MM-DD")
    print("   - GET /api/zb-pool/history?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD")
    print("\n💡 提示: 所有日期格式统一为 YYYY-MM-DD")
    print("=" * 60)

if __name__ == '__main__':
    print("🚀 开始测试股票池日期查询功能")
    print("⚠️  注意: 请确保Flask应用正在运行 (python app.py)")
    print()
    
    try:
        # 测试涨停股票池
        test_zt_pool_date_query()
        
        # 测试跌停股票池
        test_dt_pool_date_query()
        
        # 测试炸板股票池
        test_zb_pool_date_query()
        
        # 打印使用说明
        print_summary()
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 连接错误: 无法连接到服务器")
        print("💡 请先启动Flask应用: python app.py")
        print_summary()
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

