-- Supabase数据库初始化脚本
-- 执行此脚本创建所有表、索引、函数和视图

-- ============================================
-- 1. 交易复盘记录表
-- ============================================
CREATE TABLE IF NOT EXISTS trading_reviews (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    stock_code VARCHAR(10) NOT NULL,
    stock_name VARCHAR(50) NOT NULL,
    operation VARCHAR(4) NOT NULL CHECK (operation IN ('buy', 'sell')),
    price DECIMAL(10, 2) NOT NULL,
    quantity INTEGER NOT NULL,
    total_amount DECIMAL(12, 2) NOT NULL,
    reason TEXT NOT NULL,
    review TEXT NOT NULL,
    profit DECIMAL(12, 2),
    profit_percent DECIMAL(6, 2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    user_id UUID REFERENCES auth.users(id)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_trading_reviews_date ON trading_reviews(date);
CREATE INDEX IF NOT EXISTS idx_trading_reviews_stock_code ON trading_reviews(stock_code);
CREATE INDEX IF NOT EXISTS idx_trading_reviews_user_id ON trading_reviews(user_id);
CREATE INDEX IF NOT EXISTS idx_trading_reviews_date_stock ON trading_reviews(date, stock_code);

-- 更新时间触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 更新时间触发器
DROP TRIGGER IF EXISTS update_trading_reviews_updated_at ON trading_reviews;
CREATE TRIGGER update_trading_reviews_updated_at 
    BEFORE UPDATE ON trading_reviews 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 2. 板块历史数据表
-- ============================================
CREATE TABLE IF NOT EXISTS sector_history (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    time TIME,
    index INTEGER NOT NULL,
    name VARCHAR(50) NOT NULL,
    change_percent DECIMAL(6, 2) NOT NULL,
    total_volume DECIMAL(12, 2) NOT NULL,
    total_amount DECIMAL(12, 2) NOT NULL,
    net_inflow DECIMAL(12, 2) NOT NULL,
    up_count INTEGER NOT NULL,
    down_count INTEGER NOT NULL,
    avg_price DECIMAL(10, 2) NOT NULL,
    leading_stock VARCHAR(50),
    leading_stock_price DECIMAL(10, 2),
    leading_stock_change_percent DECIMAL(6, 2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_sector_history_date ON sector_history(date);
CREATE INDEX IF NOT EXISTS idx_sector_history_name ON sector_history(name);
CREATE INDEX IF NOT EXISTS idx_sector_history_date_name ON sector_history(date, name);

-- ============================================
-- 3. 涨停股票池历史表
-- ============================================
CREATE TABLE IF NOT EXISTS zt_pool_history (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    time TIME,
    index INTEGER NOT NULL,
    code VARCHAR(10) NOT NULL,
    name VARCHAR(50) NOT NULL,
    change_percent DECIMAL(6, 2) NOT NULL,
    latest_price DECIMAL(10, 2) NOT NULL,
    turnover DECIMAL(12, 2) NOT NULL,
    circulating_market_value DECIMAL(15, 2) NOT NULL,
    total_market_value DECIMAL(15, 2) NOT NULL,
    turnover_rate DECIMAL(6, 2) NOT NULL,
    sealing_funds DECIMAL(12, 2) NOT NULL,
    first_sealing_time TIME,
    last_sealing_time TIME,
    explosion_count INTEGER NOT NULL DEFAULT 0,
    zt_statistics VARCHAR(50),
    continuous_boards INTEGER NOT NULL DEFAULT 0,
    industry VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_zt_pool_date ON zt_pool_history(date);
CREATE INDEX IF NOT EXISTS idx_zt_pool_code ON zt_pool_history(code);
CREATE INDEX IF NOT EXISTS idx_zt_pool_date_code ON zt_pool_history(date, code);
CREATE INDEX IF NOT EXISTS idx_zt_pool_industry ON zt_pool_history(industry);
CREATE INDEX IF NOT EXISTS idx_zt_pool_continuous_boards ON zt_pool_history(continuous_boards);

-- ============================================
-- 4. 炸板股票池历史表
-- ============================================
CREATE TABLE IF NOT EXISTS zbgc_pool_history (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    time TIME,
    index INTEGER NOT NULL,
    code VARCHAR(10) NOT NULL,
    name VARCHAR(50) NOT NULL,
    change_percent DECIMAL(6, 2) NOT NULL,
    latest_price DECIMAL(10, 2) NOT NULL,
    limit_price DECIMAL(10, 2) NOT NULL,
    turnover DECIMAL(12, 2) NOT NULL,
    circulating_market_value DECIMAL(15, 2) NOT NULL,
    total_market_value DECIMAL(15, 2) NOT NULL,
    turnover_rate DECIMAL(6, 2) NOT NULL,
    rise_speed DECIMAL(8, 4) NOT NULL,
    first_sealing_time TIME,
    explosion_count INTEGER NOT NULL DEFAULT 0,
    zt_statistics VARCHAR(50),
    amplitude DECIMAL(6, 2) NOT NULL,
    industry VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_zbgc_pool_date ON zbgc_pool_history(date);
CREATE INDEX IF NOT EXISTS idx_zbgc_pool_code ON zbgc_pool_history(code);
CREATE INDEX IF NOT EXISTS idx_zbgc_pool_date_code ON zbgc_pool_history(date, code);
CREATE INDEX IF NOT EXISTS idx_zbgc_pool_explosion_count ON zbgc_pool_history(explosion_count);

-- ============================================
-- 5. 跌停股票池历史表
-- ============================================
CREATE TABLE IF NOT EXISTS dtgc_pool_history (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    time TIME,
    index INTEGER NOT NULL,
    code VARCHAR(10) NOT NULL,
    name VARCHAR(50) NOT NULL,
    change_percent DECIMAL(6, 2) NOT NULL,
    latest_price DECIMAL(10, 2) NOT NULL,
    turnover DECIMAL(12, 2) NOT NULL,
    circulating_market_value DECIMAL(15, 2) NOT NULL,
    total_market_value DECIMAL(15, 2) NOT NULL,
    pe_ratio DECIMAL(10, 2),
    turnover_rate DECIMAL(6, 2) NOT NULL,
    sealing_funds DECIMAL(12, 2) NOT NULL,
    last_sealing_time TIME,
    board_turnover DECIMAL(12, 2) NOT NULL,
    continuous_limit_down INTEGER NOT NULL DEFAULT 0,
    open_count INTEGER NOT NULL DEFAULT 0,
    industry VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_dtgc_pool_date ON dtgc_pool_history(date);
CREATE INDEX IF NOT EXISTS idx_dtgc_pool_code ON dtgc_pool_history(code);
CREATE INDEX IF NOT EXISTS idx_dtgc_pool_date_code ON dtgc_pool_history(date, code);
CREATE INDEX IF NOT EXISTS idx_dtgc_pool_continuous_limit_down ON dtgc_pool_history(continuous_limit_down);

-- ============================================
-- 6. 板块异动历史表
-- ============================================
CREATE TABLE IF NOT EXISTS board_change_history (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    time TIME,
    name VARCHAR(50) NOT NULL,
    change_percent DECIMAL(6, 2) NOT NULL,
    net_inflow DECIMAL(12, 2) NOT NULL,
    total_change_count INTEGER NOT NULL,
    most_frequent_stock_code VARCHAR(10),
    most_frequent_stock_name VARCHAR(50),
    most_frequent_direction VARCHAR(10),
    change_types JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_board_change_date ON board_change_history(date);
CREATE INDEX IF NOT EXISTS idx_board_change_name ON board_change_history(name);
CREATE INDEX IF NOT EXISTS idx_board_change_date_name ON board_change_history(date, name);
CREATE INDEX IF NOT EXISTS idx_board_change_total_count ON board_change_history(total_change_count);
-- JSONB GIN索引
CREATE INDEX IF NOT EXISTS idx_board_change_types ON board_change_history USING GIN (change_types);

-- ============================================
-- 7. 统计函数
-- ============================================
CREATE OR REPLACE FUNCTION get_trading_statistics(p_user_id UUID)
RETURNS TABLE (
    total_records BIGINT,
    total_profit DECIMAL,
    win_count BIGINT,
    loss_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT as total_records,
        COALESCE(SUM(profit), 0) as total_profit,
        COUNT(*) FILTER (WHERE profit > 0)::BIGINT as win_count,
        COUNT(*) FILTER (WHERE profit < 0)::BIGINT as loss_count
    FROM trading_reviews
    WHERE user_id = p_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================
-- 8. 视图
-- ============================================

-- 每日涨停统计视图
CREATE OR REPLACE VIEW daily_zt_statistics AS
SELECT 
    date,
    COUNT(*) as total_count,
    AVG(change_percent) as avg_change_percent,
    AVG(continuous_boards) as avg_continuous_boards,
    SUM(turnover) as total_turnover,
    COUNT(DISTINCT industry) as industry_count
FROM zt_pool_history
GROUP BY date
ORDER BY date DESC;

-- 板块涨跌幅排名视图
CREATE OR REPLACE VIEW sector_ranking AS
SELECT 
    name,
    date,
    change_percent,
    net_inflow,
    ROW_NUMBER() OVER (PARTITION BY date ORDER BY change_percent DESC) as rank
FROM sector_history
ORDER BY date DESC, change_percent DESC;

-- ============================================
-- 9. Row Level Security (RLS)
-- ============================================

-- 交易复盘记录 - 用户只能访问自己的数据
ALTER TABLE trading_reviews ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own trading reviews" ON trading_reviews;
CREATE POLICY "Users can view own trading reviews"
    ON trading_reviews
    FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own trading reviews" ON trading_reviews;
CREATE POLICY "Users can insert own trading reviews"
    ON trading_reviews
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own trading reviews" ON trading_reviews;
CREATE POLICY "Users can update own trading reviews"
    ON trading_reviews
    FOR UPDATE
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own trading reviews" ON trading_reviews;
CREATE POLICY "Users can delete own trading reviews"
    ON trading_reviews
    FOR DELETE
    USING (auth.uid() = user_id);

-- 历史数据表 - 公开只读
ALTER TABLE sector_history ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Public read access" ON sector_history;
CREATE POLICY "Public read access"
    ON sector_history
    FOR SELECT
    USING (true);

ALTER TABLE zt_pool_history ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Public read access" ON zt_pool_history;
CREATE POLICY "Public read access"
    ON zt_pool_history
    FOR SELECT
    USING (true);

ALTER TABLE zbgc_pool_history ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Public read access" ON zbgc_pool_history;
CREATE POLICY "Public read access"
    ON zbgc_pool_history
    FOR SELECT
    USING (true);

ALTER TABLE dtgc_pool_history ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Public read access" ON dtgc_pool_history;
CREATE POLICY "Public read access"
    ON dtgc_pool_history
    FOR SELECT
    USING (true);

ALTER TABLE board_change_history ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Public read access" ON board_change_history;
CREATE POLICY "Public read access"
    ON board_change_history
    FOR SELECT
    USING (true);

-- ============================================
-- 10. 实时订阅（需要在Supabase Dashboard中配置）
-- ============================================
-- 在Supabase Dashboard -> Database -> Replication 中启用
-- 或使用以下SQL（需要超级用户权限）：
-- ALTER PUBLICATION supabase_realtime ADD TABLE trading_reviews;
-- ALTER PUBLICATION supabase_realtime ADD TABLE sector_history;
-- ALTER PUBLICATION supabase_realtime ADD TABLE zt_pool_history;

