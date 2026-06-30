# SOP: Pipeline Inspector (Pipeline Bottlenecks & Health Analysis)

## Objective
Analyze CRM deal data and GTM stage metrics to identify progression bottlenecks, velocity delays, and pipeline hygiene issues. This analysis enables GTM leadership to optimize sales cycles and improve deal flow efficiency.

## Required Inputs
- `metrics_summary.json` (Calculated metrics including average sales cycle, count of deals, and stage velocities).
- `crm_snapshot.json` (Detailed deal records for pipeline stage inspection).

## Analysis Guidelines

### 1. Velocity and Bottleneck Analysis
- Compare stage velocity (`avg_days` spent in each stage) against historical norms or baseline expectations.
- Identify "bottleneck stages"—stages where deals spend a disproportionate amount of time relative to the total sales cycle.
- Look for stages with high deal volume/accumulation combined with slow movement (e.g., deals stalling at "Qualified To Buy" or "Presentation Scheduled").

### 2. Pipeline Hygiene Assessment
Identify high-risk hygiene flags:
- **Aging/Stalled Deals**: Open deals that have not been modified or updated in a duration longer than `1.5x` the average stage velocity.
- **Missing Data**: Open deals with critical missing fields (e.g., null amounts, missing close dates).
- **Overdue Close Dates**: Open deals with target close dates in the past (using the current system date as reference).

### 3. Stage Conversion & Leakage
- Evaluate the drop-off rate of deals across the stages (from Qualification to Closed).
- Pinpoint if deals are primarily leaking (being lost) in early-stage discovery or late-stage negotiation.

## Expected Output Format
The agent must generate a structured analysis (in JSON or Markdown) containing:
1. **Summary Metrics**: Core pipeline status (total deals analyzed, avg sales cycle).
2. **Top Bottlenecks**: Identified stages causing friction, with average duration and counts.
3. **Hygiene Findings**: Count of overdue close dates, stagnant/stalled opportunities, and missing amounts.
4. **Actionable Recommendations**: Clear, prioritized recommendations for sales managers to unblock stalled pipeline.
