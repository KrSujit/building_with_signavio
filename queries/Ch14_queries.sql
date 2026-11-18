-- Building with SAP Signavio, Chapter 14: every query printed in the chapter, in order.
-- Chapters 13-14: SQL (Trino dialect, Process Intelligence transformations). Chapters 15-16: SiGNAL.
-- Source: github.com/KrSujit/building_with_signavio

-- ---------------------------------------------------------------
-- Q01  Section: 14.5 Six SAP Habits to Know
-- 1. Dates and times arrive as numbers. In SAP, a date is text (20260128) and a time is text (070109), stored in two columns: ERDAT and ERZET, UDATE and UTIME, CP
-- ---------------------------------------------------------------
from_unixtime(vbak.erdat / 1000 + vbak.erzet / 1000)   -- seconds since 1970 → 2026-01-28 07:01:09

-- ---------------------------------------------------------------
-- Q02  Section: CaseLink: One View for Every Link
-- The result is one row for each combination of order item, delivery item, billing item, and accounting document: 207,315 rows for Velora's 180,389 items. Every e
-- ---------------------------------------------------------------
WITH CaseLink_Delivery AS (
    SELECT c_caseid, mandt, lips_vbeln_delivery AS lips_vbeln
    FROM CaseLink
    WHERE lips_vbeln_delivery IS NOT NULL
    GROUP BY c_caseid, mandt, lips_vbeln_delivery
)

-- ---------------------------------------------------------------
-- Q03  Section: Sales: Creating the Order
-- The order header knows who created it and when. The collector 3.1 Create Sales Order reads the data view vbap_vbak_prep, which adds the item counts and the orde
-- ---------------------------------------------------------------
SELECT DISTINCT
    CaseLink.c_caseid,
    COALESCE(from_unixtime(vbak_erdat / 1000 + vbak_erzet / 1000),
             from_unixtime(vbak_erdat / 1000))                AS c_time,
    CASE
        WHEN tvak_kalvg = 'C' THEN 'Create Sales Order (Free of Charge)'
        WHEN tvak_kalvg != 'C' AND NumberOfFreeOfChargeItems > 0 THEN 'Create Sales Order (incl. F.o.C. Items)'
        ELSE 'Create Sales Order'
    END                                                         AS c_eventname,
    NumberOfSalesOrderItems, NumberOf3rdPartyItems, ...
FROM vbap_vbak_prep AS vbap_vbak
    INNER JOIN CaseLink_SalesOrder AS CaseLink ON vbap_vbak.vbap_vbeln = CaseLink.vbap_vbeln
WHERE vbak_erdat IS NOT NULL
  AND vbak_vbtyp = 'C'                                          -- C = sales order

-- ---------------------------------------------------------------
-- Q04  Section: Sales: Events from Change Documents
-- Header changes (3.3 Change Events Sales Order Header). This collector reads the changes to VBAK and VBUK, cuts the order number out of TABKEY, and joins to the 
-- ---------------------------------------------------------------
CASE
    WHEN cdposhdr.fname = 'CMGST' AND cdposhdr.value_new = 'A' THEN 'Credit Check Passed'
    WHEN cdposhdr.fname = 'CMGST' AND cdposhdr.value_new = 'B' THEN 'Credit Check Failed'
    WHEN cdposhdr.fname = 'CMGST' AND cdposhdr.value_new = 'D' THEN 'Document Released By Credit Representative'
    WHEN cdposhdr.fname = 'LIFSK' AND ... THEN 'Set Sales Order Delivery Block'
    ...
    WHEN ddftx.scrtext_m IS NOT NULL THEN
        CASE WHEN cdposhdr.chngind = 'U' THEN 'Change' ... END || ' ' || 'Sales Order ' || ddftx.scrtext_m
    ELSE ... || ' ' || 'Sales Order (' || cdposhdr.fname || ')'
END AS c_eventname
...
WHERE cdposhdr.tabname IN ('VBAK', 'VBUK')
  AND cdposhdr.fname IN ('AMTBL', 'AUDAT', 'AUGRU', ..., 'CMGST', ..., 'LIFSK', ..., 'VDATU', ...)

-- ---------------------------------------------------------------
-- Q05  Section: Sales: Events from Change Documents
-- Price changes (8.3 Change Price Sales Order Item). This collector reads VBAP-NETPR and adds an event attribute that's worth knowing:
-- ---------------------------------------------------------------
'Change Sales Order Item Price' AS c_eventname,
CASE WHEN CAST(<old value> AS DECIMAL(38,2)) > CAST(<new value> AS DECIMAL(38,2))
     THEN 'Price Decreased' ELSE 'Price Increased'
END AS ChangePriceIdentifier,
cdposhdr.value_old AS ChangeOldValue,
cdposhdr.value_new AS ChangeNewValue,
...
WHERE cdposhdr.tabname IN ('VBAP') AND cdposhdr.fname = 'NETPR' AND cdposhdr.chngind = 'U'

