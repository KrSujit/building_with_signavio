-- =====================================================================================
-- Building with SAP Signavio – companion file S13
-- S13_Transformation_Examples.sql
-- Simplified transformation scripts for the events in Chapter 13
-- =====================================================================================
-- HOW TO USE
--   * Each script builds ONE Velora activity for the case "sales order" (PD-039), with the
--     columns case_id, activity, event_time, user_id, system. Velora's activity names are the
--     Dictionary names (PD-040).
--   * Dialect: Trino SQL, as in Process Intelligence transformations. Dates and times arrive
--     from the SAP extractor as milliseconds (Chapter 14, Section 14.5), hence
--     from_unixtime(date / 1000 + time / 1000).
--   * Script 3 (Release credit block) is printed in Section 13.4; the others follow the same
--     pattern. They are deliberately SIMPLE: one case per order, no currency conversion, no
--     cancellations, no time zone handling. Chapter 14 shows how SAP's template builds the same
--     events at item level, and the production pipeline uses the template (PD-043).
--   * Time zones: normalize every timestamp to CET in your pipeline (PD-045). The fictional
--     Velora tables are already in one time zone, so the scripts below don't convert.
--   * Try them on the fictional Velora SAP tables from chapters/Ch14/Dummy SAP Tables
--     (node make_tables.js). On those tables, each script returns exactly the count of its
--     activity in S13_O2C_EventLog.csv; the expected count is given in each header.
--   * All data is FICTIONAL (Velora Group SE).
-- =====================================================================================


-- -------------------------------------------------------------------------------------
-- 1. Create sales order                          expected on the Velora tables: 41,300
--    VBAK: one row per sales order (VBTYP = 'C'), created on ERDAT at ERZET by ERNAM.
-- -------------------------------------------------------------------------------------
SELECT
    k.vbeln                                         AS case_id,     -- sales order number
    'Create sales order'                            AS activity,
    from_unixtime(k.erdat / 1000 + k.erzet / 1000)  AS event_time,
    k.ernam                                         AS user_id,     -- pseudonymized later (PD-044)
    'SAP ECC'                                       AS system
FROM vbak k
WHERE k.vbtyp = 'C'                                 -- C = sales order
  AND k.vkorg IN ('DE01', 'CZ01');                  -- Düsseldorf and Brno (Table 13.1)


-- -------------------------------------------------------------------------------------
-- 2. Block for credit                            expected on the Velora tables: 12,109
--    Change document on the overall credit status VBUK-CMGST, new value B (blocked).
-- -------------------------------------------------------------------------------------
SELECT
    h.objectid                                      AS case_id,
    'Block for credit'                              AS activity,
    from_unixtime(h.udate / 1000 + h.utime / 1000)  AS event_time,
    h.username                                      AS user_id,     -- SYSTEM: the automatic credit check
    'SAP ECC'                                       AS system
FROM cdhdr h
JOIN cdpos p
  ON  p.objectclas = h.objectclas
  AND p.objectid   = h.objectid
  AND p.changenr   = h.changenr
WHERE h.objectclas = 'VERKBELEG'
  AND p.fname      = 'CMGST'                        -- overall credit status
  AND p.value_new  = 'B';                           -- blocked (A = check passed, D = released)


-- -------------------------------------------------------------------------------------
-- 3. Release credit block                        expected on the Velora tables: 11,561
--    As printed in Section 13.4.
-- -------------------------------------------------------------------------------------
-- Event: Release credit block
SELECT
    h.objectid                         AS case_id,     -- sales order number
    'Release credit block'             AS activity,
    from_unixtime(h.udate / 1000 + h.utime / 1000)     -- the extractor delivers dates and
                                       AS event_time,  -- times in milliseconds (Chapter 14)
    h.username                         AS user_id,     -- pseudonymized later
    'SAP ECC'                          AS system
FROM cdhdr h
JOIN cdpos p
  ON  p.objectclas = h.objectclas
  AND p.objectid   = h.objectid
  AND p.changenr   = h.changenr
WHERE h.objectclas = 'VERKBELEG'
  AND p.fname      = 'CMGST'          -- overall credit status
  AND p.value_new = 'D'               -- released (A = check passed, B = blocked)
;


-- -------------------------------------------------------------------------------------
-- 4. Create delivery                             expected on the Velora tables: 55,066
--    LIKP: delivery header; LIPS-VGBEL links the delivery items to the sales order.
--    An order with two deliveries gets two events.
-- -------------------------------------------------------------------------------------
SELECT DISTINCT
    i.vgbel                                         AS case_id,     -- reference document = sales order
    'Create delivery'                               AS activity,
    from_unixtime(d.erdat / 1000 + d.erzet / 1000)  AS event_time,
    d.ernam                                         AS user_id,
    'SAP ECC'                                       AS system
