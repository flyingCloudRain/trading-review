from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date
from models.stock_fund_flow_history import StockFundFlowHistory
from utils.time_utils import get_data_date
import akshare as ak
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class StockFundFlowHistoryService:
    """个股资金流历史数据服务"""
    
    @staticmethod
    def save_stock_fund_flow(db: Session, stock_code: str, target_date: Optional[date] = None) -> bool:
        """
        保存个股资金流数据（即时数据）
        使用 stock_individual_fund_flow 接口获取单个股票的历史资金流数据
        
        Args:
            db: 数据库会话
            stock_code: 股票代码（6位数字）
            target_date: 可选，指定保存的日期。如果为None，则使用当日交易日
        
        Returns:
            bool: 是否保存成功
        """
        from utils.time_utils import get_utc8_date
        
        if target_date is None:
            data_date = get_data_date()
        else:
            data_date = target_date
        
        try:
            # 调用 stock_individual_fund_flow 接口获取单个股票的资金流历史数据
            # 该接口返回120天的历史数据，取最新一条作为当日数据
            df_fund = ak.stock_individual_fund_flow(stock=stock_code)
            
            if df_fund is None or df_fund.empty:
                logger.warning(f"股票代码 {stock_code} 的资金流数据为空")
                return False
            
            # 按日期排序，获取最新的一条数据
            if '日期' in df_fund.columns:
                df_fund['日期'] = pd.to_datetime(df_fund['日期'])
                df_fund = df_fund.sort_values('日期', ascending=False)
            
            # 获取最新的一条数据（当日数据）
            latest_data = df_fund.iloc[0]
            
            # 检查该日期和股票代码的数据是否已存在
            existing = db.query(StockFundFlowHistory).filter(
                and_(
                    StockFundFlowHistory.date == data_date,
                    StockFundFlowHistory.stock_code == stock_code
                )
            ).first()
            
            # 辅助函数：解析数值（处理字符串格式，如 "1.23万" 或 "1.23亿"）
            def parse_amount(value):
                """解析金额字符串，支持万、亿等单位"""
                if pd.isna(value) or value is None:
                    return None
                if isinstance(value, (int, float)):
                    return float(value)
                if isinstance(value, str):
                    value = value.strip()
                    if not value or value == '-':
                        return None
                    # 移除可能的逗号分隔符
                    value = value.replace(',', '')
                    # 处理单位
                    if '亿' in value:
                        num = float(value.replace('亿', ''))
                        return num * 100000000
                    elif '万' in value:
                        num = float(value.replace('万', ''))
                        return num * 10000
                    else:
                        try:
                            return float(value)
                        except:
                            return None
                return None
            
            # 辅助函数：解析百分比
            def parse_percent(value):
                """解析百分比字符串"""
                if pd.isna(value) or value is None:
                    return None
                if isinstance(value, (int, float)):
                    return float(value)
                if isinstance(value, str):
                    value = value.strip().replace('%', '').replace(',', '')
                    if not value or value == '-':
                        return None
                    try:
                        return float(value)
                    except:
                        return None
                return None
            
            # 字段映射和计算
            # stock_individual_fund_flow 返回的字段：
            # 日期、收盘价、涨跌幅、主力净流入-净额、主力净流入-净占比、超大单净流入-净额等
            
            # 计算流入和流出资金
            # 超大单和大单的净流入可能是正数（流入）或负数（流出）
            # 流入资金 = 超大单净流入（如果为正）+ 大单净流入（如果为正）
            # 流出资金 = -超大单净流入（如果为负）+ -大单净流入（如果为负）
            main_net_inflow = float(latest_data.get('主力净流入-净额', 0)) if pd.notna(latest_data.get('主力净流入-净额')) else 0
            super_large_net = float(latest_data.get('超大单净流入-净额', 0)) if pd.notna(latest_data.get('超大单净流入-净额')) else 0
            large_net = float(latest_data.get('大单净流入-净额', 0)) if pd.notna(latest_data.get('大单净流入-净额')) else 0
            
            # 分别计算流入和流出
            inflow = (super_large_net if super_large_net > 0 else 0) + (large_net if large_net > 0 else 0)
            outflow = (-super_large_net if super_large_net < 0 else 0) + (-large_net if large_net < 0 else 0)
            
            # 如果流入或流出为0，设为None
            inflow = inflow if inflow > 0 else None
            outflow = outflow if outflow > 0 else None
            
            # 准备数据（根据实际接口返回的字段进行映射）
            fund_flow_data = {
                'date': data_date,
                'stock_code': str(stock_code).zfill(6),  # 确保是6位字符串
                'stock_name': None,  # stock_individual_fund_flow 接口不返回股票名称，可后续从其他接口补充
                'latest_price': float(latest_data.get('收盘价', 0)) if pd.notna(latest_data.get('收盘价')) else None,
                'change_percent': float(latest_data.get('涨跌幅', 0)) if pd.notna(latest_data.get('涨跌幅')) else None,
                'turnover_rate': None,  # 该接口不提供换手率
                'inflow': inflow,
                'outflow': outflow,
                'net_amount': main_net_inflow if main_net_inflow != 0 else None,
                'turnover': None,  # 该接口不提供成交额
            }
            
            if existing:
                # 更新现有数据
                for key, value in fund_flow_data.items():
                    setattr(existing, key, value)
                logger.info(f"更新股票 {stock_code} 在 {data_date} 的资金流数据")
            else:
                # 创建新数据
                fund_flow = StockFundFlowHistory(**fund_flow_data)
                db.add(fund_flow)
                logger.info(f"保存股票 {stock_code} 在 {data_date} 的资金流数据")
            
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"保存股票 {stock_code} 资金流数据失败: {str(e)}", exc_info=True)
            raise Exception(f'Failed to save stock fund flow data: {str(e)}')
    
    @staticmethod
    def save_multiple_stocks_fund_flow(db: Session, stock_codes: List[str], target_date: Optional[date] = None) -> Dict[str, bool]:
        """
        批量保存多个股票的资金流数据
        
        Args:
            db: 数据库会话
            stock_codes: 股票代码列表
            target_date: 可选，指定保存的日期
        
        Returns:
            Dict[str, bool]: 每个股票代码的保存结果
        """
        results = {}
        for stock_code in stock_codes:
            try:
                success = StockFundFlowHistoryService.save_stock_fund_flow(db, stock_code, target_date)
                results[stock_code] = success
            except Exception as e:
                logger.error(f"保存股票 {stock_code} 资金流数据失败: {str(e)}")
                results[stock_code] = False
        return results
    
    @staticmethod
    def get_fund_flow_by_stock_and_date(db: Session, stock_code: str, target_date: date) -> Optional[Dict]:
        """根据股票代码和日期获取资金流数据"""
        fund_flow = db.query(StockFundFlowHistory).filter(
            and_(
                StockFundFlowHistory.stock_code == stock_code,
                StockFundFlowHistory.date == target_date
            )
        ).first()
        
        return fund_flow.to_dict() if fund_flow else None
    
    @staticmethod
    def get_fund_flow_by_date(db: Session, target_date: date) -> List[Dict]:
        """根据日期获取所有股票的资金流数据"""
        fund_flows = db.query(StockFundFlowHistory).filter(
            StockFundFlowHistory.date == target_date
        ).all()
        
        return [ff.to_dict() for ff in fund_flows]
    
    @staticmethod
    def get_fund_flow_by_stock(db: Session, stock_code: str, limit: int = 30) -> List[Dict]:
        """根据股票代码获取最近N天的资金流数据"""
        fund_flows = db.query(StockFundFlowHistory).filter(
            StockFundFlowHistory.stock_code == stock_code
        ).order_by(StockFundFlowHistory.date.desc()).limit(limit).all()
        
        return [ff.to_dict() for ff in fund_flows]
    
    @staticmethod
    def save_all_stocks_fund_flow_from_individual(db: Session, target_date: Optional[date] = None) -> Dict[str, int]:
        """
        从 stock_fund_flow_individual(symbol="即时") 接口获取所有股票的资金流数据并保存
        
        Args:
            db: 数据库会话
            target_date: 可选，指定保存的日期。如果为None，则使用当日交易日
        
        Returns:
            Dict[str, int]: 包含成功和失败数量的字典
                - success_count: 成功保存的股票数量
                - failed_count: 保存失败的股票数量
                - total_count: 总股票数量
        """
        from utils.time_utils import get_utc8_date
        
        if target_date is None:
            data_date = get_data_date()
        else:
            data_date = target_date
        
        success_count = 0
        failed_count = 0
        
        try:
            logger.info(f"开始从 stock_fund_flow_individual 接口获取所有股票的资金流数据...")
            logger.info(f"保存日期: {data_date}")
            
            # 调用 stock_fund_flow_individual 接口获取所有股票的即时资金流数据
            df_fund = ak.stock_fund_flow_individual(symbol="即时")
            
            if df_fund is None or df_fund.empty:
                logger.warning("stock_fund_flow_individual 接口返回空数据")
                return {
                    'success_count': 0,
                    'failed_count': 0,
                    'total_count': 0
                }
            
            total_count = len(df_fund)
            logger.info(f"获取到 {total_count} 只股票的资金流数据")
            
            # 辅助函数：解析数值（处理字符串格式，如 "1.23万" 或 "1.23亿"）
            def parse_amount(value):
                """解析金额字符串，支持万、亿等单位"""
                if pd.isna(value) or value is None:
                    return None
                if isinstance(value, (int, float)):
                    return float(value)
                if isinstance(value, str):
                    value = value.strip()
                    if not value or value == '-':
                        return None
                    # 移除可能的逗号分隔符
                    value = value.replace(',', '')
                    # 处理单位
                    if '亿' in value:
                        num = float(value.replace('亿', ''))
                        return num * 100000000
                    elif '万' in value:
                        num = float(value.replace('万', ''))
                        return num * 10000
                    else:
                        try:
                            return float(value)
                        except:
                            return None
                return None
            
            # 辅助函数：解析百分比
            def parse_percent(value):
                """解析百分比字符串"""
                if pd.isna(value) or value is None:
                    return None
                if isinstance(value, (int, float)):
                    return float(value)
                if isinstance(value, str):
                    value = value.strip().replace('%', '').replace(',', '')
                    if not value or value == '-':
                        return None
                    try:
                        return float(value)
                    except:
                        return None
                return None
            
            # 批量处理数据
            batch_size = 100  # 每批处理100条
            for i in range(0, total_count, batch_size):
                batch_df = df_fund.iloc[i:i+batch_size]
                
                for _, row in batch_df.iterrows():
                    try:
                        # 获取股票代码（转换为字符串并补齐6位）
                        stock_code = str(int(row['股票代码'])).zfill(6)
                        
                        # 检查该日期和股票代码的数据是否已存在
                        existing = db.query(StockFundFlowHistory).filter(
                            and_(
                                StockFundFlowHistory.date == data_date,
                                StockFundFlowHistory.stock_code == stock_code
                            )
                        ).first()
                        
                        # 准备数据
                        fund_flow_data = {
                            'date': data_date,
                            'stock_code': stock_code,
                            'stock_name': str(row.get('股票简称', '')) if pd.notna(row.get('股票简称')) else None,
                            'latest_price': float(row.get('最新价', 0)) if pd.notna(row.get('最新价')) else None,
                            'change_percent': parse_percent(row.get('涨跌幅')),
                            'turnover_rate': parse_percent(row.get('换手率')),
                            'inflow': parse_amount(row.get('流入资金')),
                            'outflow': parse_amount(row.get('流出资金')),
                            'net_amount': parse_amount(row.get('净额')),
                            'turnover': parse_amount(row.get('成交额')),
                        }
                        
                        if existing:
                            # 更新现有数据
                            for key, value in fund_flow_data.items():
                                setattr(existing, key, value)
                        else:
                            # 创建新数据
                            fund_flow = StockFundFlowHistory(**fund_flow_data)
                            db.add(fund_flow)
                        
                        success_count += 1
                        
                        # 每100条提交一次
                        if success_count % batch_size == 0:
                            db.commit()
                            logger.info(f"已处理 {success_count}/{total_count} 只股票...")
                    
                    except Exception as e:
                        failed_count += 1
                        logger.error(f"保存股票 {row.get('股票代码', 'N/A')} 资金流数据失败: {str(e)}")
                        # 继续处理下一条，不中断整个流程
                        continue
                
                # 提交当前批次
                try:
                    db.commit()
                except Exception as e:
                    db.rollback()
                    logger.error(f"提交批次数据失败: {str(e)}")
            
            logger.info(f"✅ 批量保存完成: 成功 {success_count} 只，失败 {failed_count} 只，总计 {total_count} 只")
            
            return {
                'success_count': success_count,
                'failed_count': failed_count,
                'total_count': total_count
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"批量保存所有股票资金流数据失败: {str(e)}", exc_info=True)
            raise Exception(f'Failed to save all stocks fund flow data: {str(e)}')

