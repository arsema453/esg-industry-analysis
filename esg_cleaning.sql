-- esg_cleaning.sql
-- Loads raw ESG-by-industry data and fixes inconsistent naming
-- that created 4 duplicate industries (e.g. "and" vs "&").

-- 1. Import (run from sqlite3 CLI in the folder with esg_raw.csv):
--   .open esg.db
--   .mode csv
--   .import esg_raw.csv esg_raw

-- 2. Normalize inconsistent naming
UPDATE esg_raw
SET Industry = TRIM(REPLACE(Industry, ' and ', ' & '));

-- 3. Confirm: should show 43 distinct names instead of 47
SELECT COUNT(DISTINCT Industry) FROM esg_raw;

-- 4. Build the clean, industry-level table (averaging merged duplicates)
DROP TABLE IF EXISTS esg_clean;

CREATE TABLE esg_clean AS
SELECT
  Industry AS industry,
  ROUND(AVG("Environment Score"), 1) AS environment_score,
  ROUND(AVG("Social Score"), 1) AS social_score,
  ROUND(AVG("Governance Score"), 1) AS governance_score,
  ROUND(AVG("Total ESG Score"), 1) AS total_esg_score
FROM esg_raw
GROUP BY Industry;

-- 5. Verify: should be 43
SELECT COUNT(*) FROM esg_clean;
