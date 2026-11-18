-- =====================================================================================
-- Building with SAP Signavio – companion file S16
-- S16_Pipeline_Attributes.sql
-- The event collector and case attribute SQL with department and order_size_class
-- (Chapter 16, Section 16.3, Worked Case: Adding One of Each)
-- =====================================================================================
-- HOW TO USE
--   * Pipeline: O2C – Velora (daily), built from the CSV files in data/ (manual upload):
--       o2c_events = S13_O2C_EventLog.csv       (unzip data/S13_O2C_EventLog.zip)
--       o2c_cases  = S13_O2C_CaseAttributes.csv (unzip data/S13_O2C_CaseAttributes.zip)
--   * Paste script 1 into the event collector and script 2 into the case attribute collector
--     (Data Management > pipeline > Business Objects), use Preview, then run T&L.
--   * Script 1 is exactly the SQL printed in Step 1 of the worked case.
--   * Script 2 is the SQL printed in Step 2 PLUS four columns of the CSV that the chapter's
--     printed version leaves out ("slightly shortened", Section 16.3): customer_id,
--     customer_name, order_lines, and drop_shipment. Later queries in Chapter 16 use
--     customer_name and drop_shipment, so keep them. They are marked "-- added".
--   * All data is FICTIONAL (Velora Group SE).
-- =====================================================================================

-- 1. Event collector: events with four event attributes (department is new)
SELECT e.case_id AS c_caseid,
       e.activity AS c_eventname,
       CAST(date_parse(e."timestamp", '%Y-%m-%d %H:%i:%s') AS timestamp) AS c_time,
       e.plant    AS plant,
       e."user"   AS user_code,
       e.system   AS it_system,
       CASE substr(e."user", 1, 6)
            WHEN 'User_1' THEN 'Order Desk Düsseldorf'
            WHEN 'User_2' THEN 'Order Desk Brno'
            WHEN 'User_3' THEN 'Credit Management Pune'
            WHEN 'User_4' THEN 'Accounts Receivable'
            WHEN 'User_5' THEN 'Billing'
            ELSE 'System'
       END        AS department                -- new event attribute
FROM o2c_events AS e
WHERE e.case_id IS NOT NULL
;

-- 2. Case attributes: one row per case (order_size_class is new)
SELECT c.case_id AS c_caseid,
       c.customer_id,                                       -- added
       replace(c.customer_name, '"', '') AS customer_name,  -- added
       c.customer_segment,
       c.sales_org AS sales_organization,
       c.plant     AS delivering_plant,
       CAST(c.order_value_eur AS double) AS order_value_eur,
       c.payment_terms,
       CAST(c.order_lines AS integer) AS order_lines,       -- added
       c.drop_shipment,                                     -- added
       CASE WHEN CAST(c.order_value_eur AS double) <  5000 THEN '1 Small (< €5k)'
            WHEN CAST(c.order_value_eur AS double) < 25000 THEN '2 Medium (€5k–25k)'
            ELSE '3 Large (≥ €25k)'
       END AS order_size_class                 -- new case attribute
FROM o2c_cases AS c
;
