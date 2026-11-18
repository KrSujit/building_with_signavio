# S16 – SiGNAL Queries

*Building with SAP Signavio – companion file S16*

Every query printed in Chapter 16, in the order of the chapter, with the question it answers and the result it returned on Velora's **fictional** order-to-cash data (41,300 orders; process *O2C – Velora (daily)* built from `data/S13_O2C_EventLog.zip` and `data/S13_O2C_CaseAttributes.zip` with the pipeline SQL in `S16_Pipeline_Attributes.sql`). The P2P queries of Section 16.12 run on Velora's P2P process, which is not part of the companion data.

## How to use

1. Open a dashboard of your process, switch on **Edit**, and choose **Create Widget > Charts and Tables > SIGNAL** (or use the SiGNAL editor of a metric, Section 16.11).
2. Copy a query from a code block below and run it. The text under *Question* explains what it answers; *Result in the book* is what it returned on the Velora data.
3. Metric definitions (blocks that start with an aggregation instead of SELECT) go into the metric editor, not into a widget. Variables such as `${Variable.billing_target_days}` must exist first (see `S16_Metrics_Export.json`).
4. If your numbers differ, check first that your process uses the case and event attributes from `S16_Pipeline_Attributes.sql`, and that you count cases, not events.

## Q01 – 16.2 How SiGNAL Sees a Process › Your First Queries

**Question:** Helena's first question was the simplest: how many orders, and how much money?

```sql
SELECT COUNT(case_id)        AS orders,
       SUM(order_value_eur)  AS value_eur
FROM THIS_PROCESS
```

**Result in the book:** 41,300 orders worth €755.3 million.

## Q02 – 16.2 How SiGNAL Sees a Process › Your First Queries

**Question:** Then the same by sales organization:

```sql
SELECT sales_organization,
       COUNT(case_id)        AS orders,
       SUM(order_value_eur)  AS value_eur
FROM THIS_PROCESS
ORDER BY orders DESC
```

| sales_organization | orders | value_eur |
|---|---|---|
| DE01 | 23,414 | 428,455,431 |
| CZ01 | 17,886 | 326,817,224 |

*Table 16.4: Orders and value by sales organization*

## Q03 – 16.3 Case Attributes and Event Attributes › Where Attributes Come From

**Question:** Here are the two scripts of Velora's CSV pipeline from Chapter 13, slightly shortened:

```sql
-- Event collector: events with three event attributes
SELECT e.case_id AS c_caseid,
       e.activity AS c_eventname,
       CAST(date_parse(e."timestamp", '%Y-%m-%d %H:%i:%s') AS timestamp) AS c_time,
       e.plant    AS plant,          -- event attribute
       e."user"   AS user_code,      -- event attribute
       e.system   AS it_system       -- event attribute
FROM o2c_events AS e
WHERE e.case_id IS NOT NULL
```

## Q04 – 16.3 Case Attributes and Event Attributes › Where Attributes Come From

```sql
-- Case attributes: one row per case
SELECT c.case_id                      AS c_caseid,
       c.customer_segment,
       c.sales_org                    AS sales_organization,
       c.plant                        AS delivering_plant,   -- renamed: plant is an event attribute
       CAST(c.order_value_eur AS double) AS order_value_eur,
       c.payment_terms
FROM o2c_cases AS c
```

## Q05 – 16.3 Case Attributes and Event Attributes › Worked Case: Adding One of Each

**Question:** **Step 1: Add the event attribute to the event collector.** Open the pipeline *O2C – Velora (daily)* → *Business Objects* → the event collector, and add one column:

```sql
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
```

## Q06 – 16.3 Case Attributes and Event Attributes › Worked Case: Adding One of Each

**Question:** **Step 2: Add the case attribute to the case attribute SQL.**

```sql
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
```

## Q07 – 16.3 Case Attributes and Event Attributes › Worked Case: Adding One of Each

**Question:** **Step 4: Query them.** A case attribute is read directly:

```sql
SELECT order_size_class,
       COUNT(case_id) AS orders,
       AVG(CASE WHEN (SELECT BOOL_OR(event_name = 'Block for credit')) THEN 1 ELSE 0 END) * 100
           AS blocked_pct
FROM THIS_PROCESS
ORDER BY order_size_class
```

