"""Run SAP Signavio's standard 'Order to Cash (SAP ECC)' template SQL, unchanged, on the
Velora dummy SAP tables. Signavio runs Trino SQL; this script runs it in DuckDB with a thin
dialect shim (function names only - no logic is changed).

usage: python3 run_template.py <tables_dir> <template.json | template_dir> <out_dir> [velora_ext_dir]
  template.json = the export of SAP's "Order to Cash (SAP ECC)" pipeline template (data views + collectors)
"""
import duckdb, os, re, sys, glob, time, json

TABLES, TPL, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(OUT, exist_ok=True)

DATES = set('erdat aedat audat vdatu edatu mbdat wadat udate datvr badat frgdt lfdat bedat kdatb kdate lewed kodat wadat_ist bldat budat cpudt fkdat zfbdt valut augdt madat stodt budat_mkpf tdfdate tdldate datbg daten'.split())
TIMES = set('erzet utime uhrvr eruhr ezeit mbuhr wauhr lfuhr kouhr cputm uatbg uaten tdftime tdltime'.split())
NUMS = set('netwr kwmeng kbmeng netpr wmeng bmeng menge lfimg ormng lgmng brgew kcmeng kcbrgew kcntgew fkimg mwsbp skfbp kursk mwsbk wrbtr wmwst fwbas nebtr skfbt sknto wskto zbd1t zbd2t zbd3t zbd1p zbd2p frath ukurs ffact tfact wkurs ktmng uebto untto plifz currdec'.split())

con = duckdb.connect()
con.execute("SET threads TO 8")
# --- Trino -> DuckDB shims (same semantics)
con.execute("CREATE MACRO from_unixtime(x) AS make_timestamp(CAST(round(x * 1000000) AS BIGINT))")
con.execute("CREATE MACRO tdate_add(u, n, ts) AS ts + to_days(CAST(n AS INT))")
con.execute("CREATE MACRO tdate(x) AS CAST(x AS DATE)")
con.execute("CREATE MACRO is_nan(x) AS isnan(x)")
con.execute("CREATE MACRO parse_datetime(s, f) AS strptime(s, '%Y%m%d')")

for f in sorted(glob.glob(os.path.join(TABLES, '*.csv'))):
    t = os.path.basename(f)[:-4]
    cols = open(f, encoding='utf-8').readline().strip().split(',')
    types = {c: ('BIGINT' if c in DATES or c in TIMES else 'DOUBLE' if c in NUMS else 'VARCHAR') for c in cols}
    con.execute(f"CREATE TABLE {t} AS SELECT * FROM read_csv('{f}', header=true, columns={types!r}, quote='\"', escape='\"')")


def split_args(s, i):
    """s[i] == '(' -> list of top-level args and index after ')'"""
    depth, start, args, q = 0, i + 1, [], False
    j = i
    while j < len(s):
        c = s[j]
        if c == "'":
            q = not q
        elif not q:
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    args.append(s[start:j]); return args, j + 1
            elif c == ',' and depth == 1:
                args.append(s[start:j]); start = j + 1
        j += 1
    raise ValueError('unbalanced')


def rewrite_concat(sql):
    # Trino CONCAT returns NULL if any argument is NULL; DuckDB's concat skips NULLs. Use || (NULL-propagating).
    out, i = [], 0
    pat = re.compile(r'\bCONCAT\s*\(', re.I)
    while True:
        m = pat.search(sql, i)
        if not m:
            out.append(sql[i:]); break
        out.append(sql[i:m.start()])
        args, end = split_args(sql, m.end() - 1)
        out.append('(' + ' || '.join('CAST((' + rewrite_concat(a) + ') AS VARCHAR)' for a in args) + ')')
        i = end
    return ''.join(out)


def strip_comments(sql):
    out = []
    for line in sql.split('\n'):
        q, k = False, None
        for j, c in enumerate(line):
            if c == "'": q = not q
            if not q and line[j:j + 2] == '--': k = j; break
        out.append(line if k is None else line[:k])
    return '\n'.join(out)


