-- Building with SAP Signavio, Chapter 13: every query printed in the chapter, in order.
-- Chapters 13-14: SQL (Trino dialect, Process Intelligence transformations). Chapters 15-16: SiGNAL.
-- Source: github.com/KrSujit/building_with_signavio

-- ---------------------------------------------------------------
-- Q01  Section: Transformation Scripts
-- Transformation in Process Intelligence uses SQL scripts. Each script produces events of one or more types: which activity, which case, which timestamp, which at
-- ---------------------------------------------------------------
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
