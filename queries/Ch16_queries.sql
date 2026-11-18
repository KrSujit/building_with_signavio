-- Building with SAP Signavio, Chapter 16: every query printed in the chapter, in order.
-- Chapters 13-14: SQL (Trino dialect, Process Intelligence transformations). Chapters 15-16: SiGNAL.
-- Source: github.com/KrSujit/building_with_signavio

-- ---------------------------------------------------------------
-- Q01  Section: Your First Queries
-- Helena's first question was the simplest: how many orders, and how much money?
-- ---------------------------------------------------------------
SELECT COUNT(case_id)        AS orders,
       SUM(order_value_eur)  AS value_eur
FROM THIS_PROCESS

-- ---------------------------------------------------------------
-- Q02  Section: Your First Queries
-- Then the same by sales organization:
-- ---------------------------------------------------------------
SELECT sales_organization,
       COUNT(case_id)        AS orders,
       SUM(order_value_eur)  AS value_eur
FROM THIS_PROCESS
ORDER BY orders DESC

-- ---------------------------------------------------------------
-- Q03  Section: Where Attributes Come From
-- Here are the two scripts of Velora's CSV pipeline from Chapter 13, slightly shortened:
-- ---------------------------------------------------------------
-- Event collector: events with three event attributes
SELECT e.case_id AS c_caseid,
       e.activity AS c_eventname,
       CAST(date_parse(e."timestamp", '%Y-%m-%d %H:%i:%s') AS timestamp) AS c_time,
       e.plant    AS plant,          -- event attribute
       e."user"   AS user_code,      -- event attribute
       e.system   AS it_system       -- event attribute
FROM o2c_events AS e
WHERE e.case_id IS NOT NULL

-- ---------------------------------------------------------------
-- Q04  Section: Where Attributes Come From
-- ---------------------------------------------------------------
-- Case attributes: one row per case
SELECT c.case_id                      AS c_caseid,
       c.customer_segment,
       c.sales_org                    AS sales_organization,
       c.plant                        AS delivering_plant,   -- renamed: plant is an event attribute
       CAST(c.order_value_eur AS double) AS order_value_eur,
       c.payment_terms
FROM o2c_cases AS c

-- ---------------------------------------------------------------
-- Q05  Section: Worked Case: Adding One of Each
-- Step 1: Add the event attribute to the event collector. Open the pipeline O2C – Velora (daily) → Business Objects → the event collector, and add one column:
-- ---------------------------------------------------------------
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

-- ---------------------------------------------------------------
-- Q06  Section: Worked Case: Adding One of Each
-- Step 2: Add the case attribute to the case attribute SQL.
-- ---------------------------------------------------------------
SELECT c.case_id AS c_caseid,
       c.customer_segment,
       c.sales_org AS sales_organization,
       c.plant     AS delivering_plant,
       CAST(c.order_value_eur AS double) AS order_value_eur,
       c.payment_terms,
       CASE WHEN CAST(c.order_value_eur AS double) <  5000 THEN '1 Small (< €5k)'
            WHEN CAST(c.order_value_eur AS double) < 25000 THEN '2 Medium (€5k–25k)'
            ELSE '3 Large (≥ €25k)'
       END AS order_size_class                 -- new case attribute
FROM o2c_cases AS c

-- ---------------------------------------------------------------
-- Q07  Section: Worked Case: Adding One of Each
-- Step 4: Query them. A case attribute is read directly:
-- ---------------------------------------------------------------
SELECT order_size_class,
       COUNT(case_id) AS orders,
       AVG(CASE WHEN (SELECT BOOL_OR(event_name = 'Block for credit')) THEN 1 ELSE 0 END) * 100
           AS blocked_pct
FROM THIS_PROCESS
ORDER BY order_size_class

-- ---------------------------------------------------------------
-- Q08  Section: Worked Case: Adding One of Each
-- An event attribute needs an event level. Across all cases, flatten the process:
-- ---------------------------------------------------------------
SELECT department,
       COUNT(1) AS events
FROM FLATTEN(THIS_PROCESS)
ORDER BY events DESC

-- ---------------------------------------------------------------
-- Q09  Section: Worked Case: Adding One of Each
-- Inside a case, use a subquery. This query counts, for every order, how many departments touched it, and averages that by segment:
-- ---------------------------------------------------------------
SELECT customer_segment,
       AVG((SELECT COUNT(DISTINCT department))) AS departments_per_order
FROM THIS_PROCESS

