"""Small BPMN 2.0 XML writer with automatic diagram interchange (DI) layout.
Nodes are placed on a grid: column = position in the flow, lane = row."""
from xml.sax.saxutils import escape as esc
import re

SIZE = {"task": (120, 80), "sub": (120, 80), "call": (120, 80), "start": (30, 30), "end": (28, 28),
        "xor": (40, 40), "and": (40, 40), "or": (40, 40), "evgw": (40, 40), "timer": (30, 30), "msgcatch": (30, 30),
        "msgthrow": (30, 30), "msgend": (28, 28), "data": (90, 66), "store": (70, 60), "milestone": (30, 30)}
LANE_H, COL_W, X0, LANE_LABEL = 150, 165, 190, 30


def _id(s):
    return re.sub(r"[^A-Za-z0-9_]", "_", s)


class Model:
    def __init__(self, name, pid, lanes, doc="", pool=None, attrs=None, lane_h=150):
        self.LH = lane_h
        self.name, self.pid, self.lanes, self.doc = name, _id(pid), lanes, doc
        self.pool = pool or "Velora"
        self.nodes, self.flows, self.assocs, self.boundaries = [], [], [], []
        self.attrs = attrs or {}
        self.ext_pools, self.msgflows = [], []

    def n(self, nid, typ, name, lane, col, doc="", dy=0, called=None):
        self.nodes.append(dict(id=_id(nid), t=typ, name=name, lane=lane, col=col, doc=doc, dy=dy, called=called))
        return _id(nid)

    def f(self, a, b, name="", loop=False):
        self.flows.append(dict(id=f"F_{len(self.flows)+1}", a=_id(a), b=_id(b), name=name, loop=loop))

    def boundary(self, bid, name, attached, timer=True):
        self.boundaries.append(dict(id=_id(bid), name=name, att=_id(attached), timer=timer))
        return _id(bid)

    def data(self, did, name, lane, col, task, direction="out", store=False, dy=55):
        self.nodes.append(dict(id=_id(did), t="store" if store else "data", name=name, lane=lane, col=col, doc="", dy=dy, called=None))
        self.assocs.append(dict(id=f"A_{len(self.assocs)+1}", d=_id(did), task=_id(task), dir=direction))

    def external(self, name, above=True):
        self.ext_pools.append(dict(id=_id("P_" + name), name=name, above=above))

    def msg(self, a, b, name, off=30):
        self.msgflows.append(dict(id=f"M_{len(self.msgflows)+1}", a=_id(a), b=_id(b), name=name, off=off))

    # ---------- layout
    def _geom(self):
        top = 40 + 130 * sum(1 for p in self.ext_pools if p["above"])
        self.top = top
        g = {}
        for nd in self.nodes:
            w, h = SIZE[nd["t"]]
            li = self.lanes.index(nd["lane"])
            cx = round(X0 + nd["col"] * COL_W)
            cy = top + li * self.LH + self.LH / 2 + nd["dy"]
            g[nd["id"]] = (cx - w / 2, cy - h / 2, w, h)
        for bd in self.boundaries:
            x, y, w, h = g[bd["att"]]
            g[bd["id"]] = (x + w - 40, y + h - 15, 30, 30)
        maxcol = max(nd["col"] for nd in self.nodes)
        self.width = X0 + maxcol * COL_W + 120
        return g

    def _cands(self, g, a, b, loop):
        ax, ay, aw, ah = g[a]; bx, by, bw, bh = g[b]
        acx, acy, bcx, bcy = ax + aw / 2, ay + ah / 2, bx + bw / 2, by + bh / 2
        if any(bd["id"] == a for bd in self.boundaries):
            if bcy > acy: return [[(acx, ay + ah), (acx, bcy), (bx, bcy)]]
            return [[(acx, ay + ah), (acx, ay + ah + 20), (bx - 20, ay + ah + 20), (bx - 20, bcy), (bx, bcy)]]
        if loop or bcx < acx - 5:
            low = max(ay + ah, by + bh) + 28
            return [[(acx, ay + ah), (acx, low), (bcx, low), (bcx, by + bh)]]
        if abs(acy - bcy) < 2:
            return [[(ax + aw, acy), (bx, bcy)]]
        if abs(acx - bcx) < 2:
            return [[(acx, ay + ah if bcy > acy else ay), (bcx, by if bcy > acy else by + bh)]]
        GW = ("xor", "and", "or", "evgw")
        src = next((n for n in self.nodes if n["id"] == a), None)
        vert = [(acx, ay + ah if bcy > acy else ay), (acx, bcy), (bx, bcy)]
        horiz = [(ax + aw, acy), (bcx, acy), (bcx, by if bcy > acy else by + bh)]
        return [vert, horiz] if (src and src["t"] in GW) else [horiz, vert]

    def _wp(self, g, a, b, loop):
        key = (a, b)
        if not hasattr(self, "_routes"): self._routes = {}
        if key in self._routes: return self._routes[key]
        best, bs = None, None
        for k, c in enumerate(self._cands(g, a, b, loop)):
            sc = self._score(g, c, a, b) * 10 + k
            if bs is None or sc < bs: best, bs = c, sc
        self._routes[key] = best
        self._segs = getattr(self, "_segs", []) + [(best[i], best[i + 1]) for i in range(len(best) - 1)]
        return best

    def _score(self, g, wp, a, b):
        n = 0
        for i in range(len(wp) - 1):
            p, q = wp[i], wp[i + 1]
            for nid, r in g.items():
                if nid in (a, b): continue
                if any(bd["id"] == nid and bd["att"] in (a, b) for bd in self.boundaries): continue
                if any(bd["id"] in (a, b) and bd["att"] == nid for bd in self.boundaries): continue
                if _hit(p, q, r): n += 1
            for (u, v) in getattr(self, "_segs", []):
                if _overlap(p, q, u, v): n += 1
        return n

    # ---------- XML
    def xml(self):
        self._routes, self._segs = {}, []
        g = self._geom()
        tag = {"task": "task", "sub": "subProcess", "call": "callActivity", "start": "startEvent", "end": "endEvent",
               "xor": "exclusiveGateway", "and": "parallelGateway", "or": "inclusiveGateway", "evgw": "eventBasedGateway",
               "timer": "intermediateCatchEvent", "msgcatch": "intermediateCatchEvent", "msgthrow": "intermediateThrowEvent",
               "msgend": "endEvent", "milestone": "intermediateThrowEvent"}
        inc = {nd["id"]: [] for nd in self.nodes}; out = {nd["id"]: [] for nd in self.nodes}
        for bd in self.boundaries: inc[bd["id"]] = []; out[bd["id"]] = []
        for fl in self.flows: out[fl["a"]].append(fl["id"]); inc[fl["b"]].append(fl["id"])
        P = []
        P.append(f'<process id="{self.pid}" name="{esc(self.name)}" isExecutable="false">')
        if self.doc: P.append(f'  <documentation>{esc(self.doc)}</documentation>')
        P.append(f'  <laneSet id="LS_{self.pid}">')
        for li, ln in enumerate(self.lanes):
            refs = "".join(f"<flowNodeRef>{nd['id']}</flowNodeRef>" for nd in self.nodes if nd["lane"] == ln and nd["t"] not in ("data", "store"))
            refs += "".join(f"<flowNodeRef>{bd['id']}</flowNodeRef>" for bd in self.boundaries if next(n for n in self.nodes if n["id"] == bd["att"])["lane"] == ln)
            P.append(f'    <lane id="L_{self.pid}_{li}" name="{esc(ln)}">{refs}</lane>')
        P.append('  </laneSet>')
        for nd in self.nodes:
            t = nd["t"]
            if t == "data":
                P.append(f'  <dataObject id="DO_{nd["id"]}"/>')
                P.append(f'  <dataObjectReference id="{nd["id"]}" name="{esc(nd["name"])}" dataObjectRef="DO_{nd["id"]}"/>'); continue
            if t == "store":
                P.append(f'  <dataStoreReference id="{nd["id"]}" name="{esc(nd["name"])}"/>'); continue
            attrs = f' calledElement="{_id(nd["called"])}"' if (t == "call" and nd["called"]) else ""
            body = ""
            if nd["doc"]: body += f"<documentation>{esc(nd['doc'])}</documentation>"
            body += "".join(f"<incoming>{x}</incoming>" for x in inc[nd["id"]]) + "".join(f"<outgoing>{x}</outgoing>" for x in out[nd["id"]])
            if t == "timer": body += f'<timerEventDefinition id="TD_{nd["id"]}"/>'
            if t in ("msgcatch", "msgthrow", "msgend"): body += f'<messageEventDefinition id="MD_{nd["id"]}"/>'
            ins = [a for a in self.assocs if a["task"] == nd["id"] and a["dir"] == "in"]
            outs = [a for a in self.assocs if a["task"] == nd["id"] and a["dir"] == "out"]
            if ins: body += f'<property id="Prop_{nd["id"]}" name="__targetRef_placeholder"/>'
            for a in ins: body += f'<dataInputAssociation id="{a["id"]}"><sourceRef>{a["d"]}</sourceRef><targetRef>Prop_{nd["id"]}</targetRef></dataInputAssociation>'
            for a in outs: body += f'<dataOutputAssociation id="{a["id"]}"><targetRef>{a["d"]}</targetRef></dataOutputAssociation>'
            P.append(f'  <{tag[t]} id="{nd["id"]}" name="{esc(nd["name"])}"{attrs}>{body}</{tag[t]}>')
        for bd in self.boundaries:
            body = "".join(f"<outgoing>{x}</outgoing>" for x in out[bd["id"]])
            body += f'<timerEventDefinition id="TD_{bd["id"]}"/>' if bd["timer"] else ""
            P.append(f'  <boundaryEvent id="{bd["id"]}" name="{esc(bd["name"])}" attachedToRef="{bd["att"]}" cancelActivity="false">{body}</boundaryEvent>')
        for fl in self.flows:
            P.append(f'  <sequenceFlow id="{fl["id"]}" name="{esc(fl["name"])}" sourceRef="{fl["a"]}" targetRef="{fl["b"]}"/>')
        P.append('</process>')

        # collaboration
        C = [f'<collaboration id="C_{self.pid}">', f'  <participant id="P_{self.pid}" name="{esc(self.pool)}" processRef="{self.pid}"/>']
        for ep in self.ext_pools: C.append(f'  <participant id="{ep["id"]}" name="{esc(ep["name"])}"/>')
        for m in self.msgflows: C.append(f'  <messageFlow id="{m["id"]}" name="{esc(m["name"])}" sourceRef="{m["a"]}" targetRef="{m["b"]}"/>')
        C.append('</collaboration>')

        # DI
        D = [f'<bpmndi:BPMNDiagram id="D_{self.pid}" name="{esc(self.name)}"><bpmndi:BPMNPlane id="PL_{self.pid}" bpmnElement="C_{self.pid}">']
        H = self.LH * len(self.lanes)
        D.append(f'<bpmndi:BPMNShape id="S_P_{self.pid}" bpmnElement="P_{self.pid}" isHorizontal="true"><dc:Bounds x="40" y="{self.top}" width="{self.width}" height="{H}"/></bpmndi:BPMNShape>')
        for li, ln in enumerate(self.lanes):
            D.append(f'<bpmndi:BPMNShape id="S_L_{self.pid}_{li}" bpmnElement="L_{self.pid}_{li}" isHorizontal="true"><dc:Bounds x="{40+LANE_LABEL}" y="{self.top+li*self.LH}" width="{self.width-LANE_LABEL}" height="{self.LH}"/></bpmndi:BPMNShape>')
        ya, yb = 40, self.top + H + 40
        pg = {}
        for ep in self.ext_pools:
            y = ya if ep["above"] else yb
            if ep["above"]: ya += 130
            else: yb += 130
            pg[ep["id"]] = (40, y, self.width, 90)
            D.append(f'<bpmndi:BPMNShape id="S_{ep["id"]}" bpmnElement="{ep["id"]}" isHorizontal="true"><dc:Bounds x="40" y="{y}" width="{self.width}" height="90"/></bpmndi:BPMNShape>')
        for nid, (x, y, w, h) in g.items():
            extra = ' isMarkerVisible="true"' if any(n["id"] == nid and n["t"] == "xor" for n in self.nodes) else ""
            exp = ' isExpanded="false"' if any(n["id"] == nid and n["t"] == "sub" for n in self.nodes) else ""
            D.append(f'<bpmndi:BPMNShape id="S_{nid}" bpmnElement="{nid}"{extra}{exp}><dc:Bounds x="{x:.0f}" y="{y:.0f}" width="{w}" height="{h}"/></bpmndi:BPMNShape>')
        for fl in self.flows:
            wp = "".join(f'<di:waypoint x="{x:.0f}" y="{y:.0f}"/>' for x, y in self._wp(g, fl["a"], fl["b"], fl["loop"]))
            D.append(f'<bpmndi:BPMNEdge id="E_{fl["id"]}" bpmnElement="{fl["id"]}">{wp}</bpmndi:BPMNEdge>')
        for a in self.assocs:
            dx, dy, dw, dh = g[a["d"]]; tx, ty, tw, th = g[a["task"]]
            if abs((dy + dh / 2) - (ty + th / 2)) < 60 and dx + dw < tx:
                p1, p2 = (dx + dw, dy + dh / 2), (tx, dy + dh / 2 if ty < dy + dh / 2 < ty + th else ty + th / 2)
            elif dy > ty + th: p1, p2 = (dx + dw / 2, dy), (tx + tw / 2, ty + th)
            elif dy + dh < ty: p1, p2 = (dx + dw / 2, dy + dh), (tx + tw / 2, ty)
            else: p1, p2 = (dx + dw / 2, dy), (tx + tw / 2, ty + th)
            if a["dir"] == "out": p1, p2 = p2, p1
            D.append(f'<bpmndi:BPMNEdge id="E_{a["id"]}" bpmnElement="{a["id"]}"><di:waypoint x="{p1[0]:.0f}" y="{p1[1]:.0f}"/><di:waypoint x="{p2[0]:.0f}" y="{p2[1]:.0f}"/></bpmndi:BPMNEdge>')
        for m in self.msgflows:
            def anchor(i):
                if i in pg: x, y, w, h = pg[i]; return (None, y, h)
                x, y, w, h = g[i]; return (x + w / 2, y, h)
            sa, sb = anchor(m["a"]), anchor(m["b"])
            if sa[0] is None and sb[0] is None:
                x = 40 + self.width - 120
            else:
                x = (sa[0] if sa[0] is not None else sb[0]) + m["off"]
            y1 = sa[1] + sa[2] if sa[1] < sb[1] else sa[1]
            y2 = sb[1] if sa[1] < sb[1] else sb[1] + sb[2]
            D.append(f'<bpmndi:BPMNEdge id="E_{m["id"]}" bpmnElement="{m["id"]}"><di:waypoint x="{x:.0f}" y="{y1:.0f}"/><di:waypoint x="{x:.0f}" y="{y2:.0f}"/></bpmndi:BPMNEdge>')
        D.append('</bpmndi:BPMNPlane></bpmndi:BPMNDiagram>')
        head = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<!-- Building with SAP Signavio - companion file. Fictional company Velora Group SE. '
                'Import in SAP Signavio Process Manager: Explorer > Import > BPMN 2.0 XML. -->\n'
                '<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" '
                'xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" '
                f'id="Defs_{self.pid}" targetNamespace="http://velora.example/bpmn" exporter="building_with_signavio" exporterVersion="1.0">')
        return head + "\n" + "\n".join(C) + "\n" + "\n".join(P) + "\n" + "\n".join(D) + "\n</definitions>\n"


