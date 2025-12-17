#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 stock_fund_flow_individual 接口（symbol="即时"）
"""
import akshare as ak
import pandas as pd

# 调用接口
print("🔄 正在调用 ak.stock_fund_flow_individual(symbol='即时')...")
print("=" * 80)

stock_fund_flow_individual_df = ak.stock_fund_flow_individual(symbol="即时")

print("✅ 接口调用成功！")
print()
print(f"📊 数据形状: {stock_fund_flow_individual_df.shape} (行数: {stock_fund_flow_individual_df.shape[0]}, 列数: {stock_fund_flow_individual_df.shape[1]})")
print()
print("📋 列名:")
print(stock_fund_flow_individual_df.columns.tolist())
print()
print("=" * 80)
print("📄 完整数据:")
print("=" * 80)
print(stock_fund_flow_individual_df)
print()
print("=" * 80)
print("📄 前20行数据（详细）:")
print("=" * 80)
print(stock_fund_flow_individual_df.head(20).to_string())
print()
print("=" * 80)
print("📊 数据统计信息:")
print("=" * 80)
print(f"总股票数: {len(stock_fund_flow_individual_df)}")
print(f"列数: {len(stock_fund_flow_individual_df.columns)}")
print()
print("数据类型:")
print(stock_fund_flow_individual_df.dtypes)

