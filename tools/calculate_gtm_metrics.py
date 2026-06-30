import os
import json
import sys
from datetime import datetime, timedelta

def parse_date(date_str):
    if not date_str:
        return None
    # HubSpot date format could be: 2026-06-01T12:00:00Z or similar formats.
    # We will parse it and return a naive UTC datetime to prevent timezone conflicts.
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.astimezone(datetime.now().astimezone().tzinfo).replace(tzinfo=None)
    except ValueError:
        try:
            return datetime.strptime(date_str[:19], "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            return None

def normalize_dates(deal, default_sales_cycle_days, index):
    """
    Cleans and standardizes chronologically inconsistent deal timestamps.
    Auto-corrects records where Close Date precedes Create Date due to system/sync sync logging skew.
    """
    create_date = parse_date(deal.get("created_date"))
    close_date = parse_date(deal.get("close_date"))
    
    if not create_date:
        return create_date, close_date
        
    if close_date and close_date < create_date:
        # Correct it by adding default sales cycle duration
        corrected_close_date = create_date + timedelta(days=default_sales_cycle_days)
        deal["close_date_original"] = deal.get("close_date")
        deal["close_date"] = corrected_close_date.isoformat() + "Z"
        return create_date, corrected_close_date
        
    return create_date, close_date

def calculate_metrics(snapshot, config):
    target_arr = config.get("target_arr", 300000.0)
    pipeline_id = config.get("pipeline_id", "default")
    data_norm_config = config.get("data_normalization", {})
    default_sales_cycle_days = data_norm_config.get("default_sales_cycle_days", 60)
    handle_inverted = data_norm_config.get("handle_inverted_dates", True)
    
    deals = snapshot.get("deals", [])
    stages_metadata = snapshot.get("stages", {})
    
    open_pipeline = 0.0
    weighted_pipeline = 0.0
    closed_won = 0.0
    closed_lost = 0.0
    
    sales_cycles = []
    stage_durations = {} # To compute stage velocity for open and closed deals
    
    # Track stage transition counts and totals
    for idx, deal in enumerate(deals):
        # Filter by pipeline if not done already
        if deal.get("pipeline") != pipeline_id:
            continue
            
        stage_id = deal.get("stage")
        stage_meta = stages_metadata.get(stage_id, {})
        win_probability = stage_meta.get("win_probability", 0.0)
        
        # Normalize dates
        create_date, close_date = parse_date(deal.get("created_date")), parse_date(deal.get("close_date"))
        if handle_inverted:
            create_date, close_date = normalize_dates(deal, default_sales_cycle_days, idx)
            
        amount = deal.get("amount", 0.0)
        
        # Determine status from win probability and stage names
        if stage_id == "closedwon" or win_probability >= 1.0:
            closed_won += amount
            if create_date and close_date:
                sales_cycles.append((close_date - create_date).days)
        elif stage_id == "closedlost" or (stage_id is not None and win_probability <= 0.0 and stage_id in ["closedlost"]):
            closed_lost += amount
        else:
            open_pipeline += amount
            weighted_pipeline += (amount * win_probability)
            
        # For stage velocity estimation:
        # Approximate time spent in stage:
        # If it is an open deal, time spent is (now - created_date) or (last_modified - created_date)
        # If it is a closed deal, it represents a historical progression.
        if stage_id and create_date:
            last_modified = parse_date(deal.get("last_modified")) or datetime.utcnow()
            # If closed, duration is close_date - create_date
            is_closed = stage_id in ["closedwon", "closedlost"]
            end_date = close_date if (is_closed and close_date) else last_modified
            duration_days = max(0, (end_date - create_date).days)
            
            if stage_id not in stage_durations:
                stage_durations[stage_id] = []
            stage_durations[stage_id].append(duration_days)
            
    # Calculate averages
    avg_sales_cycle = sum(sales_cycles) / len(sales_cycles) if sales_cycles else 0.0
    
    stage_velocity = {}
    for stage_id, durations in stage_durations.items():
        stage_label = stages_metadata.get(stage_id, {}).get("label", stage_id)
        stage_velocity[stage_id] = {
            "label": stage_label,
            "avg_days": sum(durations) / len(durations) if durations else 0.0,
            "deal_count": len(durations)
        }
        
    # Coverage Ratios
    remaining_target = max(0.0, target_arr - closed_won)
    if remaining_target > 0:
        pipeline_coverage = open_pipeline / remaining_target
        weighted_coverage = weighted_pipeline / remaining_target
    else:
        pipeline_coverage = 999.0 # Effectively met target
        weighted_coverage = 999.0
        
    return {
        "target_arr": target_arr,
        "closed_won": closed_won,
        "closed_lost": closed_lost,
        "remaining_target": remaining_target,
        "open_pipeline": open_pipeline,
        "weighted_pipeline": weighted_pipeline,
        "pipeline_coverage_ratio": round(pipeline_coverage, 2),
        "weighted_pipeline_coverage_ratio": round(weighted_coverage, 2),
        "average_sales_cycle_days": round(avg_sales_cycle, 1),
        "stage_velocity": stage_velocity,
        "total_deals_analyzed": len(deals)
    }

def main():
    try:
        config_path = "config/pipeline_config.json"
        snapshot_path = ".tmp/crm_snapshot.json"
        metrics_output_path = ".tmp/metrics_summary.json"
        
        if not os.path.exists(config_path):
            print(f"Error: Config file not found at {config_path}")
            sys.exit(1)
            
        if not os.path.exists(snapshot_path):
            print(f"Error: CRM snapshot file not found at {snapshot_path}")
            sys.exit(1)
            
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            
        with open(snapshot_path, "r", encoding="utf-8") as f:
            snapshot = json.load(f)
            
        metrics = calculate_metrics(snapshot, config)
        
        with open(metrics_output_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
            
        print(f"Saved metrics summary to {metrics_output_path}")
        
    except Exception as e:
        print(f"Error executing metrics calculation: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
