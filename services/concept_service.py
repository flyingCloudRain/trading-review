import akshare as ak
from typing import List, Dict, Optional
import pandas as pd
import time

class ConceptService:
    """概念板块信息服务（同花顺概念一览表）"""
    
    @classmethod
    def get_concept_summary(cls) -> List[Dict]:
        """
        获取同花顺概念一览表（包含资金流数据）
        优先使用 stock_fund_flow_concept 接口，该接口提供完整的资金流数据
        对应akshare接口: stock_fund_flow_concept
        数据来源: https://data.10jqka.com.cn/funds/gnzjl/
        """
        try:
            max_retries = 3
            retry_delay = 2
            
            for retry in range(max_retries):
                try:
                    # 优先使用概念资金流接口（提供完整的资金流数据）
                    df = ak.stock_fund_flow_concept()
                    if df is not None and not df.empty:
                        return cls._convert_fund_flow_to_dict(df)
                except Exception as e:
                    if retry < max_retries - 1:
                        time.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        # 如果 stock_fund_flow_concept 失败，尝试使用其他接口
                        try:
                            # 尝试使用 stock_board_concept_name_ths
                            df = ak.stock_board_concept_name_ths()
                            if df is not None and not df.empty:
                                return cls._dataframe_to_dict_list(df)
                        except:
                            pass
                        # 最后尝试使用 stock_board_concept_name_em
                        try:
                            df = ak.stock_board_concept_name_em()
                            if df is not None and not df.empty:
                                return cls._convert_concept_list_to_dict(df)
                        except:
                            pass
                        raise Exception(f'Failed to get concept summary after {max_retries} retries: {str(e)}')
            
            raise Exception('Unable to get concept summary data')
            
        except Exception as e:
            raise Exception(f'Failed to get concept summary: {str(e)}')
    
    @classmethod
    def _dataframe_to_dict_list(cls, df: pd.DataFrame) -> List[Dict]:
        """将DataFrame转换为字典列表（类似行业板块格式）"""
        result = []
        for idx, row in df.iterrows():
            concept = {
                'index': int(row.get('序号', idx + 1)),
                'name': str(row.get('板块', row.get('概念名称', row.get('板块名称', '')))),
                'changePercent': float(row.get('涨跌幅', 0)),
                'totalVolume': float(row.get('总成交量', 0)),
                'totalAmount': float(row.get('总成交额', 0)),
                'netInflow': float(row.get('净流入', 0)),
                'upCount': int(row.get('上涨家数', 0)),
                'downCount': int(row.get('下跌家数', 0)),
                'avgPrice': float(row.get('均价', 0)),
                'leadingStock': str(row.get('领涨股', '')),
                'leadingStockPrice': float(row.get('领涨股-最新价', 0)) if pd.notna(row.get('领涨股-最新价')) else 0,
                'leadingStockChangePercent': float(row.get('领涨股-涨跌幅', 0)),
            }
            result.append(concept)
        return result
    
    @classmethod
    def _convert_fund_flow_to_dict(cls, df: pd.DataFrame) -> List[Dict]:
        """
        将概念资金流DataFrame转换为字典列表（主要方法）
        数据来源: stock_fund_flow_concept
        列名: ['序号', '行业', '行业指数', '行业-涨跌幅', '流入资金', '流出资金', '净额', '公司家数', '领涨股', '领涨股-涨跌幅', '当前价']
        """
        result = []
        for idx, row in df.iterrows():
            # 流入资金和流出资金单位是万元，需要转换为亿元
            inflow_yuan = float(row.get('流入资金', 0)) if pd.notna(row.get('流入资金')) else 0
            outflow_yuan = float(row.get('流出资金', 0)) if pd.notna(row.get('流出资金')) else 0
            net_yuan = float(row.get('净额', 0)) if pd.notna(row.get('净额')) else 0
            
            # 转换为亿元（从万元转换为亿元：除以10000）
            inflow_yi = round(inflow_yuan / 10000, 2)
            outflow_yi = round(outflow_yuan / 10000, 2)
            net_yi = round(net_yuan / 10000, 2)
            
            concept = {
                'index': int(row.get('序号', idx + 1)),
                'name': str(row.get('行业', '')),  # 注意：这里"行业"字段实际是概念名称
                'changePercent': float(row.get('行业-涨跌幅', 0)) if pd.notna(row.get('行业-涨跌幅')) else 0,
                'totalVolume': 0,  # 资金流接口没有成交量数据
                'totalAmount': round(inflow_yuan + outflow_yuan, 2) / 10000 if (inflow_yuan + outflow_yuan) > 0 else 0,  # 总成交额（亿元）
                'netInflow': net_yi,  # 净流入（亿元）
                'upCount': 0,  # 资金流接口没有上涨家数
                'downCount': 0,  # 资金流接口没有下跌家数
                'avgPrice': float(row.get('行业指数', 0)) if pd.notna(row.get('行业指数')) else 0,  # 使用行业指数作为均价
                'leadingStock': str(row.get('领涨股', '')) if pd.notna(row.get('领涨股')) else '',
                'leadingStockPrice': float(row.get('当前价', 0)) if pd.notna(row.get('当前价')) else 0,
                'leadingStockChangePercent': float(row.get('领涨股-涨跌幅', 0)) if pd.notna(row.get('领涨股-涨跌幅')) else 0,
            }
            result.append(concept)
        return result
    
    @classmethod
    def _convert_concept_list_to_dict(cls, df: pd.DataFrame) -> List[Dict]:
        """将概念板块列表DataFrame转换为字典列表（备用方法）"""
        result = []
        for idx, row in df.iterrows():
            concept = {
                'index': int(idx + 1),
                'name': str(row.get('板块名称', row.get('概念名称', ''))),
                'changePercent': 0,  # 概念列表可能没有涨跌幅，需要后续获取
                'totalVolume': 0,
                'totalAmount': 0,
                'netInflow': 0,
                'upCount': 0,
                'downCount': 0,
                'avgPrice': 0,
                'leadingStock': '',
                'leadingStockPrice': 0,
                'leadingStockChangePercent': 0,
            }
            result.append(concept)
        return result