FROM likp d
JOIN lips i
  ON  i.mandt = d.mandt
  AND i.vbeln = d.vbeln
WHERE d.vbtyp = 'J'                                 -- J = delivery
  AND i.vgtyp = 'C';                                -- the reference is a sales order


-- -------------------------------------------------------------------------------------
-- 5. Post goods issue                            expected on the Velora tables: 55,066
--    The time of the goods issue is the creation time of the material document in the
--    document flow VBFA (delivery J -> goods movement R). VBFA-VBELV is the delivery,
--    so the delivery items lead back to the sales order.
-- -------------------------------------------------------------------------------------
SELECT DISTINCT
    i.vgbel                                         AS case_id,
    'Post goods issue'                              AS activity,
    from_unixtime(f.erdat / 1000 + f.erzet / 1000)  AS event_time,
    d.ernam                                         AS user_id,     -- simplified: the delivery's creator
    'SAP ECC'                                       AS system
FROM vbfa f
JOIN likp d
  ON  d.mandt = f.mandt
  AND d.vbeln = f.vbelv
JOIN lips i
  ON  i.mandt = d.mandt
  AND i.vbeln = d.vbeln
WHERE f.vbtyp_v = 'J'                               -- preceding document: delivery
  AND f.vbtyp_n = 'R'                               -- subsequent document: goods movement
  AND i.vgtyp   = 'C';


-- -------------------------------------------------------------------------------------
-- 6. Create invoice                              expected on the Velora tables: 43,837
--    VBRK: billing header (VBTYP M = invoice, O = credit memo); VBRP-AUBEL is the sales
--    order. Orders with a credit memo were invoiced twice (Chapter 14, Section 14.10).
-- -------------------------------------------------------------------------------------
SELECT DISTINCT
    p.aubel                                         AS case_id,
    'Create invoice'                                AS activity,
    from_unixtime(b.erdat / 1000 + b.erzet / 1000)  AS event_time,
    b.ernam                                         AS user_id,
    'SAP ECC'                                       AS system
FROM vbrk b
JOIN vbrp p
  ON  p.mandt = b.mandt
  AND p.vbeln = b.vbeln
WHERE b.vbtyp = 'M'                                 -- M = invoice
  AND (b.fksto IS NULL OR b.fksto = '');            -- not cancelled (blank, not NULL, in SAP)


-- -------------------------------------------------------------------------------------
-- 7. Clear payment                               expected on the Velora tables: 37,891
--    The invoice's customer line in BSEG (KOART D, posting key 01) carries the clearing
--    document in AUGBL and its fiscal year in AUGGJ. Velora counts only clearings by a
--    customer payment (document type DZ), not clearings against a credit memo (PD-048).
--    Join the clearing document on AUGGJ, not on the invoice's year: payments that cross
--    the year end are the reason (Chapter 14, Section 14.8).
-- -------------------------------------------------------------------------------------
SELECT DISTINCT
    p.aubel                                         AS case_id,
    'Clear payment'                                 AS activity,
    from_unixtime(c.cpudt / 1000 + c.cputm / 1000)  AS event_time,
    c.usnam                                         AS user_id,
    'SAP ECC'                                       AS system
FROM bkpf a                                         -- accounting document of the invoice
JOIN bseg s
  ON  s.mandt = a.mandt
  AND s.bukrs = a.bukrs
  AND s.belnr = a.belnr
  AND s.gjahr = a.gjahr
JOIN bkpf c                                         -- the clearing document
  ON  c.mandt = s.mandt
  AND c.bukrs = s.bukrs
  AND c.belnr = s.augbl
  AND c.gjahr = s.auggj
JOIN vbrp p
  ON  p.mandt = a.mandt
  AND p.vbeln = a.awkey                             -- AWKEY = billing document number
WHERE a.awtyp = 'VBRK'
  AND s.koart = 'D'                                 -- customer line
  AND s.bschl = '01'                                -- invoice
  AND c.blart = 'DZ';                               -- customer payment