def tr(sql):
    sql = strip_comments(sql)
    sql = re.sub(r"\bDATE_ADD\s*\(", "tdate_add(", sql, flags=re.I)
    sql = re.sub(r"(?<![\w.])DATE\s*\(", "tdate(", sql)
    sql = rewrite_concat(sql)
    return sql


# --- data views (created in dependency order)
if TPL.endswith('.json'):
    J = json.load(open(TPL, encoding='utf-8'))
    DV_SRC = J['dataViews']
    EC_SRC = {(c['bo'] + '__' + c['name']).replace(' ', '_').replace('/', '-'): c['sql'] for c in J['collectors'] if c.get('enabled', True)}
else:
    DV_SRC = {os.path.basename(f)[:-4]: open(f).read() for f in glob.glob(os.path.join(TPL, 'dv', '*.sql'))}
    EC_SRC = {os.path.basename(f)[:-4]: open(f).read() for f in glob.glob(os.path.join(TPL, 'ec', '*.sql'))}
dvs = {k: tr(v) for k, v in DV_SRC.items()}
pending, errors = dict(dvs), {}
while pending:
    progress = False
    for name, sql in list(pending.items()):
        try:
            con.execute(f'CREATE TABLE "{name}" AS {sql}')
            del pending[name]; progress = True
            print(f'data view {name:24s} {con.execute(f"SELECT COUNT(*) FROM \"{name}\"").fetchone()[0]:>9,}')
        except Exception as e:
            errors[name] = str(e).split('\n')[0]
    if not progress:
        for n in pending: print('DV FAIL', n, errors[n])
        sys.exit(1)

# --- event collectors and case attribute collectors
ev_parts, attr = [], {}
EXT = sys.argv[4] if len(sys.argv) > 4 else None
ext = {os.path.basename(f)[:-4]: open(f, encoding='utf-8').read() for f in sorted(glob.glob(os.path.join(EXT, '*.sql')))} if EXT else {}
jobs = [(k, v) for k, v in sorted(EC_SRC.items()) if k not in ext] + sorted(ext.items())   # a Velora file with the same name replaces SAP's collector
for name, src in jobs:
    sql = tr(src)
    t0 = time.time()
    try:
        con.execute(f'CREATE TABLE "x_{name}" AS {sql}')
    except Exception as e:
        print('EC FAIL', name, str(e).split('\n')[0][:300]); continue
    n = con.execute(f'SELECT COUNT(*) FROM "x_{name}"').fetchone()[0]
    print(f'collector {name:58s} {n:>9,}  {time.time()-t0:5.1f}s')
    cols = [r[0] for r in con.execute(f'DESCRIBE "x_{name}"').fetchall()]
    if 'c_eventname' in cols:
        ev_parts.append(f'SELECT c_caseid, c_time, c_eventname, \'{name}\' AS collector FROM "x_{name}"')
    else:
        attr[name] = cols

if ev_parts:
    con.execute('CREATE TABLE eventlog AS ' + ' UNION ALL '.join(ev_parts))
    con.execute(f"COPY (SELECT * FROM eventlog ORDER BY c_caseid, c_time, c_eventname) TO '{OUT}/template_eventlog.csv' (HEADER)")
    print('\nevents', con.execute('SELECT COUNT(*), COUNT(DISTINCT c_caseid) FROM eventlog').fetchone())
    for r in con.execute('SELECT c_eventname, collector, COUNT(*) n, COUNT(DISTINCT c_caseid) c FROM eventlog GROUP BY 1,2 ORDER BY 3 DESC').fetchall():
        print(f'  {r[0]:52s} {r[2]:>9,} {r[3]:>8,}   [{r[1]}]')
for name, cols in attr.items():
    print('\ncase attributes', name, cols[:40])
    con.execute(f"COPY \"x_{name}\" TO '{OUT}/{name}.csv' (HEADER)")
con.close()
