#!/usr/bin/env node
// Building with SAP Signavio - companion file, Chapter 14 (folder "Dummy SAP Tables")
//
// Writes the 51 fictional SAP ECC tables (CSV) for Velora Group SE's 41,300 sales orders
// and checks every table against its fingerprint in data/sap_tpl_hashes.json.
// All content is FICTIONAL: Velora Group SE, its customers and users do not exist.
//
// This script is a thin wrapper. The logic lives in the repository's data folder:
//   data/gen_o2c.js            builds Velora's order-level event log (S13_O2C_EventLog.csv and
//                              S13_O2C_CaseAttributes.csv, byte for byte as shipped in data/*.zip)
//   data/gen_sap.js            turns that log into the SAP ECC tables, in the format the
//                              SAP Signavio extractor delivers (Section 14.5)
//   data/hash.js               32-bit FNV-1a fingerprint of a table
//   data/sap_tpl_hashes.json   the expected fingerprint of each of the 51 tables
//
// Usage:   node make_tables.js [output_folder]        (default: ./tables)
// Needs:   Node.js 18 or later, about 1.5 GB of free memory, about 250 MB of disk space.
// Runtime: about 15 to 30 seconds.

'use strict';
const fs = require('fs');
const path = require('path');

function findData() {
  // The data folder of the repository (chapters/Ch14/Dummy SAP Tables -> ../../../data),
  // or a copy of the four files next to this script.
  const candidates = [path.join(__dirname, '..', '..', '..', 'data'), __dirname, path.join(__dirname, 'data')];
  for (const d of candidates) {
    if (['gen_o2c.js', 'gen_sap.js', 'hash.js', 'sap_tpl_hashes.json'].every((f) => fs.existsSync(path.join(d, f)))) return d;
  }
  console.error('Cannot find gen_o2c.js, gen_sap.js, hash.js and sap_tpl_hashes.json.');
  console.error('Keep this script in chapters/Ch14/Dummy SAP Tables of the repository, or copy the four files from data/ next to it.');
  process.exit(2);
}

const DATA = findData();
const genO2C = require(path.join(DATA, 'gen_o2c.js'));
const genSAP = require(path.join(DATA, 'gen_sap.js'));
const h32 = require(path.join(DATA, 'hash.js'));
const expected = JSON.parse(fs.readFileSync(path.join(DATA, 'sap_tpl_hashes.json'), 'utf8'));

const OUT = path.resolve(process.argv[2] || path.join(__dirname, 'tables'));
fs.mkdirSync(OUT, { recursive: true });

const t0 = Date.now();
console.log('1/3  Building Velora\'s order-level event log (41,300 orders) ...');
const o2c = genO2C(41300);
console.log(`     ${o2c.stats.cases.toLocaleString('en-US')} cases, ${o2c.stats.events.toLocaleString('en-US')} events`);

console.log('2/3  Building the SAP ECC tables ...');
const tables = genSAP({ events: o2c.events, cases: o2c.cases });

console.log(`3/3  Writing and checking the tables in ${OUT}`);
let ok = 0;
const problems = [];
for (const name of Object.keys(expected).sort()) {
  const csv = tables[name];
  if (csv === undefined) { problems.push(`${name}: not generated`); continue; }
  fs.writeFileSync(path.join(OUT, name + '.csv'), csv, 'utf8');
  const rows = csv.split('\n').length - 2;               // header line and trailing newline
  const h = h32(csv);
  const good = h === expected[name];
  if (good) ok++; else problems.push(`${name}: fingerprint ${h}, expected ${expected[name]}`);
  console.log(`     ${good ? 'OK  ' : 'FAIL'} ${name.padEnd(14)} ${rows.toLocaleString('en-US').padStart(9)} rows`);
}
for (const name of Object.keys(tables)) if (!(name in expected)) problems.push(`${name}: generated but not in sap_tpl_hashes.json`);

console.log(`\n${ok} of ${Object.keys(expected).length} tables match their fingerprint (${((Date.now() - t0) / 1000).toFixed(1)} s).`);
if (problems.length) {
  console.error('Problems:\n  ' + problems.join('\n  '));
  process.exit(1);
}
console.log('Next: load the tables into a manual upload source data set (Section 14.11, Step 3),');
console.log('or run the template locally with run_template.py (see README.md).');
