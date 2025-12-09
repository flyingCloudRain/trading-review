-- ============================================
-- 数据库迁移脚本：为 trading_reviews 表添加止盈价和止损价字段
-- ============================================
-- 执行方式：
-- 1. 在 Supabase Dashboard 的 SQL Editor 中执行此脚本
-- 2. 或者通过 psql 命令行执行
-- ============================================

-- 检查并添加 take_profit_price 列
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'trading_reviews' 
        AND column_name = 'take_profit_price'
    ) THEN
        ALTER TABLE trading_reviews 
        ADD COLUMN take_profit_price DECIMAL(10, 2);
        RAISE NOTICE '✅ 成功添加 take_profit_price 列';
    ELSE
        RAISE NOTICE '✅ take_profit_price 列已存在，跳过';
    END IF;
END $$;

-- 检查并添加 stop_loss_price 列
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'trading_reviews' 
        AND column_name = 'stop_loss_price'
    ) THEN
        ALTER TABLE trading_reviews 
        ADD COLUMN stop_loss_price DECIMAL(10, 2);
        RAISE NOTICE '✅ 成功添加 stop_loss_price 列';
    ELSE
        RAISE NOTICE '✅ stop_loss_price 列已存在，跳过';
    END IF;
END $$;

-- 验证列是否添加成功
SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'trading_reviews'
    AND column_name IN ('take_profit_price', 'stop_loss_price')
ORDER BY column_name;

