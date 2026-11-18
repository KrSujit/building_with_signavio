-- Velora extension - Send Order Confirmation - Event Collector --
-- Output message BA00 (order confirmation) on the sales order, processed successfully (VSTAT = '1').
WITH CaseLink_SalesOrder AS (
    SELECT c_caseid, mandt, vbap_vbeln
    FROM CaseLink
    GROUP BY c_caseid, mandt, vbap_vbeln
    )
SELECT DISTINCT
    CaseLink.c_caseid,
    CASE
        WHEN nast.uhrvr IS NULL THEN from_unixtime(nast.datvr / 1000)
        ELSE from_unixtime(nast.datvr / 1000 + nast.uhrvr / 1000)
    END AS c_time,
    'Send Order Confirmation' AS c_eventname,
    nast.kschl AS OutputType,
    nast.nacha AS OutputMedium,
    nast.usnam AS EventCreatedByUserId
FROM nast
    INNER JOIN CaseLink_SalesOrder AS CaseLink ON nast.mandt = CaseLink.mandt
                                              AND nast.objky = CaseLink.vbap_vbeln
WHERE nast.kappl = 'V1'
  AND nast.kschl = 'BA00'
  AND nast.vstat = '1'
  AND nast.datvr IS NOT NULL
