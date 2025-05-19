from utils.delete_webhooks_github import delete_all_github_webhooks
from utils.delete_webhooks_taiga import delete_all_taiga_webhooks
from utils.get_taiga_token import get_token
from config.settings import TAIGA_USERNAME, TAIGA_PASSWORD, WEBHOOK_URL_TAIGA, WEBHOOK_URL_GITHUB

import requests


def list_points(project_id, token):
    url = f"https://api.taiga.io/api/v1/search?project={project_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()


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
    return resp.json()

token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ3MzA3MDI1LCJqdGkiOiIwMzA5NDcyNzZlMjc0YzQxYWM0N2NiYTllNzE2NGYyMyIsInVzZXJfaWQiOjc1OTg5Nn0.bYh7cfGv6WzhpdQB1nXu75oEI3uklWvEQAkoItY5R9j0WPutzVcXbAbeXkBH-sfJa6k-QjVCKfFYruqGSH4819q7tCYzc67sqgiA0MTsJkKuzUa_2aa1owyHMtiDYGMK3ZhN8W7KQxarMEvHXEtyrUKBI5gU_ewUoqtLBcplCBSFfrIvC9UqjA7OzS3YlBaS9YCYP3vt0ndg_qGRq1hqb64sByx7eld_6z-1Rm2KmfqHztqj6miR4K3KhNlO45lyNti_WE4nZJxfku4yXo8G91MSVFQSCZgLXUvRL-DO0b28Fu6LQX5T9or3cDNvuaGuT0SP3A1Jf-KIYU21sWYnrA"

pro_id = "1649607"

if __name__ == "__main__":
    # Get the token from Taiga
    
    print(milestone_stats(pro_id,"438046",token))
    
    
