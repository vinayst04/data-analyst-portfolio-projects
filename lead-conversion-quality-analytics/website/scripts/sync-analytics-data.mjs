import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const dashboardDir = path.resolve(scriptDir, '..');
const exportDir = path.resolve(dashboardDir, '..', 'data', 'exports');
const outputPath = path.join(dashboardDir, 'src', 'data.ts');

function parseCsv(text) {
  const rows = [];
  let row = [];
  let value = '';
  let quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const char = text[i];
    if (quoted) {
      if (char === '"' && text[i + 1] === '"') {
        value += '"';
        i += 1;
      } else if (char === '"') {
        quoted = false;
      } else {
        value += char;
      }
    } else if (char === '"') {
      quoted = true;
    } else if (char === ',') {
      row.push(value);
      value = '';
    } else if (char === '\n') {
      row.push(value.replace(/\r$/, ''));
      rows.push(row);
      row = [];
      value = '';
    } else {
      value += char;
    }
  }
  if (value.length || row.length) {
    row.push(value.replace(/\r$/, ''));
    rows.push(row);
  }
  const [headers, ...body] = rows.filter((entry) => entry.some((cell) => cell !== ''));
  return body.map((entry) => Object.fromEntries(headers.map((header, index) => [header.replace(/^\uFEFF/, ''), entry[index] ?? ''])));
}

function readCsv(name) {
  return parseCsv(fs.readFileSync(path.join(exportDir, name), 'utf8'));
}

function n(value) {
  return Number(value);
}

function q(value) {
  return JSON.stringify(value);
}

function fixed(value, digits = 2) {
  return n(value).toFixed(digits);
}

const monthly = readCsv('monthly_trends.csv');
const segments = readCsv('segment_performance.csv');
const scenarioRows = readCsv('target_scenarios.csv');

const dimensionSpecs = [
  ['Ad group', 'Ad group'],
  ['Debt level', 'Debt level'],
  ['Partner', 'Partner'],
];

const monthLines = monthly.map((row) => {
  const month = new Date(`${row.MonthStart}T00:00:00Z`).toLocaleString('en-US', { month: 'short', timeZone: 'UTC' });
  return `  { month: ${q(month)}, leads: ${n(row.Leads)}, closed: ${n(row.Closed)}, rate: ${fixed(n(row.CloseRate) * 100)}, positive: ${fixed(n(row.PositiveSignalRate) * 100)}, low: ${fixed(n(row.CloseRateWilsonLow) * 100)}, high: ${fixed(n(row.CloseRateWilsonHigh) * 100)} }`;
});

const dimensionBlocks = dimensionSpecs.map(([label, sourceDimension]) => {
  const rows = segments
    .filter((row) => row.Dimension === sourceDimension && row.MeetsReliableN === '1')
    .sort((a, b) => n(b.CloseRate) - n(a.CloseRate) || n(b.Leads) - n(a.Leads));
  if (!rows.length) throw new Error(`No reliable rows found for ${sourceDimension}`);
  const lines = rows.map((row) => `    { segment: ${q(row.Segment)}, leads: ${n(row.Leads)}, closed: ${n(row.Closed)}, rate: ${fixed(n(row.CloseRate) * 100)}, lift: ${fixed(row.LiftVsOverall)}, significant: ${row.StatisticallyDistinctFDR05 === '1'} }`);
  return `  ${q(label)}: [\n${lines.join(',\n')}\n  ]`;
});

const confidenceByScenario = {
  'Portfolio conversion target': 'Planning benchmark',
  'Observed ad-group mix test': 'Directional hypothesis',
  'Conservative ad-group mix test': 'Lower-bound hypothesis',
};

const scenarioLines = scenarioRows.map((row) => `  { name: ${q(row.Scenario)}, affected: ${n(row.LeadsAffected)}, destination: ${fixed(n(row.AssumedDestinationRate) * 100)}, incremental: ${fixed(row.ExpectedIncrementalCloses)}, total: ${Math.round(n(row.ExpectedTotalCloses))}, rate: ${fixed(n(row.ExpectedCloseRate) * 100)}, confidence: ${q(confidenceByScenario[row.Scenario] ?? 'Assumption-driven')} }`);

const generated = `// Generated from ../data/exports by scripts/sync-analytics-data.mjs. Do not hand-edit.\nexport const months = [\n${monthLines.join(',\n')}\n];\n\nexport const dimensions = {\n${dimensionBlocks.join(',\n')}\n} as const;\n\nexport const scenarios = [\n${scenarioLines.join(',\n')}\n];\n`;

if (process.argv.includes('--check')) {
  const existing = fs.readFileSync(outputPath, 'utf8').replace(/\r\n/g, '\n');
  if (existing !== generated) {
    console.error('Website analytics data does not reconcile to the current exports. Run npm run sync:data.');
    process.exit(1);
  }
  console.log(`PASS: ${path.relative(dashboardDir, outputPath)} reconciles to monthly, segment, and scenario exports.`);
} else {
  fs.writeFileSync(outputPath, generated, 'utf8');
  console.log(`Wrote ${path.relative(dashboardDir, outputPath)} from ${path.relative(dashboardDir, exportDir)}.`);
}
