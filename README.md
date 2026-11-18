# Building with SAP Signavio: Companion Files

Companion repository for the book **Building with SAP Signavio** by Sujit Kumar.

The book follows one fictional company through a year of process excellence with the SAP Signavio suite: from the first process model to a governed process house, a DMN credit decision, simulation, process mining on SAP ECC data, fit-to-standard for SAP S/4HANA, value tracking, and AI. The company is **Velora Group SE**, an invented manufacturer of compressors, pumps and fluid-handling systems headquartered in Düsseldorf, with sites in Brno and Pune (plant and Global Capability Center), whose order-to-cash process is the thread through every chapter. This repository holds the files the chapters use: importable BPMN and DMN models, the book's tables as CSV, a fictional event log with 41,300 sales orders, fictional SAP ECC tables, SQL and SiGNAL queries, and templates.

## What's inside

| Folder | Contents |
|---|---|
| [`chapters/`](chapters/) | Companion files per chapter (`ChNN/`): workbooks, documents, templates, and scripts named in each chapter's *Companion Files* box |
| [`models/`](models/README.md) | Ten BPMN 2.0 models and one DMN 1.3 decision, importable into SAP Signavio Process Manager, with PNG previews |
| [`data/`](data/) | The fictional O2C event log and case attributes (zipped CSV) and the generators behind the SAP-style tables |
| [`tables/`](tables/) | Every table printed in the book as CSV, per chapter and appendix |
| [`queries/`](queries/) | SQL and SiGNAL queries from Chapters 13 to 16 |
| [`tools/`](tools/README.md) | Python scripts that generate the BPMN and DMN models |
| [`validation/`](validation/README.md) | Checks for the models: schema, import, lint, rendering, and decision logic |

## Find the files for a chapter

Each chapter folder has a README that lists its files and the sections that use them.

