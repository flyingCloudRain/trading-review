import akshare as ak
from typing import List, Dict, Optional
import pandas as pd
import json

class BoardChangeService:
    """板块异动服务"""
    
    @classmethod
    def get_board_changes(cls) -> List[Dict]:
        """
        获取当日板块异动详情
        :return: 板块异动列表
        """
        try:
            # 调用akshare接口
            df = ak.stock_board_change_em()
            
            # 转换为字典列表
            return cls._dataframe_to_dict_list(df)
        except Exception as e:
            raise Exception(f'Failed to get board changes: {str(e)}')
    
    @classmethod
    def _dataframe_to_dict_list(cls, df: pd.DataFrame) -> List[Dict]:
        """将DataFrame转换为字典列表"""
        result = []
        for _, row in df.iterrows():
            # 处理主力净流入（从元转换为亿元）
            net_inflow_yuan = float(row.get('主力净流入', 0)) if pd.notna(row.get('主力净流入')) else 0
            net_inflow_yi = round(net_inflow_yuan / 100000000, 2)
            
            # 处理异动类型列表（JSON字符串）
            change_types_str = str(row.get('板块具体异动类型列表及出现次数', ''))
            change_types = []
            if change_types_str and change_types_str != 'nan':
                try:
                    # 尝试解析为JSON
                    if isinstance(change_types_str, str) and change_types_str.startswith('['):
                        change_types = json.loads(change_types_str)
                except:
                    # 如果解析失败，保持原样
                    change_types = change_types_str
            
            board = {
                'name': str(row.get('板块名称', '')),
                'changePercent': float(row.get('涨跌幅', 0)) if pd.notna(row.get('涨跌幅')) else 0,
                'netInflow': net_inflow_yi,  # 转换为亿元
                'totalChangeCount': int(row.get('板块异动总次数', 0)) if pd.notna(row.get('板块异动总次数')) else 0,
                'mostFrequentStockCode': str(row.get('板块异动最频繁个股及所属类型-股票代码', '')) if pd.notna(row.get('板块异动最频繁个股及所属类型-股票代码')) else '',
                'mostFrequentStockName': str(row.get('板块异动最频繁个股及所属类型-股票名称', '')) if pd.notna(row.get('板块异动最频繁个股及所属类型-股票名称')) else '',
                'mostFrequentDirection': str(row.get('板块异动最频繁个股及所属类型-买卖方向', '')) if pd.notna(row.get('板块异动最频繁个股及所属类型-买卖方向')) else '',
                'changeTypes': change_types,  # 异动类型列表
            }
            result.append(board)
        return result

