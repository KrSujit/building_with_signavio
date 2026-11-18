"""S08_Credit_Check.dmn: DMN 1.3 with DRD layout (DMNDI)."""
from xml.sax.saxutils import escape as e

RISK = [("<= 5", ">= 3", '"Low"'), ("<= 5", "< 3", '"Medium"'), ("(5..20]", "-", '"Medium"'), ("> 20", "-", '"High"')]
REL = [('"Low"', "<= 20", "-", "false", "Release", "Old limits are the main cause of blocks"),
       ('"Low"', "> 20", "true", "false", "Release with notice to Sales", "Insurer covers the risk"),
       ('"Low"', "> 20", "false", "-", "Review by analyst", ""),
       ('"Low"', "<= 20", "-", "true", "Review by analyst", "Disputes first"),
       ('"Medium"', "<= 10", "-", "false", "Release with notice to Sales", ""),
       ('"Medium"', "> 10", "-", "-", "Review by analyst", ""),
       ('"Medium"', "<= 10", "-", "true", "Review by analyst", ""),
       ('"High"', "-", "-", "-", "Review by analyst", "Analyst may reject"),
       ('"Low"', "> 20", "true", "true", "Review by analyst", "Disputes first (rule added after the gap check, Section 8.7)")]

def ent(v): return f"<text>{e(v)}</text>" if v != "-" else "<text>-</text>"

