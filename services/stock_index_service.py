import akshare as ak
from typing import List, Dict, Optional
import pandas as pd

class StockIndexService:
    """A股指数服务"""
    
    # 常用的A股指数代码
    INDEX_CODES: Dict[str, str] = {
        '000001': '上证指数',
        '399001': '深证成指',
        '399006': '创业板指',
        '000016': '上证50',
        '000300': '沪深300',
        '000905': '中证500',
        '399005': '中小板指',
    }
    
    @classmethod
    def get_index_codes(cls) -> Dict[str, str]:
        """获取指数代码列表"""
        return cls.INDEX_CODES.copy()
    
    @classmethod
    def get_index_info(cls, code: str) -> Dict:
        """获取指定指数信息"""
        if code not in cls.INDEX_CODES:
            raise ValueError(f'Invalid index code: {code}')
        
        try:
            # 使用akshare获取指数实时行情
            # 注意：这里使用模拟数据，实际akshare可能需要其他接口
            # 可以使用 ak.tool_trade_date_hist_sina() 等接口
            return cls._get_mock_index_data(code)
        except Exception as e:
            raise Exception(f'Failed to get index info: {str(e)}')
    
    @classmethod
    def get_all_indices(cls) -> List[Dict]:
        """获取所有主要指数信息"""
        indices = []
        for code in cls.INDEX_CODES.keys():
            try:
                index_info = cls.get_index_info(code)
                indices.append(index_info)
            except Exception as e:
                print(f'Error getting index {code}: {str(e)}')
        return indices
    
    @classmethod
    def search_by_name(cls, keyword: str) -> List[Dict]:
        """根据名称搜索指数"""
        matching_codes = [
            code for code, name in cls.INDEX_CODES.items()
            if keyword in name
        ]
        
        if not matching_codes:
            return []
        
        indices = []
        for code in matching_codes:
            try:
                index_info = cls.get_index_info(code)
                indices.append(index_info)
            except Exception as e:
                print(f'Error getting index {code}: {str(e)}')
        return indices
    
    @staticmethod
    def normalize_index_code(code: str) -> str:
        """
        标准化指数代码为6位格式，去除前缀
        从 'sh000001' 或 'sz399006' 格式提取数字部分，统一为6位
        
        支持的格式：
        - 'sh000001' → '000001' (去除 sh 前缀)
        - 'sz399006' → '399006' (去除 sz 前缀)
        - '000001'   → '000001' (已经是6位格式，保持不变)
        
        Args:
            code: 原始代码，可能包含前缀如 'sh'、'sz'
        
        Returns:
            str: 标准化后的6位代码，如 '000001'、'000300'、'399006'
        """
        if not code:
            return ''
        
        code_str = str(code).strip()
        
        # 去除前缀 sh 或 sz
        if code_str.startswith('sh') or code_str.startswith('sz'):
            code_str = code_str[2:]
        
        # 返回处理后的代码（应该已经是6位格式）
        return code_str
    
    @classmethod
    def get_index_spot(cls, symbol: Optional[str] = None) -> List[Dict]:
        """
        获取指数实时行情（使用 stock_zh_index_spot_em）
        注意：此方法作为备用数据源，主要数据源请使用 get_index_spot_sina()
        
        Args:
            symbol: 指数系列，可选值：
                   - "上证系列指数"
                   - "深证系列指数"
                   - None (获取所有指数，默认)
        
        Returns:
            List[Dict]: 指数实时行情列表
        """
        import time
        max_retries = 3
        retry_delay = 2  # 秒
        
        for attempt in range(max_retries):
            try:
                # 调用 akshare 接口获取指数实时行情
                if symbol:
                    df = ak.stock_zh_index_spot_em(symbol=symbol)
                else:
                    df = ak.stock_zh_index_spot_em()
                
                if df.empty:
                    return []
                
                # 转换为字典列表
                indices = []
                for _, row in df.iterrows():
                    raw_code = str(row.get('代码', ''))
                    normalized_code = cls.normalize_index_code(raw_code)
                    
                    index_data = {
                        'code': normalized_code,
                        'name': str(row.get('名称', '')),
                        'currentPrice': float(row.get('最新价', 0)) if pd.notna(row.get('最新价')) else 0,
                        'changePercent': float(row.get('涨跌幅', 0)) if pd.notna(row.get('涨跌幅')) else 0,
                        'change': float(row.get('涨跌额', 0)) if pd.notna(row.get('涨跌额')) else 0,
                        'volume': float(row.get('成交量', 0)) if pd.notna(row.get('成交量')) else 0,
                        'amount': float(row.get('成交额', 0)) if pd.notna(row.get('成交额')) else 0,
                        'open': float(row.get('今开', 0)) if pd.notna(row.get('今开')) else 0,
                        'high': float(row.get('最高', 0)) if pd.notna(row.get('最高')) else 0,
                        'low': float(row.get('最低', 0)) if pd.notna(row.get('最低')) else 0,
                        'prevClose': float(row.get('昨收', 0)) if pd.notna(row.get('昨收')) else 0,
                        'amplitude': float(row.get('振幅', 0)) if pd.notna(row.get('振幅')) else 0,
                        'volumeRatio': float(row.get('量比', 0)) if pd.notna(row.get('量比')) else 0,
                    }
                    indices.append(index_data)
                
                return indices
            except (ConnectionError, TimeoutError, Exception) as e:
                error_msg = str(e)
                # 检查是否是连接相关错误
                if 'Connection' in error_msg or 'Remote end closed' in error_msg or 'timeout' in error_msg.lower():
                    if attempt < max_retries - 1:
                        print(f"⚠️ 网络连接失败，正在重试 ({attempt + 1}/{max_retries})...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # 指数退避
                        continue
                    else:
                        raise Exception(f'网络连接失败，已重试 {max_retries} 次。请检查网络连接或稍后重试。原始错误: {error_msg}')
                else:
                    # 非连接错误，直接抛出
                    raise Exception(f'Failed to get index spot data: {error_msg}')
        
        return []
    
    @classmethod
    def get_index_spot_sina(cls) -> List[Dict]:
        """
        获取指数实时行情（使用 stock_zh_index_spot_sina）
        推荐使用此方法作为主要数据源，数据更完整（564条数据，包含355个深证指数）
        
        Returns:
            List[Dict]: 指数实时行情列表
        """
        try:
            # 调用 akshare 新浪接口获取指数实时行情
            df = ak.stock_zh_index_spot_sina()
            
            if df.empty:
                return []
            
            # 转换为字典列表
            indices = []
            for _, row in df.iterrows():
                raw_code = str(row.get('代码', ''))
                normalized_code = cls.normalize_index_code(raw_code)
                
                index_data = {
                    'code': normalized_code,
                    'name': str(row.get('名称', '')),
                    'currentPrice': float(row.get('最新价', 0)) if pd.notna(row.get('最新价')) else 0,
                    'changePercent': float(row.get('涨跌幅', 0)) if pd.notna(row.get('涨跌幅')) else 0,
                    'change': float(row.get('涨跌额', 0)) if pd.notna(row.get('涨跌额')) else 0,
                    'volume': float(row.get('成交量', 0)) if pd.notna(row.get('成交量')) else 0,
                    'amount': float(row.get('成交额', 0)) if pd.notna(row.get('成交额')) else 0,
                    'open': float(row.get('今开', 0)) if pd.notna(row.get('今开')) else 0,
                    'high': float(row.get('最高', 0)) if pd.notna(row.get('最高')) else 0,
                    'low': float(row.get('最低', 0)) if pd.notna(row.get('最低')) else 0,
                    'prevClose': float(row.get('昨收', 0)) if pd.notna(row.get('昨收')) else 0,
                    'amplitude': 0,  # 新浪接口没有振幅字段
                    'volumeRatio': 0,  # 新浪接口没有量比字段
                }
                indices.append(index_data)
            
            return indices
        except Exception as e:
            raise Exception(f'Failed to get index spot data from sina: {str(e)}')
    
    @classmethod
    def _get_mock_index_data(cls, code: str) -> Dict:
        """获取模拟指数数据（实际项目中应替换为真实API调用）"""
        import random
        from datetime import datetime
        
        name = cls.INDEX_CODES[code]
        base_prices = {
            '000001': 3000,
            '399001': 11000,
            '399006': 2200,
            '000016': 2500,
            '000300': 3800,
            '000905': 5500,
            '399005': 7000,
        }
        
        base_price = base_prices.get(code, 3000)
        change_percent = (random.random() - 0.5) * 4  # -2% 到 +2%
        change = base_price * (change_percent / 100)
        current_price = base_price + change
        
        return {
            'code': code,
            'name': name,
            'currentPrice': round(current_price, 2),
            'change': round(change, 2),
            'changePercent': round(change_percent, 2),
            'volume': random.randint(100000000, 1000000000),
            'amount': random.randint(10000000000, 50000000000),
            'updateTime': datetime.now().isoformat(),
        }