| order_size_class | orders | blocked_pct |
|---|---|---|
| 1 Small (< €5k) | 6,691 | 28.0 |
| 2 Medium (€5k–25k) | 25,900 | 28.7 |
| 3 Large (≥ €25k) | 8,709 | 27.8 |

*Table 16.6: Credit block rate by order size class*

## Q08 – 16.3 Case Attributes and Event Attributes › Worked Case: Adding One of Each

**Question:** An event attribute needs an event level. Across all cases, flatten the process:

```sql
SELECT department,
       COUNT(1) AS events
FROM FLATTEN(THIS_PROCESS)
ORDER BY events DESC
```

| department | events |
|---|---|
| Order Desk Düsseldorf | 150,048 |
| Order Desk Brno | 114,861 |
| Billing | 87,674 |
| System | 50,000 |
| Accounts Receivable | 44,342 |
| Credit Management Pune | 21,874 |

*Table 16.7: Events by department*

## Q09 – 16.3 Case Attributes and Event Attributes › Worked Case: Adding One of Each

**Question:** Inside a case, use a subquery. This query counts, for every order, how many departments touched it, and averages that by segment:

```sql
SELECT customer_segment,
       AVG((SELECT COUNT(DISTINCT department))) AS departments_per_order
FROM THIS_PROCESS
```

## Q10 – 16.3 Case Attributes and Event Attributes › Event Attributes in Case Questions

**Question:** The most useful pattern combines both levels: a **case question about event attributes**. Tomas wanted to know how many Brno orders had a credit release without a documented review. The release is an event; Brno is a case attribute; "without a review" is a condition on the case's events:

```sql
SELECT sales_organization,
       COUNT(case_id) AS orders
FROM THIS_PROCESS
WHERE event_name MATCHES ('Release credit block')
  AND NOT event_name MATCHES ('Review blocked order')
```

**Result in the book:** 2,229 orders, all in CZ01. Not one in Düsseldorf. These are the phone releases of Brno's trusted-customer list from Chapter 7: the plant calls Pune, and the analyst releases the block without writing the review note.

## Q11 – 16.4 Aggregations and Grouping

**Question:** Some examples with Velora's results:

```sql
-- Customers and orders by segment
SELECT customer_segment,
       COUNT(DISTINCT customer_id) AS customers,
       COUNT(case_id)              AS orders
FROM THIS_PROCESS
ORDER BY orders DESC
```

| customer_segment | customers | orders |
|---|---|---|
| Direct industrial | 784 | 22,997 |
| Distributor | 435 | 12,914 |
| OEM | 181 | 5,389 |

*Table 16.10: Customers and orders by segment*

## Q12 – 16.4 Aggregations and Grouping

```sql
-- Average events and users per order
SELECT AVG((SELECT COUNT(1)))                 AS events_per_order,
       AVG((SELECT COUNT(DISTINCT user_code))) AS users_per_order
FROM THIS_PROCESS
```

**Result in the book:** 11.4 events and 5.5 users per order on average.

## Q13 – 16.4 Aggregations and Grouping

```sql
-- Number of variants
SELECT COUNT(DISTINCT event_name) AS variants
FROM THIS_PROCESS
```

**Result in the book:** 4,084. At case level, *event_name* is the whole sequence of a case's events, so counting its distinct values counts variants.

## Q14 – 16.4 Aggregations and Grouping › Rounding, IF, and CASE

**Question:** `ROUND(AVG(order_value_eur), 0)` rounds; `IF(condition, then, else)` and `CASE WHEN … THEN … ELSE … END` create categories:

```sql
SELECT IF(drop_shipment = 'yes', 'Drop shipment', 'From stock') AS fulfilment,
       COUNT(case_id) AS orders
FROM THIS_PROCESS
```

**Result in the book:** 40,739 from stock, 561 drop shipments.

## Q15 – 16.5 Durations and Time › Cycle Time

**Question:** Cycle time per case comes from the case's own events:

```sql
SELECT sales_organization,
       AVG((SELECT LAST(end_time) - FIRST(end_time))) / 86400000 AS avg_cycle_days
FROM THIS_PROCESS
ORDER BY avg_cycle_days DESC
```

**Result in the book:** CZ01 53.8 days, DE01 50.4 days.

## Q16 – 16.5 Durations and Time › Between Two Steps

**Question:** For the time between two specific steps, pick each step's time with FIRST or LAST and a FILTER:

