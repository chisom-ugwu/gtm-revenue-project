# SOP: Forecast Risk Analyst (Revenue Target & Coverage Analysis)

## Objective
Evaluate open pipeline health, coverage ratios, and historical win probabilities against the target ARR quota to identify risks to hitting the revenue target.

## Required Inputs
- `metrics_summary.json` (Core summary containing target ARR, closed won, open pipeline, and pipeline coverage ratios).
- `crm_snapshot.json` (Raw deal data for risk classification).

## Analysis Guidelines

### 1. Quota Attainment & Target Tracking
- Assess the gap between **Closed Won ARR** and the **Target ARR** (Remaining Target).
- Determine whether target achievement is mathematically viable based on the open pipeline.

### 2. Pipeline Coverage Analysis
Evaluate the **Pipeline Coverage Ratio** (Open Pipeline / Remaining Target):
- **High Risk**: Coverage Ratio < 3.0. There is insufficient pipeline to cover the target (standard sales cycles assume a 33% or lower average close rate, meaning 3x coverage is the baseline healthy ratio).
- **Moderate Risk**: Coverage Ratio between 3.0 and 4.0.
- **Low Risk**: Coverage Ratio > 4.0.
- Assess **Weighted Coverage Ratio** (Weighted Pipeline / Remaining Target). If Weighted Coverage is < 1.0, the target is at high risk even if raw coverage looks sufficient.

### 3. Concentration & Risk Profile
- **Deal Concentration Risk**: Analyze if a single large deal represents > 30% of the total open pipeline or > 50% of the remaining target.
- **Stage Concentration**: Identify if pipeline is heavily backweighted (majority of open value sitting in early stages like "Appointment Scheduled" or "Qualified to Buy" vs. late stages like "Contract Sent").

## Expected Output Format
The agent must generate a structured risk assessment containing:
1. **Target Status**: Quota Progress, Remaining Target, Target Attainment %.
2. **Coverage Assessment**: Raw coverage ratio, weighted coverage ratio, and coverage risk level (High, Medium, Low).
3. **ARR at Risk**: Value and count of high-risk deals (stalled, high concentration, overdue).
4. **Key Risk Vectors**: Top 3 specific threats to achieving the target (e.g., "Single deal dependency", "Lack of late-stage coverage", "Stagnant early-stage deals").
