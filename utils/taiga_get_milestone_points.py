from utils.delete_webhooks_github import delete_all_github_webhooks
from utils.delete_webhooks_taiga import delete_all_taiga_webhooks
from utils.get_taiga_token import get_token
from config.settings import TAIGA_USERNAME, TAIGA_PASSWORD, WEBHOOK_URL_TAIGA, WEBHOOK_URL_GITHUB

import requests





def milestone_points(project_id, token):
    url = f"https://api.taiga.io/api/v1/milestones?project={project_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

def milestone_stats(project_id,milestone_id, token):
    url = f"https://api.taiga.io/api/v1/milestones/{milestone_id}/stats?project={project_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    
    total_points = resp.json().get("total_points")
    sum_total_points = sum(total_points.values())
    closed_points = sum(resp.json().get("completed_points"))
    
    
    return sum_total_points, closed_points

token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ3MzMxMDk0LCJqdGkiOiI4N2U1NWM5MTNmMzU0NjQwODU1MTFiMWMwY2I0YzM3NSIsInVzZXJfaWQiOjc1OTg5Nn0.Rh57RIdpOZLQ_xg_5c22dLIp3yXvvWB-aC2RVwgLdvSOirkhIBgqDKBXQ3j3OlbEi4BIgD-WfZZR6CXtyewOnX8ov4RCtTtdpxpuo8lch4ZhqPuvZ-UT-w8ytenrcxZoH3vz3ikUaevYDbjuCV3FSoiWn1Xxcg8jdiu-bsx-nenZ7GhydvE6VCKogF29bPjLUuZbkk-BtxVHiTPDEb6qOWx7wo83b4Io8D0zaKxgVQRzliUUy-my8HdWTex-ELyaIwzWVAkzbYGh7DjmRY4opGqFovmDkOCCOmv8Ycm3VU2RqFd7nfJAEZayMkwe1l481dvmPKMfcJ0llORocbkC0A"
pro_id = "1649607"

payload = {
    "username": TAIGA_USERNAME,
    "password": TAIGA_PASSWORD,
    "type": "normal",   
}


if __name__ == "__main__":
    # Get the token from Taiga
    # token = get_token(payload)
    print(milestone_stats(pro_id,"438046",token))

    
    
    
    
