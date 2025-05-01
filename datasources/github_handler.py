from typing import Dict
import requests
import re
from config.settings import GITHUB_TOKEN



def parse_github_event(raw_payload: Dict) -> Dict:
    """
    Parse a GitHub event payload into a more detailed structure.
    The webhook has a header "X-GitHub-Event" that tells you the type of event.
    We can handle "push" and "issues" events.
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
    '''
    Function to parse a GitHub push event payload.
    '''
    event_type = "commit" # The event type is "push" but we will call it "commit" in our system

    # Retrieve the team name and repo name from the payload
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


        # Check if the commit message contains a task reference, it can be in english or catalan, ¿spanish¿ (e.g., "task #123")
        pattern = r'(?i)\b(?:task|tasca)\b(?:\s*#?\s*(\d+))?'
        match = re.search(pattern, message)
        if match:
            task_is_written = True
            task_reference = match.group(1)
            if task_reference is not None:
                task_reference = int(task_reference)
        else:
            task_is_written = False
            task_reference = None

        verified = "false"
        verified_reason = "unsigned"
        
        # By default, push event doesn't include stats like additions/deletions unless you do an extra API call. We'll set them to 0 or placeholders
        commit_stats = {
            "total": 0,
            "additions": 0,
            "deletions": 0
        }
        
        # Make an API call to GitHub to retrieve commit stats
        #To use this API, we need to authenticate with a token. We will use the GITHUB_TOKEN environment variable.
        try:
            commit_headers = {
                "Accept": "application/vnd.github.v3+json"
            }
            if GITHUB_TOKEN:
                commit_headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
            
            #URL to get the commit stats with the API. Repo_name is the owner/repo_name and commit_sha is the sha of the commit
            commit_api_url = f"https://api.github.com/repos/{repo_name}/commits/{commit_sha}"

            #We make the request to the API
            commit_api_response = requests.get(commit_api_url, headers=commit_headers)
            commit_api_response.raise_for_status() #If the status code is not 200, an exception is raised
            commit_api_data = commit_api_response.json()#We get the data in json format
            stats = commit_api_data.get("stats", {})#We get the stats of the commit
            commit_stats = {
                "total": stats.get("total", 0),
                "additions": stats.get("additions", 0),
                "deletions": stats.get("deletions", 0)
            }
        except Exception as e:            
            # If the API call fails, commit_stats will still be zeros.
            print(f"Error retrieving commit stats for {commit_sha}: {e}")
        

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
            "task_is_written": task_is_written, 
            "task_reference": task_reference, 
            "verified": verified,
            "verified_reason": verified_reason,
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
    '''
    Function to parse a GitHub issue event payload.
    '''
    # Retrieve the event information from the payload
    action = raw_payload.get("action", "unknown-action")# e.g. "issue_opened"
    event_type = "issue"   
    
    # Retrieve the team name and repo name from the payload
    team_name = raw_payload.get("organization", {}).get("login", "UnknownTeam")
    repo_name = raw_payload["repository"].get("full_name", "unknown-repo")

    # sender is the user who performed the action, retrieve their info
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

    # Finally, return a dict containing the full structure
    return {
        "event": event_type,         
        "action": action,          
        "repo_name": repo_name,
        "team_name": team_name,
        "sender_info": sender_info,
        "issue": issue_obj
    }
