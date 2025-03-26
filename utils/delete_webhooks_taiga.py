import pymongo
import requests
from config.settings import MONGO_URI, DB_NAME, TAIGA_TOKEN, WEBHOOK_URL_TAIGA


mongo_client = pymongo.MongoClient(MONGO_URI) # URI to connect to the database
db = mongo_client[DB_NAME] # Name of the database

TAIGA_API_URL = "https://api.taiga.io"


#We define two functions to list and delete the webhooks using the API of github.
#The first function lists all the webhooks created on a repository, we need the owner and the repository name. Also a owner or admin token is needed to authenticate the request.
def list_taiga_hooks(project_id):
    url = f"{TAIGA_API_URL}/api/v1/webhooks?project={project_id}"
    headers = {
        "Authorization": f"Bearer {TAIGA_TOKEN}"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

#The second function deletes a webhook, we need the owner, the repository name and the id of the webhook to delete. 
# Also a owner or admin token is needed to authenticate the request.
def delete_taiga_hook(hook_id):
    url = f"{TAIGA_API_URL}/api/v1/webhooks/{hook_id}"
    headers = {
        "Authorization": f"Bearer {TAIGA_TOKEN}"
    }
    resp = requests.delete(url, headers=headers)
    resp.raise_for_status()
    return resp


# We get all collections with 'commits' in their name and store them in a list. From them we will extract the repositories names and owners.
all_collections = db.list_collection_names()
taiga_collections = [c for c in all_collections if "epic" in c]



#We iterate over the collections and the repositories to delete the webhooks
#We first get the repositories in the collection and then we get the hooks for each repository
for col_name in taiga_collections:
    distinct_project_ids = db[col_name].distinct("project_id")
    
    for project_id in distinct_project_ids:
        hooks = list_taiga_hooks(project_id)
        print(f"Found {len(hooks)} hooks for project {project_id}")
        for hook in hooks:
            if hook["url"] == WEBHOOK_URL_TAIGA:
                try:
                    delete_taiga_hook(hook["id"])
                    print(f"Deleted taiga hook {hook['id']} from project {project_id}")
                except requests.HTTPError as e:
                    print(f"Error deleting taiga hook {hook['id']}: {e}")