-- ==============================================================================
-- Project: Audit Transaction Exception Analysis
-- File: audit_queries.sql
-- Database Engine: SQLite / SQL Server Compatible
-- Description: Core analytical queries designed for internal audit and advisory
--              teams to isolate high-risk transactions requiring substantive review.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. Total transaction amount and volume by department
-- Audit Purpose: Baseline expenditure profiling across business units to establish
--                materiality thresholds and focus testing on high-spend departments.
-- ------------------------------------------------------------------------------
SELECT
    Department,
    COUNT(*) AS transaction_count,
    ROUND(SUM(Amount), 2) AS total_amount,
    ROUND(AVG(Amount), 2) AS average_amount
FROM transactions
GROUP BY Department
ORDER BY total_amount DESC;


-- ------------------------------------------------------------------------------
-- 2. High-value transactions (> ₹50,000 threshold)
-- Audit Purpose: Identify transactions exceeding standard managerial signing authority
--                to verify dual approval, purchase order matching, and executive sign-off.
-- ------------------------------------------------------------------------------
SELECT
    Transaction_ID,
    Date,
    Department,
    Employee_ID,
    Vendor,
    Amount,
    Payment_Method
FROM transactions
WHERE Amount > 50000
ORDER BY Amount DESC;


-- ------------------------------------------------------------------------------
-- 3. Possible duplicate transactions (identical Date, Vendor, and Amount)
-- Audit Purpose: Detect potential double-billing, duplicate ERP voucher entry,
--                or fraudulent split-disbursements.
-- ------------------------------------------------------------------------------
SELECT
    Date,
    Vendor,
    Amount,
    COUNT(*) AS duplicate_count
FROM transactions
GROUP BY Date, Vendor, Amount
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC, Amount DESC;


-- ------------------------------------------------------------------------------
-- 4. Weekend transactions (Saturday or Sunday)
-- Audit Purpose: Flag transactions recorded during non-standard business days to
--                assess off-hours accounting activity, unauthorized system access,
--                or backdated journal entries.
-- Note:
--   - SQLite: strftime('%w', Date) returns '0' for Sunday and '6' for Saturday.
--   - SQL Server alternative: DATEPART(dw, Date) IN (1, 7) or DATENAME(dw, Date) IN ('Saturday', 'Sunday')
-- ------------------------------------------------------------------------------
SELECT
    Transaction_ID,
    Date,
    CASE strftime('%w', Date)
        WHEN '0' THEN 'Sunday'
        WHEN '6' THEN 'Saturday'
    END AS Weekend_Day,
    Department,
    Employee_ID,
    Vendor,
    Amount,
    Payment_Method
FROM transactions
WHERE strftime('%w', Date) IN ('0', '6')
ORDER BY Date ASC, Amount DESC;


-- ------------------------------------------------------------------------------
-- 5. ADVANCED AUDIT QUERY: Compound Exception Risk Ranking
-- Audit Purpose: Prioritizes records violating MULTIPLE control rules simultaneously
--                (e.g., high value AND posted on a weekend, or weekend duplicate).
-- ------------------------------------------------------------------------------
WITH ScoredTransactions AS (
    SELECT
        t.Transaction_ID,
        t.Date,
        t.Department,
        t.Employee_ID,
        t.Vendor,
        t.Amount,
        t.Payment_Method,
        -- Rule 1 Flag
        CASE WHEN t.Amount > 50000 THEN 1 ELSE 0 END AS flag_high_value,
        -- Rule 2 Flag
        CASE WHEN strftime('%w', t.Date) IN ('0', '6') THEN 1 ELSE 0 END AS flag_weekend,
        -- Rule 3 Flag (Window function to detect duplicates)
        CASE WHEN COUNT(*) OVER(PARTITION BY t.Date, t.Vendor, t.Amount) > 1 THEN 1 ELSE 0 END AS flag_duplicate
    FROM transactions t
)
SELECT
    Transaction_ID,
    Date,
    Department,
    Employee_ID,
    Vendor,
    Amount,
    Payment_Method,
    (flag_high_value + flag_weekend + flag_duplicate) AS risk_score,
    TRIM(
        (CASE WHEN flag_high_value = 1 THEN 'High Value; ' ELSE '' END) ||
        (CASE WHEN flag_weekend = 1 THEN 'Weekend; ' ELSE '' END) ||
        (CASE WHEN flag_duplicate = 1 THEN 'Possible Duplicate; ' ELSE '' END),
        '; '
    ) AS exception_reasons
FROM ScoredTransactions
WHERE (flag_high_value + flag_weekend + flag_duplicate) > 0
ORDER BY risk_score DESC, Amount DESC;


-- ------------------------------------------------------------------------------
-- 6. AUDIT SUMMARY BY VENDOR: Top 10 Vendors by Flagged Exposure
-- Audit Purpose: Identifies vendor relationships exhibiting recurring anomalies
--                for targeted vendor audits and contract compliance review.
-- ------------------------------------------------------------------------------
SELECT
    Vendor,
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN Amount > 50000 OR strftime('%w', Date) IN ('0', '6') THEN 1 ELSE 0 END) AS flagged_count,
    ROUND(SUM(Amount), 2) AS total_spend,
    ROUND(SUM(CASE WHEN Amount > 50000 OR strftime('%w', Date) IN ('0', '6') THEN Amount ELSE 0 END), 2) AS flagged_spend
FROM transactions
GROUP BY Vendor
ORDER BY flagged_spend DESC
LIMIT 10;