-- ---------------------------------------------------------------
-- Q10  Section: Event Attributes in Case Questions
-- The most useful pattern combines both levels: a case question about event attributes. Tomas wanted to know how many Brno orders had a credit release without a d
-- ---------------------------------------------------------------
SELECT sales_organization,
       COUNT(case_id) AS orders
FROM THIS_PROCESS
WHERE event_name MATCHES ('Release credit block')
  AND NOT event_name MATCHES ('Review blocked order')

-- ---------------------------------------------------------------
-- Q11  Section: 16.4 Aggregations and Grouping
-- Some examples with Velora's results:
-- ---------------------------------------------------------------
-- Customers and orders by segment
SELECT customer_segment,
       COUNT(DISTINCT customer_id) AS customers,
       COUNT(case_id)              AS orders
FROM THIS_PROCESS
ORDER BY orders DESC

-- ---------------------------------------------------------------
-- Q12  Section: 16.4 Aggregations and Grouping
-- Table 16.10: Customers and orders by segment
-- ---------------------------------------------------------------
-- Average events and users per order
SELECT AVG((SELECT COUNT(1)))                 AS events_per_order,
       AVG((SELECT COUNT(DISTINCT user_code))) AS users_per_order
FROM THIS_PROCESS

-- ---------------------------------------------------------------
-- Q13  Section: 16.4 Aggregations and Grouping
-- Result: 11.4 events and 5.5 users per order on average.
-- ---------------------------------------------------------------
-- Number of variants
SELECT COUNT(DISTINCT event_name) AS variants
FROM THIS_PROCESS

-- ---------------------------------------------------------------
-- Q14  Section: Rounding, IF, and CASE
-- ROUND(AVG(order_value_eur), 0) rounds; IF(condition, then, else) and CASE WHEN … THEN … ELSE … END create categories:
-- ---------------------------------------------------------------
SELECT IF(drop_shipment = 'yes', 'Drop shipment', 'From stock') AS fulfilment,
       COUNT(case_id) AS orders
FROM THIS_PROCESS

-- ---------------------------------------------------------------
-- Q15  Section: Cycle Time
-- Cycle time per case comes from the case's own events:
-- ---------------------------------------------------------------
SELECT sales_organization,
       AVG((SELECT LAST(end_time) - FIRST(end_time))) / 86400000 AS avg_cycle_days
FROM THIS_PROCESS
ORDER BY avg_cycle_days DESC

-- ---------------------------------------------------------------
-- Q16  Section: Between Two Steps
-- For the time between two specific steps, pick each step's time with FIRST or LAST and a FILTER:
-- ---------------------------------------------------------------
-- Median days from order to first invoice
SELECT sales_organization,
       MEDIAN(((SELECT FIRST(end_time) FILTER (WHERE event_name = 'Create invoice'))
             - (SELECT FIRST(end_time))) / 86400000) AS order_to_invoice_days
FROM THIS_PROCESS

-- ---------------------------------------------------------------
-- Q17  Section: Between Two Steps
-- The goods-issue-to-invoice time shows where Brno loses them:
-- ---------------------------------------------------------------
SELECT sales_organization,
       MEDIAN(((SELECT FIRST(end_time) FILTER (WHERE event_name = 'Create invoice'))
             - (SELECT LAST(end_time)  FILTER (WHERE event_name = 'Post goods issue'))) / 86400000)
           AS gi_to_invoice_days
FROM THIS_PROCESS
WHERE drop_shipment = 'no'

-- ---------------------------------------------------------------
-- Q18  Section: Thresholds with DURATION
-- Compare a duration with a threshold using DURATION:
-- ---------------------------------------------------------------
SELECT COUNT(case_id) FILTER (WHERE
           (SELECT FIRST(end_time) FILTER (WHERE event_name = 'Release credit block'))
         - (SELECT FIRST(end_time) FILTER (WHERE event_name = 'Block for credit'))
         > DURATION '2days') AS released_after_2_days,
       COUNT(case_id) FILTER (WHERE
           (SELECT BOOL_OR(event_name = 'Block for credit'))) AS blocked_orders
FROM THIS_PROCESS

-- ---------------------------------------------------------------
-- Q19  Section: Percentiles
-- Averages hide the tail. The 90th percentile shows how long the slowest tenth takes:
-- ---------------------------------------------------------------
SELECT sales_organization,
       PERCENTILE_CONT(0.9) WITHIN GROUP (
           ORDER BY ((SELECT LAST(end_time) - FIRST(end_time)) / 86400000)) AS p90_cycle_days
