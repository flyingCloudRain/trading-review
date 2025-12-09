-- ============================================
-- 创建交易原因表 (trading_reasons)
-- ============================================
-- 执行方式：
-- 1. 在 Supabase Dashboard 的 SQL Editor 中执行此脚本
-- 2. 或者通过 psql 命令行执行
-- ============================================

-- 创建交易原因表
CREATE TABLE IF NOT EXISTS trading_reasons (
    id BIGSERIAL PRIMARY KEY,
    reason VARCHAR(100) NOT NULL UNIQUE,
    display_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_trading_reasons_reason ON trading_reasons(reason);
CREATE INDEX IF NOT EXISTS idx_trading_reasons_display_order ON trading_reasons(display_order);

-- 更新时间触发器
DROP TRIGGER IF EXISTS update_trading_reasons_updated_at ON trading_reasons;
CREATE TRIGGER update_trading_reasons_updated_at 
    BEFORE UPDATE ON trading_reasons 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- 插入默认交易原因（如果不存在）
INSERT INTO trading_reasons (reason, display_order) VALUES
    ('点位突破', 1),
    ('双突破趋势点位', 2),
    ('双突破趋势形态', 3),
    ('双突破趋势量能', 4),
    ('突破回调站稳', 5),
    ('回调非波拉切', 6),
    ('技术面突破', 7),
    ('技术面回调', 8),
    ('基本面改善', 9),
    ('基本面恶化', 10),
    ('消息面利好', 11),
    ('消息面利空', 12),
    ('资金面流入', 13),
    ('资金面流出', 14),
    ('板块轮动', 15),
    ('超跌反弹', 16),
    ('趋势跟随', 17),
    ('止盈离场', 18),
    ('止损离场', 19),
    ('调仓换股', 20),
    ('其他', 21)
ON CONFLICT (reason) DO NOTHING;

-- 验证表结构
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'trading_reasons'
ORDER BY ordinal_position;

-- 验证数据
SELECT id, reason, display_order, created_at 
FROM trading_reasons 
ORDER BY display_order, id;

