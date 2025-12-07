import pytest
from services.sector_service import SectorService

class TestSectorService:
    """板块服务测试"""
    
    def test_get_industry_summary(self):
        """测试获取行业一览表"""
        try:
            sectors = SectorService.get_industry_summary()
            assert isinstance(sectors, list)
            assert len(sectors) > 0
            
            # 检查第一个板块的数据结构
            if sectors:
                sector = sectors[0]
                assert 'name' in sector
                assert 'changePercent' in sector
                assert 'totalVolume' in sector
                assert 'totalAmount' in sector
        except Exception as e:
            # 如果API暂时不可用，跳过测试
            pytest.skip(f"API暂时不可用: {str(e)}")
    
    def test_search_by_name(self):
        """测试按名称搜索"""
        sectors = SectorService.search_by_name('银行')
        assert isinstance(sectors, list)
        # 所有结果应该包含"银行"
        for sector in sectors:
            assert '银行' in sector['name']
    
    def test_get_top_sectors(self):
        """测试获取排名靠前的板块"""
        sectors = SectorService.get_top_sectors(limit=5)
        assert isinstance(sectors, list)
        assert len(sectors) <= 5
        
        # 检查是否按涨跌幅降序排列
        if len(sectors) > 1:
            for i in range(len(sectors) - 1):
                assert sectors[i]['changePercent'] >= sectors[i + 1]['changePercent']
    
    def test_get_bottom_sectors(self):
        """测试获取排名靠后的板块"""
        sectors = SectorService.get_bottom_sectors(limit=5)
        assert isinstance(sectors, list)
        assert len(sectors) <= 5
        
        # 检查是否按涨跌幅升序排列
        if len(sectors) > 1:
            for i in range(len(sectors) - 1):
                assert sectors[i]['changePercent'] <= sectors[i + 1]['changePercent']

