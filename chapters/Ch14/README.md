# Chapter 14 – Inside the SAP Tables

Companion files for *Building with SAP Signavio*. Velora Group SE is a fictional company; all data is fictional.

| File | What it is | Used in the book |
|---|---|---|
| Dummy SAP Tables/README.md | How to build the tables, run SAP's template locally, and reconcile the result | Sections 14.1, 14.10, 14.11 |
| Dummy SAP Tables/make_tables.js | Writes the 51 fictional SAP ECC tables (CSV, about 250 MB) for Velora's 41,300 orders to `tables/` and checks every table against `data/sap_tpl_hashes.json` (51 of 51 must match). Thin wrapper around `data/gen_o2c.js` and `data/gen_sap.js` | Section 14.11, Step 1 |
| Dummy SAP Tables/sap_o2c_ecc_template.json | **Not included.** SAP's template is SAP content and is not redistributed. The README explains how to take the 17 data views and 53 collectors from your own pipeline | Sections 14.4, 14.11 |
| Dummy SAP Tables/velora_ext/ | Velora's four extension collectors (Send Order Confirmation, Review Blocked Order, Send Invoice, Receive Incoming Payment) and `apply_clearing_fix.py`, which writes the fixed *2. Clearing Events* collector from your own copy of the template | Section 14.8, Table 14.5; Section 14.11, Step 4 |
| Dummy SAP Tables/run_template.py | Runs the template's data views and collectors plus the extensions on the tables (DuckDB with a thin Trino shim) | Section 14.10 |
| Dummy SAP Tables/reconcile_template.py | Rolls the item-level result up to the order and compares it with S13_O2C_EventLog.csv (Table 14.8) | Section 14.10 |
| Dummy SAP Tables/gen_sap.js → [`data/gen_sap.js`](../../data/gen_sap.js) | The generator that built the tables; kept once in `data/` with `gen_o2c.js`, `hash.js`, and `sap_tpl_hashes.json` | Section 14.11 |

The tables themselves are not in the repository; `make_tables.js` regenerates them in 15–30 seconds. Tested: 51 of 51 fingerprints match, and template + extensions + fix reproduce all 468,799 events of Table 14.8 (2,331,867 item-level events in 24 activities without *5. Goods Movements*).