FROM THIS_PROCESS

-- ---------------------------------------------------------------
-- Q20  Section: Trends with DATE_TRUNC
-- DATE_TRUNC('month', …) (or 'week', 'quarter', 'year') cuts a timestamp to the start of its period, which makes it a grouping column:
-- ---------------------------------------------------------------
SELECT DATE_TRUNC('quarter', (SELECT FIRST(end_time))) AS quarter,
       COUNT(case_id) AS orders
FROM THIS_PROCESS
ORDER BY quarter

-- ---------------------------------------------------------------
-- Q21  Section: Date Parts and Date Filters
-- DATE_PART extracts a part of a timestamp: 'hour', 'day', 'month', 'year', 'day_of_week' (1 is Monday). Filter by date with a DATE literal:
-- ---------------------------------------------------------------
-- On which weekday does Brno invoice?
SELECT DATE_PART('day_of_week', end_time) AS weekday,
       COUNT(1) AS invoices
FROM FLATTEN(THIS_PROCESS)
WHERE event_name = 'Create invoice' AND plant = 'CZ10'
ORDER BY weekday

-- ---------------------------------------------------------------
-- Q22  Section: Date Parts and Date Filters
-- Ninety-four percent of Brno's invoices are created on Fridays: the weekly billing run that Chapter 15 found behind the 3.2 days. The few on other days are corre
-- ---------------------------------------------------------------
-- Orders created from April onwards
SELECT COUNT(case_id) FROM THIS_PROCESS
WHERE (SELECT FIRST(end_time)) >= DATE '2026-04-01'

-- ---------------------------------------------------------------
-- Q23  Section: WHERE Removes Cases, FILTER Restricts One Number
-- A count isn't a rate. For the credit memo rate (Velora calls it the invoice correction rate), the query needs all orders and the orders with a credit memo in th
-- ---------------------------------------------------------------
SELECT COUNT(case_id) FILTER (WHERE (SELECT BOOL_OR(event_name = 'Create credit memo')))
         * 100.0 / COUNT(case_id) AS correction_pct
FROM THIS_PROCESS

-- ---------------------------------------------------------------
-- Q24  Section: Calculated Categories
-- The question behind PD-050 (Chapter 15) was whether late price changes cause credit memos. A CASE expression on an event condition creates the two groups:
-- ---------------------------------------------------------------
SELECT CASE WHEN (SELECT BOOL_OR(event_name = 'Change price after credit release'))
            THEN 'Late price change' ELSE 'No late price change' END AS order_group,
       COUNT(case_id) AS orders,
       COUNT(case_id) FILTER (WHERE (SELECT BOOL_OR(event_name = 'Create credit memo')))
         * 100.0 / COUNT(case_id) AS credit_memo_pct
FROM THIS_PROCESS

-- ---------------------------------------------------------------
-- Q25  Section: Which Attribute Drives It?
-- The same pattern tests one attribute after the other. Helena's size hypothesis failed (Table 16.6). The sales organization doesn't:
-- ---------------------------------------------------------------
SELECT sales_organization,
       AVG(CASE WHEN (SELECT BOOL_OR(event_name = 'Block for credit')) THEN 1 ELSE 0 END) * 100
           AS blocked_pct
FROM THIS_PROCESS

-- ---------------------------------------------------------------
-- Q26  Section: Which Attribute Drives It?
-- And payment terms explain dunning:
-- ---------------------------------------------------------------
SELECT payment_terms,
       COUNT(case_id) AS orders,
       AVG(CASE WHEN (SELECT BOOL_OR(event_name = 'Send dunning notice')) THEN 1 ELSE 0 END) * 100
           AS dunned_pct
FROM THIS_PROCESS
ORDER BY payment_terms

-- ---------------------------------------------------------------
-- Q27  Section: Lists and Patterns: IN and LIKE
-- ### Lists and Patterns: IN and LIKE
-- ---------------------------------------------------------------
SELECT COUNT(case_id) FROM THIS_PROCESS
WHERE payment_terms IN ('NT45', 'NT60')
  AND customer_name LIKE '%GmbH'

-- ---------------------------------------------------------------
-- Q28  Section: 16.7 Sequences: MATCHES and BEHAVIOR
-- A whole variant is just a long pattern. The share of the happy path:
-- ---------------------------------------------------------------
SELECT COUNT(case_id) FILTER (WHERE event_name MATCHES (
           ^ 'Create sales order' -> 'Send order confirmation' -> 'Create delivery' -> 'Pick goods'
           -> 'Post goods issue' -> 'Create invoice' -> 'Send invoice'
           -> 'Receive incoming payment' -> 'Clear payment' $))
       * 100.0 / COUNT(case_id) AS happy_path_pct