def _hit(p, q, r):
    x, y, w, h = r; x -= 4; y -= 4; w += 8; h += 8
    (x1, y1), (x2, y2) = p, q
    if abs(y1 - y2) < 1: return y < y1 < y + h and max(min(x1, x2), x) < min(max(x1, x2), x + w)
    if abs(x1 - x2) < 1: return x < x1 < x + w and max(min(y1, y2), y) < min(max(y1, y2), y + h)
    return False


def _overlap(p, q, u, v):
    if abs(p[1] - q[1]) < 1 and abs(u[1] - v[1]) < 1 and abs(p[1] - u[1]) < 3:
        return min(max(p[0], q[0]), max(u[0], v[0])) - max(min(p[0], q[0]), min(u[0], v[0])) > 6
    if abs(p[0] - q[0]) < 1 and abs(u[0] - v[0]) < 1 and abs(p[0] - u[0]) < 3:
        return min(max(p[1], q[1]), max(u[1], v[1])) - max(min(p[1], q[1]), min(u[1], v[1])) > 6
    return False


def lint(m):
    """Report flows that cross shapes, flows that overlay each other, and overlapping shapes."""
    m._routes, m._segs = {}, []
    g = m._geom(); issues = []
    def hit(p, q, r):
        x, y, w, h = r; x -= 4; y -= 4; w += 8; h += 8
        (x1, y1), (x2, y2) = p, q
        if abs(y1 - y2) < 1:  # horizontal
            return y < y1 < y + h and max(min(x1, x2), x) < min(max(x1, x2), x + w)
        if abs(x1 - x2) < 1:
            return x < x1 < x + w and max(min(y1, y2), y) < min(max(y1, y2), y + h)
        return False
    for fl in m.flows:
        wp = m._wp(g, fl["a"], fl["b"], fl["loop"])
        for k in range(len(wp) - 1):
            for nid, r in g.items():
                if nid in (fl["a"], fl["b"]): continue
                if any(b["id"] == nid and b["att"] in (fl["a"], fl["b"]) for b in m.boundaries): continue
                if any(b["id"] in (fl["a"], fl["b"]) and b["att"] == nid for b in m.boundaries): continue
                if hit(wp[k], wp[k + 1], r): issues.append(f"flow {fl['a']}->{fl['b']} crosses {nid}")
    segs = []
    for fl in m.flows:
        wp = m._wp(g, fl["a"], fl["b"], fl["loop"])
        for k in range(len(wp) - 1):
            for (u, v, o) in segs:
                if o != fl["id"] and _overlap(wp[k], wp[k + 1], u, v): issues.append(f"flow {fl['a']}->{fl['b']} overlays another flow")
            segs.append((wp[k], wp[k + 1], fl["id"]))
    ids = list(g)
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a, b = g[ids[i]], g[ids[j]]
            if any(bd["id"] in (ids[i], ids[j]) for bd in m.boundaries): continue
            if a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]:
                issues.append(f"shapes overlap {ids[i]} / {ids[j]}")
    return issues
