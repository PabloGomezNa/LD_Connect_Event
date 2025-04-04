import requests
import json

def notify_eval_push(event_type,team_name):
    event_data = {
        "event_type": event_type,
        "team_name": team_name,
    }
    resp = requests.post("http://localhost:5001/api/event", json=event_data)
    print("LD_Eval responded with", resp.status_code, resp.json())

# Then call notify_eval_push("LDTestOrganization") etc.