FROM THIS_PROCESS

-- ---------------------------------------------------------------
-- Q29  Section: Conditions on Steps: BEHAVIOR
-- MATCHES compares event names. BEHAVIOR lets you name steps with any condition, including event attributes, and then match the sequence of those named steps:
-- ---------------------------------------------------------------
SELECT COUNT(case_id)
FROM THIS_PROCESS
WHERE BEHAVIOR
        (event_name = 'Block for credit')                      AS blocked,
        (event_name = 'Release credit block' AND plant = 'IN10') AS released_in_pune
      MATCHES (blocked -> released_in_pune)

-- ---------------------------------------------------------------
-- Q30  Section: 16.8 Event-Level Analysis with FLATTEN
-- Some questions are about events, not cases: how many events per activity, at which hour, by which department. FLATTEN(THIS_PROCESS) turns the process into one r
-- ---------------------------------------------------------------
SELECT event_name, COUNT(1) AS events
FROM FLATTEN(THIS_PROCESS)
ORDER BY events DESC
LIMIT 5

-- ---------------------------------------------------------------
-- Q31  Section: 16.8 Event-Level Analysis with FLATTEN
-- Result: Create delivery and Post goods issue 55,066 each, Pick goods 54,505, Create invoice 43,837, Create sales order 41,300.
-- ---------------------------------------------------------------
-- When are orders entered?
SELECT DATE_PART('hour', end_time) AS hour, COUNT(1) AS orders
FROM FLATTEN(THIS_PROCESS)
WHERE event_name = 'Create sales order'
ORDER BY hour

-- ---------------------------------------------------------------
-- Q32  Section: Waiting Time Before Each Step: Window Functions
-- Katrin's question "how long does an order wait before each step?" needs the time since the previous event. That's a window function: LAG(end_time) returns the p
-- ---------------------------------------------------------------
SELECT event_name,
       AVG(wait) / 86400000 AS avg_wait_days
FROM (
    SELECT event_name,
           end_time - LAG(end_time) OVER (PARTITION BY case_id ORDER BY end_time) AS wait
    FROM FLATTEN(THIS_PROCESS)
) AS t
ORDER BY avg_wait_days DESC
LIMIT 5

-- ---------------------------------------------------------------
-- Q33  Section: 16.9 Subqueries and Multi-Step Questions
-- When a question has two steps ("first count orders per customer, then count the customers with many"), put the first step in a subquery in FROM:
-- ---------------------------------------------------------------
SELECT COUNT(1) AS frequent_customers
FROM (
    SELECT customer_name, COUNT(case_id) AS orders
    FROM THIS_PROCESS
) AS t
WHERE orders > 60

-- ---------------------------------------------------------------
-- Q34  Section: 16.9 Subqueries and Multi-Step Questions
-- Rework is a subquery question too. How many orders were invoiced more than once?
-- ---------------------------------------------------------------
SELECT COUNT(case_id)
FROM THIS_PROCESS
WHERE (SELECT COUNT(1) FILTER (WHERE event_name = 'Create invoice')) > 1

-- ---------------------------------------------------------------
-- Q35  Section: The Price of a Correction
-- The last query of Malik's list combined everything: a calculated category, a sequence condition, and a duration between steps.
-- ---------------------------------------------------------------
SELECT CASE WHEN (SELECT BOOL_OR(event_name = 'Create credit memo'))
            THEN 'With credit memo' ELSE 'Clean invoice' END AS invoice,
       COUNT(case_id) AS orders,
       MEDIAN(((SELECT LAST(end_time)  FILTER (WHERE event_name = 'Clear payment'))
             - (SELECT FIRST(end_time) FILTER (WHERE event_name = 'Create invoice'))) / 86400000)
           AS median_invoice_to_payment_days
FROM THIS_PROCESS
WHERE event_name MATCHES ('Clear payment')

-- ---------------------------------------------------------------
-- Q36  Section: 16.11 Metrics: Queries Everyone Can Reuse
-- A metric contains only the expression, not the whole query. The correction rate as a metric is:
-- ---------------------------------------------------------------
COUNT(case_id) FILTER (WHERE (SELECT BOOL_OR(event_name = 'Create credit memo')))
  * 100.0 / COUNT(case_id)

