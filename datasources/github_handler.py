# datasources/github_handler.py

from typing import Dict
import requests

import os #We will use to import global variables
GITHUB_TOKEN = os.getenv("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", "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")  

'''
The webhook has a header "X-GitHub-Event" that tells you the type of event.
For a push event, the payload structure is described here:
X-GitHub-Event: push

For an issue event, the payload structure is described here:
X-GitHub-Event: issues
'''

#Firt we need to know with the header whether the event is a push event or an issue event
#Then we can parse the payload accordingly

def parse_github_event(raw_payload: Dict) -> Dict:
    """
    Parse a GitHub event payload into a more detailed structure,
    similar to what you used to store before.
    """
    event_type = raw_payload.get("X-GitHub-Event")
    if event_type == "push":
        return parse_github_push_event(raw_payload)
    elif event_type == "issues":
        return parse_github_issue_event(raw_payload)
    else:
        return {
            "event": event_type,
            "error": "Unsupported event type"
            }



def parse_github_push_event(raw_payload: Dict) -> Dict:
    event_type = "commit"


    # Top-level stuff
    team_name = raw_payload.get("organization", {}).get("login", "UnknownTeam")
    repo_name = raw_payload["repository"].get("full_name", "unknown-repo")

    # The 'sender' object is at the top level
    sender = raw_payload.get("sender", {})
    
    sender_info = {
        "id": sender.get("id", ""),
        "login": sender.get("login", ""),
        "url": sender.get("url", ""),
        "type": sender.get("type", ""),
        "site_admin": sender.get("site_admin", False)
    }
    
    
    commits_info = []
    # The push event typically has a "commits" array
    for c in raw_payload.get("commits", []):
        # Basic fields from the commit
        commit_sha = c.get("id")
        commit_url = c.get("url", "")
        message = c.get("message", "")
        date = c.get("timestamp")

        # Built author information
        author_login = c.get("author", {}).get("username", "")
        author_name  = c.get("author", {}).get("name", "")
        author_email = c.get("author", {}).get("email", "")

        # Compute message stats
        message_char_count = len(message)
        message_word_count = len(message.split())

        # By default, push event doesn't include stats like additions/deletions unless you do an extra API call. We'll set them to 0 or placeholders
        commit_stats = {
            "total": 0,
            "additions": 0,
            "deletions": 0
        }
        
        # Make an API call to GitHub to retrieve commit stats
        try:
            commit_headers = {
                "Accept": "application/vnd.github.v3+json"
            }
            if GITHUB_TOKEN:
                commit_headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
            
            # The commit_url is the same as the API URL 
            commit_api_response = requests.get(commit_url, headers=commit_headers)
            commit_api_response.raise_for_status()
            commit_api_data = commit_api_response.json()
            stats = commit_api_data.get("stats", {})
            commit_stats = {
                "total": stats.get("total", 0),
                "additions": stats.get("additions", 0),
                "deletions": stats.get("deletions", 0)
            }
        except Exception as e:
            print(f"Error retrieving commit stats for {commit_sha}: {e}")
            # If the API call fails, commit_stats will still be zeros.
        

        verified = "false"
        verified_reason = "unsigned"

        # Build a final doc for this commit.
        commit_doc = {
            "sha": commit_sha,
            "url": commit_url,
            "user": {
                "login": author_login,
                "name": author_name,
                "email": author_email,
            },
            "repository": repo_name,
            "date": date,
            "message": message,
            "message_char_count": message_char_count,
            "message_word_count": message_word_count,
            #"task_is_written":, #ns que es
            #"task_reference", #ns que es
            "verified": verified, #ns que es de momento
            "verified_reason": verified_reason, #nose que es de momento PUEDE QUE SEA LO DE FIRMA DE SEGURIDAD?
            "stats": commit_stats
        }

        commits_info.append(commit_doc)

    # Finally, return a dict containing the full structure
    return {
        "event": event_type,
        "repo_name": repo_name,
        "team_name": team_name,
        "sender_info": sender_info,
        "commits": commits_info
    }



def parse_github_issue_event(raw_payload: Dict) -> Dict:
    """
    Handle an issues event, e.g. "opened", "closed", "edited", etc.
    Return a dict with top-level fields plus an "issue" block.
    """

    # The action is typically raw_payload["action"] = "opened" / "closed" / "edited"
    action = raw_payload.get("action", "unknown-action")
    event_type = f"issue_{action}"   # e.g. "issue_opened"

    team_name = raw_payload.get("organization", {}).get("login", "UnknownTeam")
    repo_name = raw_payload["repository"].get("full_name", "unknown-repo")

    # sender is the user who performed the action (opened, closed, etc.)
    sender = raw_payload.get("sender", {})
    sender_info = {
        "id": sender.get("id", ""),
        "login": sender.get("login", ""),
        "url": sender.get("url", ""),
        "type": sender.get("type", ""),
        "site_admin": sender.get("site_admin", False)
    }

    # The "issue" object is typically raw_payload["issue"]
    issue_data = raw_payload.get("issue", {})
    issue_number = issue_data.get("number", 0)
    issue_title  = issue_data.get("title", "")
    issue_state  = issue_data.get("state", "")
    issue_body   = issue_data.get("body", "")
    issue_user   = issue_data.get("user", {})
    issue_user_login = issue_user.get("login", "")
    issue_user_id = issue_user.get("id", "")

    # We can store relevant info about the issue as a dictionary
    issue_obj = {
        "number": issue_number,
        "title": issue_title,
        "state": issue_state,
        "body": issue_body,
        "user": {
            "login": issue_user_login,
            "id": issue_user_id
        }
    }

    return {
        "event": event_type,          # e.g. "issue_opened"
        "repo_name": repo_name,
        "team_name": team_name,
        "sender_info": sender_info,
        "issue": issue_obj
    }
