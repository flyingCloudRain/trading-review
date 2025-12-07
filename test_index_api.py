#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试指数API接口
"""
import requests
import json
import sys

def test_index_api(base_url='http://localhost:5000'):
    """测试指数API接口"""
    print("=" * 60)
    print("📊 测试指数API接口")
    print("=" * 60)
    
    endpoints = {
        '/api/stock-index/spot': '获取指数实时行情',
        '/api/stock-index/codes': '获取指数代码列表',
        '/api/stock-index': '获取所有指数（模拟数据）',
    }
    
    for endpoint, description in endpoints.items():
        print(f"\n{'=' * 60}")
        print(f"🔗 {description}")
        print(f"   接口: {base_url}{endpoint}")
        print(f"{'=' * 60}")
        
        try:
            print(f"\n🔄 正在调用接口...")
            response = requests.get(f"{base_url}{endpoint}", timeout=30)
            
            print(f"📡 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    if endpoint == '/api/stock-index/spot':
                        indices = data.get('data', [])
                        count = data.get('count', 0)
                        source = data.get('source', '')
                        
                        print(f"\n✅ 请求成功！")
                        print(f"📈 数据来源: {source}")
                        print(f"📊 指数数量: {count}")
                        
                        if indices:
                            print(f"\n📋 前10个指数数据:")
                            print("-" * 100)
                            print(f"{'序号':<6} {'代码':<10} {'名称':<25} {'最新价':<12} {'涨跌幅':<10} {'涨跌额':<12}")
                            print("-" * 100)
                            
                            for i, idx in enumerate(indices[:10], 1):
                                code = idx.get('code', '')
                                name = idx.get('name', '')
                                price = idx.get('currentPrice', 0)
                                change_pct = idx.get('changePercent', 0)
                                change = idx.get('change', 0)
                                
                                print(f"{i:<6} {code:<10} {name[:25]:<25} {price:<12.2f} {change_pct:<10.2f}% {change:<12.2f}")
                            
                            print("-" * 100)
                            
                            # 显示主要指数
                            print(f"\n🔍 主要指数信息:")
                            main_indices = ['000001', '399001', '399006', '000016', '000300', '000905']
                            found_main = False
                            for idx in indices:
                                if idx.get('code') in main_indices:
                                    found_main = True
                                    print(f"  • {idx.get('name')} ({idx.get('code')}): {idx.get('currentPrice'):.2f}, "
                                          f"涨跌幅: {idx.get('changePercent'):+.2f}%, "
                                          f"涨跌额: {idx.get('change'):+.2f}")
                            
                            if not found_main:
                                print("  ⚠️  未找到主要指数")
                    else:
                        print(f"\n✅ 请求成功！")
                        data_content = data.get('data', {})
                        if isinstance(data_content, dict):
                            print(f"📋 数据内容:")
                            for key, value in list(data_content.items())[:10]:
                                print(f"  {key}: {value}")
                        elif isinstance(data_content, list):
                            print(f"📋 数据数量: {len(data_content)}")
                            if data_content:
                                print(f"📋 前5条数据:")
                                for i, item in enumerate(data_content[:5], 1):
                                    print(f"  {i}. {item}")
                else:
                    error = data.get('error', 'Unknown error')
                    print(f"\n❌ 请求失败: {error}")
            else:
                print(f"\n❌ HTTP错误: {response.status_code}")
                print(f"响应内容: {response.text[:200]}")
                
        except requests.exceptions.ConnectionError:
            print(f"\n❌ 连接失败: Flask应用可能未运行")
            print(f"💡 请先启动Flask应用: python3 app.py")
            break
        except requests.exceptions.Timeout:
            print(f"\n❌ 请求超时")
        except Exception as e:
            print(f"\n❌ 发生错误: {str(e)}")
            import traceback
            traceback.print_exc()

def test_direct_service():
    """直接测试服务类"""
    print("\n" + "=" * 60)
    print("直接测试服务类 (StockIndexService.get_index_spot)")
    print("=" * 60)
    
    try:
        from services.stock_index_service import StockIndexService
        
        print("\n🔄 正在调用 akshare.stock_zh_index_spot_em()...")
        indices = StockIndexService.get_index_spot()
        
        print(f"\n✅ 成功获取 {len(indices)} 个指数数据")
        
        if indices:
            print(f"\n📋 前5个指数数据:")
            for i, idx in enumerate(indices[:5], 1):
                print(f"{i}. {idx.get('name')} ({idx.get('code')}): "
                      f"最新价={idx.get('currentPrice'):.2f}, "
                      f"涨跌幅={idx.get('changePercent'):+.2f}%, "
                      f"成交量={idx.get('volume'):,.0f}")
        else:
            print("⚠️  未获取到指数数据")
            
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='测试指数API接口')
    parser.add_argument('--url', type=str, default='http://localhost:5000', help='Flask应用URL')
    parser.add_argument('--direct', action='store_true', help='直接测试服务类，不通过API')
    args = parser.parse_args()
    
    if args.direct:
        test_direct_service()
    else:
        test_index_api(args.url)

