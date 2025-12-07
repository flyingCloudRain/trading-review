import akshare as ak
from typing import List, Dict, Optional
import pandas as pd
# 注意：Config 类在此文件中未使用，但保留导入以防将来需要
# from config import Config

class SectorService:
    """板块信息服务（同花顺行业一览表）"""
    
    @classmethod
    def get_industry_summary(cls) -> List[Dict]:
        """
        获取同花顺行业一览表
        对应akshare接口: stock_board_industry_summary_ths
        """
        try:
            df = ak.stock_board_industry_summary_ths()
            return cls._dataframe_to_dict_list(df)
        except Exception as e:
            raise Exception(f'Failed to get industry summary: {str(e)}')
    
    @classmethod
    def _dataframe_to_dict_list(cls, df: pd.DataFrame) -> List[Dict]:
        """将DataFrame转换为字典列表"""
        result = []
        for _, row in df.iterrows():
            sector = {
                'index': int(row.get('序号', 0)),
                'name': str(row.get('板块', '')),
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
            result.append(sector)
        return result

