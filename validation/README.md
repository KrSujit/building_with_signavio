# Validation of the BPMN and DMN companion files

Every model file in this repository is checked with independent tools before release.

| Check | Tool | What it proves |
|---|---|---|
| XML schema | OMG BPMN 2.0 and DMN 1.3 XSD (lxml) | The file is valid BPMN 2.0 / DMN 1.3 XML |
| Import | bpmn-moddle and dmn-moddle (bpmn.io) | The model loads without warnings in bpmn.io tools |
| Rendering | bpmn-js and dmn-js (bpmn.io) | The diagram interchange (layout) is complete and renders |
| Lint | bpmnlint, `recommended` rules | No disconnected elements, no implicit splits or joins, no duplicate flows, no overlapping elements |
| Layout | own check (`tools/bpmn.py`, `lint()`) | No sequence flow crosses a shape or lies on another flow |
| Decision logic | own FEEL unary-test evaluator | Every boundary case matches exactly one rule (hit policy UNIQUE); expected results for the cases in Chapter 8 |
| Target tool | SAP Signavio Process Manager: Check syntax, SAP Signavio Best Practices | Imports and passes the checks the book uses |

## Known, intentional lint findings

`start-event-required` and `end-event-required` are reported for the collapsed subprocesses in *Order to Cash – overview (L2)*, *Order to Cash – collaboration (L2)*, and *Manage credit*. These subprocesses are deliberately empty: in SAP Signavio each one links to its own L3 diagram (Chapter 6). SAP Signavio's own checks accept this.

## Run the checks yourself

```bash
npm install bpmn-moddle dmn-moddle bpmnlint
node validation/lint.mjs models/

pip install lxml
python3 validation/dmn_test.py            # checks models/S08_Credit_Check.dmn

python3 tools/mk_bpmn.py --out /tmp/check  # regenerate; files must be identical to models/
```

See [tools/README.md](../tools/README.md) for the generators.
