# Chapter 13 – Getting the Data Out of ECC

Companion files for *Building with SAP Signavio*. Velora Group SE is a fictional company; all data is fictional.

| File | What it is | Used in the book |
|---|---|---|
| S13_Pipeline_Design.xlsx | Pipeline design workbook: scoping answers (Table 13.1), table list with filters, delta fields and pseudonymized fields, the 51-table list (Table 14.1), event definitions for all 19 activities with expected counts, the one-page list of template changes, load checks, incomplete-case rules, pipeline components | Sections 13.1, 13.3, 13.4, 13.6; build in Section 13.8 |
| S13_Transformation_Examples.sql | Simplified transformation scripts (Trino SQL) for Create sales order, Block for credit, Release credit block (as printed in Section 13.4), Create delivery, Post goods issue, Create invoice, Clear payment, Change price after credit release, the Case status attribute, and the three load checks. Tested on the fictional SAP tables of Chapter 14: each event script reproduces the count in S13_O2C_EventLog.csv | Section 13.4; build in Section 13.8, Steps 3–4 |
| S13_Works_Council_Annex.docx | Example annex to an IT agreement for process mining with pseudonymized data: scope, data, pseudonymization, the three agreed rules, resolving a pseudonym, event and attribute list, request form | Section 13.5; PD-044 |