```sql
-- Median days from order to first invoice
SELECT sales_organization,
       MEDIAN(((SELECT FIRST(end_time) FILTER (WHERE event_name = 'Create invoice'))
             - (SELECT FIRST(end_time))) / 86400000) AS order_to_invoice_days
FROM THIS_PROCESS
```

**Result in the book:** CZ01 10.3 days, DE01 6.9 days. On the median, a Brno order reaches its invoice 3.4 days later than a Düsseldorf order.

## Q17 – 16.5 Durations and Time › Between Two Steps

**Question:** The goods-issue-to-invoice time shows where Brno loses them:

```sql
SELECT sales_organization,
       MEDIAN(((SELECT FIRST(end_time) FILTER (WHERE event_name = 'Create invoice'))
             - (SELECT LAST(end_time)  FILTER (WHERE event_name = 'Post goods issue'))) / 86400000)
           AS gi_to_invoice_days
FROM THIS_PROCESS
WHERE drop_shipment = 'no'
```

**Result in the book:** CZ01 3.2 days, DE01 0.8 days. The drop shipments are excluded with WHERE because they're invoiced before the goods issue; including them would produce negative durations.

## Q18 – 16.5 Durations and Time › Thresholds with DURATION

**Question:** Compare a duration with a threshold using DURATION:

```sql
SELECT COUNT(case_id) FILTER (WHERE
           (SELECT FIRST(end_time) FILTER (WHERE event_name = 'Release credit block'))
         - (SELECT FIRST(end_time) FILTER (WHERE event_name = 'Block for credit'))
         > DURATION '2days') AS released_after_2_days,
       COUNT(case_id) FILTER (WHERE
           (SELECT BOOL_OR(event_name = 'Block for credit'))) AS blocked_orders
FROM THIS_PROCESS
```

**Result in the book:** 5,977 of 11,735 blocked orders waited more than two days for their first release.

## Q19 – 16.5 Durations and Time › Percentiles

**Question:** Averages hide the tail. The 90th percentile shows how long the slowest tenth takes:

```sql
SELECT sales_organization,
       PERCENTILE_CONT(0.9) WITHIN GROUP (
           ORDER BY ((SELECT LAST(end_time) - FIRST(end_time)) / 86400000)) AS p90_cycle_days
FROM THIS_PROCESS
```

**Result in the book:** CZ01 78.9 days, DE01 75.1 days.

## Q20 – 16.5 Durations and Time › Trends with DATE_TRUNC

**Question:** `DATE_TRUNC('month', …)` (or 'week', 'quarter', 'year') cuts a timestamp to the start of its period, which makes it a grouping column:

```sql
SELECT DATE_TRUNC('quarter', (SELECT FIRST(end_time))) AS quarter,
       COUNT(case_id) AS orders
FROM THIS_PROCESS
ORDER BY quarter
```

## Q21 – 16.5 Durations and Time › Date Parts and Date Filters

**Question:** `DATE_PART` extracts a part of a timestamp: 'hour', 'day', 'month', 'year', 'day_of_week' (1 is Monday). Filter by date with a DATE literal:

```sql
-- On which weekday does Brno invoice?
SELECT DATE_PART('day_of_week', end_time) AS weekday,
       COUNT(1) AS invoices
FROM FLATTEN(THIS_PROCESS)
WHERE event_name = 'Create invoice' AND plant = 'CZ10'
ORDER BY weekday
```

## Q22 – 16.5 Durations and Time › Date Parts and Date Filters

**Question:** Ninety-four percent of Brno's invoices are created on Fridays: the weekly billing run that Chapter 15 found behind the 3.2 days. The few on other days are corrected invoices after credit memos.

```sql
-- Orders created from April onwards
SELECT COUNT(case_id) FROM THIS_PROCESS
WHERE (SELECT FIRST(end_time)) >= DATE '2026-04-01'
```

**Result in the book:** 24,327.

## Q23 – 16.6 Conditions: WHERE, FILTER, and CASE › WHERE Removes Cases, FILTER Restricts One Number

**Question:** A count isn't a rate. For the credit memo rate (Velora calls it the invoice correction rate), the query needs all orders and the orders with a credit memo in the same row. WHERE would remove the orders without a credit memo from the whole query, and the denominator would be wrong. **FILTER** restricts only one aggregate:

```sql
SELECT COUNT(case_id) FILTER (WHERE (SELECT BOOL_OR(event_name = 'Create credit memo')))
         * 100.0 / COUNT(case_id) AS correction_pct
FROM THIS_PROCESS
```