-- -------------------------------------------------------------------------------------
-- 8. Change price after credit release           expected on the Velora tables: 5,547
--    A change of the net price VBAP-NETPR after the order's FIRST credit check, passed or
--    blocked (rule PD-047, agreed with Katrin Vogel, Chapter 14). All other price changes
--    stay 'Change price' (4,568 on the Velora tables; 10,115 price changes in total).
--    This is the rule Velora's event log uses. Variant 8b below is the literal reading of
--    the Build exercise in Section 13.8, Step 3.2 ("after the last Release credit block").
-- -------------------------------------------------------------------------------------
WITH first_check AS (
    SELECT h.objectid AS case_id,
           MIN(from_unixtime(h.udate / 1000 + h.utime / 1000)) AS first_credit_check
    FROM cdhdr h
    JOIN cdpos p
      ON  p.objectclas = h.objectclas AND p.objectid = h.objectid AND p.changenr = h.changenr
    WHERE h.objectclas = 'VERKBELEG' AND p.fname = 'CMGST'
      AND p.value_new IN ('A', 'B')                 -- check passed or blocked
    GROUP BY h.objectid
),
price_changes AS (
    SELECT DISTINCT
        h.objectid                                      AS case_id,
        from_unixtime(h.udate / 1000 + h.utime / 1000)  AS event_time,
        h.username                                      AS user_id
    FROM cdhdr h
    JOIN cdpos p
      ON  p.objectclas = h.objectclas AND p.objectid = h.objectid AND p.changenr = h.changenr
    WHERE h.objectclas = 'VERKBELEG'
      AND p.tabname    = 'VBAP'
      AND p.fname      = 'NETPR'                    -- net price of the item (old values need SAP Note 2246160)
)
SELECT
    c.case_id,
    'Change price after credit release'             AS activity,
    c.event_time,
    c.user_id,
    'SAP ECC'                                       AS system
FROM price_changes c
JOIN first_check f
  ON f.case_id = c.case_id
WHERE c.event_time > f.first_credit_check;


-- -------------------------------------------------------------------------------------
-- 8b. Variant: price change after the LAST 'Release credit block'
--     expected on the Velora tables: 1,477 (a stricter question: "changed after the
--     analyst released it"). Use it to see how much the definition matters.
-- -------------------------------------------------------------------------------------
WITH releases AS (
    SELECT h.objectid AS case_id,
           MAX(from_unixtime(h.udate / 1000 + h.utime / 1000)) AS last_release
    FROM cdhdr h
    JOIN cdpos p
      ON  p.objectclas = h.objectclas AND p.objectid = h.objectid AND p.changenr = h.changenr
    WHERE h.objectclas = 'VERKBELEG' AND p.fname = 'CMGST' AND p.value_new = 'D'
    GROUP BY h.objectid
),
price_changes AS (
    SELECT DISTINCT
        h.objectid                                      AS case_id,
        from_unixtime(h.udate / 1000 + h.utime / 1000)  AS event_time,
        h.username                                      AS user_id
    FROM cdhdr h
    JOIN cdpos p
      ON  p.objectclas = h.objectclas AND p.objectid = h.objectid AND p.changenr = h.changenr
    WHERE h.objectclas = 'VERKBELEG' AND p.tabname = 'VBAP' AND p.fname = 'NETPR'
)
SELECT
    c.case_id,
    'Change price after last release (variant)'     AS activity,
    c.event_time,
    c.user_id,
    'SAP ECC'                                       AS system
FROM price_changes c
JOIN releases r
  ON r.case_id = c.case_id
WHERE c.event_time > r.last_release;


-- -------------------------------------------------------------------------------------
-- 9. Case attribute: Case status (open or complete)    expected: 37,891 complete, 3,409 open
--    (Section 13.1, PD-045b.) A case is complete when it has a 'Clear payment' event.
--    Run on the event log the scripts above produce (here called eventlog).
-- -------------------------------------------------------------------------------------
SELECT
    case_id,
    CASE WHEN COUNT_IF(activity = 'Clear payment') > 0 THEN 'complete' ELSE 'open' END AS case_status
FROM eventlog
GROUP BY case_id;


-- -------------------------------------------------------------------------------------
-- 10. Load checks (Section 13.6, PD-045): run after every load; alert when out of range.
-- -------------------------------------------------------------------------------------
-- 10a. New cases today against the average of the previous seven days
SELECT
    COUNT_IF(CAST(first_event AS DATE) = current_date)                              AS new_cases_today,
    COUNT_IF(CAST(first_event AS DATE) BETWEEN current_date - INTERVAL '7' DAY
                                           AND current_date - INTERVAL '1' DAY) / 7.0 AS avg_new_cases_prev_7_days
FROM (SELECT case_id, MIN(event_time) AS first_event FROM eventlog GROUP BY case_id) t;

-- 10b. Latest event timestamp against the load time (should be less than one day old)
SELECT MAX(event_time) AS latest_event, current_timestamp AS load_time FROM eventlog;

-- 10c. Share of cases without a 'Create sales order' event (should be 0%)
SELECT
    ROUND(100.0 * COUNT_IF(has_create = 0) / COUNT(*), 2) AS pct_cases_without_create_sales_order
FROM (SELECT case_id, COUNT_IF(activity = 'Create sales order') AS has_create
      FROM eventlog GROUP BY case_id) t;
