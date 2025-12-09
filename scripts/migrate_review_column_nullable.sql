-- ============================================
-- 数据库迁移脚本：将 trading_reviews 表的 review 列改为可空
-- ============================================
-- 执行方式：
-- 1. 在 Supabase Dashboard 的 SQL Editor 中执行此脚本
-- 2. 或者通过 psql 命令行执行
-- ============================================

-- 检查 review 列的当前状态
SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'trading_reviews'
    AND column_name = 'review';

-- 将 review 列改为可空
DO $$
BEGIN
    -- 检查 review 列是否存在且为 NOT NULL
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'trading_reviews' 
        AND column_name = 'review'
        AND is_nullable = 'NO'
    ) THEN
        ALTER TABLE trading_reviews 
        ALTER COLUMN review DROP NOT NULL;
        RAISE NOTICE '✅ 成功将 review 列改为可空';
    ELSE
        RAISE NOTICE '✅ review 列已经是可空的，无需修改';
    END IF;
END $$;

-- 验证修改结果
SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'trading_reviews'
    AND column_name = 'review';