**Result in the book:** 7.47%. Helena's mandate P3 wants it under 4%.

## Q24 – 16.6 Conditions: WHERE, FILTER, and CASE › Calculated Categories

**Question:** The question behind PD-050 (Chapter 15) was whether late price changes cause credit memos. A CASE expression on an event condition creates the two groups:

```sql
SELECT CASE WHEN (SELECT BOOL_OR(event_name = 'Change price after credit release'))
            THEN 'Late price change' ELSE 'No late price change' END AS order_group,
       COUNT(case_id) AS orders,
       COUNT(case_id) FILTER (WHERE (SELECT BOOL_OR(event_name = 'Create credit memo')))
         * 100.0 / COUNT(case_id) AS credit_memo_pct
FROM THIS_PROCESS
```

| order_group | orders | credit_memo_pct |
|---|---|---|
| No late price change | 35,753 | 3.85 |
| Late price change | 5,547 | 30.77 |

*Table 16.11: Credit memo rate with and without a late price change*

## Q25 – 16.6 Conditions: WHERE, FILTER, and CASE › Which Attribute Drives It?

**Question:** The same pattern tests one attribute after the other. Helena's size hypothesis failed (Table 16.6). The sales organization doesn't:

```sql
SELECT sales_organization,
       AVG(CASE WHEN (SELECT BOOL_OR(event_name = 'Block for credit')) THEN 1 ELSE 0 END) * 100
           AS blocked_pct
FROM THIS_PROCESS
```

**Result in the book:** CZ01 40.4%, DE01 19.2%. Brno orders are blocked twice as often. The decision table from Chapter 8 treats both sites the same; Brno's customer mix doesn't.

## Q26 – 16.6 Conditions: WHERE, FILTER, and CASE › Which Attribute Drives It?

**Question:** And payment terms explain dunning:

```sql
SELECT payment_terms,
       COUNT(case_id) AS orders,
       AVG(CASE WHEN (SELECT BOOL_OR(event_name = 'Send dunning notice')) THEN 1 ELSE 0 END) * 100
           AS dunned_pct
FROM THIS_PROCESS
ORDER BY payment_terms
```

| payment_terms | orders | dunned_pct |
|---|---|---|
| NT30 | 34,953 | 15.1 |
| NT45 | 1,571 | 18.3 |
| NT60 | 4,776 | 18.8 |

*Table 16.12: Dunning rate by payment terms*

## Q27 – 16.6 Conditions: WHERE, FILTER, and CASE › Lists and Patterns: IN and LIKE

```sql
SELECT COUNT(case_id) FROM THIS_PROCESS
WHERE payment_terms IN ('NT45', 'NT60')
  AND customer_name LIKE '%GmbH'
```

**Result in the book:** 816 orders from German limited companies with long payment terms.

## Q28 – 16.7 Sequences: MATCHES and BEHAVIOR

**Question:** A whole variant is just a long pattern. The share of the happy path:

```sql
SELECT COUNT(case_id) FILTER (WHERE event_name MATCHES (
           ^ 'Create sales order' -> 'Send order confirmation' -> 'Create delivery' -> 'Pick goods'
           -> 'Post goods issue' -> 'Create invoice' -> 'Send invoice'
           -> 'Receive incoming payment' -> 'Clear payment' $))
       * 100.0 / COUNT(case_id) AS happy_path_pct
FROM THIS_PROCESS
```

**Result in the book:** 18.1%, the same as the top variant in the Variant Explorer.

## Q29 – 16.7 Sequences: MATCHES and BEHAVIOR › Conditions on Steps: BEHAVIOR

**Question:** MATCHES compares event names. **BEHAVIOR** lets you name steps with any condition, including event attributes, and then match the sequence of those named steps:

```sql
SELECT COUNT(case_id)
FROM THIS_PROCESS
WHERE BEHAVIOR
        (event_name = 'Block for credit')                      AS blocked,
        (event_name = 'Release credit block' AND plant = 'IN10') AS released_in_pune
      MATCHES (blocked -> released_in_pune)
```

**Result in the book:** 954 orders, the same as the direct pattern above, because every release happens in Pune. If Brno ever starts releasing locally, this query will show it while the simpler one won't.

## Q30 – 16.8 Event-Level Analysis with FLATTEN

