# Dummy SAP Tables

*Building with SAP Signavio – companion folder for Chapter 14*

This folder lets you rebuild Velora's order-to-cash event log from SAP ECC tables, without an SAP system, as described in Chapter 14. **All data is fictional.** Velora Group SE, its customers, users, and documents don't exist. The table and field names, formats, and document links follow SAP ECC and the extractor format described in Section 14.5; the content is simplified (one company code per sales organization, no taxes, no batches).

## What's in the folder

| File | What it is | Used in |
|---|---|---|
| `make_tables.js` | Writes the 51 SAP ECC tables (CSV) for Velora's 41,300 orders to `tables/` and checks each one against its fingerprint | Section 14.11, Step 1 |
| `velora_ext/Velora__1_Send_Order_Confirmation.sql` | Extension collector: NAST, application V1, output type BA00, status 1 | Section 14.8, Table 14.5 |
| `velora_ext/Velora__2_Review_Blocked_Order.sql` | Extension collector: STXH credit review note (text object VBBK, text ID ZCRV) | Section 14.8 |
| `velora_ext/Velora__3_Send_Invoice.sql` | Extension collector: NAST, application V3, output type RD00, status 1 | Section 14.8, Table 14.5 |
| `velora_ext/Velora__4_Receive_Incoming_Payment.sql` | Extension collector: bank statement (BKPF document type ZE, FF_5), reference = invoice | Section 14.8 |
| `velora_ext/apply_clearing_fix.py` | Writes Velora's fixed copy of SAP's *2. Clearing Events* from **your own** copy of the template | Section 14.8, Section 14.11 Step 4 |
| `run_template.py` | Runs the template's data views and collectors, plus the extensions, on the tables (DuckDB) | Section 14.10 |
| `reconcile_template.py` | Rolls the item-level result up to the order and compares it with `S13_O2C_EventLog.csv` (Table 14.8) | Section 14.10 |
| `gen_sap.js` | The generator that builds the tables. It lives in the repository's `data/` folder (`data/gen_sap.js`), together with `gen_o2c.js`, `hash.js`, and `sap_tpl_hashes.json`; `make_tables.js` loads it from there | Section 14.11 |

## What's not in the folder, and why

**SAP's template (`sap_o2c_ecc_template.json`)** and **SAP's original collector SQL** are SAP content and are not redistributed here. You take them from your own SAP Signavio workspace:

1. Create a pipeline from the template *Order to Cash (SAP ECC)* (Section 14.11, Step 2). It contains 17 data views and 53 collectors in five business objects.
2. Copy the SQL into a folder `template/` with this layout, which `run_template.py` reads:
   - `template/dv/<data view name>.sql` for each of the 17 data views, for example `template/dv/CaseLink.sql`.
   - `template/ec/<Business object>__<Collector name>.sql` for each collector, with spaces replaced by `_` and `/` by `-`, for example `template/ec/Accounting__2._Clearing_Events.sql` and `template/ec/Billing__1._Create-Cancel_Invoice.sql`.
3. If you already have the template as one JSON file with the keys `dataViews` (name → SQL) and `collectors` (a list of objects with `bo`, `name`, `sql`, and optionally `enabled`), you can pass that file instead of the folder.

Leave out *5. Goods Movements* (business object *Delivery*) when you copy, as Velora disables it (PD-046).

## Step by step

You need Node.js 18 or later, Python 3.9 or later, and the DuckDB Python package (`pip install duckdb`). The tables take about 250 MB of disk space.

```bash
# 1. Build and check the 51 tables (about 15-30 seconds)
node make_tables.js                       # writes ./tables/*.csv, ends with "51 of 51 tables match"

# 2. Create Velora's fixed clearing collector from your own copy of the template
python3 velora_ext/apply_clearing_fix.py template/          # or: template.json
#    -> writes velora_ext/Accounting__2._Clearing_Events.sql

# 3. Run the template unchanged, plus the Velora extensions and the fix
python3 run_template.py tables template/ out velora_ext     # or: template.json instead of template/

# 4. Reconcile with Velora's event log (unzip data/S13_O2C_EventLog.zip first)
python3 reconcile_template.py out/template_eventlog.csv ../../../data/S13_O2C_EventLog.csv
```

`run_template.py` runs SAP's Trino SQL in DuckDB with a thin shim for a few function names (`from_unixtime`, `date_add`, `date`, `is_nan`, `parse_datetime`, `concat`); it doesn't change the logic. A Velora file in `velora_ext/` with the same name as a template collector replaces it, which is how the fixed clearing collector takes the place of SAP's.

## What you should see

`make_tables.js` reports **51 of 51 tables match their fingerprint**. Row counts match Table 14.1, for example VBAK 41,300, VBAP 180,389, CDHDR 139,053, LIKP 55,066, VBRK 46,922, BKPF 125,789, and STXH 9,506.

`reconcile_template.py` reproduces Table 14.8: every activity in the *Velora log*, *From SAP tables*, and *Same order and time* columns has the same count, for example *Create sales order* 41,300, *Block for credit* 12,109, *Clear payment* 37,891. Without the fix (skip step 2), *Clear payment* drops to 33,414.

## If something goes wrong

| Message | Cause | Fix |
|---|---|---|
| `Cannot find gen_o2c.js, gen_sap.js ...` | The script was moved out of the repository | Keep it in `chapters/Ch14/Dummy SAP Tables`, or copy the four files from `data/` next to it |
| `FAIL <table>` in `make_tables.js` | A modified generator, or a Node.js version older than 18 | Restore `data/gen_sap.js` from the repository; update Node.js |
| `JavaScript heap out of memory` | Not enough memory for Node.js | `node --max-old-space-size=4096 make_tables.js` |
| `The collector does not look like the template version ...` | Your template version differs from the one in the book | Apply the two-line change from Section 14.8 by hand |
| `ModuleNotFoundError: duckdb` | DuckDB not installed | `pip install duckdb` |
