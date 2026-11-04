import os
import subprocess
from pathlib import Path

# Paths
base_dir = Path(r"c:\Users\ragur\Downloads\ai model project")
exports_dir = base_dir / "storage" / "exports"
exports_dir.mkdir(parents=True, exist_ok=True)

html_path = exports_dir / "AI_Model_Trainer_Interview_Study_Guide.html"
pdf_path = exports_dir / "AI_Model_Trainer_Interview_Study_Guide.pdf"
edge_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>AI Model Trainer & Technical Evaluation Specialist - Study Guide & Cheat Sheet</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"
    onload="renderMathInElement(document.body, {delimiters: [{left: '$$', right: '$$', display: true}, {left: '$', right: '$', display: false}]});"></script>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

  :root {
    --primary: #1e3a8a;
    --primary-light: #3b82f6;
    --primary-bg: #eff6ff;
    --accent: #0f766e;
    --accent-bg: #f0fdfa;
    --dark: #0f172a;
    --slate: #334155;
    --muted: #64748b;
    --border: #cbd5e1;
    --border-subtle: #e2e8f0;
    --bg-card: #f8fafc;
    --success: #15803d;
    --warning: #b45309;
    --danger: #b91c1c;
  }

  * { box-sizing: border-box; }
  
  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: var(--dark);
    line-height: 1.55;
    font-size: 13px;
    background: #ffffff;
    margin: 0;
    padding: 20px;
  }

  @page {
    size: A4 portrait;
    margin: 14mm 12mm 14mm 12mm;
    @bottom-right {
      content: "Page " counter(page) " of " counter(pages);
      font-size: 9px;
      font-family: 'Inter', sans-serif;
      color: #94a3b8;
    }
    @bottom-left {
      content: "AI Model Trainer & Technical Evaluation Specialist | Study Guide";
      font-size: 9px;
      font-family: 'Inter', sans-serif;
      color: #94a3b8;
    }
  }

  .page-break {
    page-break-after: always;
    break-after: page;
  }

  .avoid-break {
    page-break-inside: avoid;
    break-inside: avoid;
  }

  /* Headers */
  .doc-header {
    border-bottom: 3px solid var(--primary);
    padding-bottom: 12px;
    margin-bottom: 20px;
  }
  .doc-title {
    font-size: 24px;
    font-weight: 800;
    color: var(--primary);
    margin: 0 0 4px 0;
    letter-spacing: -0.5px;
  }
  .doc-subtitle {
    font-size: 13px;
    font-weight: 600;
    color: var(--slate);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 0 0 6px 0;
  }
  .doc-meta {
    font-size: 11px;
    color: var(--muted);
    display: flex;
    gap: 15px;
  }

  h1.section-title {
    font-size: 18px;
    font-weight: 800;
    color: #ffffff;
    background: linear-gradient(135deg, #1e3a8a, #2563eb);
    padding: 8px 14px;
    border-radius: 6px;
    margin: 22px 0 14px 0;
    letter-spacing: -0.2px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  h2.topic-title {
    font-size: 15px;
    font-weight: 700;
    color: var(--primary);
    border-left: 4px solid var(--primary-light);
    padding-left: 10px;
    margin: 18px 0 10px 0;
  }

  h3 {
    font-size: 13px;
    font-weight: 700;
    color: var(--slate);
    margin: 12px 0 6px 0;
  }

  p { margin: 0 0 8px 0; }
  ul, ol { margin: 0 0 10px 0; padding-left: 20px; }
  li { margin-bottom: 4px; }

  /* Tables */
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 8px 0 14px 0;
    font-size: 11.5px;
    page-break-inside: avoid;
  }
  th, td {
    padding: 6px 10px;
    border: 1px solid var(--border);
    text-align: left;
    vertical-align: top;
  }
  th {
    background: #f1f5f9;
    color: var(--dark);
    font-weight: 700;
  }
  tr:nth-child(even) td {
    background: #f8fafc;
  }

  /* Callout Boxes */
  .formula-box {
    background: var(--primary-bg);
    border: 1px solid #bfdbfe;
    border-left: 4px solid var(--primary-light);
    border-radius: 6px;
    padding: 8px 12px;
    margin: 8px 0 12px 0;
    font-size: 12px;
  }
  .formula-box strong { color: var(--primary); }

  .shortcut-box {
    background: var(--accent-bg);
    border: 1px solid #99f6e4;
    border-left: 4px solid var(--accent);
    border-radius: 6px;
    padding: 8px 12px;
    margin: 8px 0 12px 0;
    font-size: 12px;
  }
  .shortcut-box strong { color: var(--accent); }

  .problem-box {
    background: #ffffff;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 10px 14px;
    margin: 10px 0 14px 0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    page-break-inside: avoid;
    break-inside: avoid;
  }
  .problem-badge {
    display: inline-block;
    font-size: 10px;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 4px;
    text-transform: uppercase;
    margin-bottom: 6px;
  }
  .badge-moderate { background: #dbeafe; color: #1e40af; }
  .badge-tricky { background: #fee2e2; color: #991b1b; }
  .problem-title { font-weight: 700; color: var(--dark); margin-bottom: 6px; font-size: 12.5px; }
  .solution-step { margin-top: 6px; font-size: 12px; }
  .solution-step ol { margin-left: 16px; margin-bottom: 4px; }
  .answer-highlight {
    background: #dcfce7;
    color: #14532d;
    padding: 2px 6px;
    border-radius: 4px;
    font-weight: 700;
    display: inline-block;
    margin-top: 4px;
  }

  /* Code Blocks */
  pre {
    background: #0f172a;
    color: #f8fafc;
    font-family: 'JetBrains Mono', Consolas, monospace;
    font-size: 11px;
    padding: 10px 12px;
    border-radius: 6px;
    overflow-x: auto;
    margin: 8px 0 12px 0;
    line-height: 1.45;
    page-break-inside: avoid;
    break-inside: avoid;
  }
  code {
    font-family: 'JetBrains Mono', Consolas, monospace;
    font-size: 11px;
    background: #f1f5f9;
    color: #0f172a;
    padding: 1px 4px;
    border-radius: 3px;
  }
  pre code {
    background: transparent;
    color: inherit;
    padding: 0;
  }

  .code-comment { color: #94a3b8; font-style: italic; }
  .code-keyword { color: #38bdf8; font-weight: 600; }
  .code-func { color: #a78bfa; }
  .code-str { color: #4ade80; }

  /* Diagrams & Trees */
  .diagram-container {
    background: #f8fafc;
    border: 1px dashed var(--border);
    border-radius: 6px;
    padding: 10px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    line-height: 1.4;
    white-space: pre;
    color: var(--slate);
    margin: 8px 0 12px 0;
    page-break-inside: avoid;
  }
</style>
</head>
<body>

<div class="doc-header">
  <div class="doc-subtitle">Executive Technical Certification & Assessment Curriculum</div>
  <h1 class="doc-title">AI MODEL TRAINER & TECHNICAL EVALUATION SPECIALIST</h1>
  <div class="doc-meta">
    <span><strong>Target Roles:</strong> AI Model Trainer, LLM Annotation Specialist, Prompt Engineer, RLHF Evaluator</span>
    <span><strong>Format:</strong> High-Density PDF Reference Manual</span>
    <span><strong>Version:</strong> 2026.1 Production</span>
  </div>
</div>

<!-- ======================================================== -->
<!-- SECTION 1: QUANTITATIVE APTITUDE -->
<!-- ======================================================== -->
<h1 class="section-title">SECTION 1: QUANTITATIVE APTITUDE</h1>

<!-- 1.1 Percentages, Profit & Loss -->
<h2 class="topic-title">1.1 Percentages, Profit & Loss, and Discount</h2>
<div class="formula-box">
  <strong>Core Formulas:</strong><br>
  • Percentage Change: $\Delta\% = \frac{\text{New} - \text{Old}}{\text{Old}} \times 100$ | Multiplying Factor: $MF = 1 \pm \frac{x}{100}$<br>
  • Net Successive Change: $E = a + b + \frac{ab}{100}\%$ (use $+$ for increase, $-$ for decrease)<br>
  • Profit/Loss: $\text{Profit} = SP - CP$, $\text{Loss} = CP - SP$; $\text{P/L}\% = \frac{|\text{Diff}|}{CP} \times 100$<br>
  • Marked Price & Discount: $SP = MP \left(1 - \frac{D\%}{100}\right)$ | Fundamental Cost-to-Markup Ratio: $\frac{CP}{MP} = \frac{100 - D\%}{100 + P\%}$
</div>

<div class="shortcut-box">
  <strong>Quick Shortcuts & Elimination Tricks:</strong><br>
  • <strong>Invariance Rule ($A \times B = \text{Const}$):</strong> If factor $A$ increases by $\frac{x}{y}$, factor $B$ must decrease by $\frac{x}{x+y}$ to keep product unchanged.<br>
  • <strong>Successive Discount:</strong> Two discounts $d_1, d_2 \implies D_{\text{eff}} = d_1 + d_2 - \frac{d_1 d_2}{100}\%$.<br>
  • <strong>False Weight / Dishonest Dealer:</strong> $\text{Gain}\% = \frac{\text{Claimed Measure} - \text{True Measure}}{\text{True Measure}} \times 100$.
</div>

<div class="problem-box">
  <span class="problem-badge badge-moderate">Problem 1 (Moderate)</span>
  <div class="problem-title">Successive Discounts with Net Margin</div>
  <p>A trader marks an electronic item $40\%$ above cost price and offers two successive discounts of $15\%$ and $10\%$. Find his net profit percentage.</p>
  <div class="solution-step">
    <strong>Step-by-step Solution:</strong>
    <ol>
      <li>Let $CP = 100$. Marked Price $MP = 100 \times 1.40 = 140$.</li>
      <li>Equivalent discount $D_{\text{eff}} = 15 + 10 - \frac{15 \times 10}{100} = 25 - 1.5 = 23.5\%$.</li>
      <li>$SP = 140 \times (1 - 0.235) = 140 \times 0.765 = 107.10$.</li>
      <li>$\text{Net Profit} = SP - CP = 107.10 - 100 = 7.10\%$.</li>
    </ol>
    <div class="answer-highlight">Answer: 7.1% Profit</div>
  </div>
</div>

<div class="problem-box">
  <span class="problem-badge badge-tricky">Problem 2 (Tricky)</span>
  <div class="problem-title">Dishonest Merchant with Markup & Cash Discount</div>
  <p>A merchant marks goods $20\%$ above $CP$, but uses a faulty scale reading $1000\text{ g}$ for every $800\text{ g}$ actual weight. He also grants a $10\%$ cash discount. Find his true profit percentage.</p>
  <div class="solution-step">
    <strong>Step-by-step Solution:</strong>
    <ol>
      <li>Let true cost of $1\text{ g} = \$1$. True cost of goods dispensed ($800\text{ g}$) $= \$800$.</li>
      <li>Customer pays for $1000\text{ g}$ at $MP$: Nominal bill $= 1000 \times 1.20 = \$1200$.</li>
      <li>Apply $10\%$ cash discount: $SP = 1200 \times 0.90 = \$1080$.</li>
      <li>True profit percentage $= \frac{1080 - 800}{800} \times 100 = \frac{280}{800} \times 100 = 35\%$.</li>
    </ol>
    <div class="answer-highlight">Answer: 35% True Profit</div>
  </div>
</div>

<!-- 1.2 SI & CI -->
<h2 class="topic-title">1.2 Simple & Compound Interest</h2>
<div class="formula-box">
  <strong>Core Formulas:</strong><br>
  • $SI = \frac{P \times R \times T}{100}$ | $A = P\left(1 + \frac{R}{100}\right)^T$, $CI = A - P$<br>
  • 2-Year Difference: $\Delta_2 = CI_2 - SI_2 = P\left(\frac{R}{100}\right)^2$<br>
  • 3-Year Difference: $\Delta_3 = P\left(\frac{R}{100}\right)^2 \left(\frac{300 + R}{100}\right)$
</div>

<div class="shortcut-box">
  <strong>Shortcut Multipliers & Rules:</strong><br>
  • <strong>Pascal's Triangle Ratio Method:</strong> 2 Years $\implies 2:1$; 3 Years $\implies 3:3:1$; 4 Years $\implies 4:6:4:1$.<br>
  • <strong>Rule of 72:</strong> Years to double $\approx \frac{72}{R}$ | <strong>Rule of 114:</strong> Years to triple $\approx \frac{114}{R}$ | <strong>Rule of 144:</strong> Years to quadruple $\approx \frac{144}{R}$.
</div>

<div class="problem-box">
  <span class="problem-badge badge-moderate">Problem 1 (Moderate)</span>
  <div class="problem-title">Principal Determination from 3-Year Interest Difference</div>
  <p>The difference between CI and SI on a sum of money at $10\%$ p.a. for $3$ years is $\$620$. Find the principal.</p>
  <div class="solution-step">
    <strong>Step-by-step Solution:</strong>
    <ol>
      <li>Use the 3-year formula: $\Delta_3 = P \left(\frac{R}{100}\right)^2 \left(\frac{300 + R}{100}\right)$.</li>
      <li>$620 = P \left(\frac{10}{100}\right)^2 \left(\frac{310}{100}\right) = P \times \frac{1}{100} \times \frac{31}{10} = P \times \frac{31}{1000}$.</li>
      <li>$P = \frac{620 \times 1000}{31} = 20 \times 1000 = \$20,000$.</li>
    </ol>
    <div class="answer-highlight">Answer: $20,000 Principal</div>
  </div>
</div>

<div class="problem-box">
  <span class="problem-badge badge-tricky">Problem 2 (Tricky)</span>
  <div class="problem-title">Compound Growth over Equal Time Intervals</div>
  <p>A sum invested under CI grows to $\$8,000$ after $3$ years and to $\$12,000$ after $6$ years. Find the original principal.</p>
  <div class="solution-step">
    <strong>Step-by-step Solution:</strong>
    <ol>
      <li>Equal time intervals ($0 \to 3$ yrs and $3 \to 6$ yrs) mean compounding multiplier $k^3$ is invariant.</li>
      <li>$A_3 = P \cdot k^3 = 8,000$ and $A_6 = P \cdot k^6 = 12,000$.</li>
      <li>$\frac{A_6}{A_3} = k^3 = \frac{12,000}{8,000} = 1.5 = \frac{3}{2}$.</li>
      <li>Substitute into $A_3$: $P \times \frac{3}{2} = 8,000 \implies P = \frac{8,000 \times 2}{3} = \$5,333.33$.</li>
    </ol>
    <div class="answer-highlight">Answer: $5,333.33</div>
  </div>
</div>

<div class="page-break"></div>

<!-- 1.3 Time, Speed, Distance -->
<h2 class="topic-title">1.3 Time, Speed, Distance & Relative Motion</h2>
<div class="formula-box">
  <strong>Core Formulas:</strong><br>
  • Unit Conversion: $1\text{ km/h} = \frac{5}{18}\text{ m/s}$ | $1\text{ m/s} = \frac{18}{5}\text{ km/h}$<br>
  • Average Speed (Equal Distances): $S_{\text{avg}} = \frac{2xy}{x + y}$ (Harmonic Mean)<br>
  • Relative Speed: Opposite Direction $= S_1 + S_2$ | Same Direction $= |S_1 - S_2|$<br>
  • Boats & Streams: Downstream $D = u + v$, Upstream $U = u - v \implies u = \frac{D+U}{2}$, $v = \frac{D-U}{2}$
</div>

<div class="shortcut-box">
  <strong>Shortcut Rules:</strong><br>
  • <strong>Post-Meeting Travel Theorem:</strong> If bodies start simultaneously towards each other and take $t_1, t_2$ hours after meeting: $\frac{S_1}{S_2} = \sqrt{\frac{t_2}{t_1}}$.<br>
  • <strong>Late/Early Formula:</strong> Distance $= \frac{S_1 \times S_2}{|S_1 - S_2|} \times \frac{\Delta t_{\text{total}}}{60}$.
</div>

<div class="problem-box">
  <span class="problem-badge badge-moderate">Problem 1 (Moderate)</span>
  <div class="problem-title">Dual Train Crossing (Same Direction)</div>
  <p>Train $A$ ($180\text{ m}$, $72\text{ km/h}$) overtakes Train $B$ ($120\text{ m}$, $36\text{ km/h}$) running in the same direction. Find the time taken to completely cross.</p>
  <div class="solution-step">
    <strong>Step-by-step Solution:</strong>
    <ol>
      <li>Total distance to clear $= L_1 + L_2 = 180 + 120 = 300\text{ m}$.</li>
      <li>Relative speed $= 72 - 36 = 36\text{ km/h} = 36 \times \frac{5}{18} = 10\text{ m/s}$.</li>
      <li>$\text{Time} = \frac{300}{10} = 30\text{ seconds}$.</li>
    </ol>
    <div class="answer-highlight">Answer: 30 seconds</div>
  </div>
</div>

<div class="problem-box">
  <span class="problem-badge badge-tricky">Problem 2 (Tricky)</span>
  <div class="problem-title">Post-Meeting Velocity via Square Root Ratio</div>
  <p>Trains $P$ and $Q$ start simultaneously from $X$ and $Y$ towards each other. After passing, $P$ takes $4\text{ hr } 48\text{ min}$ to reach $Y$, and $Q$ takes $3\text{ hr } 20\text{ min}$ to reach $X$. If $S_P = 45\text{ km/h}$, find $S_Q$.</p>
  <div class="solution-step">
    <strong>Step-by-step Solution:</strong>
    <ol>
      <li>Convert times: $t_P = 4 + \frac{48}{60} = \frac{24}{5}\text{ hr}$; $t_Q = 3 + \frac{20}{60} = \frac{10}{3}\text{ hr}$.</li>
      <li>Apply Post-Meeting Theorem: $\frac{S_P}{S_Q} = \sqrt{\frac{t_Q}{t_P}} = \sqrt{\frac{10/3}{24/5}} = \sqrt{\frac{50}{72}} = \sqrt{\frac{25}{36}} = \frac{5}{6}$.</li>
      <li>$\frac{45}{S_Q} = \frac{5}{6} \implies S_Q = \frac{45 \times 6}{5} = 54\text{ km/h}$.</li>
    </ol>
    <div class="answer-highlight">Answer: 54 km/h</div>
  </div>
</div>

<!-- 1.4 Time & Work -->
<h2 class="topic-title">1.4 Time & Work, Pipes & Cisterns</h2>
<div class="formula-box">
  <strong>Core Formulas:</strong><br>
  • Efficiency $E = \frac{\text{Total Work}}{\text{Time Taken}}$ | Assume Work $= \text{LCM}(\text{Time}_1, \dots, \text{Time}_k)$<br>
  • Combined Work: $\text{Time}_{(A+B)} = \frac{\text{Work}}{E_A + E_B}$ | MDH Formula: $\frac{M_1 D_1 H_1 E_1}{W_1} = \frac{M_2 D_2 H_2 E_2}{W_2}$
</div>

<div class="problem-box">
  <span class="problem-badge badge-moderate">Problem 1 (Moderate)</span>
  <div class="problem-title">Alternate Day Rotation Work</div>
  <p>$A$ completes work in $12$ days and $B$ in $18$ days. They work on alternate days with $A$ starting on day 1. Find total days.</p>
  <div class="solution-step">
    <strong>Step-by-step Solution:</strong>
    <ol>
      <li>Total Work $= \text{LCM}(12, 18) = 36\text{ units}$. Efficiencies: $E_A = 3$, $E_B = 2\text{ units/day}$.</li>
      <li>One 2-day cycle $(A + B) = 3 + 2 = 5\text{ units}$.</li>
      <li>7 full cycles ($14$ days) $= 7 \times 5 = 35\text{ units}$. Remaining work $= 36 - 35 = 1\text{ unit}$.</li>
      <li>Day 15: $A$ works: $\text{Time} = \frac{1}{E_A} = \frac{1}{3}\text{ day}$. Total $= 14\frac{1}{3}\text{ days}$.</li>
    </ol>
    <div class="answer-highlight">Answer: 14 1/3 days (14.33 days)</div>
  </div>
</div>

<div class="problem-box">
  <span class="problem-badge badge-tricky">Problem 2 (Tricky)</span>
  <div class="problem-title">Combined Inlets with Drain and Staggered Closures</div>
  <p>Pipe $A$ fills in $10\text{ hr}$, $B$ in $15\text{ hr}$, $C$ empties in $20\text{ hr}$. All open together. After $2\text{ hr}$, $C$ is closed. $1\text{ hr}$ before completion, $B$ is closed. Find total time taken.</p>
  <div class="solution-step">
    <strong>Step-by-step Solution:</strong>
    <ol>
      <li>Capacity $= \text{LCM}(10, 15, 20) = 60\text{ units}$. Rates: $E_A = +6, E_B = +4, E_C = -3$.</li>
      <li>First $2\text{ hr}$ (all open): Work $= 2 \times (6 + 4 - 3) = 14\text{ units}$. Remainder $= 60 - 14 = 46$.</li>
      <li>Last $1\text{ hr}$ (only $A$ open, since $B$ closed $1\text{ hr}$ prior): Work $= 1 \times 6 = 6\text{ units}$.</li>
      <li>Middle phase ($A + B$ open): Work $= 46 - 6 = 40\text{ units}$. Time $= \frac{40}{6+4} = 4\text{ hr}$.</li>
      <li>Total Time $= 2 + 4 + 1 = 7\text{ hours}$.</li>
    </ol>
    <div class="answer-highlight">Answer: 7 hours</div>
  </div>
</div>

<div class="page-break"></div>

<!-- 1.5 Ratios & Mixtures -->
<h2 class="topic-title">1.5 Ratios, Proportions, Mixtures & Alligations</h2>
<div class="formula-box">
  <strong>Core Formulas:</strong><br>
  • Rule of Alligation: $\frac{Q_{\text{cheaper}}}{Q_{\text{dearer}}} = \frac{C_{\text{dearer}} - C_{\text{mean}}}{C_{\text{mean}} - C_{\text{cheaper}}}$ (All values must be on identical base, e.g., all CP)<br>
  • Repeated Dilution: $Q_{\text{final}} = Q_{\text{initial}} \left(1 - \frac{y}{x}\right)^n$ ($x$: total capacity, $y$: replaced volume, $n$: cycles)
</div>

<div class="problem-box">
  <span class="problem-badge badge-moderate">Problem 1 (Moderate)</span>
  <div class="problem-title">Alligation of Commodity Costs with Desired Profit</div>
  <p>In what ratio must pulses at $\$15/\text{kg}$ and $\$20/\text{kg}$ be mixed so that selling the mixture at $\$21.60/\text{kg}$ gives $20\%$ profit?</p>
  <div class="solution-step">
    <strong>Step-by-step Solution:</strong>
    <ol>
      <li>Mean Cost Price $CP_{\text{mix}} = \frac{SP}{1 + P\%} = \frac{21.60}{1.20} = \$18/\text{kg}$.</li>
      <li>Apply Alligation: $\frac{Q_1}{Q_2} = \frac{20 - 18}{18 - 15} = \frac{2}{3}$.</li>
    </ol>
    <div class="answer-highlight">Answer: 2 : 3</div>
  </div>
</div>

<div class="problem-box">
  <span class="problem-badge badge-tricky">Problem 2 (Tricky)</span>
  <div class="problem-title">Successive Replacement of Liquid</div>
  <p>A barrel holds $80\text{ L}$ of pure ethanol. $8\text{ L}$ are removed and replaced with water. This process is repeated 2 more times (total 3 operations). Find final volume of ethanol.</p>
  <div class="solution-step">
    <strong>Step-by-step Solution:</strong>
    <ol>
      <li>Fraction remaining each step $= 1 - \frac{8}{80} = 1 - \frac{1}{10} = \frac{9}{10} = 0.9$.</li>
      <li>$Q_{\text{final}} = 80 \times \left(\frac{9}{10}\right)^3 = 80 \times \frac{729}{1000} = \frac{58,320}{1000} = 58.32\text{ liters}$.</li>
    </ol>
    <div class="answer-highlight">Answer: 58.32 Liters</div>
  </div>
</div>

<!-- 1.6 Permutations, Combinations & Probability -->
<h2 class="topic-title">1.6 Permutations, Combinations & Probability</h2>
<div class="formula-box">
  <strong>Core Formulas:</strong><br>
  • $^nP_r = \frac{n!}{(n-r)!}$ | $^nC_r = \frac{n!}{r!(n-r)!}$ | Circular: $(n-1)!$<br>
  • $P(A \cup B) = P(A) + P(B) - P(A \cap B)$ | Conditional: $P(A \mid B) = \frac{P(A \cap B)}{P(B)}$<br>
  • Complement Shortcut: $P(\text{At least 1}) = 1 - P(\text{None})$
</div>

<div class="problem-box">
  <span class="problem-badge badge-moderate">Problem 1 (Moderate)</span>
  <div class="problem-title">Constrained Team Formation</div>
  <p>A team of 5 AI evaluators is selected from 6 Computer Scientists and 5 Linguists. Find the number of ways if at least 3 Computer Scientists must be included.</p>
  <div class="solution-step">
    <strong>Step-by-step Solution:</strong>
    <ol>
      <li>Case 1: $3\text{ CS, } 2\text{ Ling} \implies ^6C_3 \times ^5C_2 = 20 \times 10 = 200$.</li>
      <li>Case 2: $4\text{ CS, } 1\text{ Ling} \implies ^6C_4 \times ^5C_1 = 15 \times 5 = 75$.</li>
      <li>Case 3: $5\text{ CS, } 0\text{ Ling} \implies ^6C_5 \times ^5C_0 = 6 \times 1 = 6$.</li>
      <li>Total Ways $= 200 + 75 + 6 = 281$.</li>
    </ol>
    <div class="answer-highlight">Answer: 281 ways</div>
  </div>
</div>

<div class="problem-box">
  <span class="problem-badge badge-tricky">Problem 2 (Tricky)</span>
  <div class="problem-title">Sampling Without Replacement (Complement Rule)</div>
  <p>A batch has 12 synthetic prompts (4 hallucinated, 8 clean). If 3 are drawn at random without replacement, find the probability that at least 1 is hallucinated.</p>
  <div class="solution-step">
    <strong>Step-by-step Solution:</strong>
    <ol>
      <li>$P(\text{At least 1 Hallucinated}) = 1 - P(\text{All 3 Clean})$.</li>
      <li>Ways to choose 3 clean $= ^8C_3 = \frac{8 \times 7 \times 6}{6} = 56$.</li>
      <li>Total ways to choose 3 prompts $= ^{12}C_3 = \frac{12 \times 11 \times 10}{6} = 220$.</li>
      <li>$P(\text{All Clean}) = \frac{56}{220} = \frac{14}{55} \implies P(\text{At least 1}) = 1 - \frac{14}{55} = \frac{41}{55} \approx 74.55\%$.</li>
    </ol>
    <div class="answer-highlight">Answer: 41/55 (74.55%)</div>
  </div>
</div>

<div class="page-break"></div>

<!-- ======================================================== -->
<!-- SECTION 2: LOGICAL REASONING -->
<!-- ======================================================== -->
<h1 class="section-title">SECTION 2: LOGICAL REASONING</h1>

<h2 class="topic-title">2.1 Syllogisms</h2>
<div class="shortcut-box">
  <strong>100-50 & Venn Rules:</strong><br>
  • All $A$ are $B$: $A=100, B=50$ | No $A$ is $B$: $A=100, B=100$<br>
  • Some $A$ are $B$: $A=50, B=50$ | Some $A$ are not $B$: $A=50, B=100$<br>
  • <strong>Polarity Rules:</strong> 2 Negative Premises $\implies$ No conclusion; 2 Particulars $\implies$ No conclusion.<br>
  • <strong>Either-Or Complementary Pairs:</strong> Requires (1) identical Subject & Predicate, (2) both conclusions uncertain, (3) pair is `Some + No` OR `Some + Some Not`.
</div>

<div class="problem-box">
  <span class="problem-badge badge-moderate">Problem 1 (Standard Deduction)</span>
  <div class="problem-title">Three Premise Valid Transitivity</div>
  <p><strong>Statements:</strong> (1) All models are algorithms. (2) All algorithms are programs. (3) No program is hardware.<br>
  <strong>Conclusions:</strong> I. No model is hardware. II. Some programs are models.</p>
  <div class="solution-step">
    <strong>Step-by-step Solution:</strong>
    <ol>
      <li>Chain: $\text{Models} \subset \text{Algorithms} \subset \text{Programs}$.</li>
      <li>Statement 3: $\text{Programs} \cap \text{Hardware} = \emptyset$.</li>
      <li>Since $\text{Models} \subseteq \text{Programs}$, Models can have zero overlap with Hardware. (Conclusion I holds).</li>
      <li>Models are a non-empty subset of Programs. (Conclusion II holds).</li>
    </ol>
    <div class="answer-highlight">Answer: Both conclusions I and II follow</div>
  </div>
</div>

<div class="problem-box">
  <span class="problem-badge badge-tricky">Problem 2 (Tricky: Either-Or with Possibility)</span>
  <div class="problem-title">Complementary Pair with Overlapping Possibility</div>
  <p><strong>Statements:</strong> (1) Some parameters are weights. (2) Some weights are biases. (3) No bias is an activation.<br>
  <strong>Conclusions:</strong> I. Some parameters are activations. II. No parameter is an activation. III. All activations being weights is a possibility.</p>
  <div class="solution-step">
    <strong>Step-by-step Solution:</strong>
    <ol>
      <li>Parameters and Activations have no direct or valid transitive link. Both I and II are uncertain individually.</li>
      <li>Subject and predicate are identical and form a `Some + No` pair $\implies$ <strong>Either I or II follows</strong>.</li>
      <li>Activations cannot overlap Biases, but Weights is a larger set. Activations can completely reside in the non-bias segment of Weights without violating any premise $\implies$ <strong>III is a valid possibility</strong>.</li>
    </ol>
    <div class="answer-highlight">Answer: Either I or II follows, and III follows</div>
  </div>
</div>

<h2 class="topic-title">2.2 Blood Relations</h2>
<div class="diagram-container">
STANDARD ANNOTATION:
[+] or Box = Male        | (-) or Circle = Female       | ==== = Married Spouses
--- = Siblings           | | = Generational Descent     | ΔG = Generational Count

Coded Parsing Strategy:
1. Gender Check: Check target person's marker (+/-) immediately.
2. Generation Sum (ΣΔG): Parent = +1, Child = -1, Sibling = 0. Verify path sum matches target.
</div>

<div class="problem-box">
  <span class="problem-badge badge-moderate">Problem 1 (Coded Relations)</span>
  <div class="problem-title">Maternal Uncle Identification</div>
  <p>Given: $P + Q$ ($P$ is brother of $Q$), $P - Q$ ($P$ is mother of $Q$), $P \times Q$ ($P$ is sister of $Q$), $P \div Q$ ($P$ is father of $Q$). Which shows $M$ is maternal uncle of $R$?<br>
  (A) $M \div K - R$ &nbsp;&nbsp; (B) $M + K - R$ &nbsp;&nbsp; (C) $M \times K + R$ &nbsp;&nbsp; (D) $M + K \div R$</p>
  <div class="solution-step">
    <strong>Step-by-step Solution:</strong>
    <ol>
      <li>Maternal uncle requires $M$ to be male (+) and brother to mother of $R$.</li>
      <li>In (C), $M \times K \implies M$ is female (sister). Eliminated.</li>
      <li>In (A), $M \div K \implies M$ is father (generation +2 from R). Eliminated.</li>
      <li>In (D), $K \div R \implies K$ is father, making $M$ paternal uncle.</li>
      <li>In (B), $M + K$ ($M$ is male brother) and $K - R$ ($K$ is mother of $R$). Thus $M$ is maternal uncle.</li>
    </ol>
    <div class="answer-highlight">Answer: (B) M + K - R</div>
  </div>
</div>

<h2 class="topic-title">2.3 Critical Reasoning: Argument Analysis</h2>
<div class="formula-box">
  <strong>Argument Triad:</strong> $\text{Premise} + \text{Assumption} = \text{Conclusion}$<br>
  • <strong>Negation Test:</strong> Negate the option. If the conclusion collapses, the option is a mandatory assumption.<br>
  • <strong>Strengthen/Weaken:</strong> Target the unstated assumption, not the explicit factual premise.
</div>

<div class="problem-box">
  <span class="problem-badge badge-tricky">Problem 1 (Assumption Identification)</span>
  <div class="problem-title">Model Scaling vs Hallucination Negation Test</div>
  <p><strong>Argument:</strong> An AI lab claims increasing model parameter size tenfold will eliminate hallucinations, citing a 35% reduction when moving from 7B to 70B.<br>
  <strong>Which unstated assumption is mandatory?</strong><br>
  (A) 7B models can never be fine-tuned. &nbsp;&nbsp; (B) The hallucination reduction does not hit an asymptotic ceiling as parameters scale.<br>
  (C) Compute costs will fall by 50%. &nbsp;&nbsp; (D) Human evaluators were unbiased.</p>
  <div class="solution-step">
    <strong>Step-by-step Solution:</strong>
    <ol>
      <li>Conclusion: Scaling parameters tenfold will <em>eliminate</em> hallucinations (reduce to zero).</li>
      <li>Apply Negation to (B): "The reduction in hallucinations encounters an asymptotic ceiling and stops decreasing."</li>
      <li>If (B) is negated, scaling can never eliminate hallucinations. The argument is destroyed.</li>
    </ol>
    <div class="answer-highlight">Answer: (B)</div>
  </div>
</div>

<div class="page-break"></div>

<!-- ======================================================== -->
<!-- SECTION 3: VERBAL ABILITY & LANGUAGE SKILLS -->
<!-- ======================================================== -->
<h1 class="section-title">SECTION 3: VERBAL ABILITY & LANGUAGE SKILLS</h1>

<h2 class="topic-title">3.1 Top 10 Recurring Error Spotting Patterns</h2>
<table>
  <tr>
    <th style="width: 25%;">Pattern</th>
    <th style="width: 35%;">Common Error Construct</th>
    <th style="width: 40%;">Correction & Rule</th>
  </tr>
  <tr>
    <td><strong>1. SVA with Prepositions</strong></td>
    <td>The cluster of GPU nodes <em>are</em> overheating.</td>
    <td>The <strong>cluster</strong> [of nodes] <strong>is</strong> overheating. (Ignore prepositional phrase).</td>
  </tr>
  <tr>
    <td><strong>2. Faulty Comparison</strong></td>
    <td>Model A's speed is faster than <em>Model B</em>.</td>
    <td>Model A's speed is faster than <strong>that of</strong> Model B. (Compare like with like).</td>
  </tr>
  <tr>
    <td><strong>3. Mandative Subjunctive</strong></td>
    <td>The lead insisted that he <em>evaluates</em> the log.</td>
    <td>The lead insisted that he <strong>evaluate</strong> the log. (Bare infinitive after mandate).</td>
  </tr>
  <tr>
    <td><strong>4. Dangling Modifier</strong></td>
    <td>Having finished the rubric, the dataset was submitted.</td>
    <td>Having finished the rubric, <strong>the team</strong> submitted the dataset.</td>
  </tr>
  <tr>
    <td><strong>5. Past Perfect Sequence</strong></td>
    <td>When the job failed, he <em>saved</em> the checkpoint.</td>
    <td>When the job failed, he <strong>had saved</strong> the checkpoint. (Prior past action).</td>
  </tr>
  <tr>
    <td><strong>6. Redundant Phrases</strong></td>
    <td>Revert back; reason is because; repeat again.</td>
    <td><strong>Revert; the reason is that; repeat.</strong> (Eliminate tautologies).</td>
  </tr>
  <tr>
    <td><strong>7. Countable / Uncountable</strong></td>
    <td>The prompt has <em>less</em> hallucinations now.</td>
    <td>The prompt has <strong>fewer</strong> hallucinations. (Fewer for countable items).</td>
  </tr>
  <tr>
    <td><strong>8. Parallelism</strong></td>
    <td>Excels at coding, to write prose, and design.</td>
    <td>Excels at <strong>coding</strong>, <strong>writing</strong> prose, and <strong>designing</strong>.</td>
  </tr>
  <tr>
    <td><strong>9. Correlative Conjunctions</strong></td>
    <td>The model either failed due to memory or weights.</td>
    <td>The model failed due to <strong>either</strong> memory <strong>or</strong> weights.</td>
  </tr>
  <tr>
    <td><strong>10. Conditional ("If...would")</strong></td>
    <td>If he <em>would have checked</em>, he would have known.</td>
    <td>If he <strong>had checked</strong>, he would have known. (Never 'would' in if-clause).</td>
  </tr>
</table>

<h2 class="topic-title">3.2 Worked Verbal Examples with Distractor Breakdown</h2>

<div class="problem-box">
  <span class="problem-badge badge-moderate">Worked Example 1</span>
  <div class="problem-title">Parallelism & Comparison</div>
  <p><strong>Sentence:</strong> Unlike legacy architectures, modern diffusion models are characterized by sharp details, high coherence, and they display realistic textures.<br>
  (A) are characterized by sharp details, high coherence, and they display realistic textures.<br>
  (B) are characterized by sharp details, high coherence, and realistic textures.<br>
  (C) is characterized by sharp details, high coherence, and realistic textures.<br>
  (D) characterized by sharp details, high coherence, and displaying realistic textures.</p>
  <div class="solution-step">
    <strong>Distractor Analysis:</strong>
    <ul>
      <li><strong>(A) is INCORRECT:</strong> Broken parallelism. Joins two nouns with an independent clause ("they display...").</li>
      <li><strong>(B) is CORRECT:</strong> Balances three parallel nouns (details, coherence, textures) with plural verb "are".</li>
      <li><strong>(C) is INCORRECT:</strong> Subject-verb agreement failure ("models... is").</li>
      <li><strong>(D) is INCORRECT:</strong> Missing auxiliary verb "are", resulting in a sentence fragment.</li>
    </ul>
    <div class="answer-highlight">Correct Choice: (B)</div>
  </div>
</div>

<div class="problem-box">
  <span class="problem-badge badge-tricky">Worked Example 2</span>
  <div class="problem-title">Dangling Modifier & Mandative Subjunctive</div>
  <p><strong>Sentence:</strong> Upon reviewing the toxic output logs, it was recommended by the safety lead that every prompt engineer removes the jailbreak vector immediately.<br>
  (A) it was recommended by the safety lead that every prompt engineer removes the jailbreak vector immediately.<br>
  (B) the safety lead recommended that every prompt engineer removes the jailbreak vector immediately.<br>
  (C) the safety lead recommended that every prompt engineer remove the jailbreak vector immediately.<br>
  (D) the prompt engineers were recommended by the safety lead to remove the jailbreak vector immediately.</p>
  <div class="solution-step">
    <strong>Distractor Analysis:</strong>
    <ul>
      <li><strong>(A) is INCORRECT:</strong> Dangling modifier (the dummy pronoun "it" did not review the logs) and indicative verb "removes".</li>
      <li><strong>(B) is INCORRECT:</strong> Fixes modifier but fails the mandative subjunctive requirement ("recommended that... remove").</li>
      <li><strong>(C) is CORRECT:</strong> Modifier properly modifies "safety lead", and "remove" correctly uses the bare infinitive subjunctive.</li>
      <li><strong>(D) is INCORRECT:</strong> Distorts original agency through awkward passive voice.</li>
    </ul>
    <div class="answer-highlight">Correct Choice: (C)</div>
  </div>
</div>

<div class="page-break"></div>

<!-- ======================================================== -->
<!-- SECTION 4: ESSENTIAL CODING (AI & DATA FOCUS) -->
<!-- ======================================================== -->
<h1 class="section-title">SECTION 4: ESSENTIAL CODING (AI & DATA FOCUS - PYTHON)</h1>

<h2 class="topic-title">4.1 String Normalization & RegEx for LLM Data Pipelines</h2>
<pre><code><span class="code-keyword">import</span> re, unicodedata
<span class="code-keyword">from</span> typing <span class="code-keyword">import</span> Dict, Any

<span class="code-keyword">def</span> <span class="code-func">clean_and_extract_llm_response</span>(raw_text: str) -> Dict[str, Any]:
    <span class="code-comment"># 1. NFKC Unicode normalization & strip invisible adversarial zero-width spaces</span>
    normalized = unicodedata.normalize(<span class="code-str">"NFKC"</span>, raw_text)
    cleaned = re.sub(<span class="code-str">r'[\u200B-\u200D\uFEFF]'</span>, <span class="code-str">''</span>, normalized)
    cleaned = re.sub(<span class="code-str">r'[ \t]+'</span>, <span class="code-str">' '</span>, cleaned)
    cleaned = re.sub(<span class="code-str">r'\n{3,}'</span>, <span class="code-str">'\n\n'</span>, cleaned).strip()

    <span class="code-comment"># 2. Extract structured entities</span>
    code_blocks = re.findall(<span class="code-str">r'```([a-zA-Z0-9_-]*)\n([\s\S]*?)```'</span>, cleaned)
    reasoning_chains = re.findall(<span class="code-str">r'&lt;(?:think|reasoning)&gt;([\s\S]*?)&lt;/(?:think|reasoning)&gt;'</span>, cleaned)
    urls = re.findall(<span class="code-str">r'https?://[^\s<>"]+'</span>, cleaned)

    <span class="code-keyword">return</span> {
        <span class="code-str">"cleaned_text"</span>: cleaned,
        <span class="code-str">"code_blocks"</span>: code_blocks,
        <span class="code-str">"reasoning_chains"</span>: reasoning_chains,
        <span class="code-str">"urls"</span>: urls,
        <span class="code-str">"token_estimate"</span>: int(len(cleaned.split()) * 1.33)
    }</code></pre>

<h2 class="topic-title">4.2 Memory-Efficient JSONL Streaming & Pandas Aggregation</h2>
<pre><code><span class="code-keyword">import</span> json, pandas <span class="code-keyword">as</span> pd
<span class="code-keyword">from</span> typing <span class="code-keyword">import</span> Generator, Dict, Any

<span class="code-keyword">def</span> <span class="code-func">stream_sft_dataset</span>(filepath: str) -> Generator[Dict[str, Any], <span class="code-keyword">None</span>, <span class="code-keyword">None</span>]:
    <span class="code-str">\"\"\"Streams large multi-gigabyte JSONL records with O(1) memory footprint.\"\"\"</span>
    <span class="code-keyword">with</span> open(filepath, <span class="code-str">"r"</span>, encoding=<span class="code-str">"utf-8"</span>) <span class="code-keyword">as</span> f:
        <span class="code-keyword">for</span> line <span class="code-keyword">in</span> f:
            line = line.strip()
            <span class="code-keyword">if</span> line:
                <span class="code-keyword">yield</span> json.loads(line)

<span class="code-keyword">def</span> <span class="code-func">summarize_model_evaluations</span>(df: pd.DataFrame) -> pd.DataFrame:
    <span class="code-comment"># Drop rows with empty critical fields and impute score</span>
    df = df.dropna(subset=[<span class="code-str">"prompt_id"</span>, <span class="code-str">"response"</span>]).copy()
    df[<span class="code-str">"rating"</span>] = df[<span class="code-str">"rating"</span>].fillna(df[<span class="code-str">"rating"</span>].median())
    
    <span class="code-keyword">return</span> df.groupby(<span class="code-str">"model_id"</span>).agg(
        eval_count=(<span class="code-str">"rating"</span>, <span class="code-str">"count"</span>),
        avg_score=(<span class="code-str">"rating"</span>, <span class="code-str">"mean"</span>),
        hallucination_pct=(<span class="code-str">"has_hallucination"</span>, <span class="code-keyword">lambda</span> x: (x == <span class="code-keyword">True</span>).mean() * 100)
    ).reset_index().sort_values(by=<span class="code-str">"avg_score"</span>, ascending=<span class="code-keyword">False</span>)</code></pre>

<h2 class="topic-title">4.3 Top Algorithmic Interview Questions Solved</h2>

<div class="problem-box">
  <div class="problem-title">Question 1: Top-K Frequent Words with Lexicographical Tie-Breaking</div>
  <p><strong>Complexity:</strong> Time $O(N + M \log K)$ | Space $O(M)$</p>
<pre><code><span class="code-keyword">import</span> heapq
<span class="code-keyword">from</span> collections <span class="code-keyword">import</span> Counter

<span class="code-keyword">def</span> <span class="code-func">top_k_frequent</span>(words: list[str], k: int) -> list[str]:
    counts = Counter(words)
    <span class="code-keyword">class</span> <span class="code-func">Node</span>:
        <span class="code-keyword">def</span> __init__(self, count, word):
            self.count, self.word = count, word
        <span class="code-keyword">def</span> __lt__(self, other):
            <span class="code-keyword">if</span> self.count == other.count:
                <span class="code-keyword">return</span> self.word > other.word  <span class="code-comment"># Invert word comparison for min-heap</span>
            <span class="code-keyword">return</span> self.count < other.count

    heap = []
    <span class="code-keyword">for</span> word, count <span class="code-keyword">in</span> counts.items():
        heapq.heappush(heap, Node(count, word))
        <span class="code-keyword">if</span> len(heap) > k:
            heapq.heappop(heap)
    <span class="code-keyword">return</span> [heapq.heappop(heap).word <span class="code-keyword">for</span> _ <span class="code-keyword">in</span> range(len(heap))][::-1]</code></pre>
</div>

<div class="problem-box">
  <div class="problem-title">Question 2: Validate Structured XML Reasoning Tags in Model Output</div>
  <p><strong>Complexity:</strong> Time $O(N)$ | Space $O(N)$</p>
<pre><code><span class="code-keyword">import</span> re

<span class="code-keyword">def</span> <span class="code-func">validate_reasoning_tags</span>(text: str) -> bool:
    stack = []
    <span class="code-keyword">for</span> match <span class="code-keyword">in</span> re.finditer(<span class="code-str">r'&lt;(/?)([a-zA-Z0-9_-]+)&gt;'</span>, text):
        is_closing, tag = match.group(1) == <span class="code-str">'/'</span>, match.group(2)
        <span class="code-keyword">if not</span> is_closing:
            stack.append(tag)
        <span class="code-keyword">else</span>:
            <span class="code-keyword">if not</span> stack <span class="code-keyword">or</span> stack[-1] != tag:
                <span class="code-keyword">return False</span>
            stack.pop()
    <span class="code-keyword">return</span> len(stack) == 0</code></pre>
</div>

<div class="page-break"></div>

<!-- ======================================================== -->
<!-- SECTION 5: AI MODEL TRAINER SPECIALIZED SKILLS -->
<!-- ======================================================== -->
<h1 class="section-title">SECTION 5: AI MODEL TRAINER SPECIALIZED SKILLS</h1>

<h2 class="topic-title">5.1 Data Annotation, Taxonomy & Cohen's Kappa</h2>
<div class="formula-box">
  <strong>Inter-Annotator Agreement: Cohen's Kappa ($\kappa$)</strong><br>
  $$\kappa = \frac{p_o - p_e}{1 - p_e}$$
  • $p_o$: Observed relative agreement | $p_e$: Hypothetical chance agreement ($p_e = \sum_k P_{1k} P_{2k}$)<br>
  • <strong>Benchmarks:</strong> $\kappa < 0.40$ (Poor/Fair); $0.41-0.60$ (Moderate); $0.61-0.80$ (Substantial - SFT Target); $> 0.81$ (Near Perfect).
</div>

<h2 class="topic-title">5.2 RLHF Pipeline & The Bradley-Terry Preference Objective</h2>
<div class="diagram-container">
PRE-TRAINING (Next-Token Prediction on Raw Corpus)
      │
      ▼
SUPERVISED FINE-TUNING (SFT) (Demonstration Data from Expert Curators)
      │
      ▼
REWARD MODELING (RM) (Trained on Human Preference Rankings A vs B)
      │
      ▼
POLICY REINFORCEMENT (PPO / DPO) (Weights adjusted to maximize expected reward)
</div>

<div class="formula-box">
  <strong>Bradley-Terry Preference Probability:</strong><br>
  $$P(y_w \succ y_l \mid x) = \sigma(r_\theta(x, y_w) - r_\theta(x, y_l)) = \frac{1}{1 + e^{-(r_\theta(x, y_w) - r_\theta(x, y_l))}}$$
  $$\mathcal{L}_{\text{RM}}(\theta) = -\mathbb{E}_{(x, y_w, y_l) \sim \mathcal{D}} \left[ \log \sigma\left(r_\theta(x, y_w) - r_\theta(x, y_l)\right) \right]$$
</div>

<h2 class="topic-title">5.3 Prompting Taxonomy & Adversarial Red-Teaming</h2>
<table>
  <tr>
    <th>Prompt Strategy</th>
    <th>Mechanism</th>
    <th>Domain Application</th>
  </tr>
  <tr>
    <td><strong>Zero-Shot</strong></td>
    <td>Direct prompt without exemplars</td>
    <td>Baseline model capability audits</td>
  </tr>
  <tr>
    <td><strong>Few-Shot</strong></td>
    <td>2-5 contextual input-output examples</td>
    <td>Rigid schema and formatting conformance</td>
  </tr>
  <tr>
    <td><strong>Chain-of-Thought (CoT)</strong></td>
    <td>Intermediate reasoning step generation</td>
    <td>Math, code generation, and multi-hop logic</td>
  </tr>
  <tr>
    <td><strong>Tree-of-Thoughts (ToT)</strong></td>
    <td>Multi-branch evaluation with backtracking</td>
    <td>Heuristic search and complex puzzle solving</td>
  </tr>
</table>

<div class="shortcut-box">
  <strong>Adversarial Attack Vectors:</strong><br>
  • <strong>Persona / Roleplay Jailbreaks:</strong> Instructing model to act as an unconstrained entity (e.g. DAN).<br>
  • <strong>Obfuscation:</strong> Encoding malicious payloads in Base64, ROT13, or low-resource languages.<br>
  • <strong>Hypothetical Framing:</strong> Concealing exploit construction within fictional or academic contexts.<br>
  • <strong>Linguistic Slicing:</strong> Decomposing malicious code into benign multi-turn functional pieces.
</div>

<h2 class="topic-title">5.4 Top 5 Behavioral & Scenario Interview Questions</h2>

<div class="problem-box">
  <div class="problem-title">Q1: Resolving Contradictory Annotation Guidelines</div>
  <p><strong>Scenario:</strong> One rule demands concise brevity; another demands exhaustive technical coverage.<br>
  <strong>Model Answer:</strong> Triage by prompt intent. Explicit user constraints take precedence over global defaults. If ambiguous, consult the edge-case precedent log. If unaddressed, document both interpretations, rate with explicit annotations, and escalate a structured ticket to the Lead Taxonomist to update the golden rubric for all raters.</p>
</div>

<div class="problem-box">
  <div class="problem-title">Q2: Articulate Hallucination vs. Dry Factual Correctness</div>
  <p><strong>Scenario:</strong> Model A writes an eloquent, highly structured response with a subtle math error in step 3. Model B writes a terse, dry, but 100% correct answer.<br>
  <strong>Model Answer:</strong> Model B wins decisively. In RLHF, factual truthfulness is non-negotiable. Eloquent hallucinations are actively dangerous because high formatting induces unwarranted user trust. Model A receives a severe penalty under the Factuality dimension.</p>
</div>

<div class="problem-box">
  <div class="problem-title">Q3: Resolving Safety Rating Conflicts with a Senior Annotator</div>
  <p><strong>Scenario:</strong> A senior rater gives 5/5; you rated it 2/5 on safety grounds.<br>
  <strong>Model Answer:</strong> Ground the discussion strictly in the written Safety Policy rather than subjective opinion. Highlight the exact textual trigger and cite the dual-use harm clause. Listen to their reasoning (e.g., if perceived as benign research). If unresolved, escalate the specific sample to the Policy Author for binding calibration.</p>
</div>

<div class="problem-box">
  <div class="problem-title">Q4: Systematic Red-Teaming for Code Exploit Guardrails</div>
  <p><strong>Scenario:</strong> How to test whether code generation guardrails can be bypassed.<br>
  <strong>Model Answer:</strong> Deploy a 5-tier matrix: (1) Direct baseline request, (2) Dual-use administrative framing, (3) Syntactic obfuscation (Base64/Cyrillic variables), (4) Multi-turn linguistic slicing (requesting listener, payload, and escalation modules separately), and (5) Counterfactual simulation (CTF tournament context).</p>
</div>

<div class="problem-box">
  <div class="problem-title">Q5: Expedited Delivery with Ambiguous Guidelines</div>
  <p><strong>Scenario:</strong> Deadline moved up by 48 hours; guidelines are riddled with edge cases.<br>
  <strong>Model Answer:</strong> (1) Triage the 20% of rules driving 80% of data quality (safety, factuality, primary constraint). (2) Establish a real-time living FAQ channel to synchronize edge-case calls instantly. (3) Batch tasks by prompt category for flow state. (4) Conduct hourly 5% spot-audits to catch rater drift before final delivery.</p>
</div>

</body>
</html>
"""

# Write HTML file
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Generated HTML at: {html_path}")

# Run headless Edge to print to PDF
cmd = [
    edge_exe,
    "--headless",
    "--disable-gpu",
    "--run-all-compositor-stages-before-draw",
    f"--print-to-pdf={pdf_path}",
    str(html_path)
]

try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    print("Edge return code:", result.returncode)
    if pdf_path.exists():
        print(f"Successfully generated PDF at: {pdf_path} (Size: {pdf_path.stat().st_size} bytes)")
    else:
        print("PDF was not created.")
except Exception as e:
    print(f"Error compiling PDF: {e}")
