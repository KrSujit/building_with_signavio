"""Reconcile the event log produced by SAP's O2C template (+ Velora extensions) with Velora's
order-level event log. The template's case is the sales order ITEM; we roll it up to the order
(case id = mandt + vbeln + posnr -> vbeln) and compare distinct (order, activity, timestamp)."""
import duckdb, sys
LOG, VEL = sys.argv[1], sys.argv[2]
MAP = {
    'Create Sales Order': 'Create sales order',
    'Send Order Confirmation': 'Send order confirmation',
    'Change Sales Order Item Quantity': 'Change quantity',
    'Change Sales Order Req. deliv.date': 'Change requested delivery date',
    'Change Sales Order Item Price': 'Change price*',
    'Credit Check Failed': 'Block for credit',
    'Review Blocked Order': 'Review blocked order',
    'Document Released By Credit Representative': 'Release credit block',
    'Reject Sales Order Item': 'Reject order',
    'Create Delivery': 'Create delivery',
    'Execute Picking': 'Pick goods',
    'Post Goods Issue': 'Post goods issue',
    'Create Invoice': 'Create invoice',
    'Send Invoice': 'Send invoice',
    'Create Customer Credit Memo': 'Create credit memo',
    'Change Dunning Level': 'Send dunning notice',
    'Receive Incoming Payment': 'Receive incoming payment',
    'Clear Invoice': 'Clear payment',
}
con = duckdb.connect()
con.execute(f"CREATE TABLE t AS SELECT substr(c_caseid, 4, 10) AS vbeln, c_time, c_eventname FROM read_csv('{LOG}', header=true, all_varchar=true)")
con.execute("CREATE TABLE m (sap VARCHAR, vel VARCHAR)")
con.executemany("INSERT INTO m VALUES (?, ?)", list(MAP.items()))
con.execute(f"""CREATE TABLE v AS SELECT case_id AS vbeln, CAST(timestamp AS VARCHAR) AS ts,
    CASE WHEN activity LIKE 'Change price%' THEN 'Change price*' ELSE activity END AS vel
    FROM read_csv('{VEL}', header=true, all_varchar=true)""")
con.execute("""CREATE TABLE s AS SELECT DISTINCT t.vbeln, substr(CAST(t.c_time AS VARCHAR), 1, 19) AS ts, m.vel
               FROM t JOIN m ON t.c_eventname = m.sap""")
rows = con.execute("""
WITH a AS (SELECT vel, COUNT(*) n FROM (SELECT DISTINCT vbeln, ts, vel FROM v) GROUP BY 1),
     b AS (SELECT vel, COUNT(*) n FROM s GROUP BY 1),
     bth AS (SELECT vel, COUNT(*) n FROM (SELECT DISTINCT vbeln, ts, vel FROM v) INNER JOIN s USING (vbeln, ts, vel) GROUP BY 1)
SELECT COALESCE(a.vel, b.vel), a.n, b.n, bth.n FROM a FULL JOIN b USING (vel) LEFT JOIN bth USING (vel) ORDER BY 2 DESC NULLS LAST""").fetchall()
print(f"{'Velora activity':34s} {'Velora log':>11s} {'from SAP':>10s} {'same order+time':>16s}")
for r in rows: print(f"{r[0]:34s} {r[1] or 0:>11,} {r[2] or 0:>10,} {r[3] or 0:>16,}")
unm = con.execute("SELECT c_eventname, COUNT(*) FROM t WHERE c_eventname NOT IN (SELECT sap FROM m) GROUP BY 1 ORDER BY 2 DESC").fetchall()
print('\nstandard events with no Velora activity (kept in the SAP log):')
for r in unm: print(f'  {r[0]:56s} {r[1]:>9,}')
