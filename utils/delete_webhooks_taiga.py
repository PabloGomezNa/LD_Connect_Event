import pymongo
import os
import requests


mongo_client = pymongo.MongoClient("mongodb://localhost:27017") # URI to connect to the database
db = mongo_client["event_dashboard"] # Name of the database

#This token should be the token of an administrator of  all the repositories/organizations of all the students
TAIGA_TOKEN = os.getenv("eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQyOTQxMDg1LCJqdGkiOiJiMzJhZjE1NDU4NzI0OThhOTY2NWJhMWVkOTIxZjMzYSIsInVzZXJfaWQiOjc1OTg5Nn0.H8ug241uZP6q2AbSKSZZbcxRSlRE52wGwok8FfZGhVjnshGqGkbEJnhodESqI94bT6bPCToXxDeLqLEdwQDMz7t5j7vDioxyG8cxF2E2bjLVLt6-wkT6U1mdomyyYvpP78gkmlNPr0a3Jv60MplTgcSnfrQ11N2xYDzf1yNtTJsYCjZKzy5d9zqsOkILBKpqnpVu5FcJlXdYyc-K0TMNsWbi0zsA3F7OBchEfOREZcdwZNfN7Qv4s5pb38ZdPQsfD_wGrvjzgE5FdOOvV7-9gEREI7ruytTawsoHSLMd_lwxIfXBUUJxJSAb13oDKEGWY5N9fVN0B3ayuRtwjZF-nw", "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQyOTQxMDg1LCJqdGkiOiJiMzJhZjE1NDU4NzI0OThhOTY2NWJhMWVkOTIxZjMzYSIsInVzZXJfaWQiOjc1OTg5Nn0.H8ug241uZP6q2AbSKSZZbcxRSlRE52wGwok8FfZGhVjnshGqGkbEJnhodESqI94bT6bPCToXxDeLqLEdwQDMz7t5j7vDioxyG8cxF2E2bjLVLt6-wkT6U1mdomyyYvpP78gkmlNPr0a3Jv60MplTgcSnfrQ11N2xYDzf1yNtTJsYCjZKzy5d9zqsOkILBKpqnpVu5FcJlXdYyc-K0TMNsWbi0zsA3F7OBchEfOREZcdwZNfN7Qv4s5pb38ZdPQsfD_wGrvjzgE5FdOOvV7-9gEREI7ruytTawsoHSLMd_lwxIfXBUUJxJSAb13oDKEGWY5N9fVN0B3ayuRtwjZF-nw")
WEBHOOK_URL= "https://f2ab-83-40-78-160.ngrok-free.app/webhook/taiga"  # This should be the endpoint of the TAIGA webhook
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
            if hook["url"] == WEBHOOK_URL:
                try:
                    delete_taiga_hook(hook["id"])
                    print(f"Deleted taiga hook {hook['id']} from project {project_id}")
                except requests.HTTPError as e:
                    print(f"Error deleting taiga hook {hook['id']}: {e}")