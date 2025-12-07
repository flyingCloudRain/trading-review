#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试指数实时行情接口 (stock_zh_index_spot_em)
"""
import requests
import json
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:5000"

def test_index_spot_api():
    """测试指数实时行情接口（需要Flask应用运行）"""
    print("=" * 60)
    print("测试指数实时行情接口 (stock_zh_index_spot_em)")
    print("=" * 60)
    
    # 测试接口
    url = f"{BASE_URL}/api/stock-index/spot"
    
    try:
        print(f"\n📡 请求URL: {url}")
        print("⏳ 正在请求数据...")
        
        response = requests.get(url, timeout=30)
        
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                indices = data.get('data', [])
                count = data.get('count', 0)
                source = data.get('source', '')
                
                print(f"\n✅ 请求成功！")
                print(f"📈 数据来源: {source}")
                print(f"📊 指数数量: {count}")
                
                if indices:
                    print(f"\n📋 前10个指数数据:")
                    print("-" * 100)
                    print(f"{'序号':<6} {'代码':<10} {'名称':<20} {'最新价':<12} {'涨跌幅':<10} {'涨跌额':<12} {'成交量':<15}")
                    print("-" * 100)
                    
                    for i, idx in enumerate(indices[:10], 1):
                        code = idx.get('code', '')
                        name = idx.get('name', '')
                        price = idx.get('currentPrice', 0)
                        change_pct = idx.get('changePercent', 0)
                        change = idx.get('change', 0)
                        volume = idx.get('volume', 0)
                        
                        print(f"{i:<6} {code:<10} {name:<20} {price:<12.2f} {change_pct:<10.2f}% {change:<12.2f} {volume:<15,.0f}")
                    
                    print("-" * 100)
                    
                    # 显示主要指数
                    print(f"\n🔍 主要指数信息:")
                    main_indices = ['000001', '399001', '399006', '000016', '000300', '000905']
                    for idx in indices:
                        if idx.get('code') in main_indices:
                            print(f"  • {idx.get('name')} ({idx.get('code')}): {idx.get('currentPrice'):.2f}, "
                                  f"涨跌幅: {idx.get('changePercent'):+.2f}%, "
                                  f"涨跌额: {idx.get('change'):+.2f}")
                else:
                    print("⚠️ 未获取到指数数据")
            else:
                error = data.get('error', 'Unknown error')
                print(f"❌ 请求失败: {error}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ 连接错误: 无法连接到服务器 {BASE_URL}")
        print("💡 请确保Flask应用正在运行: python app.py")
    except requests.exceptions.Timeout:
        print(f"❌ 请求超时: 服务器响应时间过长")
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

def test_direct_service():
    """直接测试服务类"""
    print("\n" + "=" * 60)
    print("直接测试服务类 (StockIndexService.get_index_spot)")
    print("=" * 60)
    
    try:
        from services.stock_index_service import StockIndexService
        
        print("⏳ 正在调用 akshare.stock_zh_index_spot_em()...")
        indices = StockIndexService.get_index_spot()
        
        print(f"✅ 成功获取 {len(indices)} 个指数数据")
        
        if indices:
            print(f"\n📋 前5个指数数据:")
            for i, idx in enumerate(indices[:5], 1):
                print(f"{i}. {idx.get('name')} ({idx.get('code')}): "
                      f"最新价={idx.get('currentPrice'):.2f}, "
                      f"涨跌幅={idx.get('changePercent'):+.2f}%, "
                      f"成交量={idx.get('volume'):,.0f}")
        else:
            print("⚠️ 未获取到指数数据")
            
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    # 直接测试服务类
    test_direct_service()
    
    # 提示如何测试API接口
    print("\n" + "=" * 60)
    print("📝 API接口测试说明:")
    print("=" * 60)
    print("1. 启动Flask应用:")
    print("   python app.py")
    print()
    print("2. 在另一个终端测试API接口:")
    print("   curl http://localhost:5000/api/stock-index/spot")
    print("   或")
    print("   python -c \"import requests; r=requests.get('http://localhost:5000/api/stock-index/spot'); print(r.json())\"")
    print()
    print("3. 或使用浏览器访问:")
    print("   http://localhost:5000/api/stock-index/spot")
    print("=" * 60)