| Chapter | Folder | Key files |
|---|---|---|
| 1. Three Versions of Order to Cash | [chapters/Ch01/](chapters/Ch01/README.md) | [`S01_Decision_Log.xlsx`](chapters/Ch01/S01_Decision_Log.xlsx), [`S01_Process_Charter.docx`](chapters/Ch01/S01_Process_Charter.docx), [book tables](tables/Ch01/) |
| 2. Designing the Velora Process House | [chapters/Ch02/](chapters/Ch02/README.md) | [`S02_Modeling_Conventions.docx`](chapters/Ch02/S02_Modeling_Conventions.docx), [`S02_Process_House.xlsx`](chapters/Ch02/S02_Process_House.xlsx), [book tables](tables/Ch02/) |
| 3. Standing Up the Workspace | [chapters/Ch03/](chapters/Ch03/README.md) | [`S03_Workspace_Setup.xlsx`](chapters/Ch03/S03_Workspace_Setup.xlsx), [book tables](tables/Ch03/) |
| 4. The First Model | [chapters/Ch04/](chapters/Ch04/README.md) | [`S04_Workshop_Template.xlsx`](chapters/Ch04/S04_Workshop_Template.xlsx), [`Receive_and_check_order.bpmn`](models/Receive_and_check_order.bpmn), [book tables](tables/Ch04/) |
| 5. Speaking BPMN | [chapters/Ch05/](chapters/Ch05/README.md) | [`S05_BPMN_Cheat_Sheet.pdf`](chapters/Ch05/S05_BPMN_Cheat_Sheet.pdf), [`Release_credit_block_Brno_as_is.bpmn`](models/Release_credit_block_Brno_as_is.bpmn), [book tables](tables/Ch05/) |
| 6. Structuring a Big Process | [chapters/Ch06/](chapters/Ch06/README.md) | [`S06_Design_Rules.pdf`](chapters/Ch06/S06_Design_Rules.pdf), [`O2C_overview_L2.bpmn`](models/O2C_overview_L2.bpmn), [`O2C_collaboration_L2.bpmn`](models/O2C_collaboration_L2.bpmn), [L3 models](models/README.md), [book tables](tables/Ch06/) |
| 7. One Dictionary, Two Sites | [chapters/Ch07/](chapters/Ch07/README.md) | [`S07_Dictionary_Import.xlsx`](chapters/Ch07/S07_Dictionary_Import.xlsx), [`S07_Variant_Decisions.xlsx`](chapters/Ch07/S07_Variant_Decisions.xlsx), [book tables](tables/Ch07/) |
| 8. Deciding with DMN | [chapters/Ch08/](chapters/Ch08/README.md) | [`S08_Credit_Test_Cases.xlsx`](chapters/Ch08/S08_Credit_Test_Cases.xlsx), [`S08_Credit_Check.dmn`](models/S08_Credit_Check.dmn), [book tables](tables/Ch08/) |
| 9. Publishing to Everyone | [chapters/Ch09/](chapters/Ch09/README.md) | [`S09_Feedback_Campaign.xlsx`](chapters/Ch09/S09_Feedback_Campaign.xlsx), [`S09_Hub_Configuration.xlsx`](chapters/Ch09/S09_Hub_Configuration.xlsx), [`S09_Iberia_Journey.xlsx`](chapters/Ch09/S09_Iberia_Journey.xlsx), [`S09_Key_User_Guide.pdf`](chapters/Ch09/S09_Key_User_Guide.pdf), [book tables](tables/Ch09/) |
| 10. Controlled Documentation | [chapters/Ch10/](chapters/Ch10/README.md) | [`S10_Audit_Checklist.pdf`](chapters/Ch10/S10_Audit_Checklist.pdf), [`S10_Governance_Workflow.xlsx`](chapters/Ch10/S10_Governance_Workflow.xlsx), [`Velora_Model_approval_ISO.bpmn`](models/Velora_Model_approval_ISO.bpmn), [book tables](tables/Ch10/) |
| 11. Simulate Before You Hire | [chapters/Ch11/](chapters/Ch11/README.md) | [`S11_Report_Examples.xlsx`](chapters/Ch11/S11_Report_Examples.xlsx), [`S11_Simulation_Scenarios.xlsx`](chapters/Ch11/S11_Simulation_Scenarios.xlsx), [book tables](tables/Ch11/) |
| 12. What the Data Says | [chapters/Ch12/](chapters/Ch12/README.md) | [`S13_O2C_EventLog.zip`](data/S13_O2C_EventLog.zip), [`S13_O2C_CaseAttributes.zip`](data/S13_O2C_CaseAttributes.zip), [book tables](tables/Ch12/) |
| 13. Getting the Data Out of ECC | [chapters/Ch13/](chapters/Ch13/README.md) | [`S13_Pipeline_Design.xlsx`](chapters/Ch13/S13_Pipeline_Design.xlsx), [`S13_Transformation_Examples.sql`](chapters/Ch13/S13_Transformation_Examples.sql), [`S13_Works_Council_Annex.docx`](chapters/Ch13/S13_Works_Council_Annex.docx), [`Ch13_queries.sql`](queries/Ch13_queries.sql), [book tables](tables/Ch13/) |
| 14. Inside the SAP Tables | [chapters/Ch14/](chapters/Ch14/README.md) | [`Dummy SAP Tables`](chapters/Ch14/Dummy%20SAP%20Tables/README.md), [`Ch14_queries.sql`](queries/Ch14_queries.sql), [release zip](#large-dataset), [book tables](tables/Ch14/) |
| 15. Investigating Order to Cash | [chapters/Ch15/](chapters/Ch15/README.md) | [`S15_DSO_Investigation_Plan.xlsx`](chapters/Ch15/S15_DSO_Investigation_Plan.xlsx), [`Ch15_queries.sql`](queries/Ch15_queries.sql), [`S13_O2C_EventLog.zip`](data/S13_O2C_EventLog.zip), [book tables](tables/Ch15/) |
| 16. Asking Better Questions with SiGNAL | [chapters/Ch16/](chapters/Ch16/README.md) | [`S16_Metrics_Export.json`](chapters/Ch16/S16_Metrics_Export.json), [`S16_Pipeline_Attributes.sql`](chapters/Ch16/S16_Pipeline_Attributes.sql), [`S16_SiGNAL_Queries.md`](chapters/Ch16/S16_SiGNAL_Queries.md), [`Ch16_queries.sql`](queries/Ch16_queries.sql), [book tables](tables/Ch16/) |
| 17. Seeing ECC Through S/4HANA Eyes | [chapters/Ch17/](chapters/Ch17/README.md) | [`S17_Guided_Analysis_Record.docx`](chapters/Ch17/S17_Guided_Analysis_Record.docx), [`S17_Insights_Findings.xlsx`](chapters/Ch17/S17_Insights_Findings.xlsx), [book tables](tables/Ch17/) |
| 18. Fit to Standard | [chapters/Ch18/](chapters/Ch18/README.md) | [`S18_FitToStandard_Log.xlsx`](chapters/Ch18/S18_FitToStandard_Log.xlsx), [`S18_Toolchain_Map.xlsx`](chapters/Ch18/S18_Toolchain_Map.xlsx), [`S18_Workshop_Agenda.docx`](chapters/Ch18/S18_Workshop_Agenda.docx), [book tables](tables/Ch18/) |
| 19. From Findings to Value | [chapters/Ch19/](chapters/Ch19/README.md) | [`S19_Portfolio_Review_Template.pptx`](chapters/Ch19/S19_Portfolio_Review_Template.pptx), [`S19_Value_Cases.xlsx`](chapters/Ch19/S19_Value_Cases.xlsx), [book tables](tables/Ch19/) |
| 20. AI That Earns Its Place | [chapters/Ch20/](chapters/Ch20/README.md) | [`S20_AI_Rules.docx`](chapters/Ch20/S20_AI_Rules.docx), [`S20_AI_Test_Log.xlsx`](chapters/Ch20/S20_AI_Test_Log.xlsx), [`S20_Agent_Design_Canvas.docx`](chapters/Ch20/S20_Agent_Design_Canvas.docx), [`S20_Agent_Test_Set.xlsx`](chapters/Ch20/S20_Agent_Test_Set.xlsx), [`S20_Brno_Agent_Intent.md`](chapters/Ch20/S20_Brno_Agent_Intent.md), [`S20_FieldService_Description.txt`](chapters/Ch20/S20_FieldService_Description.txt), [book tables](tables/Ch20/) |
| 21. Year One of Process Excellence | [chapters/Ch21/](chapters/Ch21/README.md) | [`S21_Board_Presentation.pptx`](chapters/Ch21/S21_Board_Presentation.pptx), [`S21_Decision_Log.xlsx`](chapters/Ch21/S21_Decision_Log.xlsx), [book tables](tables/Ch21/) |
| Appendix A. Administrator's Handbook | [chapters/App_A/](chapters/App_A/README.md) | [book tables](tables/App_A/) |
| Appendix B. Metrics Reference | [chapters/App_B/](chapters/App_B/README.md) | [book tables](tables/App_B/) |
| Appendix C. Notation and Reports Reference | [chapters/App_C/](chapters/App_C/README.md) | [book tables](tables/App_C/) |

## Quick start

**Import a process model into SAP Signavio Process Manager**

1. Download a `.bpmn` file from [`models/`](models/README.md).
2. In Process Manager, open the **Explorer**, select a folder, and choose **Import / Export > Import BPMN 2.0 XML**.
3. Select the file, confirm, open the model, and run **Check syntax**.

Use a trial or training workspace, never a production workspace. [models/README.md](models/README.md) lists the models by chapter and explains how to link the L2 subprocesses to their L3 models.

**Load the event log into SAP Signavio Process Intelligence**

1. Unzip [`data/S13_O2C_EventLog.zip`](data/S13_O2C_EventLog.zip) and [`data/S13_O2C_CaseAttributes.zip`](data/S13_O2C_CaseAttributes.zip).
2. In Process Intelligence, create a process and upload `S13_O2C_EventLog.csv` as the event log: *case_id* is the case ID, *activity* the activity, *timestamp* the timestamp.
3. Upload `S13_O2C_CaseAttributes.csv` as the attribute log with *case_id* as the case ID.

The first upload is described in Chapter 12 (Section 12.5); Chapter 13 replaces it with a data pipeline, and Chapter 14 rebuilds the same log from SAP tables.

**Run the SiGNAL queries**

Open the O2C process in Process Intelligence, create a chart or table widget, switch the editor to SiGNAL (Dashboard > **Create Widget** > **Charts and Tables**), and paste a query from [`queries/Ch15_queries.sql`](queries/Ch15_queries.sql) or [`queries/Ch16_queries.sql`](queries/Ch16_queries.sql). Chapters 15 and 16 explain each query and show Velora's result.

## Large dataset

The 51 fictional SAP ECC tables for Chapter 14 (about 250 MB as CSV) are too large for the repository. Download **`velora-sap-ecc-dataset-v1.zip`** (about 31 MB) from the [Releases page](https://github.com/KrSujit/building_with_signavio/releases).

The zip contains:

- `tables/`: the 51 tables (VBAK, VBAP, LIKP, LIPS, VBRK, VBRP, BKPF, BSEG, CDHDR, CDPOS, NAST, and the master and configuration tables) in the format the SAP Signavio extractor delivers.
- `gen_o2c.js`, `gen_sap.js`: the deterministic generators that built the tables.
- `make_tables.js`, `verify_hashes.js`, `hash.js`, `sap_tpl_hashes.json`: rebuild the tables and check each one against its fingerprint.
- `README.md`: format, contents, and verification steps.

You can also build the same tables without the download: run `node make_tables.js` in [`chapters/Ch14/Dummy SAP Tables/`](chapters/Ch14/Dummy%20SAP%20Tables/). The result is byte-identical.

## Validation

Every model is checked against the OMG schemas, imported with bpmn.io tools, linted, rendered, and, for the DMN decision, tested rule by rule. See [validation/README.md](validation/README.md) to run the checks yourself.

## Disclaimer

Velora Group SE, its people, customers, suppliers, and all figures in this repository are **fictional**. Any resemblance to real companies or persons is coincidental. The data contains no real customer or personal data.

SAP, SAP ECC, SAP S/4HANA, SAP Signavio, SAP LeanIX, and other SAP products and services mentioned are trademarks or registered trademarks of SAP SE (or an SAP affiliate company) in Germany and other countries. All other names may be trademarks of their respective owners. This repository and the book are independent works and are **not affiliated with, sponsored by, or endorsed by SAP SE**.

**SAP template content is not included.** Where the book uses SAP's standard content, for example the transformation template *Order to Cash (SAP ECC)* in Chapter 14, export it from your own SAP Signavio workspace. The chapter folders explain where your copy goes.

Screens and menu labels change between SAP Signavio releases. If yours differ, look for the concept rather than the exact label.

## License

This repository uses two licenses:

| What | License |
|---|---|
| Code and scripts (`tools/`, `validation/`, and `.js`, `.mjs`, `.py`, `.sql` files) | [MIT](LICENSE) |
| Data, models, tables, templates, previews, and documents | [CC BY 4.0](LICENSE-CONTENT) |

Code is under MIT so that you can reuse it in your own projects without conditions beyond the notice. Content is under CC BY 4.0 so that you can share and adapt it, including commercially, as long as you credit the source. Errata and questions are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md). Changes are listed in [CHANGELOG.md](CHANGELOG.md). To cite the book, use [CITATION.cff](CITATION.cff).

## Author

**Sujit Kumar**: [github.com/KrSujit](https://github.com/KrSujit)