**Question:** Some questions are about events, not cases: how many events per activity, at which hour, by which department. **FLATTEN(THIS_PROCESS)** turns the process into one row per event, with the case attributes repeated on every row.

```sql
SELECT event_name, COUNT(1) AS events
FROM FLATTEN(THIS_PROCESS)
ORDER BY events DESC
LIMIT 5
```

**Result in the book:** *Create delivery* and *Post goods issue* 55,066 each, *Pick goods* 54,505, *Create invoice* 43,837, *Create sales order* 41,300.

## Q31 – 16.8 Event-Level Analysis with FLATTEN

```sql
-- When are orders entered?
SELECT DATE_PART('hour', end_time) AS hour, COUNT(1) AS orders
FROM FLATTEN(THIS_PROCESS)
WHERE event_name = 'Create sales order'
ORDER BY hour
```

**Result in the book:** 11,775 orders at 07:00–08:00, 11,761 at 08:00–09:00, and 5,733 at 09:00–10:00. Most orders are entered in the first two hours of the day, from the overnight e-mails.

## Q32 – 16.8 Event-Level Analysis with FLATTEN › Waiting Time Before Each Step: Window Functions

**Question:** Katrin's question "how long does an order wait before each step?" needs the time since the previous event. That's a **window function**: LAG(end_time) returns the previous event's time within a partition, here the case.

```sql
SELECT event_name,
       AVG(wait) / 86400000 AS avg_wait_days
FROM (
    SELECT event_name,
           end_time - LAG(end_time) OVER (PARTITION BY case_id ORDER BY end_time) AS wait
    FROM FLATTEN(THIS_PROCESS)
) AS t
ORDER BY avg_wait_days DESC
LIMIT 5
```

## Q33 – 16.9 Subqueries and Multi-Step Questions

**Question:** When a question has two steps ("first count orders per customer, then count the customers with many"), put the first step in a subquery in FROM:

```sql
SELECT COUNT(1) AS frequent_customers
FROM (
    SELECT customer_name, COUNT(case_id) AS orders
    FROM THIS_PROCESS
) AS t
WHERE orders > 60
```

**Result in the book:** 136 customers placed more than 60 orders in the year.

## Q34 – 16.9 Subqueries and Multi-Step Questions

**Question:** Rework is a subquery question too. How many orders were invoiced more than once?

```sql
SELECT COUNT(case_id)
FROM THIS_PROCESS
WHERE (SELECT COUNT(1) FILTER (WHERE event_name = 'Create invoice')) > 1
```

**Result in the book:** 3,085, exactly the number of credit memos, because every credit memo is followed by a corrected invoice.

## Q35 – 16.9 Subqueries and Multi-Step Questions › The Price of a Correction

**Question:** The last query of Malik's list combined everything: a calculated category, a sequence condition, and a duration between steps.

```sql
SELECT CASE WHEN (SELECT BOOL_OR(event_name = 'Create credit memo'))
            THEN 'With credit memo' ELSE 'Clean invoice' END AS invoice,
       COUNT(case_id) AS orders,
       MEDIAN(((SELECT LAST(end_time)  FILTER (WHERE event_name = 'Clear payment'))
             - (SELECT FIRST(end_time) FILTER (WHERE event_name = 'Create invoice'))) / 86400000)
           AS median_invoice_to_payment_days
FROM THIS_PROCESS
WHERE event_name MATCHES ('Clear payment')
```

| invoice | orders | median_invoice_to_payment_days |
|---|---|---|
| Clean invoice | 35,185 | 39.7 |
| With credit memo | 2,706 | 59.0 |

*Table 16.15: Invoice to payment with and without a credit memo*

## Q36 – 16.11 Metrics: Queries Everyone Can Reuse

**Question:** A metric contains only the expression, not the whole query. The correction rate as a metric is:

```sql
COUNT(case_id) FILTER (WHERE (SELECT BOOL_OR(event_name = 'Create credit memo')))
  * 100.0 / COUNT(case_id)
```

## Q37 – 16.11 Metrics: Queries Everyone Can Reuse › Library Metrics and Custom Metrics

**Question:** The metric then uses the reference name. SiGNAL compares durations with duration literals such as `DURATION '1day'`, so the number from the variable is multiplied by one day:

