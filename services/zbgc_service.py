import akshare as ak
from typing import List, Dict, Optional
import pandas as pd
from utils.time_utils import get_utc8_date_compact_str

class ZbgcService:
    """炸板股票池服务"""
    
    @classmethod
    def get_zbgc_pool(cls, date: Optional[str] = None) -> List[Dict]:
        """
        获取炸板股票池
        :param date: 交易日，格式：YYYYMMDD，默认为今日
        :return: 炸板股票列表
        """
        try:
            # 如果没有指定日期，使用今日（UTC+8时区）
            if date is None:
                date = get_utc8_date_compact_str()
            
            # 调用akshare接口
            df = ak.stock_zt_pool_zbgc_em(date=date)
            
            # 转换为字典列表
            return cls._dataframe_to_dict_list(df)
        except Exception as e:
            raise Exception(f'Failed to get zbgc pool: {str(e)}')
    
    @classmethod
    def _dataframe_to_dict_list(cls, df: pd.DataFrame) -> List[Dict]:
        """将DataFrame转换为字典列表"""
        result = []
        for _, row in df.iterrows():
            # 单位转换：从元转换为亿元（除以100000000）
            turnover_yuan = float(row.get('成交额', 0)) if pd.notna(row.get('成交额')) else 0
            circulating_mv_yuan = float(row.get('流通市值', 0)) if pd.notna(row.get('流通市值')) else 0
            total_mv_yuan = float(row.get('总市值', 0)) if pd.notna(row.get('总市值')) else 0
            
            stock = {
                'index': int(row.get('序号', 0)) if pd.notna(row.get('序号')) else 0,
                'code': str(row.get('代码', '')),
                'name': str(row.get('名称', '')),
                'changePercent': float(row.get('涨跌幅', 0)) if pd.notna(row.get('涨跌幅')) else 0,
                'latestPrice': float(row.get('最新价', 0)) if pd.notna(row.get('最新价')) else 0,
                'limitPrice': float(row.get('涨停价', 0)) if pd.notna(row.get('涨停价')) else 0,
                'turnover': round(turnover_yuan / 100000000, 2),  # 转换为亿元
                'circulatingMarketValue': round(circulating_mv_yuan / 100000000, 2),  # 转换为亿元
                'totalMarketValue': round(total_mv_yuan / 100000000, 2),  # 转换为亿元
                'turnoverRate': float(row.get('换手率', 0)) if pd.notna(row.get('换手率')) else 0,
                'riseSpeed': float(row.get('涨速', 0)) if pd.notna(row.get('涨速')) else 0,
                'firstSealingTime': str(row.get('首次封板时间', '')) if pd.notna(row.get('首次封板时间')) else '',
                'explosionCount': int(row.get('炸板次数', 0)) if pd.notna(row.get('炸板次数')) else 0,
                'ztStatistics': str(row.get('涨停统计', '')) if pd.notna(row.get('涨停统计')) else '',
                'amplitude': float(row.get('振幅', 0)) if pd.notna(row.get('振幅')) else 0,
                'industry': str(row.get('所属行业', '')) if pd.notna(row.get('所属行业')) else '',
            }
            result.append(stock)
        return result

