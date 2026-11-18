-- Velora extension - Send Invoice - Event Collector --
-- Output message RD00 (invoice) on the billing document, processed successfully. The standard
-- template only collects invoices sent by IDoc to an ordering company (intercompany, NACHA = '6').
WITH CaseLink_Billing AS (
    SELECT c_caseid, mandt, vbrp_vbeln
    FROM CaseLink
    WHERE vbrp_vbeln IS NOT NULL
    GROUP BY c_caseid, mandt, vbrp_vbeln
    )
SELECT DISTINCT
    CaseLink.c_caseid,
    CASE
        WHEN nast.uhrvr IS NULL THEN from_unixtime(nast.datvr / 1000)
        ELSE from_unixtime(nast.datvr / 1000 + nast.uhrvr / 1000)
    END AS c_time,
    'Send Invoice' AS c_eventname,
    nast.objky AS BillingDocumentId,
    nast.nacha AS OutputMedium,
    nast.usnam AS EventCreatedByUserId
FROM nast
    INNER JOIN CaseLink_Billing AS CaseLink ON nast.mandt = CaseLink.mandt
                                           AND nast.objky = CaseLink.vbrp_vbeln
WHERE nast.kappl = 'V3'
  AND nast.kschl = 'RD00'
  AND nast.vstat = '1'
  AND nast.datvr IS NOT NULL
