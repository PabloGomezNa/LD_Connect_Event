# import requests



# GITHUB_TOKEN   = "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"

# def gh_paginated(url, headers):
#     """Itera sobre todas las páginas ‘Link: rel="next"’ devolviendo JSON list/dict."""
#     while url:
#         r = requests.get(url, headers=headers)
#         r.raise_for_status()
#         print(r)
#         yield from r.json()
        
        

# def collect_github(org: str, repo: str, prj: str) -> None:
#     """Recorre commits, issues y PRs y los inserta en Mongo."""


#     base = f"https://api.github.com/repos/{org}/{repo}"
#     headers = {
#         "Accept": "application/vnd.github+json",
#         "Authorization": f"Bearer {GITHUB_TOKEN}",
#     }

#     commits_url = f"{base}/commits?per_page=100"
#     print(commits_url)
#     commits_raw = list(gh_paginated(commits_url, headers))
    
    



# if __name__ == "__main__":
#     collect_github("LDTestOrganization", "LD_test", "LDTestProject")
    
import os, requests

token = "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"
if not token:
    raise RuntimeError("Pon tu token en la variable GITHUB_TOKEN")

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json"
}

url = "https://api.github.com/repos/LDTestOrganization/LD_test/issues?state=all&per_page=100&filter=all"
r = requests.get(url, headers=headers)
print(r.json())
