-- Velora extension - Receive Incoming Payment - Event Collector --
-- The electronic bank statement (FF_5) posts the money to the bank clearing account the moment it
-- arrives, with the invoice number as reference. The AR clerk clears the invoice later (F-28), which
-- the standard template collects as 'Clear Invoice'. This collector adds the arrival of the money.
WITH CaseLink_Billing AS (
    SELECT c_caseid, mandt, vbrp_vbeln
    FROM CaseLink
    WHERE vbrp_vbeln IS NOT NULL
    GROUP BY c_caseid, mandt, vbrp_vbeln
    )
SELECT DISTINCT
    CaseLink.c_caseid,
    CASE
        WHEN bkpf.cputm IS NULL THEN from_unixtime(bkpf.cpudt / 1000)
        ELSE from_unixtime(bkpf.cpudt / 1000 + bkpf.cputm / 1000)
    END AS c_time,
    'Receive Incoming Payment' AS c_eventname,
    CONCAT(bkpf.bukrs, bkpf.belnr, bkpf.gjahr) AS BankStatementDocumentId,
    bkpf.usnam AS EventCreatedByUserId
FROM bkpf
    INNER JOIN CaseLink_Billing AS CaseLink ON bkpf.mandt = CaseLink.mandt
                                           AND bkpf.xblnr = CaseLink.vbrp_vbeln
WHERE bkpf.blart = 'ZE'
  AND bkpf.tcode = 'FF_5'
  AND bkpf.cpudt IS NOT NULL