-- ---------------------------------------------------------------
-- Q06  Section: 14.8 Extending the Template
-- Each extension starts the way SAP's collectors do: with a CTE on CaseLink. Here is the credit review note.
-- ---------------------------------------------------------------
-- Velora extension - Review Blocked Order - Event Collector --
-- Velora's credit team writes a credit review note (text ID ZCRV) on the sales order header.
-- STXH keeps when the note was first written and when it was last changed: two events at most.
WITH CaseLink_SalesOrder AS (
    SELECT c_caseid, mandt, vbap_vbeln
    FROM CaseLink
    GROUP BY c_caseid, mandt, vbap_vbeln
    ),
review AS (
    SELECT mandt, tdname, from_unixtime(tdfdate / 1000 + tdftime / 1000) AS t, tdfuser AS username
    FROM stxh WHERE tdobject = 'VBBK' AND tdid = 'ZCRV'
    UNION
    SELECT mandt, tdname, from_unixtime(tdldate / 1000 + tdltime / 1000) AS t, tdluser AS username
    FROM stxh WHERE tdobject = 'VBBK' AND tdid = 'ZCRV'
    )
SELECT DISTINCT
    CaseLink.c_caseid,
    review.t                AS c_time,
    'Review Blocked Order'  AS c_eventname,
    review.username         AS EventCreatedByUserId
FROM review
    INNER JOIN CaseLink_SalesOrder AS CaseLink ON review.mandt = CaseLink.mandt
                                              AND review.tdname = CaseLink.vbap_vbeln
WHERE review.t IS NOT NULL

-- ---------------------------------------------------------------
-- Q07  Section: 14.8 Extending the Template
-- The payment extension shows a different kind of link. The bank statement program (FF_5) posts the incoming money to a bank clearing account, with no customer li
-- ---------------------------------------------------------------
SELECT DISTINCT
    CaseLink.c_caseid,
    from_unixtime(bkpf.cpudt / 1000 + bkpf.cputm / 1000)  AS c_time,
    'Receive Incoming Payment'                            AS c_eventname,
    CONCAT(bkpf.bukrs, bkpf.belnr, bkpf.gjahr)            AS BankStatementDocumentId,
    bkpf.usnam                                            AS EventCreatedByUserId
FROM bkpf
    INNER JOIN CaseLink_Billing AS CaseLink ON bkpf.mandt = CaseLink.mandt
                                           AND bkpf.xblnr = CaseLink.vbrp_vbeln
WHERE bkpf.blart = 'ZE' AND bkpf.tcode = 'FF_5'

-- ---------------------------------------------------------------
-- Q08  Section: 14.8 Extending the Template
-- The fix for the year-end bug changes two lines of SAP's collector. It drops the fiscal year from the first join and checks the clearing document's year against 
-- ---------------------------------------------------------------
INNER JOIN CaseLink_AccountingClearing AS CaseLink
        ON bseg_bkpf_clearing.mandt = CaseLink.mandt
       AND bseg_bkpf_clearing.bkpf_bukrs = CaseLink.bkpf_bukrs
       AND bseg_bkpf_clearing.bkpf_belnr = CaseLink.bkpf_belnr_clearing
INNER JOIN bseg_bkpf
        ON CaseLink.mandt = bseg_bkpf.mandt AND CaseLink.bkpf_bukrs = bseg_bkpf.bkpf_bukrs
       AND CaseLink.bkpf_belnr = bseg_bkpf.bkpf_belnr AND CaseLink.bkpf_gjahr = bseg_bkpf.bkpf_gjahr
       AND bseg_bkpf_clearing.bkpf_gjahr = bseg_bkpf.bseg_auggj  -- fiscal year of the clearing document

-- ---------------------------------------------------------------
-- Q09  Section: Event Attributes
-- Every template collector adds the user and the user type:
-- ---------------------------------------------------------------
cdposhdr.username AS EventCreatedByUserId,
CASE
    WHEN vusr02_header.ustyp = 'A' AND (cdposhdr.tcode IS NULL OR cdposhdr.tcode = '') THEN 'System'
    WHEN vusr02_header.ustyp = 'A' THEN 'Dialog'
    WHEN vusr02_header.ustyp = 'B' THEN 'System'
    ...
END AS EventCreatedByUserType

-- ---------------------------------------------------------------
-- Q10  Section: Step 5: Load and Compare
-- 4. Count orders, not cases, in a SiGNAL query, and compare the result with Table 14.8:
-- ---------------------------------------------------------------
SELECT event_name, COUNT(DISTINCT "SalesOrderId") AS orders, COUNT(1) AS events
FROM FLATTEN(THIS_PROCESS)
GROUP BY event_name
ORDER BY events DESC
