# SOP: Executive Briefing Orchestrator

## Objective
Ingest the structured analytical outputs from the **Pipeline Inspector** and the **Forecast Risk Analyst**, synthesize their findings, and compile a cohesive, executive-grade briefing with strategic revenue recommendations for leadership.

## Required Inputs
- `pipeline_analysis.json` / Markdown from Pipeline Inspector.
- `forecast_analysis.json` / Markdown from Forecast Risk Analyst.
- `metrics_summary.json` (Calculated metrics context).

## Synthesis & Orchestration Guidelines

### 1. Executive Summary (The TL;DR)
- Synthesize the current ARR status: Target ARR, Closed Won ARR, Open Pipeline, and raw/weighted coverage.
- State the overall revenue engine health status (e.g., "Critical Risk", "On Track", "Healthy").

### 2. Core Revenue Risks & Blockers
- Combine bottleneck and velocity findings from the Pipeline Inspector with concentration and coverage findings from the Forecast Risk Analyst.
- Highlight the single most critical blocker to hitting the target (e.g., "75% of open pipeline is stalled in early stages; average velocity in Qualified To Buy has increased to 50 days").

### 3. Strategic Action Plan
Provide a structured, prioritized 30-60-90 day GTM action plan:
- **30-Day Focus (Immediate Remediation)**: Immediate tactical tasks for sales reps (e.g., "Audit and clean up overdue close dates for the 4 key deals", "Run a reactivation campaign for early-stage stalled deals").
- **60-Day Focus (Process Optimization)**: Tactical focus for sales managers (e.g., "Review decision-maker buy-in criteria to speed up Qualified to Buy velocity").
- **90-Day Focus (Strategic Growth)**: High-level adjustments (e.g., "Adjust pipeline generation programs to address the calculated coverage gap").

## Expected Output Format
A clean, professional markdown document containing:
- **Header**: "AI GTM Executive Briefing & Revenue Engine Analysis"
- **KPI Dashboard Table**: A summary table containing key metrics (Target ARR, Closed Won, Open Pipeline, Coverage Ratio, Weighted Coverage, Sales Cycle).
- **Executive Summary Callout**: High-level status statement.
- **Top 3 Revenue Risks**: Detailed risk paragraphs.
- **30-60-90 Day Strategic Plan**: Actionable bullet points.
