import os
import json
import sys
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

HUBSPOT_ACCESS_TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN")
BASE_URL = "https://api.hubapi.com"


def get_headers():
    if not HUBSPOT_ACCESS_TOKEN or HUBSPOT_ACCESS_TOKEN == "your_token_here":
        return None
    return {
        "Authorization": f"Bearer {HUBSPOT_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

def get_default_stages():
    return {
        "appointmentscheduled": {"label": "Appointment Scheduled", "win_probability": 0.20},
        "qualifiedtobuy": {"label": "Qualified To Buy", "win_probability": 0.40},
        "presentationscheduled": {"label": "Presentation Scheduled", "win_probability": 0.60},
        "decisionmakerboughtin": {"label": "Decision Maker Bought-In", "win_probability": 0.80},
        "contractsent": {"label": "Contract Sent", "win_probability": 0.90},
        "closedwon": {"label": "Closed Won", "win_probability": 1.00},
        "closedlost": {"label": "Closed Lost", "win_probability": 0.00}
    }

def get_default_deals():
    # Simulate fallback deal records for local evaluation and offline validation
    return [
        {
            "id": "sim_deal_1",
            "name": "Acme Corp Enterprise Expansion",
            "amount": 120000.0,
            "stage": "closedwon",
            "pipeline": "default",
            "created_date": "2026-01-15T09:00:00Z",
            "close_date": "2024-03-20T17:00:00Z", # Chronological metadata variance (needs cleaning)
            "last_modified": "2026-03-20T17:00:00Z"
        },
        {
            "id": "sim_deal_2",
            "name": "Beta Inc Integration",
            "amount": 30000.0,
            "stage": "closedwon",
            "pipeline": "default",
            "created_date": "2026-03-10T10:00:00Z",
            "close_date": "2024-04-12T18:00:00Z", # Chronological metadata variance (needs cleaning)
            "last_modified": "2026-04-12T18:00:00Z"
        },
        {
            "id": "sim_deal_3",
            "name": "Gamma Corp CRM Modernization",
            "amount": 90000.0,
            "stage": "contractsent",
            "pipeline": "default",
            "created_date": "2026-05-01T11:00:00Z",
            "close_date": "2026-07-15T12:00:00Z",
            "last_modified": "2026-06-20T14:30:00Z"
        },
        {
            "id": "sim_deal_4",
            "name": "Delta Ltd Tier 1 Support Pack",
            "amount": 50000.0,
            "stage": "presentationscheduled",
            "pipeline": "default",
            "created_date": "2026-05-15T08:30:00Z",
            "close_date": "2026-08-01T17:00:00Z",
            "last_modified": "2026-06-25T11:00:00Z"
        },
        {
            "id": "sim_deal_5",
            "name": "Epsilon Group Custom API Portal",
            "amount": 110000.0,
            "stage": "decisionmakerboughtin",
            "pipeline": "default",
            "created_date": "2026-06-02T14:00:00Z",
            "close_date": "2026-09-01T17:00:00Z",
            "last_modified": "2026-06-27T09:15:00Z"
        },
        {
            "id": "sim_deal_6",
            "name": "Zeta Systems Cloud Migration",
            "amount": 60000.0,
            "stage": "closedlost",
            "pipeline": "default",
            "created_date": "2026-02-01T09:00:00Z",
            "close_date": "2026-04-15T17:00:00Z",
            "last_modified": "2026-04-15T17:00:00Z"
        }
    ]

def fetch_pipelines_and_stages():
    """
    Fetches the deal pipelines and stages to get names and win probabilities.
    """
    headers = get_headers()
    if not headers:
        print("Using simulated stage probabilities...")
        return get_default_stages()
        
    url = f"{BASE_URL}/crm/v3/pipelines/deals"
    print("Fetching HubSpot deal pipelines and stage metadata...")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch pipelines: {response.status_code} - {response.text}")
        response.raise_for_status()
        
    data = response.json()
    
    stages_map = {}
    for pipeline in data.get("results", []):
        if pipeline.get("id") == "default" or pipeline.get("label", "").lower() == "default":
            for stage in pipeline.get("stages", []):
                stage_id = stage.get("id")
                label = stage.get("label")
                metadata = stage.get("metadata", {})
                probability_str = metadata.get("probability", "0.0")
                try:
                    probability = float(probability_str)
                except ValueError:
                    probability = 0.0
                
                stages_map[stage_id] = {
                    "label": label,
                    "win_probability": probability
                }
            break
            
    if not stages_map:
        print("Warning: Default pipeline stages not found. Using standard HubSpot stage fallback mapping.")
        stages_map = get_default_stages()
    return stages_map

def fetch_all_deals():
    """
    Fetches all deals in the default pipeline.
    """
    headers = get_headers()
    if not headers:
        print("Using simulated deals snapshot...")
        return get_default_deals()
        
    url = f"{BASE_URL}/crm/v3/objects/deals"
    properties = ["amount", "dealstage", "pipeline", "createdate", "closedate", "hs_lastmodifieddate", "dealname"]
    params = {
        "properties": ",".join(properties),
        "limit": 100
    }
    
    deals = []
    has_more = True
    after = None
    
    print("Fetching all deals from HubSpot...")
    while has_more:
        if after:
            params["after"] = after
            
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Failed to fetch deals: {response.status_code} - {response.text}")
            response.raise_for_status()
            
        data = response.json()
        results = data.get("results", [])
        
        for deal in results:
            properties_data = deal.get("properties", {})
            pipeline_id = properties_data.get("pipeline", "default")
            
            if pipeline_id != "default":
                continue
                
            amount_str = properties_data.get("amount")
            try:
                amount = float(amount_str) if amount_str is not None else 0.0
            except ValueError:
                amount = 0.0
                
            deals.append({
                "id": deal.get("id"),
                "name": properties_data.get("dealname", "Unnamed Deal"),
                "amount": amount,
                "stage": properties_data.get("dealstage"),
                "pipeline": pipeline_id,
                "created_date": properties_data.get("createdate"),
                "close_date": properties_data.get("closedate"),
                "last_modified": properties_data.get("hs_lastmodifieddate")
            })
            
        paging = data.get("paging", {})
        next_page = paging.get("next", {})
        after = next_page.get("after")
        has_more = after is not None
        
    print(f"Successfully fetched {len(deals)} deals in the default pipeline.")
    return deals

def main():
    try:
        stages_map = fetch_pipelines_and_stages()
        deals = fetch_all_deals()
        
        # Structure the snapshot
        snapshot = {
            "extracted_at": datetime.now().isoformat() + "Z",
            "stages": stages_map,
            "deals": deals
        }
        
        # Ensure .tmp directory exists
        os.makedirs(".tmp", exist_ok=True)
        
        snapshot_path = ".tmp/crm_snapshot.json"
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2)
            
        print(f"Saved crm snapshot to {snapshot_path}")
        
    except Exception as e:
        print(f"Error executing extraction: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
