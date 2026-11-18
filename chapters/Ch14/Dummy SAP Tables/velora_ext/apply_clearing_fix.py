"""Building with SAP Signavio - companion file, Chapter 14 (folder "Dummy SAP Tables/velora_ext")

Writes Velora's fixed copy of SAP's standard collector "2. Clearing Events" (business object
Accounting) from YOUR OWN copy of the Order to Cash (SAP ECC) template, as described in Section 14.8.

Why a script and not the SQL file? The collector is SAP content. This repository doesn't
redistribute it. The script applies Velora's two-line change to the SQL you take from your
own pipeline, and writes the result next to this script as Accounting__2._Clearing_Events.sql,
the file name run_template.py expects for a collector that replaces SAP's.

The fix: SAP's collector joins the clearing document on the fiscal year of the INVOICE
(BKPF-GJAHR). An invoice posted in December and cleared in January then loses its
'Clear Invoice' event (4,477 of Velora's 37,891 paid orders). Velora drops the fiscal year
from the first join and checks the clearing document's year against BSEG-AUGGJ instead.

usage:
  python3 apply_clearing_fix.py <template.json | template_dir | collector.sql>
    template.json   a file {"dataViews": {...}, "collectors": [{"bo", "name", "sql"}, ...]}
    template_dir    a folder with ec/Accounting__2._Clearing_Events.sql (layout of run_template.py)
    collector.sql   the SQL of "2. Clearing Events" copied from the pipeline editor
"""
import json, os, re, sys

HEADER = ("-- Velora fix of SAP's standard collector: the original joins the clearing document on the INVOICE's fiscal year\n"
          "-- (BKPF-GJAHR), so an invoice posted in December and paid in January loses its 'Clear Invoice' event.\n")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Accounting__2._Clearing_Events.sql')

# 1. the join of the clearing document: drop the invoice's fiscal year
OLD_JOIN = re.compile(r"(INNER JOIN CaseLink_AccountingClearing AS CaseLink ON bseg_bkpf_clearing\.mandt = CaseLink\.mandt"
                      r" AND bseg_bkpf_clearing\.bkpf_bukrs = CaseLink\.bkpf_bukrs"
                      r" AND bseg_bkpf_clearing\.bkpf_belnr = CaseLink\.bkpf_belnr_clearing)"
                      r" AND bseg_bkpf_clearing\.bkpf_gjahr = CaseLink\.bkpf_gjahr")
NEW_JOIN = (r"\1 -- Velora fix: the fiscal year of the clearing document is checked on the next join "
            r"(BSEG-AUGGJ), not taken from the invoice")
# 2. the join of the cleared line: check the clearing document's year against BSEG-AUGGJ
OLD_LINE = re.compile(r"(\n(\s*)INNER JOIN bseg_bkpf ON CaseLink\.mandt = bseg_bkpf\.mandt AND CaseLink\.bkpf_bukrs = bseg_bkpf\.bkpf_bukrs"
                      r" AND CaseLink\.bkpf_belnr = bseg_bkpf\.bkpf_belnr AND CaseLink\.bkpf_gjahr = bseg_bkpf\.bkpf_gjahr)\n")
NEW_LINE = (r"\1\n                         AND bseg_bkpf_clearing.bkpf_gjahr = bseg_bkpf.bseg_auggj "
            r"-- Velora fix: payments that cross the fiscal year\n")


def load(src):
    if os.path.isdir(src):
        return open(os.path.join(src, 'ec', 'Accounting__2._Clearing_Events.sql'), encoding='utf-8').read()
    if src.lower().endswith('.json'):
        j = json.load(open(src, encoding='utf-8'))
        hits = [c for c in j['collectors'] if c.get('bo') == 'Accounting' and c.get('name') == '2. Clearing Events']
        if len(hits) != 1:
            sys.exit('The template has no single collector "2. Clearing Events" in business object Accounting.')
        return hits[0]['sql']
    return open(src, encoding='utf-8').read()


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sql = load(sys.argv[1])
    if 'Velora fix' in sql:
        sys.exit('This SQL already contains the Velora fix.')
    sql, n1 = OLD_JOIN.subn(NEW_JOIN, sql, count=1)
    sql, n2 = OLD_LINE.subn(NEW_LINE, sql, count=1)
    if n1 != 1 or n2 != 1:
        sys.exit('The collector does not look like the template version described in Section 14.8 '
                 f'(join 1 found: {n1}, join 2 found: {n2}). Apply the change by hand as shown in the book.')
    with open(OUT, 'w', encoding='utf-8', newline='') as f:
        f.write(HEADER + sql)
    print('written', OUT)


if __name__ == '__main__':
    main()
