import unittest
import json
import os
from datetime import datetime

# Adjust import path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.calculate_gtm_metrics import calculate_metrics

class TestGTMMetrics(unittest.TestCase):
    
    def setUp(self):
        self.config = {
            "target_arr": 300000.0,
            "pipeline_id": "default",
            "data_normalization": {
                "handle_inverted_dates": True,
                "default_sales_cycle_days": 60
            }
        }
        
        self.snapshot = {
            "stages": {
                "appointmentscheduled": {"label": "Appointment Scheduled", "win_probability": 0.20},
                "qualifiedtobuy": {"label": "Qualified To Buy", "win_probability": 0.40},
                "presentationscheduled": {"label": "Presentation Scheduled", "win_probability": 0.60},
                "closedwon": {"label": "Closed Won", "win_probability": 1.00},
                "closedlost": {"label": "Closed Lost", "win_probability": 0.00}
            },
            "deals": [
                {
                    "id": "1",
                    "name": "Deal 1",
                    "amount": 100000.0,
                    "stage": "closedwon",
                    "pipeline": "default",
                    "created_date": "2026-06-01T12:00:00Z",
                    "close_date": "2026-06-11T12:00:00Z", # 10 days sales cycle
                    "last_modified": "2026-06-11T12:00:00Z"
                },
                {
                    "id": "2",
                    "name": "Deal 2",
                    "amount": 150000.0,
                    "stage": "presentationscheduled",
                    "pipeline": "default",
                    "created_date": "2026-06-01T12:00:00Z",
                    "close_date": "2026-08-01T12:00:00Z",
                    "last_modified": "2026-06-15T12:00:00Z"
                },
                {
                    "id": "3",
                    "name": "Anomalous Deal 3",
                    "amount": 50000.0,
                    "stage": "closedwon",
                    "pipeline": "default",
                    "created_date": "2026-06-01T12:00:00Z",
                    "close_date": "2024-06-01T12:00:00Z", # INVERTED (dated 2024)
                    "last_modified": "2026-06-15T12:00:00Z"
                }
            ]
        }
        
    def test_metrics_calculation(self):
        metrics = calculate_metrics(self.snapshot, self.config)
        
        # Target = 300,000.
        # Won deals:
        # - Deal 1 (100k, won)
        # - Deal 3 (50k, won)
        # Total Won = 150,000.
        self.assertEqual(metrics["closed_won"], 150000.0)
        
        # Remaining Target = 300,000 - 150,000 = 150,000.
        self.assertEqual(metrics["remaining_target"], 150000.0)
        
        # Open pipeline = 150,000 (Deal 2)
        # Weighted pipeline = 150,000 * 0.60 = 90,000.
        self.assertEqual(metrics["open_pipeline"], 150000.0)
        self.assertEqual(metrics["weighted_pipeline"], 90000.0)
        
        # Coverage ratio: Open Pipeline / Remaining Target = 150k / 150k = 1.00
        # Weighted Coverage ratio: Weighted Pipeline / Remaining Target = 90k / 150k = 0.60
        self.assertEqual(metrics["pipeline_coverage_ratio"], 1.00)
        self.assertEqual(metrics["weighted_pipeline_coverage_ratio"], 0.60)
        
        # Date normalization check:
        # Deal 3 has inverted dates. Create date 2026-06-01, close date 2024-06-01.
        # With handle_inverted_dates=True, corrected close date should be createdate + 60 days.
        # Deal 1 sales cycle: 10 days.
        # Deal 3 sales cycle: 60 days (corrected).
        # Average: (10 + 60) / 2 = 35 days.
        self.assertEqual(metrics["average_sales_cycle_days"], 35.0)

if __name__ == '__main__':
    unittest.main()