def build():
    X = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<!-- Building with SAP Signavio - companion file S08. Fictional company Velora Group SE. '
         'Velora Credit Policy version 1 incl. the rule added in Section 8.7. Import: Explorer > Import > DMN. -->',
         '<definitions xmlns="https://www.omg.org/spec/DMN/20191111/MODEL/" xmlns:dmndi="https://www.omg.org/spec/DMN/20191111/DMNDI/" '
         'xmlns:dc="http://www.omg.org/spec/DMN/20180521/DC/" xmlns:di="http://www.omg.org/spec/DMN/20180521/DI/" '
         'id="Decide_credit_release_defs" name="Decide credit release" namespace="http://velora.example/dmn">']
    inputs = [("in_dpd", "Days past due (average, 12 months)", "number"), ("in_years", "Years as customer", "number"),
              ("in_over", "Amount over credit limit (%)", "number"), ("in_ins", "Credit insured", "boolean"), ("in_disp", "Open disputes", "boolean")]
    for i, n, t in inputs:
        X.append(f'  <inputData id="{i}" name="{e(n)}"><variable id="v_{i}" name="{e(n)}" typeRef="{t}"/></inputData>')
    X.append('  <knowledgeSource id="ks_policy" name="Velora Credit Policy"><description>Owner: Head of Credit, with the CFO. Version 1.</description></knowledgeSource>')
    X.append('  <knowledgeSource id="ks_ins" name="Credit insurer limit"/>')
    # risk class
    X.append('  <decision id="d_risk" name="Determine customer risk class"><variable id="v_risk" name="Risk class" typeRef="string"/>')
    X.append('    <informationRequirement id="ir1"><requiredInput href="#in_dpd"/></informationRequirement>')
    X.append('    <informationRequirement id="ir2"><requiredInput href="#in_years"/></informationRequirement>')
    X.append('    <decisionTable id="dt_risk" hitPolicy="UNIQUE">')
    X.append('      <input id="i_r1" label="Days past due (average, 12 months)"><inputExpression id="ie_r1" typeRef="number"><text>Days past due (average, 12 months)</text></inputExpression></input>')
    X.append('      <input id="i_r2" label="Years as customer"><inputExpression id="ie_r2" typeRef="number"><text>Years as customer</text></inputExpression></input>')
    X.append('      <output id="o_r" label="Risk class" name="Risk class" typeRef="string"><outputValues><text>"Low","Medium","High"</text></outputValues></output>')
    for k, (a, b, o) in enumerate(RISK, 1):
        X.append(f'      <rule id="r_risk_{k}"><inputEntry id="r{k}a">{ent(a)}</inputEntry><inputEntry id="r{k}b">{ent(b)}</inputEntry><outputEntry id="r{k}o"><text>{e(o)}</text></outputEntry></rule>')
    X.append('    </decisionTable>\n  </decision>')
    # release
    X.append('  <decision id="d_rel" name="Decide credit release"><variable id="v_rel" name="Release decision" typeRef="string"/>')
    X.append('    <informationRequirement id="ir3"><requiredDecision href="#d_risk"/></informationRequirement>')
    for k, i in enumerate(["in_over", "in_ins", "in_disp"], 4):
        X.append(f'    <informationRequirement id="ir{k}"><requiredInput href="#{i}"/></informationRequirement>')
    X.append('    <authorityRequirement id="ar1"><requiredAuthority href="#ks_policy"/></authorityRequirement>')
    X.append('    <authorityRequirement id="ar2"><requiredAuthority href="#ks_ins"/></authorityRequirement>')
    X.append('    <decisionTable id="dt_rel" hitPolicy="UNIQUE">')
    for k, (lab, t) in enumerate([("Risk class", "string"), ("Amount over credit limit (%)", "number"), ("Credit insured", "boolean"), ("Open disputes", "boolean")], 1):
        X.append(f'      <input id="i_c{k}" label="{e(lab)}"><inputExpression id="ie_c{k}" typeRef="{t}"><text>{e(lab)}</text></inputExpression>' +
                 ('<inputValues><text>"Low","Medium","High"</text></inputValues>' if k == 1 else '') + '</input>')
    X.append('      <output id="o_rel" label="Release decision" name="Release decision" typeRef="string"><outputValues><text>"Release","Release with notice to Sales","Review by analyst","Reject"</text></outputValues></output>')
    for k, (a, b, c, d, o, ann) in enumerate(REL, 1):
        X.append(f'      <rule id="r_rel_{k}">' + (f'<description>{e(ann)}</description>' if ann else '') +
                 f'<inputEntry id="c{k}a">{ent(a)}</inputEntry><inputEntry id="c{k}b">{ent(b)}</inputEntry><inputEntry id="c{k}c">{ent(c)}</inputEntry><inputEntry id="c{k}d">{ent(d)}</inputEntry>'
                 f'<outputEntry id="c{k}o"><text>"{e(o)}"</text></outputEntry></rule>')
    X.append('    </decisionTable>\n  </decision>')
    # DI
    B = {"d_rel": (380, 40, 200, 70), "d_risk": (140, 220, 200, 70), "in_dpd": (20, 420, 200, 56), "in_years": (250, 420, 180, 56),
         "in_over": (500, 330, 200, 56), "in_ins": (720, 330, 180, 56), "in_disp": (720, 220, 180, 56), "ks_policy": (780, 50, 210, 60), "ks_ins": (30, 120, 210, 60)}
    edges = [("ir1", "in_dpd", "d_risk"), ("ir2", "in_years", "d_risk"), ("ir3", "d_risk", "d_rel"), ("ir4", "in_over", "d_rel"),
             ("ir5", "in_ins", "d_rel"), ("ir6", "in_disp", "d_rel"), ("ar1", "ks_policy", "d_rel"), ("ar2", "ks_ins", "d_rel")]
    X.append('  <dmndi:DMNDI><dmndi:DMNDiagram id="DRD_1" name="Decide credit release">')
    for k, (x, y, w, h) in B.items():
        X.append(f'    <dmndi:DMNShape id="S_{k}" dmnElementRef="{k}"><dc:Bounds x="{x}" y="{y}" width="{w}" height="{h}"/></dmndi:DMNShape>')
    def c(k, top):
        x, y, w, h = B[k]; return (x + w / 2, y if top else y + h)
    for eid, a, b in edges:
        (x1, y1), (x2, y2) = c(a, True), c(b, False)
        if a.startswith("ks"):
            x1, y1 = (B[a][0], B[a][1] + 30) if a == "ks_policy" else (B[a][0] + B[a][2], B[a][1] + 30)
            x2, y2 = (B[b][0] + B[b][2], B[b][1] + 35) if a == "ks_policy" else (B[b][0], B[b][1] + 35)
        if a == "in_disp": x1, y1 = B[a][0], B[a][1] + 28; x2, y2 = B[b][0] + B[b][2], B[b][1] + 60
        X.append(f'    <dmndi:DMNEdge id="E_{eid}" dmnElementRef="{eid}"><di:waypoint x="{x1:.0f}" y="{y1:.0f}"/><di:waypoint x="{x2:.0f}" y="{y2:.0f}"/></dmndi:DMNEdge>')
    X.append('  </dmndi:DMNDiagram></dmndi:DMNDI>\n</definitions>\n')
    return "\n".join(X)

if __name__ == "__main__":
    import os, sys
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "S08_Credit_Check.dmn"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(build())