```sql
-- Metric "Goods issue to invoice (orders over target)", aggregation: over cases
100.0 * COUNT(case_id) FILTER (
    WHERE (SELECT FIRST(end_time) WHERE event_name = 'Create invoice')
        - (SELECT LAST(end_time)  WHERE event_name = 'Post goods issue')
      > ${Variable.billing_target_days} * DURATION '1day'
  ) / COUNT(case_id)
```

## Q38 – 16.11 Metrics: Queries Everyone Can Reuse › Library Metrics and Custom Metrics

**Question:** A simpler first metric needs no variable at all: the average time from goods issue to invoice.

```sql
-- Metric "Goods issue to invoice (days)", aggregation: over cases (first goods issue to first invoice)
AVG(
  (SELECT FIRST(end_time) WHERE event_name = 'Create invoice')
  - (SELECT FIRST(end_time) WHERE event_name = 'Post goods issue')
)
```

## Q39 – 16.11 Metrics: Queries Everyone Can Reuse › Library Metrics and Custom Metrics

**Question:** Velora's collection then held these metric definitions, each tested in the metric preview against the O2C data:

```sql
-- Invoice correction rate (% of orders), over cases. Result: 7.47
COUNT(case_id) FILTER (WHERE (SELECT BOOL_OR(event_name = 'Create credit memo')))
  * 100.0 / COUNT(case_id)
```

## Q40 – 16.11 Metrics: Queries Everyone Can Reuse › Library Metrics and Custom Metrics

```sql
-- Late price change rate (% of orders), over cases. Result: 13.43
COUNT(case_id) FILTER (WHERE (SELECT BOOL_OR(event_name = 'Change price after credit release')))
  * 100.0 / COUNT(case_id)
```

## Q41 – 16.11 Metrics: Queries Everyone Can Reuse › Library Metrics and Custom Metrics

```sql
-- Release without review (orders), over cases. Result: 2,229
COUNT(case_id) FILTER (
  WHERE (SELECT BOOL_OR(event_name = 'Release credit block'))
    AND NOT (SELECT BOOL_OR(event_name = 'Review blocked order'))
)
```

## Q42 – 16.11 Metrics: Queries Everyone Can Reuse › Library Metrics and Custom Metrics

**Question:** To use metrics in a widget, switch the widget editor to **Interactive**, open **More > Metrics**, and drag a metric into **Measures**; drag an attribute from **More > Attributes** into **Dimensions** (Figure 16.14). The editor suggests a chart type (marked *Recommended*). If you then switch to SIGNAL, you see that the widget has copied the metric's expression into its query:

```sql
SELECT COUNT(CASE_ID) FILTER (WHERE (SELECT BOOL_OR(EVENT_NAME = 'Create credit memo'))) * 100 / COUNT(CASE_ID) AS "Invoice correction rate",
       COUNT(CASE_ID) FILTER (WHERE (SELECT BOOL_OR(EVENT_NAME = 'Change price after credit release'))) * 100 / COUNT(CASE_ID) AS "Late price change rate",
       "sales_organization"
FROM THIS_PROCESS
LIMIT 500
```

## Q43 – 16.12 The Same Method for Procure to Pay

**Question:** Velora's P2P event log (Chapter 13's pipeline, extended to purchasing) uses the purchase order item as the case. With what you've learned, the query is two patterns and a FILTER:

```sql
SELECT plant,
       COUNT(case_id) AS po_items,
       COUNT(case_id) FILTER (
           WHERE event_name MATCHES ('Receive invoice' ~> 'Create purchase order')
       ) * 100.0 / COUNT(case_id) AS after_the_fact_pct
FROM THIS_PROCESS
ORDER BY after_the_fact_pct DESC
```

## Q44 – 16.12 The Same Method for Procure to Pay

**Question:** Adding the vendor category showed the pattern: after-the-fact POs concentrated in maintenance, repair, and operations (MRO) purchasing and in external services. In Brno, 58% of MRO orders were after the fact. A PO created one day after an invoice because the buyer was on holiday isn't the same as one created five weeks later, so Rui's metric uses a variable for the tolerance:

```sql
COUNT(case_id) FILTER (WHERE
    (SELECT FIRST(end_time) FILTER (WHERE event_name = 'Create purchase order'))
  - (SELECT FIRST(end_time) FILTER (WHERE event_name = 'Receive invoice'))
  > ${Variable.atf_tolerance_days} * DURATION '1day')
* 100.0 / COUNT(case_id)
```

---

*All names and data are fictional: Velora Group SE is invented for the book. Results are those printed in Chapter 16.*
