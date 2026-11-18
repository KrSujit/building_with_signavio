-- Building with SAP Signavio, Chapter 15: every query printed in the chapter, in order.
-- Chapters 13-14: SQL (Trino dialect, Process Intelligence transformations). Chapters 15-16: SiGNAL.
-- Source: github.com/KrSujit/building_with_signavio

-- ---------------------------------------------------------------
-- Q01  Section: 15.3 The Overview Chapter
-- The four Value widgets and the trend widget use these SiGNAL queries. Paste each into a widget's SIGNAL editor (Create Widget > Charts and Tables > SIGNAL), cho
-- ---------------------------------------------------------------
-- Value widget "Orders"
SELECT COUNT(case_id) AS "Orders"
FROM THIS_PROCESS

-- ---------------------------------------------------------------
-- Q02  Section: 15.3 The Overview Chapter
-- ---------------------------------------------------------------
-- Value widget "Avg order to invoice"
SELECT
  AVG((SELECT FIRST(end_time) WHERE event_name = 'Create invoice')
    - (SELECT FIRST(end_time) WHERE event_name = 'Create sales order')) AS "Avg order to invoice"
FROM THIS_PROCESS

-- ---------------------------------------------------------------
-- Q03  Section: 15.3 The Overview Chapter
-- ---------------------------------------------------------------
-- Value widget "Avg invoice to payment"
SELECT
  AVG((SELECT FIRST(end_time) WHERE event_name = 'Clear payment')
    - (SELECT FIRST(end_time) WHERE event_name = 'Create invoice')) AS "Avg invoice to payment"
FROM THIS_PROCESS

-- ---------------------------------------------------------------
-- Q04  Section: 15.3 The Overview Chapter
-- ---------------------------------------------------------------
-- Value widget "Orders with a credit memo (%)"
SELECT
  100.0 * COUNT(case_id) FILTER (WHERE event_name MATCHES ('Create credit memo'))
  / COUNT(case_id) AS "Share with credit memo (%)"
FROM THIS_PROCESS

-- ---------------------------------------------------------------
-- Q05  Section: 15.3 The Overview Chapter
-- ---------------------------------------------------------------
-- Line chart "Invoice to payment by month and sales organization"
SELECT
  DATE_TRUNC('month', (SELECT FIRST(end_time) WHERE event_name = 'Create invoice')) AS "Invoice month",
  sales_organization AS "Sales organization",
  AVG((SELECT FIRST(end_time) WHERE event_name = 'Clear payment')
    - (SELECT FIRST(end_time) WHERE event_name = 'Create invoice')) AS "Avg invoice to payment"
FROM THIS_PROCESS
WHERE (SELECT FIRST(end_time) WHERE event_name = 'Clear payment') IS NOT NULL
GROUP BY 1, 2
ORDER BY 1

-- ---------------------------------------------------------------
-- Q06  Section: H2 and H3: Price Changes and Corrections
-- 4. Save the dashboard.
-- ---------------------------------------------------------------
-- Table widget "Distribution of invoice to payment: clean vs with credit memo"
SELECT
  event_name MATCHES ('Create credit memo') AS "Has credit memo",
  MIN(((SELECT FIRST(end_time) WHERE event_name = 'Clear payment')
     - (SELECT FIRST(end_time) WHERE event_name = 'Create invoice'))) AS "Min",
  PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY ((SELECT FIRST(end_time) WHERE event_name = 'Clear payment')
     - (SELECT FIRST(end_time) WHERE event_name = 'Create invoice'))) AS "Q1",
  MEDIAN(((SELECT FIRST(end_time) WHERE event_name = 'Clear payment')
     - (SELECT FIRST(end_time) WHERE event_name = 'Create invoice'))) AS "Median",
  PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY ((SELECT FIRST(end_time) WHERE event_name = 'Clear payment')
     - (SELECT FIRST(end_time) WHERE event_name = 'Create invoice'))) AS "Q3",
  MAX(((SELECT FIRST(end_time) WHERE event_name = 'Clear payment')
     - (SELECT FIRST(end_time) WHERE event_name = 'Create invoice'))) AS "Max"
FROM THIS_PROCESS
WHERE event_name MATCHES ('Create invoice' ~> 'Clear payment')
GROUP BY 1

-- ---------------------------------------------------------------
-- Q07  Section: 15.5 Comparing with the Model
-- The conformance widget shows these deviations case by case. To report them as shares, Malik wrote one SiGNAL query with a FILTER per category. The list of activ
-- ---------------------------------------------------------------
SELECT
  COUNT(case_id) AS cases,
  100.0 * COUNT(case_id) FILTER (WHERE (SELECT BOOL_OR(event_name IN (
      'Change quantity', 'Change price', 'Change price after credit release',
      'Change requested delivery date', 'Create credit memo', 'Send dunning notice'))))
    / COUNT(case_id) AS not_in_model_pct,
  100.0 * COUNT(case_id) FILTER (WHERE (SELECT BOOL_OR(event_name = 'Release credit block'))
      AND NOT (SELECT BOOL_OR(event_name = 'Review blocked order')))
    / COUNT(case_id) AS skip_review_pct,
  100.0 * COUNT(case_id) FILTER (WHERE event_name MATCHES ('Create invoice' ~> 'Post goods issue'))
    / COUNT(case_id) AS invoice_before_gi_pct
FROM THIS_PROCESS
