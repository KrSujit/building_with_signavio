// Velora dummy SAP ECC tables for Order to Cash, built to the spec of SAP Signavio's
// standard template "Order to Cash (SAP ECC)" (deterministic).
// Input: the output of genO2C() (events CSV + cases CSV). Output: { table: csvString }.
// Format = what the Signavio SAP extractor delivers: lower-case table and column names,
// DATS fields as epoch milliseconds (midnight UTC), TIMS fields as milliseconds since midnight,
// NUMC/CHAR keys as strings with leading zeros. Works in Node and in the browser.
function genSAP(o2c) {
  let s = 20260214;
  const rnd = () => { s = (Math.imul(s, 1103515245) + 12345) >>> 0; return s / 4294967296; };
  const choice = (a) => a[Math.floor(rnd() * a.length)];
  const randint = (a, b) => a + Math.floor(rnd() * (b - a + 1));
  const p2 = (n) => String(n).padStart(2, '0');
  const toMs = (ts) => Date.UTC(+ts.slice(0, 4), +ts.slice(5, 7) - 1, +ts.slice(8, 10), +ts.slice(11, 13), +ts.slice(14, 16), +ts.slice(17, 19));
  const fmt = (ms) => { const d = new Date(ms); return d.getUTCFullYear() + '-' + p2(d.getUTCMonth() + 1) + '-' + p2(d.getUTCDate()) + ' ' + p2(d.getUTCHours()) + ':' + p2(d.getUTCMinutes()) + ':' + p2(d.getUTCSeconds()); };
  const DAY = 86400000;
  const DD = (ts) => String(Date.UTC(+ts.slice(0, 4), +ts.slice(5, 7) - 1, +ts.slice(8, 10)));      // DATS -> epoch ms
  const TT = (ts) => String(((+ts.slice(11, 13) * 60 + +ts.slice(14, 16)) * 60 + +ts.slice(17, 19)) * 1000); // TIMS -> ms
  const ymd = (ts) => ts.slice(0, 4) + ts.slice(5, 7) + ts.slice(8, 10);
  const plusSec = (ts, sec) => fmt(toMs(ts) + sec * 1000);
  const parseCSV = (line) => { const out = []; let cur = '', q = false; for (const ch of line) { if (ch === '"') q = !q; else if (ch === ',' && !q) { out.push(cur); cur = ''; } else cur += ch; } out.push(cur); return out; };
  const esc = (v) => { v = v == null ? '' : String(v); return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; };
  const f2 = (x) => x.toFixed(2), f3 = (x) => x.toFixed(3);
  const U = (u) => u.toUpperCase();

  // ---------------- inputs
  const cases = {};
  const cl = o2c.cases.split('\n'); const ch = cl[0].split(',');
  for (let i = 1; i < cl.length; i++) { if (!cl[i]) continue; const v = parseCSV(cl[i]); const r = {}; ch.forEach((h, j) => r[h] = v[j]); cases[r.case_id] = r; }
  const EV = {};
  const el = o2c.events.split('\n');
  for (let i = 1; i < el.length; i++) { if (!el[i]) continue; const v = el[i].split(','); (EV[v[0]] = EV[v[0]] || []).push([v[2], i, v[1], v[3], v[4]]); }

  // ---------------- table layouts (template columns + a few Velora extras, marked *)
  const COLS = {
    // master data and configuration
    kna1: 'mandt,kunnr,name1,land1,ort01,ktokd,vbund',
    knvv: 'mandt,kunnr,vkorg,vtweg,spart,kdgrp,zterm',                              // * customer segment
    vusr02_header: 'mandt,bname,ustyp',
    t001: 'mandt,bukrs,butxt,land1,waers',
    t001k: 'mandt,bwkey,bukrs',
    t001w: 'mandt,werks,name1',
    tvko: 'mandt,vkorg,bukrs',
    tvkot: 'mandt,spras,vkorg,vtext',
    tvkbt: 'mandt,spras,vkbur,bezei',
    tvak: 'mandt,auart,kalvg',
    tvakt: 'mandt,spras,auart,bezei',
    tvap: 'mandt,pstyv,prsfd',
    tvapt: 'mandt,spras,pstyv,vtext',
    tvagt: 'mandt,spras,abgru,bezei',
    tvaut: 'mandt,spras,augru,bezei',
    tvlkt: 'mandt,spras,lfart,vtext',
    tvlst: 'mandt,spras,lifsp,vtext',
    tvfst: 'mandt,spras,faksp,vtext',
    t023t: 'mandt,spras,matkl,wgbez',
    makt: 'mandt,matnr,spras,maktx',
    t003t: 'mandt,spras,blart,ltext',
    tbslt: 'mandt,spras,bschl,umskz,ltext',
    t156ht: 'mandt,spras,bwart,btext',
    tcurc: 'mandt,waers,isocd',
    tcurx: 'currkey,currdec',
    tcurr: 'mandt,kurst,fcurr,tcurr,gdatu,ukurs,ffact,tfact',
    tcurf: 'mandt,kurst,fcurr,tcurr,gdatu,ffact,tfact',
    ddftx: 'tabname,fieldname,ddlanguage,domname,scrtext_m',
    dd07t: 'domname,ddlanguage,as4local,domvalue_l,ddtext',
    // sales
    vbak: 'mandt,vbeln,erdat,erzet,ernam,aedat,audat,auart,vbtyp,vkorg,vtweg,spart,vkbur,kunnr,augru,lifsk,faksk,waerk,netwr,vdatu,knumv',
    vbap: 'mandt,vbeln,posnr,matnr,arktx,matkl,pstyv,kwmeng,kbmeng,vrkme,netpr,netwr,werks,abgru,vgbel,vgpos,erdat,erzet,ernam',
    vbep: 'mandt,vbeln,posnr,etenr,edatu,ezeit,wmeng,bmeng,mbdat,mbuhr,wadat,wauhr,banfn,bnfpo',
    stxh: 'mandt,tdobject,tdname,tdid,tdspras,tdtitle,tdfuser,tdfdate,tdftime,tdluser,tdldate,tdltime', // * credit review note
    vbss: 'mandt,sammg,vbeln',
    cdhdr: 'mandant,objectclas,objectid,changenr,username,udate,utime,tcode',
    cdpos: 'mandant,objectclas,objectid,changenr,tabname,tabkey,fname,chngind,value_new,value_old',
    nast: 'mandt,kappl,objky,kschl,nacha,parnr,erdat,eruhr,usnam,datvr,uhrvr,vstat',
    // purchasing (third-party items)
    eban: 'mandt,banfn,bnfpo,badat,ernam,frgdt,lfdat,matnr,meins,menge,werks',
    ekko: 'mandt,ebeln,bstyp,bsart,bukrs,ekorg,ekgrp,lifnr,ernam,aedat,bedat,waers,wkurs,zterm,zbd1t,zbd2t,zbd3t,frgrl,kdatb,kdate,konnr,statu',
    ekpo: 'mandt,ebeln,ebelp,bstyp,banfn,bnfpo,matnr,matkl,werks,lgort,menge,meins,netpr,netwr,pstyp,knttp,bstae,eglkz,elikz,konnr,ktmng,ktpnr,kzabs,lewed,plifz,retpo,uebtk,uebto,untto',
    // logistics
    likp: 'mandt,vbeln,erdat,erzet,ernam,lfart,vbtyp,vkorg,vstel,kunnr,vsart,lfdat,lfuhr,kodat,kouhr,wadat,wadat_ist',
    lips: 'mandt,vbeln,posnr,matnr,matkl,pstyv,werks,lgnum,lfimg,ormng,lgmng,brgew,kcmeng,kcbrgew,kcntgew,kcgewei,vgbel,vgpos,vgtyp,vbelv,posnv,vbtyv,uecha,posnr_pp,aufnr,bwart,dlvtp,kdauf,kdpos,spe_gen_elikz,erdat,erzet,ernam,aedat',
    vbfa: 'mandt,vbelv,posnv,vbeln,posnn,vbtyp_v,vbtyp_n,erdat,erzet',
    mkpf: 'mandt,mblnr,mjahr,vgart,blart,bldat,budat,cpudt,cputm,aedat,usnam,tcode,xblnr,tcode2',
    mseg: 'mandt,mblnr,mjahr,zeile,bwart,matnr,werks,lgort,kdauf,kdpos,shkzg,waers,menge,meins,ebeln,ebelp,lfbja,lfbnr,lfpos,sjahr,smbln,smblp,elikz,aufnr,gjahr,bukrs,belnr,buzei,budat_mkpf,sobkz,xsauf',
    vttk: 'mandt,tknum,erdat,erzet,ernam,datbg,uatbg,daten,uaten',
    vttp: 'mandt,tknum,vbeln',
    // billing and accounting
    vbrk: 'mandt,vbeln,fkart,vbtyp,fkdat,erdat,erzet,ernam,kunag,vkorg,bukrs,gjahr,waerk,stwae,netwr,mwsbk,zterm,xblnr,fksto,sfakn,stgrd,maber,mansp,mschl',
    vbrp: 'mandt,vbeln,posnr,matnr,fkimg,netwr,mwsbp,skfbp,sktof,kursk,werks,vgbel,vgpos,aubel,aupos,erdat,erzet,ernam',
    bkpf: 'mandt,bukrs,belnr,gjahr,blart,bldat,budat,monat,cpudt,cputm,usnam,tcode,awtyp,awkey,xblnr,waers,hwaer,frath,stodt,stgrd,xstov,xreversal,xsplit',
    bseg: 'mandt,bukrs,belnr,gjahr,buzei,koart,bschl,shkzg,umskz,kunnr,wrbtr,wmwst,fwbas,nebtr,skfbt,sknto,wskto,menge,zfbdt,zterm,zbd1t,zbd2t,zbd3t,zbd1p,zbd2p,valut,augbl,augdt,auggj,vbeln,vbel2,posn2,aufnr,xref1,xref2,xref3,mansp,manst,madat,maber',
  };
  const CL = {}, W = {};
  for (const k in COLS) { CL[k] = COLS[k].split(','); W[k] = [COLS[k]]; }
  const put = (tab, o) => { if (o.mandt === undefined && o.mandant === undefined && tab !== 'tcurx' && tab !== 'ddftx' && tab !== 'dd07t') { if (CL[tab][0] === 'mandant') o.mandant = '100'; else o.mandt = '100'; } W[tab].push(CL[tab].map(c => esc(o[c])).join(',')); };
  const E_ = 'E';

  // ---------------- configuration and texts
  const ORG = { DE01: { bukrs: 'DE00', name: 'Velora Pumpen GmbH', land: 'DE', vkbur: 'D100', office: 'Düsseldorf' },
                CZ01: { bukrs: 'CZ00', name: 'Velora Brno s.r.o.', land: 'CZ', vkbur: 'C100', office: 'Brno' } };
  for (const vk in ORG) {
    const o = ORG[vk];
    put('t001', { bukrs: o.bukrs, butxt: o.name, land1: o.land, waers: 'EUR' });
    put('tvko', { vkorg: vk, bukrs: o.bukrs });
    put('tvkot', { spras: E_, vkorg: vk, vtext: o.name });
    put('tvkbt', { spras: E_, vkbur: o.vkbur, bezei: 'Sales office ' + o.office });
  }
  put('t001k', { bwkey: 'DE10', bukrs: 'DE00' }); put('t001k', { bwkey: 'CZ10', bukrs: 'CZ00' });
  put('t001w', { werks: 'DE10', name1: 'Velora plant Düsseldorf' }); put('t001w', { werks: 'CZ10', name1: 'Velora plant Brno' });
  put('tvak', { auart: 'OR', kalvg: '1' }); put('tvak', { auart: 'ZDS', kalvg: '1' });
  put('tvakt', { spras: E_, auart: 'OR', bezei: 'Standard Order' }); put('tvakt', { spras: E_, auart: 'ZDS', bezei: 'Drop-Shipment Order' });
  put('tvap', { pstyv: 'TAN', prsfd: 'X' }); put('tvap', { pstyv: 'TAS', prsfd: 'X' });
  put('tvapt', { spras: E_, pstyv: 'TAN', vtext: 'Standard Item' }); put('tvapt', { spras: E_, pstyv: 'TAS', vtext: 'Third-Party Item' });
  [['01', 'Delivery date too late'], ['02', 'Poor quality'], ['03', 'Too expensive'], ['05', 'Credit limit exceeded']].forEach(([a, b]) => put('tvagt', { spras: E_, abgru: a, bezei: b }));
  [['001', 'Poor quality'], ['002', 'Damaged in transit'], ['005', 'Wrong price']].forEach(([a, b]) => put('tvaut', { spras: E_, augru: a, bezei: b }));
  put('tvlkt', { spras: E_, lfart: 'LF', vtext: 'Outbound Delivery' });
  [['01', 'Credit limit'], ['02', 'No printout']].forEach(([a, b]) => put('tvlst', { spras: E_, lifsp: a, vtext: b }));
  [['01', 'Calculation missing'], ['02', 'Complete confirmation missing']].forEach(([a, b]) => put('tvfst', { spras: E_, faksp: a, vtext: b }));
  const MAT = [['P-1100', 'Centrifugal pump CP-110', 'PUMPS'], ['P-1250', 'Centrifugal pump CP-125', 'PUMPS'], ['P-2200', 'Multistage pump MS-22', 'PUMPS'],
    ['V-3100', 'Ball valve DN50', 'VALVES'], ['V-3200', 'Butterfly valve DN100', 'VALVES'], ['V-3400', 'Control valve CV-40', 'VALVES'],
    ['S-5000', 'Mechanical seal kit', 'SPARES'], ['S-5100', 'Impeller spare', 'SPARES'], ['M-7000', 'Motor 7.5 kW', 'MOTORS'], ['C-9000', 'Service kit annual', 'SERVICE']];
  const KG = { PUMPS: 85, VALVES: 12, SPARES: 3, MOTORS: 48, SERVICE: 6 };
  for (const [m, t] of MAT) put('makt', { matnr: m, spras: E_, maktx: t });
  [['PUMPS', 'Pumps'], ['VALVES', 'Valves'], ['SPARES', 'Spare parts'], ['MOTORS', 'Motors'], ['SERVICE', 'Service kits']].forEach(([a, b]) => put('t023t', { spras: E_, matkl: a, wgbez: b }));
  [['RV', 'Billing doc.transfer'], ['DZ', 'Customer payment'], ['AB', 'Accounting document'], ['ZE', 'Bank statement'], ['WL', 'Goods issue/delivery']].forEach(([a, b]) => put('t003t', { spras: E_, blart: a, ltext: b }));
  [['01', 'Invoice'], ['11', 'Credit memo'], ['12', 'Reverse invoice'], ['15', 'Incoming payment'], ['40', 'Debit entry'], ['50', 'Credit entry']].forEach(([a, b]) => put('tbslt', { spras: E_, bschl: a, umskz: '', ltext: b }));
  [['601', 'GD goods issue:delvy'], ['602', 'RE goods deliv. rev.']].forEach(([a, b]) => put('t156ht', { spras: E_, bwart: a, btext: b }));
  [['EUR', 'EUR'], ['USD', 'USD'], ['CZK', 'CZK']].forEach(([a, b]) => put('tcurc', { waers: a, isocd: b }));
  put('tcurx', { currkey: 'JPY', currdec: '0' });
  // monthly EUR->USD rates, type M (GDATU is stored inverted: 99999999 - yyyymmdd)
  for (let y = 2025, mo = 9; y < 2027 || mo < 1; ) {
    const d = y * 10000 + (mo + 1) * 100 + 1, rate = (1.06 + 0.04 * Math.sin((y * 12 + mo) / 3)).toFixed(5);
    put('tcurr', { kurst: 'M', fcurr: 'EUR', tcurr: 'USD', gdatu: String(99999999 - d), ukurs: rate, ffact: '1', tfact: '1' });
    if (++mo === 12) { mo = 0; y++; } if (y === 2027) break;
  }
  put('tcurf', { kurst: 'M', fcurr: 'EUR', tcurr: 'USD', gdatu: String(99999999 - 20000101), ffact: '1', tfact: '1' });
  [['VBAK', 'VDATU', 'VDATU', 'Req. deliv.date'], ['VBAK', 'LIFSK', 'LIFSK', 'Delivery block'], ['VBUK', 'CMGST', 'CMGST', 'Overall credit status'],
   ['VBAP', 'NETPR', 'NETPR', 'Net price'], ['VBAP', 'KWMENG', 'KWMENG', 'Order quantity'], ['VBAP', 'ABGRU', 'ABGRU_VA', 'Reason for rejection'],
   ['VBEP', 'WMENG', 'WMENG', 'Order quantity'], ['LIKP', 'KODAT', 'KODAT', 'Picking date'], ['BSEG', 'MANST', 'MAHNS_D', 'Dunning level'],
   ['BSEG', 'MANSP', 'MANSP', 'Dunning block'], ['USR02', 'USTYP', 'XUUSTYP', 'User Type']].forEach(([t, f, d, x]) => put('ddftx', { tabname: t, fieldname: f, ddlanguage: E_, domname: d, scrtext_m: x }));
  [['XUUSTYP', 'A', 'Dialog'], ['XUUSTYP', 'B', 'System'], ['CMGST', 'A', 'Credit check was executed, document OK'], ['CMGST', 'B', 'Credit check was executed, document not OK'], ['CMGST', 'D', 'Document released by credit representative']]
    .forEach(([d, v, x]) => put('dd07t', { domname: d, ddlanguage: E_, as4local: 'A', domvalue_l: v, ddtext: x }));

  // ---------------- customers and users
  const SEG = { 'Direct industrial': '01', 'Distributor': '02', 'OEM': '03' };
  const land = (n) => /GmbH$| AG$| KG$/.test(n) ? 'DE' : /s\.r\.o\.$|a\.s\.$/.test(n) ? 'CZ' : /S\.A\.$/.test(n) ? 'ES' : /B\.V\.$/.test(n) ? 'NL' : /Sp\. z o\.o\.$/.test(n) ? 'PL' : /Ltd$/.test(n) ? 'GB' : 'DE';
  const CITY = { DE: 'Düsseldorf', CZ: 'Brno', ES: 'Madrid', NL: 'Rotterdam', PL: 'Wrocław', GB: 'Leeds' };
  const kunnr = (c) => c.slice(1).padStart(10, '0');
  const cust = new Set(), knvv = new Set(), users = new Set();
  const ids = Object.keys(EV).sort();
  for (const id of ids) {
    const c = cases[id]; const k = kunnr(c.customer_id);
    if (!cust.has(k)) { cust.add(k); const l = land(c.customer_name); put('kna1', { kunnr: k, name1: c.customer_name, land1: l, ort01: CITY[l], ktokd: 'Z001', vbund: '' }); }
    if (!knvv.has(k + c.sales_org)) { knvv.add(k + c.sales_org); put('knvv', { kunnr: k, vkorg: c.sales_org, vtweg: '10', spart: '00', kdgrp: SEG[c.customer_segment], zterm: c.payment_terms }); }
    for (const e of EV[id]) users.add(U(e[4]));
  }
  const PURCH = ['USER_601', 'USER_602'];
  PURCH.forEach(u => users.add(u));
  [...users].sort().forEach(u => put('vusr02_header', { bname: u, ustyp: u === 'SYSTEM' ? 'B' : 'A' }));

  // ---------------- numbering
  const seq = {};
  const nxt = (kind, base, w) => { seq[kind] = (seq[kind] || 0) + 1; return String(base + seq[kind]).padStart(w || 10, '0'); };
  const cdoc = (objectclas, objectid, ts, user, tcode, rows) => {
    const chn = nxt('CHG', 0);
    put('cdhdr', { objectclas, objectid, changenr: chn, username: U(user), udate: DD(ts), utime: TT(ts), tcode });
    for (const [tabname, tabkey, fname, chngind, value_new, value_old] of rows) put('cdpos', { objectclas, objectid, changenr: chn, tabname, tabkey, fname, chngind, value_new, value_old });
  };
  const termDays = (t) => t === 'NT60' ? 60 : t === 'NT45' ? 45 : 30;

  for (const cid of ids) {
    const E = EV[cid].slice().sort((a, b) => a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : a[1] - b[1]);
    const C = cases[cid];
    const org = C.sales_org, plant = C.plant, O = ORG[org], bukrs = O.bukrs, vstel = plant.replace('10', '01');
    const kun = kunnr(C.customer_id), drop = C.drop_shipment === 'yes';
    const nlines = +C.order_lines, val = +C.order_value_eur, terms = C.payment_terms;
    const acts = E.map(e => e[2]); const create = E[0], cts = create[0], cus = U(create[4]);
    let vdatu = ymd(fmt(toMs(cts) + randint(7, 21) * DAY));
    const vdMs = (y) => String(Date.UTC(+y.slice(0, 4), +y.slice(4, 6) - 1, +y.slice(6, 8)));
    const knumv = nxt('KNV', 0);
    const rejected = acts.includes('Reject order');
    // --- header and items
    const weights = []; for (let n = 0; n < nlines; n++) weights.push(rnd() + 0.2);
    const sw = weights.reduce((a, b) => a + b, 0);
    const items = [];
    for (let n = 0; n < nlines; n++) {
      const m = choice(MAT), qty = choice([1, 1, 2, 2, 3, 4, 5, 6, 8, 10, 12, 20]);
      items.push({ pos: String((n + 1) * 10).padStart(6, '0'), m, qty, nv: Math.round(val * weights[n] / sw * 100) / 100 });
    }
    let lastChange = '';
    for (const e of E) if (/^Change/.test(e[2]) || e[2] === 'Block for credit' || e[2] === 'Release credit block' || e[2] === 'Reject order') lastChange = e[0];
    put('vbak', { vbeln: cid, erdat: DD(cts), erzet: TT(cts), ernam: cus, aedat: lastChange ? DD(lastChange) : '', audat: DD(cts), auart: drop ? 'ZDS' : 'OR', vbtyp: 'C',
      vkorg: org, vtweg: '10', spart: '00', vkbur: O.vkbur, kunnr: kun, augru: '', lifsk: '', faksk: '', waerk: 'EUR', netwr: f2(val), vdatu: vdMs(vdatu), knumv });
    const pr = drop ? nxt('PR', 10000000) : '';
    items.forEach((it, n) => {
      put('vbap', { vbeln: cid, posnr: it.pos, matnr: it.m[0], arktx: it.m[1], matkl: it.m[2], pstyv: drop ? 'TAS' : 'TAN', kwmeng: f3(it.qty), kbmeng: rejected ? '0.000' : f3(it.qty),
        vrkme: 'ST', netpr: f2(it.nv / it.qty), netwr: f2(it.nv), werks: plant, abgru: rejected ? '02' : '', vgbel: '', vgpos: '', erdat: DD(cts), erzet: TT(cts), ernam: cus });
      const wa = ymd(fmt(toMs(vdatu.slice(0, 4) + '-' + vdatu.slice(4, 6) + '-' + vdatu.slice(6, 8) + ' 00:00:00') - 2 * DAY));
      put('vbep', { vbeln: cid, posnr: it.pos, etenr: '0001', edatu: vdMs(vdatu), ezeit: '0', wmeng: f3(it.qty), bmeng: rejected ? '0.000' : f3(it.qty),
        mbdat: vdMs(wa), mbuhr: '0', wadat: vdMs(wa), wauhr: '0', banfn: pr, bnfpo: drop ? String((n + 1) * 10).padStart(5, '0') : '' });
    });
    // --- third-party items: purchase requisition at save, purchase order next working day
    if (drop) {
      const pots = fmt(toMs(cts) + randint(18, 30) * 3600000), po = nxt('PO', 4500000000), pu = choice(PURCH);
      cdoc('EINKBELEG', po, pots, pu, 'ME21N', [['EKKO', '100' + po, 'KEY', 'I', '', '']]);
      put('ekko', { ebeln: po, bstyp: 'F', bsart: 'NB', bukrs, ekorg: org.replace('01', '10'), ekgrp: '001', lifnr: '0000300100', ernam: pu, aedat: DD(pots), bedat: DD(pots), waers: 'EUR', wkurs: '1.00000',
        zterm: 'NT30', zbd1t: '30', zbd2t: '0', zbd3t: '0', frgrl: '', kdatb: '', kdate: '', konnr: '', statu: '9' });
      items.forEach((it, n) => {
        const bnfpo = String((n + 1) * 10).padStart(5, '0');
        put('eban', { banfn: pr, bnfpo, badat: DD(cts), ernam: cus, frgdt: DD(cts), lfdat: vdMs(vdatu), matnr: it.m[0], meins: 'ST', menge: f3(it.qty), werks: plant });
        cdoc('BANF', pr, plusSec(cts, 1), cus, 'VA01', [['EBAN', '100' + pr + bnfpo, 'KEY', 'I', '', '']]);
        put('ekpo', { ebeln: po, ebelp: bnfpo, bstyp: 'F', banfn: pr, bnfpo, matnr: it.m[0], matkl: it.m[2], werks: plant, lgort: '', menge: f3(it.qty), meins: 'ST',
          netpr: f2(it.nv / it.qty * 0.7), netwr: f2(it.nv * 0.7), pstyp: '5', knttp: 'X', bstae: '', eglkz: '', elikz: '', konnr: '', ktmng: '0.000', ktpnr: '', kzabs: 'X', lewed: '', plifz: '5', retpo: '', uebtk: '', uebto: '0.0', untto: '0.0' });
      });
    }
    // --- change documents on the sales order (object class VERKBELEG)
    const vb = (ts, user, tcode, rows) => cdoc('VERKBELEG', cid, ts, user, tcode, rows);
    let cm = '';
    const firstLate = E.find(e => e[2] === 'Change price after credit release');
    const firstBlock = E.find(e => e[2] === 'Block for credit');
    if (!firstBlock || (firstLate && firstLate[0] < firstBlock[0])) { // automatic credit check passed when the order was saved
      const early = E.filter(e => e[2] === 'Change price').map(e => e[0]);
      const ref = [cts, ...early].sort().pop();
      let tc = toMs(ref) + 30000;
      if (firstLate && fmt(tc) >= firstLate[0]) tc = toMs(firstLate[0]) - 30000;
      vb(fmt(tc), create[4], early.length ? 'VA02' : 'VA01', [['VBUK', '100' + cid, 'CMGST', 'U', 'A', '']]);
      cm = 'A';
    }
    const dels = [], picks = [], pgis = [], invs = [], dun = [], reviews = [];
    let memo = null, pay = null, clear = null, sendinv = null;
    for (const [ts, , a, , us] of E) {
      if (a === 'Send order confirmation') put('nast', { kappl: 'V1', objky: cid, kschl: 'BA00', nacha: '5', parnr: kun, erdat: DD(cts), eruhr: TT(cts), usnam: U(us), datvr: DD(ts), uhrvr: TT(ts), vstat: '1' });
      else if (a === 'Change quantity') {
        const it = choice(items); const nw = Math.max(1, it.qty + choice([-2, -1, 1, 2, 5]));
        vb(ts, us, 'VA02', [['VBAP', '100' + cid + it.pos, 'KWMENG', 'U', f3(nw), f3(it.qty)], ['VBEP', '100' + cid + it.pos + '0001', 'WMENG', 'U', f3(nw), f3(it.qty)]]);
      }
      else if (a === 'Change requested delivery date') {
        const nw = ymd(fmt(toMs(vdatu.slice(0, 4) + '-' + vdatu.slice(4, 6) + '-' + vdatu.slice(6, 8) + ' 00:00:00') + randint(3, 14) * DAY));
        vb(ts, us, 'VA02', [['VBAK', '100' + cid, 'VDATU', 'U', nw, vdatu]]); vdatu = nw;
      }
      else if (a === 'Change price' || a === 'Change price after credit release') {
        const it = choice(items); const old = it.nv / it.qty; const nw = old * choice([0.9, 0.92, 0.95, 0.97, 1.03, 1.05]);
        vb(ts, us, 'VA02', [['VBAP', '100' + cid + it.pos, 'NETPR', 'U', f2(nw), f2(old)]]);
      }
      else if (a === 'Block for credit') { vb(ts, us, cm ? 'VA02' : 'VA01', [['VBUK', '100' + cid, 'CMGST', 'U', 'B', cm]]); cm = 'B'; }
      else if (a === 'Review blocked order') reviews.push([ts, us]);
      else if (a === 'Release credit block') { vb(ts, us, 'VKM1', [['VBUK', '100' + cid, 'CMGST', 'U', 'D', 'B']]); cm = 'D'; }
      else if (a === 'Reject order') vb(ts, us, 'VA02', items.map(p => ['VBAP', '100' + cid + p.pos, 'ABGRU', 'U', '02', '']));
      else if (a === 'Create delivery') dels.push([ts, us]);
      else if (a === 'Pick goods') picks.push([ts, us]);
      else if (a === 'Post goods issue') pgis.push([ts, us]);
      else if (a === 'Create invoice') invs.push([ts, us]);
      else if (a === 'Send invoice') sendinv = [ts, us];
      else if (a === 'Create credit memo') memo = [ts, us];
      else if (a === 'Send dunning notice') dun.push([ts, us]);
      else if (a === 'Receive incoming payment') pay = [ts, us];
      else if (a === 'Clear payment') clear = [ts, us];
      else if (a !== 'Create sales order') throw new Error('unmapped ' + a);
    }
    if (reviews.length) {
      const f = reviews[0], l = reviews[reviews.length - 1];
      put('stxh', { tdobject: 'VBBK', tdname: cid, tdid: 'ZCRV', tdspras: E_, tdtitle: 'Credit review', tdfuser: U(f[1]), tdfdate: DD(f[0]), tdftime: TT(f[0]), tdluser: U(l[1]), tdldate: DD(l[0]), tdltime: TT(l[0]) });
    }
    // --- deliveries, picking, goods issue
    const dlvOf = {};                                   // item pos -> [delivery, delivery item]
    dels.forEach(([ts, us], k) => {
      const v = nxt('DEL', 80000000); const pg = pgis[k], pk = picks[k];
      let di = dels.length === 1 ? items : items.filter((_, j) => j % dels.length === k); if (!di.length) di = items.slice(0, 1);
      const plannedGI = fmt(toMs(ts) + DAY);
      put('likp', { vbeln: v, erdat: DD(ts), erzet: TT(ts), ernam: U(us), lfart: 'LF', vbtyp: 'J', vkorg: org, vstel, kunnr: kun, vsart: '01', lfdat: vdMs(vdatu), lfuhr: '0',
        kodat: pk ? DD(pk[0]) : DD(ts), kouhr: pk ? TT(pk[0]) : '0', wadat: DD(plannedGI), wadat_ist: pg ? DD(pg[0]) : '' });
      if (pk) { // picking confirmed: the picking date moves from the planned date (day after creation) to the actual one
        let planned = ymd(fmt(toMs(ts) + DAY)); if (planned === ymd(pk[0])) planned = ymd(fmt(toMs(ts) + 2 * DAY));
        cdoc('LIEFERUNG', v, pk[0], pk[1], 'VL02N', [['LIKP', '100' + v, 'KODAT', 'U', ymd(pk[0]), planned]]);
      }
      let mb = '';
      if (pg) { mb = nxt('MAT', 4900000000); put('mkpf', { mblnr: mb, mjahr: pg[0].slice(0, 4), vgart: 'WL', blart: 'WL', bldat: DD(pg[0]), budat: DD(pg[0]), cpudt: DD(pg[0]), cputm: TT(pg[0]), aedat: '', usnam: U(pg[1]), tcode: 'VL02N', xblnr: v, tcode2: 'VL02N' }); }
      di.forEach((it, n) => {
        const pn = String((n + 1) * 10).padStart(6, '0'), kg = KG[it.m[2]] * it.qty;
        dlvOf[it.pos] = [v, pn];
        put('lips', { vbeln: v, posnr: pn, matnr: it.m[0], matkl: it.m[2], pstyv: 'TAN', werks: plant, lgnum: plant.slice(0, 2) + '1', lfimg: f3(it.qty), ormng: f3(it.qty), lgmng: f3(it.qty),
          brgew: f3(kg), kcmeng: '0.000', kcbrgew: '0.000', kcntgew: '0.000', kcgewei: '', vgbel: cid, vgpos: it.pos, vgtyp: 'C', vbelv: '', posnv: '', vbtyv: '', uecha: '', posnr_pp: '',
          aufnr: '', bwart: '601', dlvtp: '', kdauf: '', kdpos: '', spe_gen_elikz: '', erdat: DD(ts), erzet: TT(ts), ernam: U(us), aedat: '' });
        put('vbfa', { vbelv: cid, posnv: it.pos, vbeln: v, posnn: pn, vbtyp_v: 'C', vbtyp_n: 'J', erdat: DD(ts), erzet: TT(ts) });
        if (pg) {
          const zeile = String(n + 1).padStart(4, '0');
          put('mseg', { mblnr: mb, mjahr: pg[0].slice(0, 4), zeile, bwart: '601', matnr: it.m[0], werks: plant, lgort: '0001', kdauf: cid, kdpos: it.pos, shkzg: 'H', waers: 'EUR', menge: f3(it.qty), meins: 'ST',
            ebeln: '', ebelp: '', lfbja: '', lfbnr: '', lfpos: '', sjahr: '', smbln: '', smblp: '', elikz: '', aufnr: '', gjahr: pg[0].slice(0, 4), bukrs, belnr: '', buzei: '', budat_mkpf: DD(pg[0]), sobkz: '', xsauf: '' });
          put('vbfa', { vbelv: v, posnv: pn, vbeln: mb, posnn: zeile, vbtyp_v: 'J', vbtyp_n: 'R', erdat: DD(pg[0]), erzet: TT(pg[0]) });
        }
      });
    });
    // --- billing documents with their accounting documents
    const bill = (vbtyp, fkart, ts, us, ref) => {
      const v = vbtyp === 'O' ? nxt('MEM', 91000000) : nxt('BIL', 90000000);
      put('vbrk', { vbeln: v, fkart, vbtyp, fkdat: DD(ts), erdat: DD(ts), erzet: TT(ts), ernam: U(us), kunag: kun, vkorg: org, bukrs, gjahr: ts.slice(0, 4), waerk: 'EUR', stwae: 'EUR',
        netwr: f2(val), mwsbk: '0.00', zterm: terms, xblnr: v, fksto: '', sfakn: '', stgrd: '', maber: '', mansp: '', mschl: '' });
      items.forEach((it, n) => {
        const pn = it.pos; let vgbel = cid, vgpos = it.pos, vt = 'C';
        if (ref) { vgbel = ref; vgpos = pn; vt = 'M'; } else if (!drop && dlvOf[it.pos]) { [vgbel, vgpos] = dlvOf[it.pos]; vt = 'J'; }
        put('vbrp', { vbeln: v, posnr: pn, matnr: it.m[0], fkimg: f3(it.qty), netwr: f2(it.nv), mwsbp: '0.00', skfbp: f2(it.nv), sktof: 'X', kursk: '1.00000', werks: plant,
          vgbel, vgpos, aubel: cid, aupos: it.pos, erdat: DD(ts), erzet: TT(ts), ernam: U(us) });
        put('vbfa', { vbelv: vgbel, posnv: vgpos, vbeln: v, posnn: pn, vbtyp_v: vt, vbtyp_n: vbtyp, erdat: DD(ts), erzet: TT(ts) });
      });
      const fts = plusSec(ts, randint(2, 9)), fi = nxt('FIR', 1400000000);
      put('bkpf', { bukrs, belnr: fi, gjahr: ts.slice(0, 4), blart: 'RV', bldat: DD(ts), budat: DD(ts), monat: ts.slice(5, 7), cpudt: DD(fts), cputm: TT(fts), usnam: U(us), tcode: 'VF01',
        awtyp: 'VBRK', awkey: v, xblnr: v, waers: 'EUR', hwaer: 'EUR', frath: '0.00', stodt: '', stgrd: '', xstov: '', xreversal: '', xsplit: '' });
      return { v, fi, ts, gjahr: ts.slice(0, 4), vbtyp };
    };
    const bsegD = (b, o) => put('bseg', Object.assign({ bukrs, belnr: b.fi, gjahr: b.gjahr, buzei: '001', koart: 'D', umskz: '', kunnr: kun, wrbtr: f2(val), wmwst: '0.00', fwbas: f2(val),
      nebtr: '0.00', skfbt: f2(val), sknto: '0.00', wskto: '0.00', menge: '', zfbdt: DD(b.ts), zterm: terms, zbd1t: String(termDays(terms)), zbd2t: '0', zbd3t: '0', zbd1p: '0.000', zbd2p: '0.000',
      valut: '', augbl: '', augdt: '', auggj: '', vbeln: b.v, vbel2: '', posn2: '', aufnr: '', xref1: '', xref2: '', xref3: '', mansp: '', manst: '', madat: '', maber: '' }, o));
    const bsegS = (bel, gj, buzei, bschl, shkzg, amt, extra) => put('bseg', Object.assign({ bukrs, belnr: bel, gjahr: gj, buzei, koart: 'S', bschl, shkzg, umskz: '', kunnr: '', wrbtr: f2(amt) }, extra || {}));
    const bills = invs.map(([ts, us], k) => {
      const firstAfterMemo = memo && k > 0;
      return bill('M', drop ? 'F1' : 'F2', ts, us, null, firstAfterMemo);
    });
    if (sendinv && bills.length) put('nast', { kappl: 'V3', objky: bills[0].v, kschl: 'RD00', nacha: '1', parnr: kun, erdat: DD(bills[0].ts), eruhr: TT(bills[0].ts), usnam: U(sendinv[1]), datvr: DD(sendinv[0]), uhrvr: TT(sendinv[0]), vstat: '1' });
    let mb = null;
    if (memo) mb = bill('O', 'G2', memo[0], memo[1], bills[0].v);
    // receivable lines (customer line + revenue line) and how they were cleared
    const clr = {};                                               // fi -> {augbl, augdt, auggj}
    if (mb) { // invoice and credit memo are cleared against each other: zero-balance clearing creates a header-only document
      const tc = plusSec(memo[0], 20 * 60), ab = nxt('CLR', 1700000000);
      put('bkpf', { bukrs, belnr: ab, gjahr: tc.slice(0, 4), blart: 'AB', bldat: DD(tc), budat: DD(tc), monat: tc.slice(5, 7), cpudt: DD(tc), cputm: TT(tc), usnam: U(memo[1]), tcode: 'F-32',
        awtyp: 'BKPF', awkey: ab + bukrs + tc.slice(0, 4), xblnr: '', waers: 'EUR', hwaer: 'EUR', frath: '0.00', stodt: '', stgrd: '', xstov: '', xreversal: '', xsplit: '' });
      clr[bills[0].fi] = clr[mb.fi] = { augbl: ab, augdt: DD(tc), auggj: tc.slice(0, 4) };
    }
    const pb = bills[bills.length - 1];
    if (pb && clear) {
      // bank statement posted automatically (FF_5) to the bank clearing account, reference = invoice number
      const zb = nxt('BNK', 1500000000), pts = pay[0];
      put('bkpf', { bukrs, belnr: zb, gjahr: pts.slice(0, 4), blart: 'ZE', bldat: DD(pts), budat: DD(pts), monat: pts.slice(5, 7), cpudt: DD(pts), cputm: TT(pts), usnam: U(pay[1]), tcode: 'FF_5',
        awtyp: 'BKPF', awkey: zb + bukrs + pts.slice(0, 4), xblnr: pb.v, waers: 'EUR', hwaer: 'EUR', frath: '0.00', stodt: '', stgrd: '', xstov: '', xreversal: '', xsplit: '' });
      bsegS(zb, pts.slice(0, 4), '001', '40', 'S', val, { xref1: pb.v, valut: DD(pts) });
      bsegS(zb, pts.slice(0, 4), '002', '50', 'H', val, { xref1: pb.v, valut: DD(pts) });
      // cash application: the AR clerk posts the incoming payment and clears the invoice (F-28)
      const cts2 = clear[0], dz = nxt('PAY', 1600000000), g2 = cts2.slice(0, 4);
      put('bkpf', { bukrs, belnr: dz, gjahr: g2, blart: 'DZ', bldat: DD(pts), budat: DD(cts2), monat: cts2.slice(5, 7), cpudt: DD(cts2), cputm: TT(cts2), usnam: U(clear[1]), tcode: 'F-28',
        awtyp: 'BKPF', awkey: dz + bukrs + g2, xblnr: pb.v, waers: 'EUR', hwaer: 'EUR', frath: '0.00', stodt: '', stgrd: '', xstov: '', xreversal: '', xsplit: '' });
      bsegD({ fi: dz, gjahr: g2, ts: cts2, v: '' }, { bschl: '15', shkzg: 'H', zbd1t: '0', augbl: dz, augdt: DD(cts2), auggj: g2, valut: DD(pts), xref1: pb.v });
      bsegS(dz, g2, '002', '40', 'S', val, { valut: DD(pts) });
      clr[pb.fi] = { augbl: dz, augdt: DD(cts2), auggj: g2 };
    }
    const lastDun = dun.length ? dun[dun.length - 1] : null;
    for (const b of bills) {
      const o = Object.assign({ bschl: '01', shkzg: 'S' }, clr[b.fi] || {});
      if (b === pb && lastDun) Object.assign(o, { manst: String(dun.length), madat: DD(lastDun[0]) });
      bsegD(b, o);
      bsegS(b.fi, b.gjahr, '002', '50', 'H', val);
    }
    if (mb) { bsegD(mb, Object.assign({ bschl: '11', shkzg: 'H' }, clr[mb.fi])); bsegS(mb.fi, mb.gjahr, '002', '40', 'S', val); }
    // dunning run (F150) raises the dunning level on the open invoice item -> change document on BSEG
    if (pb) dun.forEach(([ts, us], k) => cdoc('BELEG', bukrs + pb.fi + pb.gjahr, ts, us, 'F150', [['BSEG', '100' + bukrs + pb.fi + pb.gjahr + '001', 'MANST', 'U', String(k + 1), String(k)]]));
  }
  const out = {}; for (const k in W) out[k] = W[k].join('\n') + '\n';
  return out;
}
if (typeof module !== 'undefined') module.exports = genSAP;
