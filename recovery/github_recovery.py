
import json, os, time, logging, datetime, itertools, re
from typing import Dict, Iterable, List, Any, Optional

import click, requests, pymongo
from dateutil import parser as dtp
from tqdm import tqdm
import pathlib, sys
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from datasources.github_handler import parse_github_event, parse_github_push_event, parse_github_issue_event, parse_github_pullrequest_event

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s  %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("ld_backfill")


MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB  = os.getenv("MONGO_DB",  "ld_connect")

GITHUB_TOKEN   = "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"


LD_EVAL_URL    = os.getenv("LD_EVAL_URL")          

client = pymongo.MongoClient(MONGO_URI)
db     = client[MONGO_DB]







def upsert_many(coll, docs: List[Dict], key: str):
    """Inserta o actualiza muchos documentos de golpe usando `key` como PK."""
    if not docs:
        return
    ops = []
    for d in docs:
        ops.append(pymongo.UpdateOne({key: d[key]}, {"$set": d}, upsert=True))
    coll.bulk_write(ops, ordered=False)



# ──────────────────────────────────────────────────────────────────────────────
#  GITHUB BACK‑FILL                                                           │
# ──────────────────────────────────────────────────────────────────────────────
def gh_paginated(url: str, headers: Dict[str, str]) -> Iterable[Dict]:
    """Itera sobre todas las páginas ‘Link: rel="next"’ devolviendo JSON list/dict."""
    while url:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        yield from r.json()
        url = r.links.get("next", {}).get("url")


def collect_github(org: str, repo: str, prj: str) -> None:
    """Recorre commits, issues y PRs y los inserta en Mongo."""


    base = f"https://api.github.com/repos/{org}/{repo}"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
    }

    # 1) COMMITS (usa lista básica y luego stats extra)
    log.info("Descargando commits…")
    commits_url = f"{base}/commits?per_page=100"
    commits_raw = list(gh_paginated(commits_url, headers))

    # Re‑formateamos cada commit a una “push” ficticia de un solo commit
    commit_payloads = []
    for c in commits_raw:
        payload = {
            "X-GitHub-Event": "push",
            "repository": {"full_name": f"{org}/{repo}"},
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
        }
        commit_payloads.append(payload)

    # 2) ISSUES
    log.info("Descargando issues…")
    issues_url = f"{base}/issues?state=all&per_page=100&filter=all"
    issues_raw = list(gh_paginated(issues_url, headers))
    issue_payloads = []
    for i in issues_raw:
        payload = {
            "X-GitHub-Event": "issues",
            "action": "opened" if i["state"] == "open" else "closed",
            "repository": {"full_name": f"{org}/{repo}"},
            "organization": {"login": org},
            "sender": i["user"],
            "issue_id": i["id"],
        }
        issue_payloads.append(payload)

    # 3) PULL REQUESTS
    log.info("Descargando pull‑requests…")
    prs_url = f"{base}/pulls?state=all&per_page=100"
    prs_raw = list(gh_paginated(prs_url, headers))
    pr_payloads = []
    for p in prs_raw:
        payload = {
            "X-GitHub-Event": "pull_request",
            "action": "closed" if p["state"] != "open" else "opened",
            "repository": {"full_name": f"{org}/{repo}"},
            "organization": {"login": org},
            "sender": p["user"],
            "pull_request": p,
        }
        pr_payloads.append(payload)


    # ── Persistir en Mongo usando tus parsers ────────────────────────────────
    total = 0
    for raw in tqdm(itertools.chain(commit_payloads, issue_payloads, pr_payloads),
                    desc="Procesando", unit="evento"):
        parsed = parse_github_event(raw)
        if parsed.get("ignored"):
            continue

        event = parsed["event"]
        
        
        if event == "commit":
            coll = db[f"github_{prj}.commits"]
            for doc in parsed["commits"]:
                doc.update({"team_name": parsed["team_name"],
                            "prj": prj,
                            "repo_name": parsed["repo_name"],
                            "sender_info": parsed["sender_info"]})
                upsert_many(coll, [doc], "sha")
                total += 1
                
                
        elif event == "issue":
            coll = db[f"github_{prj}.issues"]
            parsed["prj"] = prj
            parsed["issue_id"] = parsed["issue"]["number"]   # o usa issue["number"]

            print(f"Parsed issue: {parsed}")
            
            # print("\n")
            # print(f"Parsed issue: {parsed["issue"]}")
            
            # print("\n")
            # print(f"Parsed issue: {parsed["issue"]["number"]}")
            
            upsert_many(coll, [parsed], "issue_id")
            total += 1
            
            
        elif event == "pull_request":
            coll = db[f"github_{prj}.pull_requests"]
            parsed["prj"] = prj
            upsert_many(coll, [parsed], "pr_number")
            total += 1
    log.info("GitHub back‑fill terminado: %s documentos grabados", total)


# # ──────────────────────────────────────────────────────────────────────────────
# #  MÉTRICAS LD‑EVAL                                                           │
# # ──────────────────────────────────────────────────────────────────────────────
# def trigger_ld_eval(prj: str):
#     if not LD_EVAL_URL:
#         log.warning("LD_EVAL_URL no configurado; omito recálculo de métricas.")
#         return
#     url = f"{LD_EVAL_URL}?prj={prj}"
#     log.info("Invocando LD‑Eval: %s", url)
#     r = requests.post(url)
#     if r.ok:
#         log.info("Métricas recalculadas con éxito.")
#     else:
#         log.error("LD‑Eval devolvió %s ‑ %s", r.status_code, r.text)





# ──────────────────────────────────────────────────────────────────────────────
#  CLI                                                                       │
# ──────────────────────────────────────────────────────────────────────────────
@click.group()
def cli():
    """Herramienta de back‑fill para LD‑Connect."""
    pass

@cli.command()
@click.option("--org",  required=True, help="GitHub organization / owner")
@click.option("--repo", required=True, help="GitHub repository name")
@click.option("--prj",  required=True, help="ID de equipo (colección Mongo)")
@click.option("--recalc/--no-recalc", default=True,
              help="Lanzar recálculo de métricas al terminar")
def github(org, repo, prj, recalc):
    """Back‑fill completo desde GitHub REST API."""
    collect_github(org, repo, prj)
    # if recalc:
    #     trigger_ld_eval(prj)



if __name__ == "__main__":
    cli()
