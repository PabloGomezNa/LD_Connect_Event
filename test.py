import argparse, requests
from typing import Dict, Iterable, Optional
from datetime import datetime, timezone
from pymongo import UpdateOne
from dateutil import parser as dtp, tz
from tqdm import tqdm

from database.mongo_client import get_collection
from datasources.github_handler import parse_github_event

from config.settings import GITHUB_TOKEN


def parse_dt(s: str | None) -> Optional[datetime]:
    '''
    Accepts ‘2025-05-01’, ‘2025-05-01T14:30’, etc. And returns the datetime tz-aware (Madrid).
    '''
    if not s:
        return None
    d = dtp.isoparse(s)
    if d.tzinfo is None:
        d = d.replace(tzinfo=tz.gettz("Europe/Madrid"))
    return d




def gh_paginated(url: str, headers: Dict[str, str]) -> Iterable[Dict]:
    while url:
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        yield from r.json()
        url = r.links.get("next", {}).get("url")


def upsert(coll, docs: list[dict], key: str) -> int:
    '''
    Upserts a list of documents into a MongoDB collection.	
    '''
    if not docs:
        return 0
    operations = [UpdateOne({key: d[key]}, {"$set": d}, upsert=True) for d in docs] #Create a list of UpdateOne operations for each document in the list, using the key to identify the document
    res = coll.bulk_write(operations, ordered=False)
    return res.matched_count + len(res.upserted_ids)




def collect_github(org: str,  repo: str, prj: str, events: list[str], since: Optional[str], until: Optional[str]):

    repo_full = f"{org}/{repo}"          

    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    sender_stub = {"login": "backfill", "organization": org}

    counters = {"commits": 0, "issues": 0, "pull_requests": 0}
    
    total = 0
    for ev in events:
        if ev == "commits":
            log_url = f"https://api.github.com/repos/{repo_full}/commits?per_page=100"
            if since: log_url += f"&since={since}"
            if until: log_url += f"&until={until}"

            payloads = []
            for c in gh_paginated(log_url, headers):
                payloads.append({
                    "X-GitHub-Event": "push",
                    "repository": {"full_name": repo_full},
                    "organization": {"login": org},
                    "sender": c["author"] or {},
                    "commits": [{
                        "id": c["sha"],
                        "url": c["url"],
                        "message": c["commit"]["message"],
                        "timestamp": c["commit"]["author"]["date"],
                        "author": {
                            "username": (c["author"] or {}).get("login", ""),
                            "name":     c["commit"]["author"]["name"],
                            "email":    c["commit"]["author"]["email"],
                        },
                    }],
                })

            coll = get_collection(f"github_{prj}.commits")
            for raw in payloads:
                doc = parse_github_event(raw)
                for c in doc["commits"]:
                    c.update({"team_name": doc["team_name"],
                              "repo_name": doc["repo_name"],
                              "sender_info": doc["sender_info"],
                              "prj": prj})
                    counters["commits"] += upsert(coll, [c], "sha")

        elif ev == "issues":
            url = f"https://api.github.com/repos/{repo_full}/issues?state=all&per_page=100"
            if since: url += f"&since={since}"
            raw_issues = list(gh_paginated(url, headers))

            coll = get_collection(f"{prj}_issues")
            for i in raw_issues:
                payload = {
                    "X-GitHub-Event": "issues",
                    "action": i["state"],
                    "repository": {"full_name": repo_full},
                    "organization": {"login": org},
                    "sender": i["user"],
                    "issue": i,
                }
                doc = parse_github_event(payload)
                doc["prj"] = prj
                doc["issue_id"] = doc["issue"]["number"]
                counters["issues"] += upsert(coll, [doc], "issue_id")

        elif ev == "pull_requests":
            url = f"https://api.github.com/repos/{repo_full}/pulls?state=closed&per_page=100"
            raw_prs = list(gh_paginated(url, headers))
            coll = get_collection(f"github_{prj}.pull_requests")
            for p in raw_prs:
                payload = {
                    "X-GitHub-Event": "pull_request",
                    "action": "closed",
                    "repository": {"full_name": repo_full},
                    "organization": {"login": org},
                    "sender": p["user"],
                    "pull_request": p,
                }
                doc = parse_github_event(payload)
                doc["prj"] = prj
                counters["pull_requests"] += upsert(coll, [doc], "pr_number")

        else:
            print(f"Event {ev} not suported.")

    for k in ("commits", "issues", "pull_requests"):
        if k in events:
            print(f" • {k.replace('_', ' '):<14} → {counters[k]:>4} documents")
    print(f"{sum(counters.values())} documents inserted.")







if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Back-fill of GITHUB for a project, to insert it in MongoDB")
    ap.add_argument("--org",  required=True, help="Organization name on Github")
    ap.add_argument("--repo", required=True, help="Repository name on Github")
    ap.add_argument("--prj", required=True, help="External ID of the project in LD-Connect")
    ap.add_argument("--events", default="commits,issues,pull_requests",help="List separated by commas pf the events to backfill, by default: commits,issues,pull_requests")
    ap.add_argument("--from-date", help="Date FROM the backfill will be made, must be in format (YYYY-MM-DD), can also put a full date with time (2025-05-01T14:30)")
    ap.add_argument("--to-date",   help="Date UNTIL the backfill will be made, must be in format (YYYY-MM-DD), can also put a full date with time (2025-05-01T14:30)")

    ns = ap.parse_args()
    evts = [e.strip() for e in ns.events.split(",") if e.strip()]
    since = parse_dt(ns.from_date).astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z") if ns.from_date else None
    until = parse_dt(ns.to_date).astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")  if ns.to_date   else None

    collect_github( org = ns.org, repo  = ns.repo, prj= ns.prj, events= evts, since = since, until= until)

