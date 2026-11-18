# data

Fictional data for *Building with SAP Signavio*. Velora Group SE is invented for the book.

| File | What it is |
|---|---|
| S13_O2C_EventLog.zip | `S13_O2C_EventLog.csv`: 41,300 sales orders, 468,799 events (Chapters 12–16) |
| S13_O2C_CaseAttributes.zip | `S13_O2C_CaseAttributes.csv`: one row per order (Chapters 12–16) |
| gen_o2c.js | Generator of both CSV files (deterministic; reproduces them byte for byte) |
| gen_sap.js | Generator of the 51 fictional SAP ECC tables of Chapter 14 from the two CSV files |
| hash.js, sap_tpl_hashes.json | Fingerprint function and the expected fingerprint of each table |

Build the SAP tables with `node "chapters/Ch14/Dummy SAP Tables/make_tables.js"`.
