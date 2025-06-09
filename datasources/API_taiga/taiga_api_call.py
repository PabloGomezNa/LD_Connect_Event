import requests
from datetime import datetime, timedelta
from utils.taiga_token.taiga_auth import get_taiga_token

_CACHE = {}                 # key = (project_id, milestone_id) -> (timestamp, stats)
TTL    = timedelta(seconds=5) # Cache time-to-live, set to 5 minutes. Means that if the same request is made within 5 minutes, it will return the cached result instead of making a new API call.

def milestone_stats(project_id,milestone_id):
    '''
    Fetches the statistics of a milestone in a Taiga project. 
    Uses caching to avoid frequent API calls to get the taiga token.
    It refreshes the cache every 5 minutes.
    '''
    if not project_id or not milestone_id:
        return {}

    key = (project_id, milestone_id)
    now = datetime.utcnow()
    if key in _CACHE and now - _CACHE[key][0]< TTL:
        return _CACHE[key][1]

    headers = {"Authorization": f"Bearer {get_taiga_token()}"}
    url = f"https://api.taiga.io/api/v1/milestones/{milestone_id}/stats"
    r   = requests.get(url, params={"project": project_id}, headers=headers, timeout=(1, 5))
    r.raise_for_status()
    js  = r.json()
    stats = {
        "milestone_total_points"         : sum(js.get("total_points", {}).values()),
        "milestone_closed_points"        : sum(js.get("completed_points", 0)),
        "milestone_total_userstories"    : js.get("total_userstories", 0),
        "milestone_completed_userstories": js.get("completed_userstories", 0),
        "milestone_total_tasks"          : js.get("total_tasks", 0),
        "milestone_completed_tasks"      : js.get("completed_tasks", 0),
    }
    _CACHE[key] = (now, stats)
    return stats