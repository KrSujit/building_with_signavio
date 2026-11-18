import fs from 'fs';
import { BpmnModdle } from 'bpmn-moddle';
import { DmnModdle } from 'dmn-moddle';
import { Linter } from 'bpmnlint';
import NodeResolver from 'bpmnlint/lib/resolver/node-resolver.js';
const dir = process.argv[2];
for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.bpmn') || f.endsWith('.dmn'))) {
  const xml = fs.readFileSync(dir + '/' + f, 'utf8');
  if (f.endsWith('.dmn')) {
    const { warnings } = await new DmnModdle().fromXML(xml, 'dmn:Definitions');
    console.log(`${f}: dmn-moddle warnings ${warnings.length}`, warnings.map(w => w.message).slice(0, 3)); continue;
  }
  const moddle = new BpmnModdle();
  const { rootElement, warnings } = await moddle.fromXML(xml);
  const linter = new Linter({ config: { extends: 'bpmnlint:recommended' }, resolver: new NodeResolver() });
  const res = await linter.lint(rootElement);
  const issues = Object.entries(res).flatMap(([rule, rs]) => rs.map(r => `${r.category}:${rule}:${r.id}:${r.message}`));
  console.log(`${f}: moddle warnings ${warnings.length}; bpmnlint ${issues.length}`);
  issues.forEach(i => console.log('   ', i));
  warnings.slice(0, 3).forEach(w => console.log('   W', w.message));
}
