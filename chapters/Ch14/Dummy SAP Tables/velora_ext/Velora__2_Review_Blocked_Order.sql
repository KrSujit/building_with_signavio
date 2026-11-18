-- Velora extension - Review Blocked Order - Event Collector --
-- Velora's credit team writes a credit review note (text ID ZCRV) on the sales order header.
-- STXH keeps when the note was first written and when it was last changed: two events at most.
WITH CaseLink_SalesOrder AS (
    SELECT c_caseid, mandt, vbap_vbeln
    FROM CaseLink
    GROUP BY c_caseid, mandt, vbap_vbeln
    ),
review AS (
    SELECT mandt, tdname, from_unixtime(tdfdate / 1000 + tdftime / 1000) AS t, tdfuser AS username FROM stxh WHERE tdobject = 'VBBK' AND tdid = 'ZCRV'
    UNION
    SELECT mandt, tdname, from_unixtime(tdldate / 1000 + tdltime / 1000) AS t, tdluser AS username FROM stxh WHERE tdobject = 'VBBK' AND tdid = 'ZCRV'
    )
SELECT DISTINCT
    CaseLink.c_caseid,
    review.t AS c_time,
    'Review Blocked Order' AS c_eventname,
    review.username AS EventCreatedByUserId
FROM review
    INNER JOIN CaseLink_SalesOrder AS CaseLink ON review.mandt = CaseLink.mandt
                                              AND review.tdname = CaseLink.vbap_vbeln
WHERE review.t IS NOT NULL
