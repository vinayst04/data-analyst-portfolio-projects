import { useState } from 'react';
import {
  ArrowDown, ArrowRight, BarChart3, CheckCircle2, Cloud, Code2, Database,
  FileSpreadsheet, FileText, Globe2, Info, Layers3, LockKeyhole,
  ServerCog, ShieldCheck, Sparkles, TableProperties
} from 'lucide-react';
import './flow.css';

type NodeId = keyof typeof nodeDetails;
type FlowNodeProps = {
  id: NodeId;
  eyebrow: string;
  title: string;
  summary: string;
  icon: React.ElementType;
  tone: 'source' | 'privacy' | 'clean' | 'analysis' | 'delivery' | 'experience';
  selected: NodeId;
  onSelect: (id: NodeId) => void;
  badge?: string;
};

const nodeDetails = {
  source: {
    tool: 'Microsoft Excel · legacy .xls workbook',
    input: 'Recruiter-provided Analyst case-study dataset',
    action: 'Preserved as the untouched source of 3,021 lead records. The project reads Sheet1 and never edits this original file.',
    output: 'Raw rows passed once to Python privacy preparation.',
    evidence: 'data/source/Analyst_case_study_dataset_1.xls'
  },
  privacy: {
    tool: 'Python · pandas · run_analysis.py',
    input: 'Original .xls worksheet',
    action: 'Removes eight direct/free-text identifier fields, replaces VendorLeadID with an anonymous LeadKey, and redacts two IP literals found in ReferralDomain.',
    output: 'A privacy-safe staging dataset with 3,021 unique LeadKey values.',
    evidence: 'data/sanitized/sanitized_staging.csv'
  },
  staging: {
    tool: 'Privacy-safe CSV hand-off',
    input: 'Output of the Python privacy step',
    action: 'Provides a stable, non-sensitive source for the no-code cleaning workflow in Excel Power Query.',
    output: 'Input connection for LeadQualityCleaning.',
    evidence: 'sanitized_staging.csv'
  },
  powerquery: {
    tool: 'Excel Power Query · LeadQualityCleaning',
    input: 'sanitized_staging.csv',
    action: 'Sets data types, cleans text, standardizes partner and widget values, replaces blanks with Unknown, and creates dates, outcome flags, score bands and widget fields.',
    output: 'Refreshed Clean Leads worksheet containing 3,021 analysis-ready records.',
    evidence: 'Applied steps are stored inside Lead_Quality_Analytics.xlsx'
  },
  cleanleads: {
    tool: 'Microsoft Excel · Clean Leads table',
    input: 'LeadQualityCleaning Power Query result',
    action: 'Acts as the canonical cleaned dataset. Excel summaries and the optional advanced Python layer both start from this refreshed table.',
    output: 'Clean source for Excel analysis and advanced analytical validation.',
    evidence: 'outputs/Lead_Quality_Analytics.xlsx · Clean Leads'
  },
  excel: {
    tool: 'Microsoft Excel workbook',
    input: 'Clean Leads Power Query table',
    action: 'Presents human-readable Summary, Trends, Segments, Opportunity, Model and QA sheets with formulas, tables and charts.',
    output: 'Editable workbook used for review and explanation.',
    evidence: 'outputs/Lead_Quality_Analytics.xlsx'
  },
  advanced: {
    tool: 'Python · advanced_analysis.py',
    input: 'Refreshed Excel Clean Leads worksheet',
    action: 'Creates reconciled trends, segment comparisons, target scenarios and QA outputs. It also performs optional confidence intervals, tests, FDR correction, regression and validation.',
    output: 'Sanitized clean-lead file plus reusable analytical CSV exports.',
    evidence: 'Optional supporting validation layer; every published output is independently reconciled.'
  },
  exports: {
    tool: 'Python-generated CSV output layer',
    input: 'Results produced from the Clean Leads analysis',
    action: 'Materializes consistent tables so downstream tools use the same totals and categories rather than rebuilding logic independently.',
    output: 'clean_leads, monthly/weekly trends, segment performance, opportunity inputs, target scenarios, trend tests and QA/model outputs.',
    evidence: 'data/sanitized + data/exports + qa'
  },
  mysql: {
    tool: 'MySQL Workbench · MySQL 8 SQL',
    input: 'Validated clean-lead and analytical output tables',
    action: 'Loads the project schema and runs straightforward KPI, monthly/weekly trend, segment, ranking, opportunity and reconciliation queries.',
    output: 'Reproducible SQL result sets; no SQLite database is used.',
    evidence: 'mysql/lead_quality_analytics_workbench.sql'
  },
  powerbi: {
    tool: 'Power BI Desktop · PBIP/TMDL',
    input: 'Validated local CSV outputs',
    action: 'Builds the semantic model, DAX measures and four interactive pages: overview, trend evidence, drivers and target opportunity.',
    output: 'LeadQualityAnalytics semantic model and report definition.',
    evidence: 'Power BI currently imports local CSVs, not Lakehouse tables.'
  },
  lakehouse: {
    tool: 'Microsoft Fabric · LeadQualityLakehouse',
    input: 'Sanitized clean data and analytical CSV outputs',
    action: 'Stores the deployed Files and Lakehouse tables and exposes the automatically created SQL analytics endpoint.',
    output: 'Cloud copy of sanitized analytical tables, gold files and SQL endpoint.',
    evidence: 'Fabric workspace: Lead Conversion & Quality Analytics'
  },
  published: {
    tool: 'Microsoft Fabric workspace · Power BI Service',
    input: 'PBIR report definition and TMDL semantic model published from the local Power BI project',
    action: 'Hosts the validated semantic model and report in the same workspace as the Lakehouse while retaining the CSV import architecture.',
    output: 'Cloud-hosted report and anonymous Publish-to-web experience.',
    evidence: 'Validated totals: 3,021 leads · 245 closed · 8.11% · target gap 46'
  },
  website: {
    tool: 'React · TypeScript · Vercel',
    input: 'Reconciled monthly, segment and scenario exports plus the public Power BI URL',
    action: 'Presents the native dashboard, embeds the interactive Power BI report and displays Fabric implementation evidence.',
    output: 'Public recruiter-facing analytics experience.',
    evidence: 'lead-quality-analytics-dashboard.vercel.app'
  }
} as const;