-- ---------------------------------------------------------------
-- Q37  Section: Library Metrics and Custom Metrics
-- The metric then uses the reference name. SiGNAL compares durations with duration literals such as DURATION '1day', so the number from the variable is multiplied
-- ---------------------------------------------------------------
-- Metric "Goods issue to invoice (orders over target)", aggregation: over cases
100.0 * COUNT(case_id) FILTER (
    WHERE (SELECT FIRST(end_time) WHERE event_name = 'Create invoice')
        - (SELECT LAST(end_time)  WHERE event_name = 'Post goods issue')
      > ${Variable.billing_target_days} * DURATION '1day'
  ) / COUNT(case_id)

-- ---------------------------------------------------------------
-- Q38  Section: Library Metrics and Custom Metrics
-- A simpler first metric needs no variable at all: the average time from goods issue to invoice.
-- ---------------------------------------------------------------
-- Metric "Goods issue to invoice (days)", aggregation: over cases
AVG(
  (SELECT FIRST(end_time) WHERE event_name = 'Create invoice')
  - (SELECT FIRST(end_time) WHERE event_name = 'Post goods issue')
)

-- ---------------------------------------------------------------
-- Q39  Section: Library Metrics and Custom Metrics
-- Velora's collection then held these metric definitions, each tested in the metric preview against the O2C data:
-- ---------------------------------------------------------------
-- Invoice correction rate (% of orders), over cases. Result: 7.47
COUNT(case_id) FILTER (WHERE (SELECT BOOL_OR(event_name = 'Create credit memo')))
  * 100.0 / COUNT(case_id)

-- ---------------------------------------------------------------
-- Q40  Section: Library Metrics and Custom Metrics
-- ---------------------------------------------------------------
-- Late price change rate (% of orders), over cases. Result: 13.43
COUNT(case_id) FILTER (WHERE (SELECT BOOL_OR(event_name = 'Change price after credit release')))
  * 100.0 / COUNT(case_id)

-- ---------------------------------------------------------------
-- Q41  Section: Library Metrics and Custom Metrics
-- ---------------------------------------------------------------
-- Release without review (orders), over cases. Result: 2,229
COUNT(case_id) FILTER (
  WHERE (SELECT BOOL_OR(event_name = 'Release credit block'))
    AND NOT (SELECT BOOL_OR(event_name = 'Review blocked order'))
)

-- ---------------------------------------------------------------
-- Q42  Section: Library Metrics and Custom Metrics
-- To use metrics in a widget, switch the widget editor to Interactive, open More > Metrics, and drag a metric into Measures; drag an attribute from More > Attribu
-- ---------------------------------------------------------------
SELECT COUNT(CASE_ID) FILTER (WHERE (SELECT BOOL_OR(EVENT_NAME = 'Create credit memo'))) * 100 / COUNT(CASE_ID) AS "Invoice correction rate",
       COUNT(CASE_ID) FILTER (WHERE (SELECT BOOL_OR(EVENT_NAME = 'Change price after credit release'))) * 100 / COUNT(CASE_ID) AS "Late price change rate",
       "sales_organization"
FROM THIS_PROCESS
LIMIT 500

-- ---------------------------------------------------------------
-- Q43  Section: 16.12 The Same Method for Procure to Pay
-- Velora's P2P event log (Chapter 13's pipeline, extended to purchasing) uses the purchase order item as the case. With what you've learned, the query is two patt
-- ---------------------------------------------------------------
SELECT plant,
       COUNT(case_id) AS po_items,
       COUNT(case_id) FILTER (
           WHERE event_name MATCHES ('Receive invoice' ~> 'Create purchase order')
       ) * 100.0 / COUNT(case_id) AS after_the_fact_pct
FROM THIS_PROCESS
ORDER BY after_the_fact_pct DESC

-- ---------------------------------------------------------------
-- Q44  Section: 16.12 The Same Method for Procure to Pay
-- Adding the vendor category showed the pattern: after-the-fact POs concentrated in maintenance, repair, and operations (MRO) purchasing and in external services.
-- ---------------------------------------------------------------
COUNT(case_id) FILTER (WHERE
    (SELECT FIRST(end_time) FILTER (WHERE event_name = 'Create purchase order'))
  - (SELECT FIRST(end_time) FILTER (WHERE event_name = 'Receive invoice'))
  > ${atf_tolerance_days})
* 100.0 / COUNT(case_id)
