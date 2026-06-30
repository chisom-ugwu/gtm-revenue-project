import unittest
import json
import os
from unittest.mock import patch, MagicMock

# Adjust import path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.extract_hubspot_data import fetch_pipelines_and_stages, fetch_all_deals

class TestHubSpotExtraction(unittest.TestCase):
    
    @patch('tools.extract_hubspot_data.requests.get')
    @patch('tools.extract_hubspot_data.HUBSPOT_ACCESS_TOKEN', 'fake-token')
    def test_fetch_pipelines_and_stages(self, mock_get):
        # Mock Response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "id": "default",
                    "label": "default",
                    "stages": [
                        {
                            "id": "appointmentscheduled",
                            "label": "Appointment Scheduled",
                            "metadata": {"probability": "0.20"}
                        },
                        {
                            "id": "closedwon",
                            "label": "Closed Won",
                            "metadata": {"probability": "1.00"}
                        }
                    ]
                }
            ]
        }
        mock_get.return_value = mock_response
        
        stages = fetch_pipelines_and_stages()
        self.assertIn("appointmentscheduled", stages)
        self.assertEqual(stages["appointmentscheduled"]["win_probability"], 0.20)
        self.assertEqual(stages["closedwon"]["win_probability"], 1.00)
        
    @patch('tools.extract_hubspot_data.requests.get')
    @patch('tools.extract_hubspot_data.HUBSPOT_ACCESS_TOKEN', 'fake-token')
    def test_fetch_all_deals_filters_default_pipeline(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "id": "1",
                    "properties": {
                        "dealname": "Deal 1",
                        "amount": "10000",
                        "dealstage": "appointmentscheduled",
                        "pipeline": "default",
                        "createdate": "2026-06-01T12:00:00Z",
                        "closedate": "2024-06-01T12:00:00Z",
                        "hs_lastmodifieddate": "2026-06-15T12:00:00Z"
                    }
                },
                {
                    "id": "2",
                    "properties": {
                        "dealname": "Deal 2",
                        "amount": "5000",
                        "dealstage": "qualifiedtobuy",
                        "pipeline": "custom_pipeline",
                        "createdate": "2026-06-01T12:00:00Z",
                        "closedate": "2026-08-01T12:00:00Z",
                        "hs_lastmodifieddate": "2026-06-15T12:00:00Z"
                    }
                }
            ],
            "paging": {}
        }
        mock_get.return_value = mock_response
        
        deals = fetch_all_deals()
        self.assertEqual(len(deals), 1)
        self.assertEqual(deals[0]["id"], "1")
        self.assertEqual(deals[0]["amount"], 10000.0)

if __name__ == '__main__':
    unittest.main()
