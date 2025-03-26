import pymongo
import requests
from config.settings import MONGO_URI, DB_NAME, GITHUB_TOKEN, WEBHOOK_URL_GITHUB



mongo_client = pymongo.MongoClient(MONGO_URI) # URI to connect to the database
db = mongo_client[DB_NAME] # Name of the database


#We define two functions to list and delete the webhooks using the API of github.
#The first function lists all the webhooks created on a repository, we need the owner and the repository name. Also a owner or admin token is needed to authenticate the request.
def list_github_hooks(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/hooks"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

#The second function deletes a webhook, we need the owner, the repository name and the id of the webhook to delete. 
# Also a owner or admin token is needed to authenticate the request.
def delete_github_hook(owner, repo, hook_id):
    url = f"https://api.github.com/repos/{owner}/{repo}/hooks/{hook_id}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}"
    }
    resp = requests.delete(url, headers=headers)
    resp.raise_for_status()
    return resp


# We get all collections with 'commits' in their name and store them in a list. From them we will extract the repositories names and owners.
all_collections = db.list_collection_names()
github_commit_collections = [c for c in all_collections if "commit" in c]



#We iterate over the collections and the repositories to delete the webhooks
#We first get the repositories in the collection and then we get the hooks for each repository
for col_name in github_commit_collections:
    distinct_repos = db[col_name].distinct("repository")
    for repo_full_name in distinct_repos:
        owner, repo = repo_full_name.split('/')
        try:
            hooks = list_github_hooks(owner, repo)
        except requests.HTTPError as e:
            print(f"Error listing hooks for {owner}/{repo}: {e}")
            continue
        
        for hook in hooks:
            config_url = hook.get("config", {}).get("url", "")
            hook_id = hook.get("id")
            
            if config_url == WEBHOOK_URL_GITHUB:
                # Delete it
                try:
                    delete_github_hook(owner, repo, hook_id)
                    print(f"Deleted hook {hook_id} for {owner}/{repo}")
                except requests.HTTPError as e:
                    print(f"Error deleting hook {hook_id} for {owner}/{repo}: {e}")