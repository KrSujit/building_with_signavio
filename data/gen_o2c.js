// Velora O2C event log generator (deterministic). Works in Node and in the browser.
// Returns {events: CSV string, cases: CSV string, stats}
function genO2C(N) {
  N = N || 41300;
  let s = 20260117;
  const r = () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
  const pick = (a) => a[Math.floor(r() * a.length)];
  const exp = (m) => -Math.log(1 - r()) * m;              // exponential, mean m (days)
  const logn = (mu, sg) => Math.exp(mu + sg * Math.sqrt(-2 * Math.log(1 - r())) * Math.cos(2 * Math.PI * r()));
  const DAY = 86400000;
  const start = Date.UTC(2025, 10, 1);                     // 2025-11-01
  const p2 = (n) => String(n).padStart(2, '0');
  const fmt = (t) => { const d = new Date(t); return d.getUTCFullYear() + '-' + p2(d.getUTCMonth() + 1) + '-' + p2(d.getUTCDate()) + ' ' + p2(d.getUTCHours()) + ':' + p2(d.getUTCMinutes()) + ':' + p2(d.getUTCSeconds()); };
  const work = (t) => { // move to next working time 07:00-17:00 Mon-Fri
    let d = new Date(t); let h = d.getUTCHours();
    if (h < 7) d.setUTCHours(7 + Math.floor(r() * 2), Math.floor(r() * 60));
    if (h >= 17) { d = new Date(d.getTime() + DAY); d.setUTCHours(7 + Math.floor(r() * 3), Math.floor(r() * 60)); }
    while (d.getUTCDay() === 0 || d.getUTCDay() === 6) d = new Date(d.getTime() + DAY);
    return d.getTime();
  };
  const nextFriday = (t) => { let d = new Date(t + DAY); while (d.getUTCDay() !== 5) d = new Date(d.getTime() + DAY); d.setUTCHours(14, Math.floor(r() * 50)); return d.getTime(); };
  const A = ['Nord', 'Rhein', 'Alpen', 'Baltic', 'Danube', 'Iberia', 'Vistula', 'Elbe', 'Moravia', 'Carpathia', 'Main', 'Ruhr', 'Tatra', 'Adria', 'Silesia', 'Lumen', 'Atlas', 'Orion', 'Vega', 'Polaris'];
  const B = ['Chemie', 'Energie', 'Brau', 'Pharma', 'Papier', 'Stahl', 'Food', 'Water', 'Pumpen', 'Process', 'Kunststoff', 'Glas', 'Mining', 'Utilities', 'Textil'];
  const C = ['GmbH', 'AG', 's.r.o.', 'a.s.', 'S.A.', 'B.V.', 'Sp. z o.o.', 'KG', 'Ltd'];
  const customers = [];
  for (let i = 0; i < 1400; i++) {
    const seg = r() < 0.55 ? 'Direct industrial' : (r() < 0.67 ? 'Distributor' : 'OEM');
    customers.push({ id: 'C' + (100000 + i * 7), name: pick(A) + ' ' + pick(B) + ' ' + pick(C), seg,
      terms: seg === 'Distributor' && r() < 0.4 ? 'NT60' : (r() < 0.04 ? 'NT45' : 'NT30'),
      trusted: r() < 0.64, risky: r() < 0.12 });
  }
  const users = (p, n) => Array.from({ length: n }, (_, i) => 'User_' + p + String(i + 1).padStart(2, '0'));
  const UDE = users('1', 14), UCZ = users('2', 9), UPU = users('3', 6), UAR = users('4', 7), UBI = users('5', 6);
  const ev = ['case_id,activity,timestamp,plant,user,system'];
  const cs = ['case_id,customer_id,customer_name,customer_segment,sales_org,plant,order_value_eur,payment_terms,order_lines,drop_shipment,created_month'];
  const st = { cases: 0, events: 0, blocked: 0, lateChange: 0, memo: 0, lines: 0 };
  for (let i = 0; i < N; i++) {
    const brno = r() < 0.43;
    const org = brno ? 'CZ01' : 'DE01', plant = brno ? 'CZ10' : 'DE10';
    const cu = pick(customers);
    const id = String(4500100000 + i * 3 + Math.floor(r() * 3));
    const lines = 1 + Math.floor(logn(1.2, 0.55));
    const val = Math.round(logn(9.4, 0.9) * 100) / 100;
    const drop = !brno && r() < 0.025;
    let t = work(start + r() * 365 * DAY);
    const E = [];
    const add = (a, tt, u, pl) => { E.push([id, a, fmt(tt), pl || plant, u, 'SAP ECC']); };
    const clerk = brno ? pick(UCZ) : pick(UDE);
    add('Create sales order', t, clerk);
    if (r() < 0.93) add('Send order confirmation', work(t + exp(0.05) * DAY), clerk);
    const nq = Math.floor(exp(0.55)), nd = Math.floor(exp(0.35));
    let tc = t;
    for (let k = 0; k < nq; k++) { tc = work(tc + exp(0.4) * DAY); add('Change quantity', tc, clerk); }
    for (let k = 0; k < nd; k++) { tc = work(tc + exp(0.5) * DAY); add('Change requested delivery date', tc, clerk); }
    t = t + (tc - t) * 0.3;
    if (r() < 0.11) { t = work(t + exp(0.4) * DAY); add('Change price', t, clerk); }
    // credit
    const blockP = brno ? 0.375 : 0.165;
    let blocked = r() < blockP * (cu.risky ? 1.3 : 1);
    const credit = () => {
      st.blocked++;
      t = work(t + exp(0.02) * DAY); add('Block for credit', t, 'SYSTEM');
      if (brno && r() < 0.31) { // phone release, review skipped
        t = work(t + (0.6 + exp(1.9)) * DAY); add('Release credit block', t, pick(UPU), 'IN10');
      } else {
        const wait = brno ? 0.5 + exp(2.4) : 0.2 + exp(0.6);
        t = work(t + wait * DAY); add('Review blocked order', t, pick(UPU), 'IN10');
        if (r() < (cu.risky ? 0.18 : 0.04)) { t = work(t + exp(0.3) * DAY); add('Reject order', t, pick(UPU), 'IN10'); return false; }
        t = work(t + exp(0.15) * DAY); add('Release credit block', t, pick(UPU), 'IN10');
      }
      return true;
    };
    if (blocked && !credit()) { st.cases++; st.events += E.length; E.forEach(e => ev.push(e.join(','))); cs.push([id, cu.id, '"' + cu.name + '"', cu.seg, org, plant, val, cu.terms, lines, 'no', E[0][2].slice(0, 7)].join(',')); continue; }
    let late = r() < (blocked ? 0.18 : 0.12);
    if (late) {
      st.lateChange++;
      t = work(t + exp(1.2) * DAY); add('Change price after credit release', t, pick(brno ? UCZ : UDE));
      if (r() < 0.21 && !(blocked && false)) { if (!credit()) { st.cases++; st.events += E.length; E.forEach(e => ev.push(e.join(','))); cs.push([id, cu.id, '"' + cu.name + '"', cu.seg, org, plant, val, cu.terms, lines, 'no', E[0][2].slice(0, 7)].join(',')); continue; } }
    }
    // delivery
    let tInv;
    if (drop) {
      t = work(t + exp(1) * DAY); tInv = t; add('Create invoice', t, pick(UBI));
      t = work(t + (2 + exp(3)) * DAY); add('Create delivery', t, pick(UDE)); t = work(t + exp(0.5) * DAY); add('Post goods issue', t, pick(UDE));
    } else {
      const nDel = lines > 2 && r() < 0.35 ? 2 + (r() < 0.25 ? 1 : 0) : 1;
      let t0 = t;
      for (let k = 0; k < nDel; k++) {
        let tk = work(t0 + (0.8 + exp(1.1) + k * (1 + exp(2))) * DAY); add('Create delivery', tk, clerk);
        tk = work(tk + (0.1 + exp(0.3)) * DAY); add('Pick goods', tk, clerk);
        tk = work(tk + (0.1 + exp(0.3)) * DAY); add('Post goods issue', tk, clerk); t = Math.max(t, tk);
      }
      t = brno ? nextFriday(t) : work(t + exp(0.6) * DAY); tInv = t; add('Create invoice', t, pick(UBI));
    }
    add('Send invoice', work(tInv + (brno ? 1 + exp(1.5) : exp(0.05)) * DAY), pick(UBI));
    // corrections
    const memo = r() < (late ? 0.316 : 0.039);
    if (memo) { st.memo++; t = work(tInv + (4 + exp(9)) * DAY); add('Create credit memo', t, pick(UBI)); t = work(t + exp(1.5) * DAY); add('Create invoice', t, pick(UBI)); }
    // payment
    const terms = cu.terms === 'NT60' ? 60 : (cu.terms === 'NT45' ? 45 : 30);
    let pay = tInv + (terms + (cu.seg === 'Distributor' ? 6 : 3) + exp(9) - 2.5) * DAY;
    if (memo) pay += (11 + exp(8)) * DAY;
    const due = tInv + terms * DAY;
    if (pay > due + 14 * DAY) { // dunning: monthly run on the 1st working day of month
      let d = new Date(due + 7 * DAY); d = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth() + 1, 1, 9, 30)); const dt = work(d.getTime());
      if (dt < pay) add('Send dunning notice', dt, pick(UAR));
    }
    const end = start + 395 * DAY;
    if (pay < end) { add('Receive incoming payment', work(pay - 0.5 * DAY), 'SYSTEM'); add('Clear payment', work(pay), pick(UAR)); }
    st.cases++; st.events += E.length; st.lines += lines;
    E.forEach(e => ev.push(e.join(',')));
    cs.push([id, cu.id, '"' + cu.name + '"', cu.seg, org, plant, val, cu.terms, lines, drop ? 'yes' : 'no', E[0][2].slice(0, 7)].join(','));
  }
  return { events: ev.join('\n'), cases: cs.join('\n'), stats: st };
}
if (typeof module !== 'undefined') module.exports = genO2C;
