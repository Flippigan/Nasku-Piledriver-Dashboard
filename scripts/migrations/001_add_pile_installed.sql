-- Migration: Add pile_installed column to piles table
-- Run this on existing databases to add the new column

ALTER TABLE piles ADD COLUMN IF NOT EXISTS pile_installed TEXT DEFAULT 'No';

-- Backfill existing data based on hammering_status and hammering_flag
UPDATE piles
SET pile_installed = CASE
    WHEN hammering_flag = 'REFUSED' THEN 'Refusal'
    WHEN hammering_status IN ('COMPLETED', 'SUCCESS') THEN 'Yes'
    ELSE 'No'
END
WHERE pile_installed IS NULL OR pile_installed = 'No';
