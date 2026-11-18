"""Regenerate the BPMN models (and the DMN decision) of "Building with SAP Signavio".

usage:
    python3 tools/mk_bpmn.py [--out DIR] [--png] [--bpmn-js PATH]

    --out DIR      output folder (default: models/ next to this tools/ folder)
    --png          also render a PNG preview of each BPMN model into DIR/previews/
                   (optional; needs: pip install playwright && playwright install chromium,
                   and bpmn-js: npm install bpmn-js)
    --bpmn-js PATH path to bpmn-viewer.production.min.js
                   (default: node_modules/bpmn-js/dist/bpmn-viewer.production.min.js
                   in the repository root, or the BPMN_JS environment variable)

Generation itself needs only the Python standard library.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import models  # noqa: E402
import dmn  # noqa: E402
from bpmn import lint  # noqa: E402

MODELS = {
    "Receive_and_check_order": models.receive_and_check,
    "Check_customer_credit": models.check_customer_credit,
    "Manage_credit": models.manage_credit,
    "Deliver_goods": models.deliver_goods,
    "Bill_customer": models.bill_customer,
    "Manage_receivables": models.manage_receivables,
    "O2C_overview_L2": models.overview,
    "O2C_collaboration_L2": lambda: models.overview(True),
    "Release_credit_block_Brno_as_is": models.brno_credit_block,
    "Velora_Model_approval_ISO": models.model_approval,
}


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def render(out, names, js_path):
    import asyncio
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        sys.exit("--png needs playwright: pip install playwright && playwright install chromium")
    if not os.path.isfile(js_path):
        sys.exit(f"bpmn-js not found at {js_path} (npm install bpmn-js, or pass --bpmn-js)")
    js = open(js_path, encoding="utf-8").read()
    prev = os.path.join(out, "previews")
    os.makedirs(prev, exist_ok=True)

    async def main():
        async with async_playwright() as p:
            b = await p.chromium.launch()
            pg = await b.new_page(viewport={"width": 2400, "height": 1100})
            await pg.set_content('<div id="c" style="width:2400px;height:1100px;background:#fff"></div>')
            await pg.add_script_tag(content=js)
            for k in names:
                xml = open(os.path.join(out, k + ".bpmn"), encoding="utf-8").read()
                r = await pg.evaluate("""async (x) => { if (window.v) window.v.destroy();
                    window.v = new BpmnJS({container: '#c'});
                    try { const r = await v.importXML(x); v.get('canvas').zoom('fit-viewport');
                          return r.warnings.map(w => w.message); } catch (e) { return ['ERR ' + e.message]; } }""", xml)
                print(f"  preview {k}.png  warnings: {r[:3] if r else 'none'}")
                await pg.screenshot(path=os.path.join(prev, k + ".png"))
            await b.close()

    asyncio.run(main())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "models"))
    ap.add_argument("--png", action="store_true")
    ap.add_argument("--bpmn-js", default=os.environ.get(
        "BPMN_JS", os.path.join(ROOT, "node_modules", "bpmn-js", "dist", "bpmn-viewer.production.min.js")))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for k, fn in MODELS.items():
        m = fn()
        problems = lint(m)
        write(os.path.join(a.out, k + ".bpmn"), m.xml())
        print(f"wrote {k}.bpmn  layout check: {'ok' if not problems else problems}")
    write(os.path.join(a.out, "S08_Credit_Check.dmn"), dmn.build())
    print("wrote S08_Credit_Check.dmn")
    if a.png:
        render(a.out, list(MODELS), a.bpmn_js)


if __name__ == "__main__":
    main()