const nodeTitles: Record<NodeId, string> = {
  source: 'Original XLS dataset', privacy: 'Privacy preparation', staging: 'Sanitized staging file',
  powerquery: 'LeadQualityCleaning', cleanleads: 'Excel Clean Leads', excel: 'Excel analysis',
  advanced: 'Advanced analysis', exports: 'Analytical exports', mysql: 'MySQL analysis',
  powerbi: 'Power BI project', lakehouse: 'Fabric Lakehouse', published: 'Published model & report', website: 'Public website'
};

function FlowNode({ id, eyebrow, title, summary, icon: Icon, tone, selected, onSelect, badge }: FlowNodeProps) {
  return <button type="button" className={`flow-node tone-${tone} ${selected === id ? 'is-selected' : ''}`} onClick={() => onSelect(id)} aria-pressed={selected === id}>
    <span className="flow-node-icon"><Icon size={17} /></span>
    <span className="flow-node-copy"><small>{eyebrow}</small><strong>{title}</strong><em>{summary}</em></span>
    {badge && <span className="flow-node-badge">{badge}</span>}
  </button>;
}

function Connector() {
  return <div className="flow-connector" aria-hidden="true"><i /><ArrowRight size={15} /></div>;
}

export default function FlowPage() {
  const [selected, setSelected] = useState<NodeId>('cleanleads');
  const detail = nodeDetails[selected];

  return <main className="flow-page">
    <div className="flow-orb flow-orb-one" /><div className="flow-orb flow-orb-two" />
    <header className="flow-header">
      <a className="flow-brand" href="/" aria-label="Lead Conversion and Quality Analytics home">
        <span><small>LEAD CONVERSION</small><b>Data lineage</b></span>
      </a>
      <span className="flow-status"><CheckCircle2 size={14} /> Implemented architecture</span>
    </header>

    <section className="flow-hero">
      <div>
        <p className="flow-kicker"><Sparkles size={13} /> END-TO-END PROJECT FLOW</p>
        <h1>Data Lineage <em>View</em></h1>
        <p className="flow-intro">Click any node to see its input, responsibility, output and implementation evidence. Solid paths show the implemented project flow; the advanced statistical layer is marked optional.</p>
      </div>
      <aside className="flow-proof"><ShieldCheck size={19} /><div><small>CONTROL TOTAL</small><b>3,021 privacy-safe leads</b><span>245 closed · 8.11% close rate</span></div></aside>
    </section>

    <section className="flow-board" aria-label="Interactive data lineage">
      <div className="flow-board-head">
        <div><p>IMPLEMENTED LINEAGE</p><h2><span>Source → privacy → cleaning</span><span className="flow-title-tail"> → analysis → delivery</span></h2></div>
        <div className="flow-legend"><span><i className="core" />Core workflow</span><span><i className="optional" />Optional validation</span><span><i className="cloud" />Cloud delivery</span></div>
      </div>

      <div className="flow-stage-labels"><span>01 · INTAKE</span><span>02 · CLEANING</span><span>03 · ANALYSIS</span><span>04 · DELIVERY</span></div>
      <div className="flow-core-row">
        <FlowNode id="source" eyebrow="SOURCE · EXCEL" title="Original XLS dataset" summary="Recruiter file · 3,021 rows" icon={FileSpreadsheet} tone="source" selected={selected} onSelect={setSelected} />
        <Connector />
        <FlowNode id="privacy" eyebrow="PYTHON · REQUIRED" title="Privacy preparation" summary="Remove PII · LeadKey · redact IPs" icon={LockKeyhole} tone="privacy" selected={selected} onSelect={setSelected} />
        <Connector />
        <FlowNode id="staging" eyebrow="SAFE HAND-OFF" title="Sanitized staging file" summary="sanitized_staging.csv · Power Query input" icon={FileText} tone="privacy" selected={selected} onSelect={setSelected} />
        <Connector />
        <FlowNode id="powerquery" eyebrow="EXCEL POWER QUERY" title="Power Query cleaning" summary="LeadQualityCleaning · types · text · dates · flags" icon={Sparkles} tone="clean" selected={selected} onSelect={setSelected} />
        <Connector />
        <FlowNode id="cleanleads" eyebrow="CANONICAL CLEAN DATA" title="Excel Clean Leads" summary="3,021 analysis-ready records" icon={TableProperties} tone="clean" selected={selected} onSelect={setSelected} badge="SOURCE OF TRUTH" />
      </div>

      <div className="flow-branch-stem"><i /><span><ArrowDown size={14} /> Clean data branches by purpose</span></div>
      <div className="flow-analysis-grid">
        <article className="flow-lane lane-excel">
          <div className="flow-lane-head"><span>REVIEW & EXPLANATION</span><b>Excel branch</b></div>
          <FlowNode id="excel" eyebrow="MICROSOFT EXCEL" title="Workbook analysis" summary="Summary · trends · segments · opportunity · QA" icon={FileSpreadsheet} tone="analysis" selected={selected} onSelect={setSelected} />
          <p>Editable analysis for recruiter review.</p>
        </article>
        <article className="flow-lane lane-python">
          <div className="flow-lane-head"><span>SUPPORTING VALIDATION</span><b>Python branch</b><em>OPTIONAL</em></div>
          <div className="flow-lane-chain">
            <FlowNode id="advanced" eyebrow="ADVANCED PYTHON" title="advanced_analysis.py" summary="Trends · tests · scenarios · QA" icon={Code2} tone="analysis" selected={selected} onSelect={setSelected} badge="OPTIONAL" />
            <Connector />
            <FlowNode id="exports" eyebrow="REUSABLE OUTPUT LAYER" title="Analytical CSV exports" summary="Clean leads · trends · segments · scenarios" icon={Layers3} tone="analysis" selected={selected} onSelect={setSelected} />
          </div>
        </article>
      </div>

      <div className="flow-distribution-label"><span>Validated exports fan out to the implemented delivery tools</span></div>
      <div className="flow-delivery-grid">
        <article className="delivery-card"><div className="delivery-number">A</div><FlowNode id="mysql" eyebrow="MYSQL WORKBENCH" title="SQL analysis" summary="KPI · trends · segments · ranking · QA" icon={Database} tone="delivery" selected={selected} onSelect={setSelected} /><p>Simple, repeatable MySQL queries. SQLite is not part of the project.</p></article>
        <article className="delivery-card delivery-chain"><div className="delivery-number">B</div><FlowNode id="powerbi" eyebrow="POWER BI DESKTOP" title="PBIP semantic model" summary="DAX measures · four report pages" icon={BarChart3} tone="delivery" selected={selected} onSelect={setSelected} /><div className="mini-connector"><ArrowDown size={14} /></div><FlowNode id="published" eyebrow="FABRIC WORKSPACE" title="Published model & report" summary="Validated cloud report · public embed" icon={Cloud} tone="delivery" selected={selected} onSelect={setSelected} /></article>
        <article className="delivery-card"><div className="delivery-number">C</div><FlowNode id="lakehouse" eyebrow="MICROSOFT FABRIC" title="LeadQualityLakehouse" summary="Files · tables · SQL analytics endpoint" icon={ServerCog} tone="delivery" selected={selected} onSelect={setSelected} /><p>Parallel deployment branch; it is not Power BI’s current data source.</p></article>
        <article className="delivery-card delivery-website"><div className="delivery-number">D</div><FlowNode id="website" eyebrow="REACT + VERCEL" title="Public website" summary="Native dashboard · Power BI embed · Fabric evidence" icon={Globe2} tone="experience" selected={selected} onSelect={setSelected} /><div className="website-inputs"><span>Analytical exports</span><span>Public Power BI report</span></div></article>
      </div>

      <section className="flow-inspector" aria-live="polite">
        <div className="inspector-title"><p>SELECTED NODE</p><h3>{nodeTitles[selected]}</h3><span>{detail.tool}</span></div>
        <dl><div><dt>Receives</dt><dd>{detail.input}</dd></div><div><dt>What happens</dt><dd>{detail.action}</dd></div><div><dt>Produces</dt><dd>{detail.output}</dd></div><div><dt>Implementation evidence</dt><dd>{detail.evidence}</dd></div></dl>
      </section>
    </section>

    <section className="flow-facts">
      <article><span>01</span><div><b>Cleaning ownership</b><p>Python protects privacy before Excel. Excel Power Query owns the explainable business cleaning process.</p></div></article>
      <article><span>02</span><div><b>Optional statistics</b><p>Advanced Python strengthens the evidence but is not required for the core assignment workflow.</p></div></article>
      <article><span>03</span><div><b>Fabric architecture</b><p>The Lakehouse and published Power BI items share one workspace, but Power BI currently imports local CSV outputs.</p></div></article>
      <article><span>04</span><div><b>Public delivery</b><p>The website combines native charts with the anonymous interactive Power BI report.</p></div></article>
    </section>
    <section className="flow-note"><Info size={18} /><p><b>Architecture boundary:</b> no arrow is drawn from the Fabric Lakehouse to Power BI because that connection is not implemented. The diagram intentionally reflects the working project rather than a proposed future architecture.</p></section>
  </main>;
}
