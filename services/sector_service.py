import akshare as ak
from typing import List, Dict, Optional
import pandas as pd
import time as time_module
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
        max_retries = 3
        retry_delay = 2
        
        for retry in range(max_retries):
            try:
                df = ak.stock_board_industry_summary_ths()
                
                # 检查返回结果
                if df is None:
                    if retry < max_retries - 1:
                        print(f"⚠️  API返回None，重试 {retry + 1}/{max_retries}...")
                        time_module.sleep(retry_delay)
                        retry_delay *= 2
                        continue
                    else:
                        raise Exception('API返回None，无法获取行业板块数据')
                
                if df.empty:
                    if retry < max_retries - 1:
                        print(f"⚠️  API返回空数据，重试 {retry + 1}/{max_retries}...")
                        time_module.sleep(retry_delay)
                        retry_delay *= 2
                        continue
                    else:
                        raise Exception('API返回空数据，无法获取行业板块数据')
                
                # 成功获取数据
                return cls._dataframe_to_dict_list(df)
                
            except Exception as e:
                error_msg = str(e)
                # 检查是否是"No tables found"错误
                if "No tables found" in error_msg or "no tables" in error_msg.lower():
                    # 检查当前时间是否在交易时间内
                    from utils.time_utils import is_trading_time
                    is_trading = is_trading_time()
                    
                    if retry < max_retries - 1:
                        print(f"⚠️  检测到'No tables found'错误，重试 {retry + 1}/{max_retries}...")
                        time_module.sleep(retry_delay)
                        retry_delay *= 2
                        continue
                    else:
                        # 提供更友好的错误信息
                        if not is_trading:
                            raise Exception(f'API返回"No tables found"错误。当前时间不在交易时间内（交易时间：9:30-11:30, 13:00-15:00），这是正常现象。请稍后在交易时间内重试。')
                        else:
                            raise Exception(f'API返回"No tables found"错误，可能是API接口临时问题。已重试{max_retries}次，请稍后重试。')
                else:
                    # 其他错误，如果是最后一次重试，则抛出异常
                    if retry < max_retries - 1:
                        print(f"⚠️  获取行业板块数据失败，重试 {retry + 1}/{max_retries}: {error_msg}")
                        time_module.sleep(retry_delay)
                        retry_delay *= 2
                        continue
                    else:
                        raise Exception(f'Failed to get industry summary after {max_retries} retries: {str(e)}')
        
        # 如果所有重试都失败
        raise Exception('Failed to get industry summary: All retries exhausted')
    
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

